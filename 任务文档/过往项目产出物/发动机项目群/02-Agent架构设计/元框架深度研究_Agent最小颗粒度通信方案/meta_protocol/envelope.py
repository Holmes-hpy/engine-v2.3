"""
元协议 · 消息契约（Envelope）v2.0
====================================
基于 AgentScope 2.0 Msg 的 metadata 扩展，零侵入式设计。
(v2.0: 增加 HMAC 签名/验签机制，防止 metadata["_protocol"] 被篡改)

使用方法：
    from agentscope.message import UserMsg
    from meta_protocol.envelope import Envelope, MsgType, Priority

    msg = UserMsg("Tony", "Hello")
    env = Envelope(
        msg_type=MsgType.TASK,
        priority=Priority.HIGH,
        ttl=300,
    )
    msg = env.wrap(msg)  # 将协议信封注入 metadata["_protocol"]，自动签名

    # 接收方解析（自动验签）
    env = Envelope.unwrap(msg)  # 从 metadata["_protocol"] 提取信封，自动验签
    if env is None:
        print("消息签名无效或缺少协议信封")
    print(env.msg_type)  # MsgType.TASK

设计原则：
    1. 所有协议字段存储在 msg.metadata["_protocol"] 中
    2. 不修改 AgentScope 源码，纯扩展
    3. Pydantic 强类型校验，字段不可随意拼写
    4. 支持 JSON 序列化，可直接持久化
    5. HMAC 签名保证 metadata["_protocol"] 不被篡改
"""

from __future__ import annotations

import hashlib
import hmac
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field


# ============================================================
# 枚举定义
# ============================================================

class MsgType(str, Enum):
    """消息类型 —— 对应10要素中的「消息类型」子项"""
    TASK = "task"        # 任务：分配工作、下达指令
    DATA = "data"        # 数据：传输调研结果、计算结果
    CONTROL = "control"  # 控制：创建/销毁Agent、切换配置
    EVENT = "event"      # 事件：通知、告警、状态变更


