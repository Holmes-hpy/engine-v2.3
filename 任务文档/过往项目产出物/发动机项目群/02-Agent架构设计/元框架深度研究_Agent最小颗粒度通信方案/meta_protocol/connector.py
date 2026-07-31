"""
元协议 · 连接器（Connector）v2.0
================================
四种连接器实现，对应四种拓扑模式。
(v2.0: 适配10要素，RouteEntry 使用 addressing + visibility 替代 reachability)

使用方式：
    from meta_protocol.connector import Hub, Pipe, Router, Broker

    # Hub: 广播/组播中心
    hub = Hub()
    hub.register(agent1, agent2, agent3)
    await hub.broadcast(sender=agent1, msg=msg)

    # Pipe: 点对点管道
    pipe = Pipe(agent1, agent2)
    await pipe.send(msg)

    # Router: 路由表
    router = Router()
    router.add_route(agent1, agent2, addressing="unicast", visibility="private")
    await router.route(msg, target=agent2)

    # Broker: 消息代理（异步+持久化）
    broker = Broker()
    broker.subscribe("research-001", agent1)
    await broker.publish("research-001", msg)

设计原则：
    基于 AgentScope Msg 的 observe() 机制，零侵入式。
    不依赖 AgentScope 源码，通过 asyncio.Queue 实现解耦。
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from meta_protocol.envelope import Envelope, MsgType, Priority


# ============================================================
# 模拟 AgentScope Agent 接口（与真实 AgentScope 兼容）
# ============================================================

class AgentRef:
    """Agent 引用 —— 包装 AgentScope Agent 实例。

    只暴露 observe() 方法，不侵入 Agent 内部逻辑。
    """

    def __init__(self, name: str, agent: Any = None):
        self.name = name
        self._agent = agent
        self._inbox: asyncio.Queue = asyncio.Queue()

    async def observe(self, msg: Any):
        """将消息注入 Agent 的上下文。

        如果有关联的真实 AgentScope Agent，调用其 observe()；
        否则消息存入内部队列供测试使用。
        """
        if self._agent and hasattr(self._agent, "observe"):
            await self._agent.observe(msg)
        await self._inbox.put(msg)

    async def receive(self, timeout: float = 5.0) -> Optional[Any]:
        """从内部队列取消息（测试用）"""
        try:
            return await asyncio.wait_for(self._inbox.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def __repr__(self):
        return f"AgentRef({self.name!r})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, AgentRef) and self.name == other.name


# ============================================================
# 连接器基类
# ============================================================

class BaseConnector:
    """连接器基类 —— 统一接口"""

    def __init__(self, name: str = "connector"):
        self.name = name
        self._stats = {"sent": 0, "received": 0, "errors": 0}

    async def send(self, msg: Any, target: Any = None, **kwargs):
        raise NotImplementedError

    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ============================================================
# Hub: 广播/组播中心
# ============================================================

class Hub(BaseConnector):
    """广播/组播中心 —— 对应 MsgHub 拓扑。

    工作原理：
        - 维护参与者列表
        - broadcast() 将消息发送给除发送者外的所有参与者
        - multicast() 将消息发送给指定参与者子集
    """

    def __init__(self, name: str = "hub"):
        super().__init__(name)
        self._participants: dict[str, AgentRef] = {}

    def register(self, *agents: AgentRef):
        """注册参与者"""
        for agent in agents:
            self._participants[agent.name] = agent

    def unregister(self, agent: AgentRef):
        """移除参与者"""
        self._participants.pop(agent.name, None)

    @property
    def participants(self) -> list[str]:
        return list(self._participants.keys())

    async def broadcast(self, sender: AgentRef, msg: Any):
        """广播消息给所有其他参与者"""
        self._stats["sent"] += 1
        tasks = []
        for name, agent in self._participants.items():
            if name != sender.name:
                tasks.append(agent.observe(msg))
        if tasks:
            await asyncio.gather(*tasks)

    async def multicast(self, sender: AgentRef, msg: Any, targets: list[str]):
        """组播消息给指定参与者"""
        self._stats["sent"] += 1
        tasks = []
        for name in targets:
            if name in self._participants and name != sender.name:
                tasks.append(self._participants[name].observe(msg))
        if tasks:
            await asyncio.gather(*tasks)

    async def send(self, msg: Any, target: Any = None, **kwargs):
        """统一send接口，默认广播"""
        sender = kwargs.get("sender")
        if target:
            await self.multicast(sender, msg, [target] if isinstance(target, str) else target)
        else:
            await self.broadcast(sender, msg)


# ============================================================
# Pipe: 点对点管道
# ============================================================

class Pipe(BaseConnector):
    """点对点管道 —— 对应 Isolated / Pipeline 拓扑。

    工作原理：
        - 两个 Agent 之间直连
        - send() 将消息从一端发送到另一端
        - 支持双向：agent_a → agent_b 和 agent_b → agent_a
    """

    def __init__(self, agent_a: AgentRef, agent_b: AgentRef, name: str = "pipe"):
        super().__init__(name)
        self.agent_a = agent_a
        self.agent_b = agent_b

    async def send(self, msg: Any, target: Any = None, **kwargs):
        """发送消息到对端"""
        sender = kwargs.get("sender")
        self._stats["sent"] += 1

        if target is None:
            # 自动判断对端
            target = self.agent_b if sender == self.agent_a else self.agent_a
        else:
            target = target if isinstance(target, AgentRef) else (
                self.agent_a if target == self.agent_a.name else self.agent_b
            )

        await target.observe(msg)


# ============================================================
# Router: 路由表
# ============================================================

@dataclass
class RouteEntry:
    target: AgentRef
    addressing: str = "unicast"     # v2.0: 从 reachability 拆分为 addressing + visibility
    visibility: str = "private"
    priority: int = 0


class Router(BaseConnector):
    """路由表 —— 根据可达性域动态选择目标。

    工作原理：
        - 维护路由表：{target_name: RouteEntry}
        - route() 根据 Envelope 的 routing 提示选择目标
        - 支持优先级：同可达性域下按优先级选择
    """

    def __init__(self, name: str = "router"):
        super().__init__(name)
        self._routes: dict[str, RouteEntry] = {}

    def add_route(
        self,
        agent: AgentRef,
        addressing: str = "unicast",
        visibility: str = "private",
        priority: int = 0,
    ):
        """添加路由条目

        Args:
            agent: 目标Agent
            addressing: 寻址方式（unicast/multicast/broadcast）
            visibility: 可见性域（private/group/global）
            priority: 优先级
        """
        self._routes[agent.name] = RouteEntry(
            target=agent,
            addressing=addressing,
            visibility=visibility,
            priority=priority,
        )

    def remove_route(self, agent_name: str):
        """移除路由条目"""
        self._routes.pop(agent_name, None)

    def resolve(
        self,
        addressing: str = None,
        visibility: str = None,
    ) -> list[AgentRef]:
        """根据可达性域解析目标列表。

        Args:
            addressing: 寻址方式，None 表示匹配所有
            visibility: 可见性域，None 表示匹配所有

        Returns:
            匹配的 AgentRef 列表，按优先级降序
        """
        entries = list(self._routes.values())

        if addressing is not None:
            entries = [e for e in entries if e.addressing == addressing]
        if visibility is not None:
            entries = [e for e in entries if e.visibility == visibility]

        entries.sort(key=lambda e: e.priority, reverse=True)
        return [e.target for e in entries]

    def resolve_address(self, addr_str: str) -> list[AgentRef]:
        """兼容旧版 reachability 字符串格式解析。

        Args:
            addr_str: 如 "unicast+private" 或 "unicast"

        Returns:
            匹配的 AgentRef 列表
        """
        if "+" in addr_str:
            addressing, visibility = addr_str.split("+", 1)
        else:
            addressing, visibility = addr_str, None
        return self.resolve(addressing=addressing, visibility=visibility)

    async def route(
        self,
        msg: Any,
        target: Any = None,
        addressing: str = None,
        visibility: str = None,
        **kwargs,
    ):
        """路由消息到目标"""
        self._stats["sent"] += 1

        if target:
            if isinstance(target, AgentRef):
                await target.observe(msg)
            else:
                entry = self._routes.get(target)
                if entry:
                    await entry.target.observe(msg)
        else:
            targets = self.resolve(addressing=addressing, visibility=visibility)
            if targets:
                await asyncio.gather(*[t.observe(msg) for t in targets])

    async def send(self, msg: Any, target: Any = None, **kwargs):
        await self.route(msg, target=target, **kwargs)


# ============================================================
# Broker: 消息代理（异步+持久化）
# ============================================================

class Broker(BaseConnector):
    """消息代理 —— 支持异步、持久化、重试。

    工作原理：
        - 基于发布-订阅模型
        - 每个 topic 维护订阅者列表
        - 支持消息持久化到文件
        - 支持重试机制
    """

    def __init__(self, name: str = "broker", storage_dir: str = None, max_retries: int = 3):
        super().__init__(name)
        self._subscriptions: dict[str, list[AgentRef]] = defaultdict(list)
        self._storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), ".broker_storage")
        self._max_retries = max_retries

    def subscribe(self, topic: str, agent: AgentRef):
        """订阅主题"""
        if agent not in self._subscriptions[topic]:
            self._subscriptions[topic].append(agent)

    def unsubscribe(self, topic: str, agent: AgentRef):
        """取消订阅"""
        self._subscriptions[topic] = [a for a in self._subscriptions[topic] if a != agent]

    async def publish(self, topic: str, msg: Any, persist: bool = False):
        """发布消息到主题"""
        self._stats["sent"] += 1

        if persist:
            self._persist(topic, msg)

        subscribers = self._subscriptions.get(topic, [])
        if not subscribers:
            return

        tasks = []
        for agent in subscribers:
            tasks.append(self._deliver_with_retry(agent, msg))
        await asyncio.gather(*tasks)

    async def _deliver_with_retry(self, agent: AgentRef, msg: Any):
        """带重试的消息投递"""
        for attempt in range(self._max_retries):
            try:
                await agent.observe(msg)
                return
            except Exception:
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(0.1 * (2 ** attempt))
                else:
                    self._stats["errors"] += 1

    def _persist(self, topic: str, msg: Any):
        """持久化消息到文件"""
        try:
            os.makedirs(self._storage_dir, exist_ok=True)
            filename = os.path.join(self._storage_dir, f"{topic}_{int(time.time())}.json")
            env = Envelope.unwrap(msg)
            data = {
                "topic": topic,
                "timestamp": time.time(),
                "envelope": env.model_dump(mode="json") if env else None,
                "content": str(msg.content) if hasattr(msg, "content") else str(msg),
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            self._stats["errors"] += 1

    async def send(self, msg: Any, target: Any = None, **kwargs):
        topic = kwargs.get("topic", "default")
        await self.publish(topic, msg, persist=kwargs.get("persist", False))