"""
元协议 · Loop 工程 v2.0
=========================
生产级可靠性机制：StopHook + CircuitBreaker + Watchdog + RalphLoop。
(v2.0: 文件锁保护 + StorageBackend抽象接口)

使用方式：
    from meta_protocol.loop_engineering import (
        StopHook, CircuitBreaker, Watchdog, RalphLoop, FileLock, StorageBackend
    )

    # FileLock: 文件锁防止并发写入
    lock = FileLock("/tmp/agent_state.lock")
    with lock:
        ralph.save(agent_name, state_dict)

    # StorageBackend: 可插拔存储后端
    backend = FileStorageBackend(save_dir="./agent_states")
    ralph = RalphLoop(backend=backend)
    ralph.save(agent_name, state_dict)
    state = ralph.load(agent_name)
"""

from __future__ import annotations

import asyncio
import fcntl
import json
import logging
import os
import signal
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


# ============================================================
# FileLock: 文件锁
# ============================================================

class FileLock:
    """文件锁 —— 用于保护持久化操作的并发安全。

    使用 fcntl.flock 实现 POSIX 文件锁，跨进程安全。

    使用方式：
        lock = FileLock("/tmp/agent_states/.lock")
        with lock:
            # 受保护的写操作
            save_state(data)

        # 或者手动管理
        lock.acquire()
        try:
            save_state(data)
        finally:
            lock.release()
    """

    def __init__(self, lock_path: str, timeout: float = 10.0):
        self._lock_path = lock_path
        self._timeout = timeout
        self._fd: Optional[int] = None

    def acquire(self) -> bool:
        """获取文件锁。

        Returns:
            True: 成功获取锁
            False: 超时未获取到锁
        """
        try:
            os.makedirs(os.path.dirname(self._lock_path), exist_ok=True)
            self._fd = os.open(self._lock_path, os.O_CREAT | os.O_RDWR, 0o644)

            start_time = time.time()
            while True:
                try:
                    fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    return True
                except BlockingIOError:
                    if time.time() - start_time >= self._timeout:
                        logger.warning(f"文件锁获取超时: {self._lock_path}")
                        return False
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"文件锁异常: {e}")
            return False

    def release(self):
        """释放文件锁"""
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
                os.close(self._fd)
            except Exception:
                pass
            finally:
                self._fd = None

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"无法获取文件锁: {self._lock_path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def __del__(self):
        self.release()


# ============================================================
# StorageBackend: 可插拔存储后端
# ============================================================

class StorageBackend(ABC):
    """存储后端抽象接口 —— 支持文件系统、Redis、数据库等。

    实现者需要实现 save/load/delete 三个方法。
    """

    @abstractmethod
    def save(self, key: str, data: dict) -> None:
        """保存数据"""
        ...

    @abstractmethod
    def load(self, key: str) -> Optional[dict]:
        """加载数据"""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """删除数据"""
        ...


class FileStorageBackend(StorageBackend):
    """文件系统存储后端（默认实现）"""

    def __init__(self, save_dir: str):
        self._save_dir = save_dir
        os.makedirs(self._save_dir, exist_ok=True)
        self._lock = FileLock(os.path.join(self._save_dir, ".storage.lock"))

    def _key_to_path(self, key: str) -> str:
        """将 key 转换为文件路径"""
        safe_key = key.replace("/", "_").replace("\\", "_")
        return os.path.join(self._save_dir, f"{safe_key}.json")

    def save(self, key: str, data: dict) -> None:
        """原子写入保存数据"""
        filepath = self._key_to_path(key)
        data_with_meta = {
            "key": key,
            "timestamp": time.time(),
            "data": data,
        }
        with self._lock:
            tmp_path = filepath + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data_with_meta, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, filepath)

    def load(self, key: str) -> Optional[dict]:
        """加载数据"""
        filepath = self._key_to_path(key)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("data")
        except (json.JSONDecodeError, IOError):
            return None

    def delete(self, key: str) -> None:
        """删除数据"""
        filepath = self._key_to_path(key)
        with self._lock:
            if os.path.exists(filepath):
                os.remove(filepath)


# ============================================================
# StopHook: 终止条件检查
# ============================================================

class StopHook:
    """循环终止钩子 —— 防止 Agent 无限循环。

    检查项：
        - 最大轮数（max_rounds）
        - 最大Token消耗（max_tokens）
        - 最大时间（max_seconds）
        - 自定义终止条件（custom_condition）
    """

    def __init__(
        self,
        max_rounds: int = 100,
        max_tokens: int = 200000,
        max_seconds: float = 3600,
        custom_condition: Callable[[], bool] = None,
    ):
        self.max_rounds = max_rounds
        self.max_tokens = max_tokens
        self.max_seconds = max_seconds
        self._custom_condition = custom_condition
        self._start_time = time.time()
        self._round = 0
        self._total_tokens = 0
        self._stopped = False
        self._stop_reason = ""

    def check(self, round_num: int = None, token_count: int = 0) -> bool:
        """检查是否应该停止。

        Returns:
            True 表示应该停止，False 表示可以继续
        """
        if self._stopped:
            return True

        if round_num is not None:
            self._round = round_num
        else:
            self._round += 1
        self._total_tokens += token_count

        # 检查轮数
        if self._round >= self.max_rounds:
            self._stop_reason = f"达到最大轮数 {self.max_rounds}"
            self._stopped = True
            return True

        # 检查Token
        if self._total_tokens >= self.max_tokens:
            self._stop_reason = f"达到最大Token {self.max_tokens}"
            self._stopped = True
            return True

        # 检查时间
        elapsed = time.time() - self._start_time
        if elapsed >= self.max_seconds:
            self._stop_reason = f"超时 {self.max_seconds}s"
            self._stopped = True
            return True

        # 自定义条件
        if self._custom_condition and self._custom_condition():
            self._stop_reason = "自定义终止条件触发"
            self._stopped = True
            return True

        return False

    @property
    def stop_reason(self) -> str:
        return self._stop_reason

    @property
    def stats(self) -> dict:
        return {
            "rounds": self._round,
            "total_tokens": self._total_tokens,
            "elapsed_seconds": time.time() - self._start_time,
            "stopped": self._stopped,
            "stop_reason": self._stop_reason,
        }

    def reset(self):
        """重置（用于迭代循环）"""
        self._start_time = time.time()
        self._round = 0
        self._total_tokens = 0
        self._stopped = False
        self._stop_reason = ""


