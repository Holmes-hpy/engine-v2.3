# meta_protocol — 元协议层 v2.0
# 基于 AgentScope 2.0 的零侵入式协议扩展
# (v2.0: 10要素体系，HMAC签名，A2A适配器，文件锁，Connector兼容性)
#
# 使用方式：
#   from meta_protocol import Envelope, PortContract, ConstraintEngine, Hub, DynamicSwitchController
#
# 模块清单：
#   envelope.py        — 消息契约（步骤一）+ HMAC签名
#   port_contract.py   — 端口契约 IDL（步骤二）10要素
#   constraint_engine.py — 约束规则引擎（步骤三）8条约束
#   connector.py       — 连接器 Hub/Pipe/Router/Broker（步骤四）
#   dynamic_switch.py  — 动态切换控制器（步骤五）+ LLM辅助 + 频率限制
#   integration.py     — AgentScope 2.0 集成中间件（步骤六）
#   loop_engineering.py — Loop 工程（步骤七）+ 文件锁 + StorageBackend
#   a2a_adapter.py     — A2A↔元协议双向适配器（新增）

from meta_protocol.envelope import Envelope, MsgType, Priority, PayloadFormat, RoutingHint
from meta_protocol.port_contract import (
    PortContract, Capabilities, MultiModePortContract,
    AddressingMode, VisibilityDomain, Distribution,
    MemoryBelonging, ContextIsolation,
    StateBoundary, Lifecycle, Reliability, MsgFormat,
    port_override,
)
from meta_protocol.constraint_engine import (
    ConstraintEngine, ValidationResult, Violation, ConstraintLevel,
    CONNECTOR_COMPATIBILITY,
)
from meta_protocol.connector import (
    AgentRef, Hub, Pipe, Router, Broker, BaseConnector, RouteEntry,
)
from meta_protocol.dynamic_switch import (
    DynamicSwitchController, SwitchRecommendation,
)
from meta_protocol.integration import MetaProtocolMiddleware
from meta_protocol.loop_engineering import (
    StopHook, CircuitBreaker, CircuitBreakerOpen, Watchdog, RalphLoop,
    FileLock, StorageBackend, FileStorageBackend,
)
from meta_protocol.a2a_adapter import (
    A2AAdapter, A2AMessage, A2ATask, A2APart,
    A2ATaskState, A2APartType,
)

__all__ = [
    # Envelope
    "Envelope", "MsgType", "Priority", "PayloadFormat", "RoutingHint",
    # Port Contract (10要素)
    "PortContract", "Capabilities", "MultiModePortContract",
    "AddressingMode", "VisibilityDomain", "Distribution",
    "MemoryBelonging", "ContextIsolation",
    "StateBoundary", "Lifecycle", "Reliability", "MsgFormat",
    "port_override",
    # Constraint Engine
    "ConstraintEngine", "ValidationResult", "Violation", "ConstraintLevel",
    "CONNECTOR_COMPATIBILITY",
    # Connector
    "AgentRef", "Hub", "Pipe", "Router", "Broker", "BaseConnector", "RouteEntry",
    # Dynamic Switch
    "DynamicSwitchController", "SwitchRecommendation",
    # Integration
    "MetaProtocolMiddleware",
    # Loop Engineering
    "StopHook", "CircuitBreaker", "CircuitBreakerOpen", "Watchdog", "RalphLoop",
    "FileLock", "StorageBackend", "FileStorageBackend",
    # A2A Adapter
    "A2AAdapter", "A2AMessage", "A2ATask", "A2APart",
    "A2ATaskState", "A2APartType",
]