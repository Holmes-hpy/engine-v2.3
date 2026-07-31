"""
元协议 · 约束规则引擎 v2.0
============================
10要素8条跨要素约束规则的自动校验。
(v2.0: 从4条恢复到8条约束，增加applied_constraints追踪 + Connector兼容性校验)

使用方式：
    from meta_protocol.constraint_engine import ConstraintEngine
    engine = ConstraintEngine()
    result = engine.validate(port_contract)
    if not result.is_valid:
        for violation in result.violations:
            print(f"违反: {violation}")
    print(f"应用的约束: {result.applied_constraints}")

约束规则（10要素8条）：
    C1(硬): 寻址=unicast → 可见性=private
    C2(硬): Memory归属=exclusive → 上下文隔离=full
    C3(硬): 分发=fan_out → 生命周期=temporary
    C4(硬): 分发=sequential → 寻址=unicast + 可见性=private
    C5(硬): 寻址=broadcast → 可见性=global
    C6(软): 寻址=unicast + 可见性=private → 建议Memory归属=exclusive
    C7(软): Memory归属=shared → 建议上下文隔离=none
    C8(软): 生命周期=temporary → 建议状态=stateless
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

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


class ConstraintLevel(str, Enum):
    HARD = "hard"  # 硬约束：违反则拒绝
    SOFT = "soft"  # 软约束：违反则警告


@dataclass
class Violation:
    rule_id: str
    level: ConstraintLevel
    message: str
    suggestion: str = ""


@dataclass
class ValidationResult:
    is_valid: bool
    violations: list[Violation] = field(default_factory=list)
    warnings: list[Violation] = field(default_factory=list)
    applied_constraints: list[str] = field(default_factory=list)

    def check(self, rule_id: str, violated: bool, v: Violation):
        """记录约束检查（无论通过与否都记录ID）。

        Args:
            rule_id: 约束规则ID
            violated: 是否违反约束（True=违反）
            v: 违反对象（仅在违反时使用）
        """
        self.applied_constraints.append(rule_id)
        if violated:
            self.add(v)

    def add(self, v: Violation):
        if v.level == ConstraintLevel.HARD:
            self.violations.append(v)
            self.is_valid = False
        else:
            self.warnings.append(v)

    def summary(self) -> str:
        parts = []
        if self.violations:
            parts.append(f"❌ {len(self.violations)}条硬约束违反:")
            for v in self.violations:
                parts.append(f"  [{v.rule_id}] {v.message}")
        if self.warnings:
            parts.append(f"⚠️ {len(self.warnings)}条软约束建议:")
            for w in self.warnings:
                parts.append(f"  [{w.rule_id}] {w.message}")
        if not parts:
            parts.append("✅ 全部约束通过")
        parts.append(f"📋 应用约束: {', '.join(self.applied_constraints)}")
        return "\n".join(parts)


# ============================================================
# Connector 兼容性表
# ============================================================

CONNECTOR_COMPATIBILITY = {
    # (addressing, distribution): [compatible_connectors]
    ("unicast", "direct"):      ["Pipe", "Router"],
    ("unicast", "sequential"):  ["Pipe"],
    ("unicast", "fan_out"):     ["Router", "Broker"],
    ("unicast", "fan_in"):      ["Router", "Broker"],
    ("multicast", "direct"):    ["Hub", "Router", "Broker"],
    ("multicast", "fan_out"):   ["Hub", "Broker"],
    ("multicast", "fan_in"):    ["Hub", "Broker"],
    ("multicast", "round_robin"): ["Hub", "Router"],
    ("broadcast", "direct"):    ["Hub", "Broker"],
    ("broadcast", "fan_out"):   ["Hub", "Broker"],
    ("broadcast", "fan_in"):    ["Hub"],
    ("broadcast", "competitive"): ["Hub", "Broker"],
}


class ConstraintEngine:
    """约束规则引擎。

    核心职责：
        1. 创建时静态校验：validate(port_contract)
        2. 运行时动态拦截：validate_switch(old, new)
        3. Connector兼容性校验：validate_connector_compatibility(port, connector_type)
    """

    # ============================================================
    # 静态校验：检查单个 PortContract 的合法性
    # ============================================================

    def validate(self, port: PortContract) -> ValidationResult:
        """对端口契约执行全部8条约束校验"""
        result = ValidationResult(is_valid=True)

        # C1（硬）：寻址=unicast → 可见性=private
        result.check("C1", port.addressing == AddressingMode.UNICAST and port.visibility != VisibilityDomain.PRIVATE,
            Violation(rule_id="C1", level=ConstraintLevel.HARD,
                message=f"寻址方式=unicast 时，可见性域必须为 private，当前为 {port.visibility.value}",
                suggestion="单播通信天然是点对点的，可见性域必须设为private以保证语义一致性。"))

        # C2（硬）：Memory归属=exclusive → 上下文隔离=full
        result.check("C2", port.memory_belonging == MemoryBelonging.EXCLUSIVE and port.context_isolation != ContextIsolation.FULL,
            Violation(rule_id="C2", level=ConstraintLevel.HARD,
                message=f"Memory归属=exclusive 时，上下文隔离必须为 full，当前为 {port.context_isolation.value}",
                suggestion="独占Memory意味着Agent拥有独立数据空间，上下文也应完全隔离以防止信息泄露。"))

        # C3（硬）：分发=fan_out → 生命周期=temporary
        result.check("C3", port.distribution == Distribution.FAN_OUT and port.lifecycle != Lifecycle.TEMPORARY,
            Violation(rule_id="C3", level=ConstraintLevel.HARD,
                message=f"分发策略=fan_out 时，生命周期必须为 temporary，当前为 {port.lifecycle.value}",
                suggestion="扇出会创建大量Agent，必须设置生命周期=临时以自动回收，防止内存泄漏。"))

        # C4（硬）：分发=sequential → 寻址=unicast + 可见性=private
        result.check("C4", port.distribution == Distribution.SEQUENTIAL and
            (port.addressing != AddressingMode.UNICAST or port.visibility != VisibilityDomain.PRIVATE),
            Violation(rule_id="C4", level=ConstraintLevel.HARD,
                message=f"分发策略=sequential 时，寻址必须为 unicast 且可见性为 private，"
                        f"当前为 addr={port.addressing.value}, vis={port.visibility.value}",
                suggestion="顺序传递要求点对点通信，unicast+private是唯一语义一致的可达性域。"))

        # C5（硬）：寻址=broadcast → 可见性=global
        result.check("C5", port.addressing == AddressingMode.BROADCAST and port.visibility != VisibilityDomain.GLOBAL,
            Violation(rule_id="C5", level=ConstraintLevel.HARD,
                message=f"寻址方式=broadcast 时，可见性域必须为 global，当前为 {port.visibility.value}",
                suggestion="广播通信面向所有Agent，可见性必须设为global以确保消息可达。"))

        # C6（软）：寻址=unicast + 可见性=private → 建议Memory归属=exclusive
        result.check("C6", port.addressing == AddressingMode.UNICAST and port.visibility == VisibilityDomain.PRIVATE
            and port.memory_belonging == MemoryBelonging.SHARED,
            Violation(rule_id="C6", level=ConstraintLevel.SOFT,
                message="寻址=unicast+可见性=private 时，建议 Memory归属=exclusive 而非 shared",
                suggestion="私有通信意味着Agent之间不应共享数据，设置Memory归属=exclusive 更安全。"))

        # C7（软）：Memory归属=shared → 建议上下文隔离=none
        result.check("C7", port.memory_belonging == MemoryBelonging.SHARED and port.context_isolation != ContextIsolation.NONE,
            Violation(rule_id="C7", level=ConstraintLevel.SOFT,
                message=f"Memory归属=shared 时，建议上下文隔离=none，当前为 {port.context_isolation.value}",
                suggestion="共享Memory的Agent通常需要完全共享上下文才能高效协作，设置上下文隔离=none。"))

        # C8（软）：生命周期=temporary → 建议状态=stateless
        result.check("C8", port.lifecycle == Lifecycle.TEMPORARY and port.state_boundary == StateBoundary.STATEFUL,
            Violation(rule_id="C8", level=ConstraintLevel.SOFT,
                message="生命周期=temporary 时，建议状态边界=stateless 而非 stateful",
                suggestion="临时Agent销毁后状态会丢失，无状态设计更安全。如有特殊需求可忽略此建议。"))

        return result

    # ============================================================
    # 运行时校验：检查配置切换是否合法
    # ============================================================

    def validate_switch(self, old: PortContract, new: PortContract) -> ValidationResult:
        """检查从 old 切换到 new 是否合法。

        额外检查：
        - 从独占切换到共享时，需确认数据不会泄露
        - 从临时切换到永久时，需确认是有意为之
        - 可见性升级时的安全检查
        """
        result = self.validate(new)

        # 隔离→共享 切换警告
        if (old.memory_belonging == MemoryBelonging.EXCLUSIVE and
                new.memory_belonging == MemoryBelonging.SHARED):
            result.add(Violation(
                rule_id="SWITCH-01",
                level=ConstraintLevel.SOFT,
                message="从独占Memory切换到共享Memory，请注意检查数据不会泄露",
                suggestion="确认切换是必要的，共享Memory意味着所有Agent可访问彼此的数据。"
            ))

        # 临时→永久 切换警告
        if old.lifecycle == Lifecycle.TEMPORARY and new.lifecycle == Lifecycle.PERMANENT:
            result.add(Violation(
                rule_id="SWITCH-02",
                level=ConstraintLevel.SOFT,
                message="从临时生命周期切换到永久生命周期，Agent将不会被自动回收",
                suggestion="确认此Agent确实需要永久存在，避免资源泄漏。"
            ))

        # 可见性升级警告
        if old.visibility == VisibilityDomain.PRIVATE and new.visibility != VisibilityDomain.PRIVATE:
            result.add(Violation(
                rule_id="SWITCH-03",
                level=ConstraintLevel.SOFT,
                message=f"可见性从 private 升级到 {new.visibility.value}，消息可能被更多Agent看到",
                suggestion="确认可见性升级是有意为之，避免敏感信息泄露。"
            ))

        return result

    # ============================================================
    # 方法拦截校验（用于装饰器场景）
    # ============================================================

    def validate_method_override(
        self, current: PortContract, method_overrides: dict
    ) -> ValidationResult:
        """校验方法级别的 port_override 是否合法。

        Args:
            current: 当前Agent的端口契约
            method_overrides: @port_override 装饰器声明的覆盖值
        """
        if not method_overrides:
            return ValidationResult(is_valid=True)

        new_data = current.model_dump()
        new_data.update(method_overrides)
        new = PortContract.model_validate(new_data)

        return self.validate_switch(current, new)

    # ============================================================
    # Connector 兼容性校验
    # ============================================================

    def validate_connector_compatibility(
        self, port: PortContract, connector_type: str
    ) -> ValidationResult:
        """检查端口契约与连接器类型是否兼容。

        Args:
            port: 端口契约
            connector_type: 连接器类型名（"Hub", "Pipe", "Router", "Broker"）

        Returns:
            ValidationResult: 不兼容时返回硬约束违反
        """
        result = ValidationResult(is_valid=True)

        key = (port.addressing.value, port.distribution.value)
        compatible = CONNECTOR_COMPATIBILITY.get(key, [])

        if connector_type not in compatible:
            result.add(Violation(
                rule_id="CONNECTOR-01",
                level=ConstraintLevel.HARD,
                message=f"端口契约 (addr={port.addressing.value}, dist={port.distribution.value}) "
                        f"与连接器类型 '{connector_type}' 不兼容",
                suggestion=f"支持的连接器类型: {', '.join(compatible) if compatible else '无'}"
            ))
            return result

        return result

    def get_compatible_connectors(self, port: PortContract) -> list[str]:
        """获取端口契约兼容的连接器类型列表"""
        key = (port.addressing.value, port.distribution.value)
        return CONNECTOR_COMPATIBILITY.get(key, [])