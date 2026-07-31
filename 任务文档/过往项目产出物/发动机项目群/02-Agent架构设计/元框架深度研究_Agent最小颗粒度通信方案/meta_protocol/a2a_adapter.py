"""
元协议 ↔ A2A 协议适配器 v1.0
==============================
双向转换层：元协议 Envelope ↔ A2A Message/Part/Task。

使用方式：
    from meta_protocol.a2a_adapter import A2AAdapter

    adapter = A2AAdapter()

    # 元协议 → A2A
    meta_env = Envelope(msg_type=MsgType.TASK, priority=Priority.HIGH)
    a2a_message = adapter.to_a2a(meta_env, task_description="调研报告")

    # A2A → 元协议
    meta_env = adapter.from_a2a(a2a_message)

设计原则：
    1. 无损转换：语义信息不丢失
    2. 降级兼容：A2A字段无对应时使用默认值
    3. 元协议优先：元协议Agent间通信时，跳过A2A转换层
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ============================================================
# A2A 协议数据模型（简化版）
# ============================================================

class A2ATaskState(str, Enum):
    """A2A Task 状态"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class A2APartType(str, Enum):
    """A2A Part 类型"""
    TEXT = "text"
    FILE = "file"
    DATA = "data"


@dataclass
class A2APart:
    """A2A Part —— 消息的最小内容单元"""
    type: A2APartType = A2APartType.TEXT
    text: str = ""
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class A2AMessage:
    """A2A Message —— 单条消息"""
    message_id: str = ""
    role: str = "user"  # user | agent
    parts: list[A2APart] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class A2ATask:
    """A2A Task —— 一个完整的工作单元"""
    id: str = ""
    session_id: str = ""
    status: A2ATaskState = A2ATaskState.SUBMITTED
    history: list[A2AMessage] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# ============================================================
# A2AAdapter
# ============================================================