# ============================================================
# CircuitBreaker: 熔断保护
# ============================================================

class CircuitBreakerOpen(Exception):
    """熔断器打开异常"""
    pass


class CircuitBreaker:
    """熔断器 —— 连续失败后拒绝调用。

    三态模型：
        CLOSED（正常）→ 连续失败N次 → OPEN（拒绝）
        OPEN → 等待reset_timeout → HALF_OPEN（试探）
        HALF_OPEN → 成功 → CLOSED / 失败 → OPEN
    """

    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._state = self.STATE_CLOSED
        self._last_failure_time = 0.0
        self._total_calls = 0
        self._total_failures = 0

    async def call(self, coro) -> Any:
        """执行受保护的调用。

        Raises:
            CircuitBreakerOpen: 熔断器已打开
        """
        if self._state == self.STATE_OPEN:
            if time.time() - self._last_failure_time >= self.reset_timeout:
                self._state = self.STATE_HALF_OPEN
                logger.info("熔断器进入半开状态，试探性调用")
            else:
                raise CircuitBreakerOpen(
                    f"熔断器打开，{self.reset_timeout - (time.time() - self._last_failure_time):.0f}s后重试"
                )

        self._total_calls += 1
        try:
            result = await coro
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self._state == self.STATE_HALF_OPEN:
            self._state = self.STATE_CLOSED
            self._failure_count = 0
            logger.info("熔断器恢复关闭")

    def _on_failure(self):
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.time()
        if self._failure_count >= self.failure_threshold:
            self._state = self.STATE_OPEN
            logger.warning(f"熔断器打开: 连续{self._failure_count}次失败")

    @property
    def state(self) -> str:
        return self._state

    @property
    def stats(self) -> dict:
        return {
            "state": self._state,
            "failure_count": self._failure_count,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
        }


# ============================================================
# Watchdog: 心跳监控
# ============================================================

class Watchdog:
    """看门狗 —— 独立异步任务监控Agent心跳。

    工作原理：
        - 启动独立异步任务
        - 定期检查心跳时间
        - 超时则触发回调（如重启Agent）
        - 不依赖Agent内部状态，即使Agent卡死也能检测
    """

    def __init__(
        self,
        agent_name: str,
        timeout: float = 30.0,
        on_timeout: Callable[[str], Any] = None,
        check_interval: float = 5.0,
    ):
        self.agent_name = agent_name
        self.timeout = timeout
        self._on_timeout = on_timeout or (lambda name: logger.error(f"Agent {name} 心跳超时!"))
        self._check_interval = check_interval
        self._last_heartbeat = time.time()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._heartbeat_count = 0
        self._timeout_count = 0

    def heartbeat(self):
        """发送心跳 —— Agent 在每次循环中调用"""
        self._last_heartbeat = time.time()
        self._heartbeat_count += 1

    async def start(self):
        """启动看门狗监控任务"""
        self._running = True
        self._last_heartbeat = time.time()
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"看门狗启动: {self.agent_name}, 超时={self.timeout}s")

    async def stop(self):
        """停止看门狗"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"看门狗停止: {self.agent_name}")

    async def _monitor_loop(self):
        while self._running:
            await asyncio.sleep(self._check_interval)
            elapsed = time.time() - self._last_heartbeat
            if elapsed > self.timeout:
                self._timeout_count += 1
                logger.warning(f"看门狗: {self.agent_name} 心跳超时 {elapsed:.1f}s (第{self._timeout_count}次)")
                try:
                    result = self._on_timeout(self.agent_name)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as e:
                    logger.error(f"看门狗回调异常: {e}")

    @property
    def stats(self) -> dict:
        return {
            "agent": self.agent_name,
            "last_heartbeat": self._last_heartbeat,
            "heartbeat_count": self._heartbeat_count,
            "timeout_count": self._timeout_count,
            "running": self._running,
        }


# ============================================================
# RalphLoop: 文件系统状态持久化
# ============================================================

class RalphLoop:
    """Ralph Loop —— 文件系统状态持久化。

    v2.0: 支持可插拔 StorageBackend + 文件锁保护。

    工作原理：
        - Agent 状态随时保存到文件
        - 崩溃后可从断点恢复
        - 不依赖外部数据库，纯文件系统

    命名来源：
        Ralph 是"捡破烂"的谐音，也是"恢复"（Recovery）的含义。
    """

    def __init__(self, save_dir: str = None, backend: StorageBackend = None):
        if backend:
            self._backend = backend
        else:
            self._backend = FileStorageBackend(
                save_dir or os.path.join(os.path.dirname(__file__), ".ralph_states")
            )

    def save(self, agent_name: str, state: dict):
        """保存Agent状态"""
        self._backend.save(agent_name, state)

    def load(self, agent_name: str) -> Optional[dict]:
        """加载Agent状态"""
        return self._backend.load(agent_name)

    def delete(self, agent_name: str):
        """删除Agent状态"""
        self._backend.delete(agent_name)

    @property
    def backend(self) -> StorageBackend:
        return self._backend