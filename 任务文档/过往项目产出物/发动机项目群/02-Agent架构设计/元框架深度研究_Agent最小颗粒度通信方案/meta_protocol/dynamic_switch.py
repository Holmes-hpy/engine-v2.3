"""
元协议 · 动态切换控制器 v2.0
==============================
Agent 运行时自主决策通信配置的核心引擎。
(v2.0: LLM辅助决策 + 切换频率限制，适配10要素体系)

使用方式：
    from meta_protocol.dynamic_switch import DynamicSwitchController
    controller = DynamicSwitchController(agent, port_contract, constraint_engine)
    await controller.analyze_and_switch(incoming_msg)

工作原理：
    1. analyze(): 规则引擎 + LLM辅助分析任务语义，推荐新配置
    2. validate(): 约束引擎校验新配置
    3. switch(): 执行切换，更新连接器
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional

from meta_protocol.envelope import Envelope, MsgType
from meta_protocol.port_contract import (
    PortContract,
    AddressingMode,
    VisibilityDomain,
    Distribution,
    MemoryBelonging,
    ContextIsolation,
    Lifecycle,
    StateBoundary,
)
from meta_protocol.constraint_engine import ConstraintEngine, ValidationResult
from meta_protocol.connector import AgentRef, Hub, Pipe, Router, Broker, BaseConnector

logger = logging.getLogger(__name__)


class SwitchRecommendation:
    """切换建议"""

    def __init__(self, reason: str, new_port: PortContract, confidence: float = 0.8):
        self.reason = reason
        self.new_port = new_port
        self.confidence = confidence

    def __repr__(self):
        return f"SwitchRecommendation({self.reason}, conf={self.confidence:.2f})"


class DynamicSwitchController:
    """动态切换控制器。

    核心职责：
        1. 规则引擎分析任务语义 → 推荐通信配置
        2. LLM辅助分析（可选）→ 提升决策准确性
        3. 约束引擎校验 → 拒绝非法配置
        4. 频率限制 → 防止频繁切换
        5. 执行切换 → 更新连接器绑定
    """

    def __init__(
        self,
        agent: AgentRef,
        port: PortContract,
        engine: ConstraintEngine = None,
        llm_analyzer: Callable = None,
        min_switch_interval: float = 5.0,
        max_switches_per_minute: int = 12,
    ):
        self.agent = agent
        self.port = port
        self.engine = engine or ConstraintEngine()
        self._connector: Optional[BaseConnector] = None
        self._history: list[tuple[PortContract, str]] = []

        # v2.0: LLM辅助决策
        self._llm_analyzer = llm_analyzer

        # v2.0: 切换频率限制
        self._min_switch_interval = min_switch_interval
        self._max_switches_per_minute = max_switches_per_minute
        self._last_switch_time: float = 0.0
        self._switch_timestamps: list[float] = []

    def bind_connector(self, connector: BaseConnector):
        """绑定连接器，切换时自动更新"""
        self._connector = connector

    def set_llm_analyzer(self, analyzer: Callable):
        """设置 LLM 辅助分析器。

        analyzer 签名: async def analyzer(task_description: str, current_port: PortContract) -> dict
        返回: {"reason": str, "overrides": dict, "confidence": float}
        """
        self._llm_analyzer = analyzer

    # ============================================================
    # 频率限制
    # ============================================================

    def _check_frequency_limit(self) -> bool:
        """检查是否超过切换频率限制。

        Returns:
            True: 允许切换
            False: 频率超限，拒绝切换
        """
        now = time.time()

        # 检查最小间隔
        if now - self._last_switch_time < self._min_switch_interval:
            logger.debug(f"切换频率超限: 距上次切换仅 {now - self._last_switch_time:.1f}s")
            return False

        # 检查每分钟上限
        self._switch_timestamps = [t for t in self._switch_timestamps if now - t < 60.0]
        if len(self._switch_timestamps) >= self._max_switches_per_minute:
            logger.warning(f"切换频率超限: 过去60秒内已有 {len(self._switch_timestamps)} 次切换")
            return False

        return True

    def _record_switch(self):
        """记录切换时间"""
        now = time.time()
        self._last_switch_time = now
        self._switch_timestamps.append(now)
        # 清理旧记录
        self._switch_timestamps = [t for t in self._switch_timestamps if now - t < 60.0]

    # ============================================================
    # 核心方法：分析 + 切换
    # ============================================================

    def analyze(self, msg: Any) -> SwitchRecommendation:
        """分析消息语义，推荐通信配置（规则引擎）。

        基于规则引擎（非LLM），确定性高，响应快。
        """
        env = Envelope.unwrap(msg)

        # 规则1: 控制消息 → 切换到扇出模式
        if env and env.msg_type == MsgType.CONTROL:
            return SwitchRecommendation(
                reason="收到控制消息，切换到扇出模式创建子Agent",
                new_port=self.port.override(
                    distribution=Distribution.FAN_OUT,
                    lifecycle=Lifecycle.TEMPORARY,
                ),
                confidence=0.9,
            )

        # 规则2: 任务消息 → 如果是独立任务，保持隔离
        if env and env.msg_type == MsgType.TASK:
            if self.port.memory_belonging == MemoryBelonging.SHARED:
                return SwitchRecommendation(
                    reason="收到任务消息，建议切换到独占Memory独立执行",
                    new_port=self.port.override(
                        memory_belonging=MemoryBelonging.EXCLUSIVE,
                        context_isolation=ContextIsolation.FULL,
                        addressing=AddressingMode.UNICAST,
                        visibility=VisibilityDomain.PRIVATE,
                    ),
                    confidence=0.7,
                )
            return SwitchRecommendation(
                reason="任务消息，保持当前隔离配置",
                new_port=self.port,
                confidence=0.9,
            )

        # 规则3: 数据消息 → 如果是扇出模式，切换到扇入收集
        if env and env.msg_type == MsgType.DATA:
            if self.port.distribution == Distribution.FAN_OUT:
                return SwitchRecommendation(
                    reason="收到数据消息，切换到扇入模式收集结果",
                    new_port=self.port.override(distribution=Distribution.FAN_IN),
                    confidence=0.85,
                )

        # 规则4: 事件消息 → 保持当前配置，不切换
        if env and env.msg_type == MsgType.EVENT:
            return SwitchRecommendation(
                reason="事件消息，保持当前配置不变",
                new_port=self.port,
                confidence=0.95,
            )

        # 默认: 不切换
        return SwitchRecommendation(
            reason="无明确切换信号，保持当前配置",
            new_port=self.port,
            confidence=0.5,
        )

    async def analyze_with_llm(self, msg: Any) -> Optional[SwitchRecommendation]:
        """使用 LLM 辅助分析（如果配置了 LLM 分析器）。

        LLM 分析器可以提供比规则引擎更细粒度的判断。
        """
        if self._llm_analyzer is None:
            return None

        try:
            # 提取任务描述
            task_desc = ""
            if hasattr(msg, "content"):
                task_desc = str(msg.content)[:500]  # 截断以防过长

            result = await self._llm_analyzer(task_desc, self.port)
            if result and result.get("overrides"):
                return SwitchRecommendation(
                    reason=result.get("reason", "LLM辅助决策"),
                    new_port=self.port.override(**result["overrides"]),
                    confidence=result.get("confidence", 0.7),
                )
        except Exception as e:
            logger.warning(f"LLM辅助分析失败: {e}")

        return None

    async def switch(self, recommendation: SwitchRecommendation) -> ValidationResult:
        """执行切换：校验 → 频率检查 → 记录 → 切换。

        Returns:
            ValidationResult: 校验结果
        """
        result = self.engine.validate_switch(self.port, recommendation.new_port)

        if not result.is_valid:
            logger.warning(f"切换被拒绝: {result.summary()}")
            return result

        # 频率限制检查
        if not self._check_frequency_limit():
            result.add(type(
                'Violation', (), {
                    'rule_id': 'FREQ-01',
                    'level': type('ConstraintLevel', (), {'HARD': 'hard'})().HARD,
                    'message': '切换频率超限，拒绝本次切换',
                    'suggestion': f'最小切换间隔 {self._min_switch_interval}s，每分钟最多 {self._max_switches_per_minute} 次'
                }
            )())
            return result

        # 记录历史
        self._history.append((self.port, recommendation.reason))
        self.port = recommendation.new_port
        self._record_switch()

        logger.info(f"切换成功: {self.agent.name} → {self.port.summary()}")

        # 更新连接器绑定
        if self._connector:
            self._update_connector()

        return result

    async def analyze_and_switch(self, msg: Any) -> tuple[SwitchRecommendation, ValidationResult]:
        """一键分析 + 切换（规则引擎 + LLM辅助）"""
        rec = self.analyze(msg)

        # LLM辅助分析（低置信度时）
        if rec.confidence < 0.7:
            llm_rec = await self.analyze_with_llm(msg)
            if llm_rec and llm_rec.confidence > rec.confidence:
                rec = llm_rec

        if rec.confidence < 0.6:
            logger.debug(f"低置信度({rec.confidence:.2f})，跳过切换: {rec.reason}")
            return rec, ValidationResult(is_valid=True)

        result = await self.switch(rec)
        return rec, result

    def _update_connector(self):
        """更新连接器绑定"""
        if isinstance(self._connector, Hub):
            # Hub 模式下，切换可达性域后重新注册
            pass
        elif isinstance(self._connector, Pipe):
            # Pipe 模式下，切换可达性域不需要操作
            pass
        elif isinstance(self._connector, Router):
            # Router 模式下，更新路由表
            pass

    # ============================================================
    # Prompt 注入（用于 AgentScope 的 onSystemPrompt）
    # ============================================================

    def get_system_prompt_appendix(self) -> str:
        """生成注入 System Prompt 的协议说明。

        Agent 理解这段后，可以在 LLM 推理中自主决策是否切换配置。
        """
        return f"""