class A2AAdapter:
    """A2A ↔ 元协议 双向适配器。

    核心职责：
        1. to_a2a(): 元协议 Envelope → A2A Message/Task
        2. from_a2a(): A2A Message/Task → 元协议 Envelope
        3. 字段映射表驱动，易于扩展
    """

    # 元协议 MsgType → A2A TaskState 映射
    MSG_TYPE_TO_TASK_STATE = {
        "task": A2ATaskState.SUBMITTED,
        "data": A2ATaskState.WORKING,
        "control": A2ATaskState.WORKING,
        "event": A2ATaskState.WORKING,
    }

    # A2A TaskState → 元协议 MsgType 映射
    TASK_STATE_TO_MSG_TYPE = {
        A2ATaskState.SUBMITTED: "task",
        A2ATaskState.WORKING: "task",
        A2ATaskState.INPUT_REQUIRED: "task",
        A2ATaskState.COMPLETED: "data",
        A2ATaskState.FAILED: "event",
        A2ATaskState.CANCELLED: "event",
    }

    def __init__(self):
        self._stats = {"to_a2a": 0, "from_a2a": 0, "errors": 0}

    # ============================================================
    # 元协议 → A2A
    # ============================================================

    def to_a2a_message(
        self,
        meta_env: Any,  # Envelope
        content: str = "",
        role: str = "agent",
    ) -> A2AMessage:
        """将元协议 Envelope 转换为 A2A Message。

        Args:
            meta_env: 元协议 Envelope 实例
            content: 消息文本内容
            role: A2A角色（user/agent）

        Returns:
            A2A Message
        """
        self._stats["to_a2a"] += 1

        # 元协议字段 → A2A metadata
        a2a_metadata = {
            "_meta_protocol": {
                "version": meta_env.version,
                "msg_type": meta_env.msg_type.value,
                "priority": meta_env.priority.value,
                "ttl": meta_env.ttl,
                "correlation_id": meta_env.correlation_id,
                "conversation_id": meta_env.conversation_id,
                "payload_format": meta_env.payload_format.value,
                "routing": {
                    "addressing": meta_env.routing.addressing,
                    "visibility": meta_env.routing.visibility,
                    "distribution": meta_env.routing.distribution,
                },
            }
        }

        # 构建 A2A Part
        parts = []
        if content:
            parts.append(A2APart(type=A2APartType.TEXT, text=content))
        # 元协议信封的完整数据作为 data part
        parts.append(A2APart(
            type=A2APartType.DATA,
            data=meta_env.model_dump(mode="json"),
            metadata={"format": "meta_protocol_envelope"},
        ))

        return A2AMessage(
            message_id=meta_env.msg_id,
            role=role,
            parts=parts,
            metadata=a2a_metadata,
        )

    def to_a2a_task(
        self,
        meta_env: Any,  # Envelope
        content: str = "",
        session_id: str = "",
    ) -> A2ATask:
        """将元协议 Envelope 转换为 A2A Task。

        Args:
            meta_env: 元协议 Envelope 实例
            content: 任务描述
            session_id: 会话ID

        Returns:
            A2A Task
        """
        self._stats["to_a2a"] += 1

        message = self.to_a2a_message(meta_env, content, "user")

        # 映射 MsgType → TaskState
        task_state = self.MSG_TYPE_TO_TASK_STATE.get(
            meta_env.msg_type.value, A2ATaskState.WORKING
        )

        return A2ATask(
            id=meta_env.conversation_id or str(uuid.uuid4()),
            session_id=session_id or meta_env.conversation_id or "",
            status=task_state,
            history=[message],
            metadata={
                "_meta_protocol": {
                    "version": meta_env.version,
                    "msg_type": meta_env.msg_type.value,
                    "priority": meta_env.priority.value,
                }
            },
        )

    # ============================================================
    # A2A → 元协议
    # ============================================================

    def from_a2a_message(self, a2a_msg: A2AMessage) -> Optional[Any]:
        """从 A2A Message 提取元协议 Envelope。

        Args:
            a2a_msg: A2A Message

        Returns:
            元协议 Envelope 实例，如果无法提取则返回 None
        """
        self._stats["from_a2a"] += 1

        try:
            # 尝试从 A2A metadata 中提取元协议信息
            meta_data = a2a_msg.metadata.get("_meta_protocol", {})
            if not meta_data:
                # 尝试从 data parts 中提取
                for part in a2a_msg.parts:
                    if part.type == A2APartType.DATA and part.metadata.get("format") == "meta_protocol_envelope":
                        meta_data = part.data
                        break

            if not meta_data:
                return None

            from meta_protocol.envelope import Envelope
            return Envelope.model_validate(meta_data)

        except Exception:
            self._stats["errors"] += 1
            return None

    def from_a2a_task(self, a2a_task: A2ATask) -> Optional[Any]:
        """从 A2A Task 提取元协议 Envelope。

        优先从最新消息中提取，其次从 Task metadata 中构建。

        Args:
            a2a_task: A2A Task

        Returns:
            元协议 Envelope 实例
        """
        self._stats["from_a2a"] += 1

        try:
            # 方案1: 从最新消息提取
            if a2a_task.history:
                latest = a2a_task.history[-1]
                env = self.from_a2a_message(latest)
                if env:
                    return env

            # 方案2: 从 Task metadata 构建
            meta_data = a2a_task.metadata.get("_meta_protocol", {})
            if meta_data:
                from meta_protocol.envelope import Envelope
                # 构建最简 Envelope
                msg_type = self.TASK_STATE_TO_MSG_TYPE.get(
                    a2a_task.status, "task"
                )
                return Envelope(
                    msg_type=msg_type,
                    conversation_id=a2a_task.id,
                    **{k: v for k, v in meta_data.items()
                       if k in ["version", "msg_type", "priority", "ttl"]},
                )

            return None

        except Exception:
            self._stats["errors"] += 1
            return None

    # ============================================================
    # 降级策略：非元协议 Agent 的安全处理
    # ============================================================

    def safe_fallback_from_a2a(self, a2a_msg: A2AMessage) -> tuple[Any, bool]:
        """从 A2A Message 安全提取元协议 Envelope（带降级标识）。

        Returns:
            (Envelope, is_fallback): 元协议信封 和 是否使用了降级模式
        """
        env = self.from_a2a_message(a2a_msg)
        if env is not None:
            return env, False

        # 降级：使用 SafeFallbackContract
        from meta_protocol.envelope import Envelope, MsgType, Priority
        from meta_protocol.port_contract import PortContract

        fallback_port = PortContract.safe_fallback()
        env = Envelope(
            msg_type=MsgType.TASK,
            priority=Priority.NORMAL,
            routing={
                "addressing": fallback_port.addressing.value,
                "visibility": fallback_port.visibility.value,
                "distribution": fallback_port.distribution.value,
            },
        )
        return env, True

    @property
    def stats(self) -> dict:
        return dict(self._stats)