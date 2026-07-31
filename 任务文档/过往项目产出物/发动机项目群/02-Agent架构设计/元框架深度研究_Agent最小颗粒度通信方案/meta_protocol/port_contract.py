"""
元协议 · 端口契约 IDL v2.0
============================
声明式配置语言，定义 Agent 的10要素通信能力。
(v2.0: 从8要素回退到10要素，拆分④⑥→寻址方式+可见性域，拆分⑦⑧→Memory归属+上下文隔离)

三种使用方式：
  1. Python 代码直接声明：
       port = PortContract(
           addressing="unicast",
           visibility="private",
           memory_belonging="exclusive",
           context_isolation="full",
           distribution="fan_out",
       )
  2. YAML 配置文件加载：
       port = PortContract.from_yaml("agent_config.yaml")
  3. 装饰器覆盖：
       @port_override(addressing="multicast", visibility="group")
       def expert_review():
           ...

10要素映射：
  A层·消息契约: ①②③ — msg_format, msg_type_whitelist, payload_format
  B层·可达性域: ④寻址方式(addressing) + ⑤可见性域(visibility)
  B层·分发策略: ⑥分发策略(distribution)
  C层·数据隔离域: ⑦Memory归属(memory_belonging) + ⑧上下文隔离(context_isolation)
  C层·状态边界: ⑨状态边界(state_boundary)
  D层·治理控制: ⑩能力/权限(capabilities) + 生命周期(lifecycle) + 可靠性(reliability)
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any, ClassVar, Dict, Optional

import yaml
from pydantic import BaseModel, Field


# ============================================================
# 枚举定义 — 10个独立维度
# ============================================================

class AddressingMode(str, Enum):
    """寻址方式 — 消息如何找到目标"""
    UNICAST = "unicast"       # 单播：指定唯一接收者
    MULTICAST = "multicast"   # 组播：指定组内所有成员
    BROADCAST = "broadcast"   # 广播：所有可达Agent


class VisibilityDomain(str, Enum):
    """可见性域 — 谁能看到消息"""
    PRIVATE = "private"       # 私有：仅发送者和接收者可见
    GROUP = "group"           # 组内：同组内所有成员可见
    GLOBAL = "global"         # 全局：任意Agent可见


class Distribution(str, Enum):
    """分发策略"""
    DIRECT = "direct"
    FAN_OUT = "fan_out"
    FAN_IN = "fan_in"
    SEQUENTIAL = "sequential"
    ROUND_ROBIN = "round_robin"
    COMPETITIVE = "competitive"


class MemoryBelonging(str, Enum):
    """Memory归属 — Memory存储的归属关系"""
    SHARED = "shared"         # 共享Memory：所有Agent共享同一份Memory
    EXCLUSIVE = "exclusive"   # 独占Memory：每个Agent拥有独立Memory
    INHERITED = "inherited"   # 继承Memory：子Agent继承父Agent的Memory


class ContextIsolation(str, Enum):
    """上下文隔离 — 上下文空间的隔离程度"""
    FULL = "full"             # 完全隔离：Agent之间上下文完全不可见
    PARTIAL = "partial"       # 部分隔离：可见元信息但不可见具体内容
    NONE = "none"             # 无隔离：上下文完全共享


class StateBoundary(str, Enum):
    """状态边界"""
    STATELESS = "stateless"
    STATEFUL = "stateful"
    SEMI_STATEFUL = "semi_stateful"


class Lifecycle(str, Enum):
    """生命周期"""
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    CONDITIONAL = "conditional"  # 条件销毁


class Reliability(str, Enum):
    """可靠性保证"""
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


class MsgFormat(str, Enum):
    """消息格式"""
    JSON = "json"
    PROTOBUF = "protobuf"
    MSGPACK = "msgpack"


# ============================================================
# 10要素配置模型
# ============================================================

class Capabilities(BaseModel):
    """能力/权限 — D层"""
    can_create_agent: bool = True
    can_send: bool = True
    can_receive: bool = True
    can_destroy: bool = False
    max_recursion_depth: int = Field(default=3, ge=0, description="最大递归创建Agent深度")


class PortContract(BaseModel):
    """端口契约 — Agent 通信能力的完整声明。

    10要素一览：
        msg_format         - 消息格式（A层·消息契约子项 ①）
        msg_type_whitelist - 允许的消息类型白名单（A层·消息契约子项 ②）
        payload_format     - 载荷格式（A层·消息契约子项 ③）
        addressing         - 寻址方式（B层·可达性域 ④）
        visibility         - 可见性域（B层·可达性域 ⑤）
        distribution       - 分发策略（B层·分发策略 ⑥）
        memory_belonging   - Memory归属（C层·数据隔离域 ⑦）
        context_isolation  - 上下文隔离（C层·数据隔离域 ⑧）
        state_boundary     - 状态边界（C层·状态边界 ⑨）
        capabilities       - 能力/权限（D层）
        lifecycle          - 生命周期（D层）
        reliability        - 可靠性（D层）
        extensions         - 扩展字段（自定义）
    """

    # A层·消息契约（①②③）
    msg_format: MsgFormat = Field(default=MsgFormat.JSON)
    msg_type_whitelist: list[str] = Field(
        default_factory=lambda: ["task", "data", "control", "event"]
    )
    payload_format: str = "text"

    # B层·可达性域（④⑤）
    addressing: AddressingMode = Field(default=AddressingMode.BROADCAST)
    visibility: VisibilityDomain = Field(default=VisibilityDomain.GLOBAL)

    # B层·分发策略（⑥）
    distribution: Distribution = Field(default=Distribution.DIRECT)

    # C层·数据隔离域（⑦⑧）
    memory_belonging: MemoryBelonging = Field(default=MemoryBelonging.SHARED)
    context_isolation: ContextIsolation = Field(default=ContextIsolation.NONE)

    # C层·状态边界（⑨）
    state_boundary: StateBoundary = Field(default=StateBoundary.STATELESS)

    # D层·治理控制（⑩）
    capabilities: Capabilities = Field(default_factory=Capabilities)
    lifecycle: Lifecycle = Field(default=Lifecycle.PERMANENT)
    reliability: Reliability = Field(default=Reliability.AT_LEAST_ONCE)

    # 扩展字段
    extensions: Dict[str, Any] = Field(
        default_factory=dict,
        description="自定义扩展字段，用于未来协议演进"
    )

    # ============================================================
    # 预设模板
    # ============================================================

    # 预定义模板注册表
    _templates: ClassVar[dict] = {}

    @classmethod
    def isolated_worker(cls, **overrides: Any) -> "PortContract":
        """独立工作者模板 —— 对应 Isolated 拓扑"""
        kwargs = dict(
            addressing=AddressingMode.UNICAST,
            visibility=VisibilityDomain.PRIVATE,
            memory_belonging=MemoryBelonging.EXCLUSIVE,
            context_isolation=ContextIsolation.FULL,
            state_boundary=StateBoundary.STATELESS,
            lifecycle=Lifecycle.TEMPORARY,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def hub_participant(cls, **overrides: Any) -> "PortContract":
        """MsgHub 参与者模板 —— 对应 MsgHub 拓扑"""
        kwargs = dict(
            addressing=AddressingMode.BROADCAST,
            visibility=VisibilityDomain.GLOBAL,
            memory_belonging=MemoryBelonging.SHARED,
            context_isolation=ContextIsolation.NONE,
            state_boundary=StateBoundary.STATEFUL,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def pipeline_stage(cls, **overrides: Any) -> "PortContract":
        """流水线阶段模板 —— 对应 Pipeline 拓扑"""
        kwargs = dict(
            addressing=AddressingMode.UNICAST,
            visibility=VisibilityDomain.PRIVATE,
            distribution=Distribution.SEQUENTIAL,
            memory_belonging=MemoryBelonging.INHERITED,
            context_isolation=ContextIsolation.PARTIAL,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def fan_out_worker(cls, **overrides: Any) -> "PortContract":
        """扇出工作者模板 —— 对应 Fan-out 拓扑"""
        kwargs = dict(
            addressing=AddressingMode.UNICAST,
            visibility=VisibilityDomain.PRIVATE,
            distribution=Distribution.FAN_OUT,
            memory_belonging=MemoryBelonging.EXCLUSIVE,
            context_isolation=ContextIsolation.FULL,
            lifecycle=Lifecycle.TEMPORARY,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def agent_scope_default(cls, **overrides: Any) -> "PortContract":
        """AgentScope 2.0 默认模板 —— 兼容原生行为"""
        kwargs = dict(
            addressing=AddressingMode.BROADCAST,
            visibility=VisibilityDomain.GLOBAL,
            memory_belonging=MemoryBelonging.SHARED,
            context_isolation=ContextIsolation.NONE,
            distribution=Distribution.DIRECT,
            state_boundary=StateBoundary.STATEFUL,
            lifecycle=Lifecycle.PERMANENT,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def auditor_observer(cls, **overrides: Any) -> "PortContract":
        """审计观察者模板 —— unicast+group：点对点通信但在组内可见（审计场景）"""
        kwargs = dict(
            addressing=AddressingMode.UNICAST,
            visibility=VisibilityDomain.GROUP,
            memory_belonging=MemoryBelonging.SHARED,
            context_isolation=ContextIsolation.PARTIAL,
            distribution=Distribution.DIRECT,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def expert_consultation(cls, **overrides: Any) -> "PortContract":
        """多专家咨询模板 —— exclusive+shared上下文：各自独立Memory但有共享上下文窗口"""
        kwargs = dict(
            addressing=AddressingMode.MULTICAST,
            visibility=VisibilityDomain.GROUP,
            memory_belonging=MemoryBelonging.EXCLUSIVE,
            context_isolation=ContextIsolation.PARTIAL,
            distribution=Distribution.FAN_OUT,
            lifecycle=Lifecycle.TEMPORARY,
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    @classmethod
    def safe_fallback(cls, **overrides: Any) -> "PortContract":
        """SafeFallbackContract —— 非元协议Agent的保守默认配置。

        当通信对端不支持元协议时，使用此模板确保安全。
        特点：最低权限、最强隔离、不过期。
        """
        kwargs = dict(
            addressing=AddressingMode.UNICAST,
            visibility=VisibilityDomain.PRIVATE,
            memory_belonging=MemoryBelonging.EXCLUSIVE,
            context_isolation=ContextIsolation.FULL,
            distribution=Distribution.DIRECT,
            state_boundary=StateBoundary.STATELESS,
            lifecycle=Lifecycle.PERMANENT,
            reliability=Reliability.AT_LEAST_ONCE,
            capabilities=Capabilities(
                can_create_agent=False,
                can_send=True,
                can_receive=True,
                can_destroy=False,
                max_recursion_depth=0,
            ),
        )
        kwargs.update(overrides)
        return cls(**kwargs)

    # ============================================================
    # MultiModePortContract — 多模式端口契约
    # ============================================================

    @classmethod
    def multi_mode(cls, modes: Dict[str, "PortContract"], default_mode: str = "default") -> "MultiModePortContract":
        """创建多模式端口契约。

        Args:
            modes: {模式名: PortContract} 映射
            default_mode: 默认模式名

        Example:
            >>> multi = PortContract.multi_mode({
            ...     "default": PortContract.hub_participant(),
            ...     "isolated_task": PortContract.isolated_worker(),
            ...     "audit": PortContract.auditor_observer(),
            ... })
        """
        return MultiModePortContract(modes=modes, default_mode=default_mode)

    # ============================================================
    # YAML 加载/保存
    # ============================================================

    @classmethod
    def from_yaml(cls, path: str) -> "PortContract":
        """从 YAML 文件加载端口契约。

        YAML 文件示例：
        ```yaml
        # agent_config.yaml
        addressing: unicast
        visibility: private
        memory_belonging: exclusive
        context_isolation: full
        distribution: fan_out
        lifecycle: temporary
        state_boundary: stateless
        capabilities:
          can_create_agent: true
          can_destroy: false
          max_recursion_depth: 3
        reliability: at_least_once
        msg_format: json
        extensions:
          custom_field: value
        ```
        """
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            data = {}
        # 兼容旧版 YAML 字段名
        data = cls._migrate_legacy_fields(data)
        return cls.model_validate(data)

    @classmethod
    def _migrate_legacy_fields(cls, data: dict) -> dict:
        """兼容旧版字段名自动迁移"""
        # reachability → addressing + visibility
        if "reachability" in data and "addressing" not in data:
            legacy = data.pop("reachability")
            if "+" in legacy:
                addr, vis = legacy.split("+", 1)
                data.setdefault("addressing", addr)
                data.setdefault("visibility", vis)
            elif legacy == "custom":
                data.setdefault("addressing", "unicast")
                data.setdefault("visibility", "private")
        # data_isolation → memory_belonging + context_isolation
        if "data_isolation" in data and "memory_belonging" not in data:
            legacy = data.pop("data_isolation")
            if legacy == "shared":
                data.setdefault("memory_belonging", "shared")
                data.setdefault("context_isolation", "none")
            elif legacy == "isolated":
                data.setdefault("memory_belonging", "exclusive")
                data.setdefault("context_isolation", "full")
            elif legacy == "inherited":
                data.setdefault("memory_belonging", "inherited")
                data.setdefault("context_isolation", "partial")
        return data

    def to_yaml(self, path: str) -> None:
        """保存端口契约到 YAML 文件"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        data = self.model_dump(mode="json")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # ============================================================
    # 覆盖方法
    # ============================================================

    def override(self, **overrides: Any) -> "PortContract":
        """创建覆盖了部分字段的新契约（不可变语义）。

        Example:
            >>> original = PortContract.isolated_worker()
            >>> switched = original.override(
            ...     addressing=AddressingMode.MULTICAST,
            ...     visibility=VisibilityDomain.GROUP,
            ... )
        """
        data = self.model_dump()
        # 处理嵌套字段
        for key, value in overrides.items():
            if isinstance(value, dict) and key in data and isinstance(data[key], dict):
                data[key].update(value)
            else:
                data[key] = value
        return PortContract.model_validate(data)

    # ============================================================
    # 辅助方法
    # ============================================================

    def summary(self) -> str:
        """返回人类可读的契约摘要"""
        return (
            f"PortContract("
            f"addr={self.addressing.value}, "
            f"vis={self.visibility.value}, "
            f"dist={self.distribution.value}, "
            f"mem={self.memory_belonging.value}, "
            f"ctx={self.context_isolation.value}, "
            f"state={self.state_boundary.value}, "
            f"lifecycle={self.lifecycle.value})"
        )

    def to_dict(self) -> dict:
        """导出为纯字典（用于序列化到 msg.metadata）"""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "PortContract":
        """从字典恢复"""
        data = cls._migrate_legacy_fields(data)
        return cls.model_validate(data)

    def is_compatible_with(self, other: "PortContract") -> bool:
        """检查两个端口契约是否兼容（用于通信可行性判断）。

        兼容性规则：
        - 寻址方式必须匹配（unicast↔unicast, multicast↔multicast, broadcast↔broadcast）
        - 可见性域：private只与private通信，group可与group/global通信，global可与所有通信
        """
        # 寻址方式必须一致
        if self.addressing != other.addressing:
            return False
        # 可见性兼容检查
        if self.visibility == VisibilityDomain.PRIVATE or other.visibility == VisibilityDomain.PRIVATE:
            if self.visibility != other.visibility:
                return False
        return True