## 通信协议配置（当前状态）

你可以根据需要调整通信模式。当前配置：
- 寻址方式: {self.port.addressing.value}
- 可见性域: {self.port.visibility.value}
- 分发策略: {self.port.distribution.value}
- Memory归属: {self.port.memory_belonging.value}
- 上下文隔离: {self.port.context_isolation.value}
- 生命周期: {self.port.lifecycle.value}

可用的寻址方式：unicast（点对点）、multicast（组播）、broadcast（广播）
可用的可见性域：private（私有）、group（组内）、global（全局）
可用的分发策略：direct（直接）、fan_out（扇出）、fan_in（扇入）、sequential（顺序）、round_robin（轮询）
可用的Memory归属：shared（共享）、exclusive（独占）、inherited（继承）
可用的上下文隔离：full（完全隔离）、partial（部分隔离）、none（无隔离）

切换建议：
- 需要独立执行任务 → unicast + private + exclusive + full
- 需要多人协作讨论 → multicast + group + shared + none
- 需要创建多个子Agent → fan_out + temporary
- 需要收集结果 → fan_in
- 审计场景 → unicast + group（点对点但组内可见）
"""

    @property
    def history(self) -> list[str]:
        return [f"{reason} → {port.summary()}" for port, reason in self._history[-10:]]

    @property
    def switch_stats(self) -> dict:
        """切换统计信息"""
        now = time.time()
        recent_switches = [t for t in self._switch_timestamps if now - t < 60.0]
        return {
            "total_switches": len(self._history),
            "last_switch_ago": now - self._last_switch_time if self._last_switch_time > 0 else None,
            "switches_last_minute": len(recent_switches),
            "min_interval": self._min_switch_interval,
            "max_per_minute": self._max_switches_per_minute,
        }