class Priority(str, Enum):
    """消息优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PayloadFormat(str, Enum):
    """载荷格式"""
    TEXT = "text"        # 纯文本（AgentScope 默认）
    JSON = "json"        # 结构化 JSON
    BINARY = "binary"    # 二进制（Protobuf/MsgPack 等）


# ============================================================
# 信封数据模型
# ============================================================

class RoutingHint(BaseModel):
    """路由提示 —— 可选，连接器可据此优化路由路径。
    注意：这是"提示"而非"强制"，实际路由由连接器决定。

    v2.0: 从 reachability 拆分为 addressing + visibility
    """
    addressing: str = Field(
        default="unicast",
        description="寻址方式提示：unicast | multicast | broadcast"
    )
    visibility: str = Field(
        default="private",
        description="可见性域提示：private | group | global"
    )
    distribution: str = Field(
        default="direct",
        description="分发策略提示：direct | fan_out | fan_in | sequential | round_robin"
    )


class Envelope(BaseModel):
    """元协议消息信封

    所有字段存储在 msg.metadata["_protocol"] 中，
    与 AgentScope 原生 Msg 完全兼容。

    字段说明：
        version          - 协议版本号，用于未来兼容性
        msg_type         - 消息类型（任务/数据/控制/事件）
        msg_id           - 本消息唯一ID（不同于 Msg.id，这是协议层ID）
        correlation_id   - 关联ID，用于追踪请求-响应链
        conversation_id  - 会话ID，用于分组相关消息
        priority         - 优先级
        ttl              - 存活时间（秒），0 表示永不过期
        payload_format   - 载荷格式
        routing          - 路由提示（可选）
        created_at       - 协议层时间戳
        signature        - HMAC 签名（自动生成，防止篡改）
    """
    version: str = Field(default="2.0", description="协议版本")
    msg_type: MsgType = Field(default=MsgType.TASK, description="消息类型")
    msg_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="协议层消息唯一ID"
    )
    correlation_id: Optional[str] = Field(
        default=None,
        description="关联ID，用于追踪请求-响应链"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="会话ID，用于分组相关消息"
    )
    priority: Priority = Field(default=Priority.NORMAL, description="优先级")
    ttl: int = Field(
        default=0,
        ge=0,
        description="存活时间（秒），0=永不过期"
    )
    payload_format: PayloadFormat = Field(
        default=PayloadFormat.TEXT,
        description="载荷格式"
    )
    routing: RoutingHint = Field(
        default_factory=RoutingHint,
        description="路由提示"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="协议层创建时间"
    )
    signature: Optional[str] = Field(
        default=None,
        description="HMAC-SHA256签名，用于防篡改"
    )

    # ============================================================
    # HMAC 签名机制
    # ============================================================

    # 协议键名 —— 存储在 AgentScope Msg 的 metadata 字典中
    PROTOCOL_KEY: ClassVar[str] = "_protocol"
    SIGNATURE_KEY: ClassVar[str] = "_protocol_sig"

    # 默认 HMAC 密钥（生产环境应从环境变量或密钥管理服务获取）
    _hmac_key: ClassVar[Optional[bytes]] = None

    @classmethod
    def set_hmac_key(cls, key: str):
        """设置 HMAC 密钥（应尽早调用，如模块加载时）。

        Args:
            key: 密钥字符串，至少16字符
        """
        if len(key) < 16:
            raise ValueError("HMAC 密钥至少需要16个字符")
        cls._hmac_key = key.encode("utf-8")

    @classmethod
    def _get_hmac_key(cls) -> bytes:
        """获取 HMAC 密钥，未设置时自动生成随机密钥（开发环境）"""
        if cls._hmac_key is None:
            cls._hmac_key = os.urandom(32)
        return cls._hmac_key

    def _compute_hmac(self) -> str:
        """计算 payload 的 HMAC-SHA256 签名。

        签名策略：
        - 对模型导出的 JSON 数据（不含 signature 字段）计算 HMAC
        - 确保签名基于所有关键字段，防止任何字段被篡改
        """
        data = self.model_dump(mode="json", exclude={"signature"})
        # 按 key 排序以确保一致性
        payload = self._canonicalize(data)
        key = self._get_hmac_key()
        sig = hmac.new(key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return sig

    @staticmethod
    def _canonicalize(data: dict) -> str:
        """将字典规范化为确定性字符串（用于签名）"""
        def _sort(obj):
            if isinstance(obj, dict):
                return {k: _sort(v) for k, v in sorted(obj.items())}
            elif isinstance(obj, list):
                return [_sort(v) for v in obj]
            return obj
        import json
        return json.dumps(_sort(data), separators=(",", ":"), ensure_ascii=False)

    def sign(self) -> "Envelope":
        """对信封签名，生成 HMAC 并存入 signature 字段"""
        self.signature = self._compute_hmac()
        return self

    def verify(self) -> bool:
        """验证签名是否匹配。

        Returns:
            True: 签名有效或未设置签名（向后兼容）
            False: 签名不匹配，数据可能被篡改
        """
        if self.signature is None:
            # 未签名消息，向后兼容旧版
            return True
        expected = self._compute_hmac()
        return hmac.compare_digest(self.signature, expected)

    # ============================================================
    # 核心方法：wrap / unwrap
    # ============================================================

    def wrap(self, msg: Any) -> Any:
        """将信封注入 AgentScope Msg 的 metadata 中（自动签名）。

        Args:
            msg: AgentScope 的 Msg 实例（UserMsg/AssistantMsg/SystemMsg）

        Returns:
            注入了协议信封的 Msg 实例（原地修改 + 返回）

        Example:
            >>> from agentscope.message import UserMsg
            >>> msg = UserMsg("Tony", "Hello")
            >>> env = Envelope(msg_type=MsgType.TASK)
            >>> msg = env.wrap(msg)
            >>> msg.metadata["_protocol"]["msg_type"]
            'task'
        """
        if not hasattr(msg, "metadata"):
            raise TypeError(
                f"msg must be an AgentScope Msg instance with 'metadata' attribute, "
                f"got {type(msg).__name__}"
            )

        if msg.metadata is None:
            msg.metadata = {}

        # 签名
        self.sign()

        # 注入协议信封
        msg.metadata[self.PROTOCOL_KEY] = self.model_dump()

        return msg

    @classmethod
    def unwrap(cls, msg: Any) -> Optional["Envelope"]:
        """从 AgentScope Msg 的 metadata 中提取协议信封（自动验签）。

        Args:
            msg: AgentScope 的 Msg 实例

        Returns:
            Envelope 实例，如果消息中没有协议信封或签名无效则返回 None

        Example:
            >>> env = Envelope.unwrap(msg)
            >>> if env and env.msg_type == MsgType.CONTROL:
            ...     handle_control_message(msg)
        """
        if not hasattr(msg, "metadata"):
            return None
        if not msg.metadata:
            return None
        protocol_data = msg.metadata.get(cls.PROTOCOL_KEY)
        if protocol_data is None:
            return None
        env = cls.model_validate(protocol_data)
        if not env.verify():
            # 签名验证失败，可能被篡改
            return None
        return env

    def is_expired(self) -> bool:
        """检查消息是否过期。

        Returns:
            True 如果消息已过期（当前时间 > 创建时间 + TTL）
        """
        if self.ttl == 0:
            return False
        try:
            created = datetime.fromisoformat(self.created_at)
            elapsed = (datetime.now() - created).total_seconds()
            return elapsed > self.ttl
        except (ValueError, TypeError):
            return False

    # ============================================================
    # 工厂方法：快捷创建常见消息类型
    # ============================================================

    @classmethod
    def task(
        cls,
        msg_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
        ttl: int = 0,
        **kwargs: Any,
    ) -> "Envelope":
        """创建任务消息信封"""
        return cls(
            msg_type=MsgType.TASK,
            msg_id=msg_id or str(uuid.uuid4()),
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            priority=priority,
            ttl=ttl,
            **kwargs,
        )

    @classmethod
    def data(
        cls,
        msg_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> "Envelope":
        """创建数据消息信封"""
        return cls(
            msg_type=MsgType.DATA,
            msg_id=msg_id or str(uuid.uuid4()),
            correlation_id=correlation_id,
            conversation_id=conversation_id,
            **kwargs,
        )

    @classmethod
    def control(
        cls,
        msg_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> "Envelope":
        """创建控制消息信封"""
        return cls(
            msg_type=MsgType.CONTROL,
            msg_id=msg_id or str(uuid.uuid4()),
            conversation_id=conversation_id,
            priority=Priority.HIGH,
            **kwargs,
        )

    @classmethod
    def event(
        cls,
        msg_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> "Envelope":
        """创建事件消息信封"""
        return cls(
            msg_type=MsgType.EVENT,
            msg_id=msg_id or str(uuid.uuid4()),
            conversation_id=conversation_id,
            **kwargs,
        )

    # ============================================================
    # 辅助方法
    # ============================================================

    def as_reply(self, in_reply_to: str) -> "Envelope":
        """创建此消息的回复信封，自动设置 correlation_id。

        Args:
            in_reply_to: 被回复的消息的 msg_id

        Returns:
            新的 Envelope，correlation_id 指向原消息
        """
        reply = self.model_copy()
        reply.msg_id = str(uuid.uuid4())
        reply.correlation_id = in_reply_to
        reply.created_at = datetime.now().isoformat()
        reply.signature = None  # 清除旧签名，wrap() 时会重新签名
        return reply

    def summary(self) -> str:
        """返回人类可读的信封摘要"""
        parts = [
            f"[v{self.version}]",
            f"type={self.msg_type.value}",
            f"id={self.msg_id[:8]}...",
            f"priority={self.priority.value}",
        ]
        if self.ttl > 0:
            parts.append(f"ttl={self.ttl}s")
        if self.correlation_id:
            parts.append(f"corr={self.correlation_id[:8]}...")
        if self.signature:
            parts.append(f"sig={self.signature[:8]}...")
        return " ".join(parts)