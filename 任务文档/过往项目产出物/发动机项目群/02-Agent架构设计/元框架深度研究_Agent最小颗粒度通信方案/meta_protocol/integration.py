"""
元协议 · AgentScope 2.0 集成中间件 v2.0
========================================
洋葱模型（Onion Model）5个挂载点的中间件实现。
(v2.0: 适配10要素体系，更新System Prompt注入)

使用方式：
    # 在 AgentScope Agent 创建时挂载
    from agentscope.agent import ReActAgent
    from meta_protocol.integration import MetaProtocolMiddleware

    agent = ReActAgent(name="Researcher", ...)
    middleware = MetaProtocolMiddleware(agent, port_contract)
    agent.register_middleware(middleware)

挂载点：
    onSystemPrompt  — 注入10要素说明到System Prompt
    onModelCall     — 消息格式校验（Envelope + HMAC验签）
    onReasoning     — 提取通信决策，触发动态切换
    onActing        — 约束规则校验
    onAgent         — 生命周期管理
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from meta_protocol.envelope import Envelope, MsgType, Priority
from meta_protocol.port_contract import (
    PortContract,
    AddressingMode,
    VisibilityDomain,
    MemoryBelonging,
    ContextIsolation,
)
from meta_protocol.constraint_engine import ConstraintEngine, ValidationResult
from meta_protocol.dynamic_switch import DynamicSwitchController, SwitchRecommendation
from meta_protocol.connector import AgentRef, Hub, BaseConnector

logger = logging.getLogger(__name__)


class MetaProtocolMiddleware:
    """元协议中间件 —— 挂载到 AgentScope 洋葱模型。

    5个挂载点：
        on_system_prompt: 注入协议说明
        on_model_call: 校验消息格式
        on_reasoning: 提取通信决策
        on_acting: 约束校验
        on_agent: 生命周期管理
    """

    def __init__(
        self,
        agent: Any,
        port: PortContract = None,
        connector: BaseConnector = None,
        engine: ConstraintEngine = None,
    ):
        self.agent = agent
        self.agent_name = getattr(agent, "name", "unknown")
        self.agent_ref = AgentRef(self.agent_name, agent)
        self.port = port or PortContract.agent_scope_default()
        self.connector = connector
        self.engine = engine or ConstraintEngine()
        self.controller = DynamicSwitchController(self.agent_ref, self.port, self.engine)
        if connector:
            self.controller.bind_connector(connector)

    # ============================================================
    # Mount Point 1: onSystemPrompt
    # ============================================================

    def on_system_prompt(self, prompt: str) -> str:
        """在 System Prompt 末尾追加10要素协议说明。

        AgentScope 中间件签名: onSystemPrompt(prompt: str) -> str
        """
        appendix = self.controller.get_system_prompt_appendix()
        return prompt + "\n" + appendix

    # ============================================================
    # Mount Point 2: onModelCall
    # ============================================================

    def on_model_call(self, msg: Any) -> Any:
        """在 LLM 调用前校验消息格式（含 HMAC 验签）。

        AgentScope 中间件签名: onModelCall(msg: Msg) -> Msg
        """
        env = Envelope.unwrap(msg)
        if env is None:
            logger.debug(f"[{self.agent_name}] 消息无协议信封或签名无效，注入默认信封")
            env = Envelope(msg_type=MsgType.TASK, priority=Priority.NORMAL)
            msg = env.wrap(msg)
        return msg

    # ============================================================
    # Mount Point 3: onReasoning
    # ============================================================

    async def on_reasoning(self, msg: Any, reasoning_output: str) -> str:
        """在 Agent 推理后提取通信决策。

        AgentScope 中间件签名: onReasoning(msg: Msg, output: str) -> str

        分析推理输出，如果Agent表达了切换意图，触发动态切换。
        """
        # 关键词匹配（10要素版本）
        switch_keywords = {
            "扇出": {"distribution": "fan_out", "lifecycle": "temporary"},
            "收集": {"distribution": "fan_in"},
            "讨论": {
                "addressing": "multicast", "visibility": "group",
                "memory_belonging": "shared", "context_isolation": "none",
            },
            "独立调研": {
                "addressing": "unicast", "visibility": "private",
                "memory_belonging": "exclusive", "context_isolation": "full",
            },
            "独立": {
                "addressing": "unicast", "visibility": "private",
                "memory_belonging": "exclusive", "context_isolation": "full",
            },
            "审计": {
                "addressing": "unicast", "visibility": "group",
            },
        }

        for keyword, overrides in switch_keywords.items():
            if keyword in reasoning_output:
                valid_overrides = {k: v for k, v in overrides.items() if v is not None}
                rec = SwitchRecommendation(
                    reason=f"推理输出检测到关键词'{keyword}'，推荐切换",
                    new_port=self.port.override(**valid_overrides),
                    confidence=0.7,
                )
                await self.controller.switch(rec)
                break

        return reasoning_output

    # ============================================================
    # Mount Point 4: onActing
    # ============================================================

    async def on_acting(self, msg: Any, action: Any) -> Any:
        """在 Agent 执行动作前校验约束。

        AgentScope 中间件签名: onActing(msg: Msg, action: Any) -> Any

        检查：
        - 是否能创建Agent
        - 是否能发送消息
        - 是否超过递归深度
        """
        # 创建Agent权限检查
        if hasattr(action, "type") and "create_agent" in str(action.type).lower():
            if not self.port.capabilities.can_create_agent:
                logger.warning(f"[{self.agent_name}] 无创建Agent权限，拦截动作")
                raise PermissionError(f"Agent {self.agent_name} 无权创建子Agent")

            if self.port.capabilities.max_recursion_depth <= 0:
                raise PermissionError(f"Agent {self.agent_name} 已达最大递归深度")

        return action

    # ============================================================
    # Mount Point 5: onAgent
    # ============================================================

    def on_agent_created(self, child_agent: Any):
        """Agent 创建时回调"""
        logger.info(f"[{self.agent_name}] 创建子Agent: {getattr(child_agent, 'name', 'unknown')}")
        self.port.capabilities.max_recursion_depth -= 1

    def on_agent_destroyed(self, agent: Any):
        """Agent 销毁时回调"""
        name = getattr(agent, "name", "unknown")
        logger.info(f"[{self.agent_name}] Agent {name} 已销毁")

    # ============================================================
    # 便捷方法：消息包装
    # ============================================================

    def wrap_message(self, msg: Any, **kwargs) -> Any:
        """快捷包装消息，自动注入协议信封（含HMAC签名）。

        Example:
            msg = middleware.wrap_message(
                raw_msg,
                msg_type=MsgType.TASK,
                priority=Priority.HIGH,
            )
        """
        env = Envelope(**kwargs)
        return env.wrap(msg)

    def unwrap_message(self, msg: Any) -> Optional[Envelope]:
        """快捷提取协议信封（含HMAC验签）"""
        return Envelope.unwrap(msg)

    # ============================================================
    # 状态查询
    # ============================================================

    def status(self) -> dict:
        return {
            "agent": self.agent_name,
            "port": self.port.to_dict(),
            "switch_history": self.controller.history,
            "switch_stats": self.controller.switch_stats,
        }