class MultiModePortContract:
    """多模式端口契约 —— 一个Agent可拥有多个通信模式。

    使用场景：
        - Agent默认使用Hub模式参与讨论
        - 接到独立任务时切换到Isolated模式
        - 审计场景切换到auditor_observer模式

    Example:
        >>> multi = MultiModePortContract(modes={
        ...     "default": PortContract.hub_participant(),
        ...     "isolated": PortContract.isolated_worker(),
        ...     "audit": PortContract.auditor_observer(),
        ... })
        >>> multi.current_mode  # "default"
        >>> multi.switch("isolated")  # 切换到isolated模式
        >>> multi.active  # PortContract.isolated_worker()
    """

    def __init__(self, modes: Dict[str, PortContract], default_mode: str = "default"):
        if default_mode not in modes:
            raise ValueError(f"默认模式 '{default_mode}' 不在 modes 中，可用模式: {list(modes.keys())}")
        self._modes = modes
        self._current_mode = default_mode
        self._history: list[tuple[str, str]] = []  # [(mode, reason), ...]

    @property
    def current_mode(self) -> str:
        """当前模式名"""
        return self._current_mode

    @property
    def active(self) -> PortContract:
        """当前激活的端口契约"""
        return self._modes[self._current_mode]

    @property
    def modes(self) -> list[str]:
        """所有可用模式名"""
        return list(self._modes.keys())

    @property
    def history(self) -> list[tuple[str, str]]:
        """切换历史"""
        return list(self._history)

    def switch(self, mode: str, reason: str = "") -> PortContract:
        """切换到指定模式。

        Args:
            mode: 目标模式名
            reason: 切换原因（用于日志）

        Returns:
            切换后的端口契约

        Raises:
            ValueError: 模式不存在
        """
        if mode not in self._modes:
            raise ValueError(f"模式 '{mode}' 不存在，可用模式: {list(self._modes.keys())}")
        if mode != self._current_mode:
            self._history.append((mode, reason))
            self._current_mode = mode
        return self._modes[mode]

    def get(self, mode: str) -> Optional[PortContract]:
        """获取指定模式（不切换）"""
        return self._modes.get(mode)

    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "current_mode": self._current_mode,
            "modes": {name: port.to_dict() for name, port in self._modes.items()},
            "history": self._history,
        }

    def summary(self) -> str:
        return (
            f"MultiModePortContract("
            f"current={self._current_mode}, "
            f"modes={list(self._modes.keys())})"
        )


# ============================================================
# 装饰器 — 运行时覆盖
# ============================================================

def port_override(**overrides: Any):
    """装饰器：标记函数执行时的端口契约覆盖。

    用法：
        @port_override(addressing=AddressingMode.MULTICAST, visibility=VisibilityDomain.GROUP)
        async def expert_review(agent, msg):
            ...

    装饰器将覆盖参数存入函数属性，由动态切换控制器在执行前读取。

    注意：这个装饰器本身不修改任何行为，只是一个标记。
    实际生效由步骤五的「动态切换控制器」负责。
    """
    def decorator(func):
        if not hasattr(func, "_port_overrides"):
            func._port_overrides = {}
        func._port_overrides.update(overrides)
        return func
    return decorator