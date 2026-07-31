"""
步骤一 · 消息契约（Envelope）可用性验证 v2.0
==========================================
验证目标：
    1. Envelope 能否正确注入 AgentScope Msg 的 metadata
    2. Envelope 能否正确从 Msg 中解析
    3. 四种消息类型的工厂方法
    4. 请求-响应链（correlation_id）
    5. TTL 过期检查
    6. JSON 序列化/反序列化
    7. 与 AgentScope 原生 Msg 互不干扰
    8. HMAC 签名/验签/防篡改（v2.0新增）
    9. A2A 适配器（v2.0新增）

运行方式：
    cd /Users/houpengyuan/Documents/trae_projects/0-A-V8.1发动机/产出物/20260719-元框架深度研究_Agent最小颗粒度通信方案
    python3 test_envelope.py
"""

import sys
import os
import json
import time
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from meta_protocol.envelope import (
    Envelope,
    MsgType,
    Priority,
    PayloadFormat,
    RoutingHint,
)
from meta_protocol.a2a_adapter import (
    A2AAdapter,
    A2AMessage,
    A2ATask,
    A2APart,
    A2APartType,
    A2ATaskState,
)


class MockMsg:
    """模拟 AgentScope 的 Msg 类"""
    def __init__(self, name: str, content: str, role: str = "user"):
        self.name = name
        self.content = content
        self.role = role
        self.id = str(uuid.uuid4())
        self.metadata: dict = {}
        self.usage = None

    def __repr__(self):
        return f"MockMsg(name={self.name!r}, content={self.content[:30]!r}...)"


PASS = 0
FAIL = 0

def check(description: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {description}")
        PASS += 1
    else:
        print(f"  ❌ {description}  — {detail}")
        FAIL += 1

def test_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# 测试 1: 基础注入与解析
# ============================================================

test_section("测试1: 基础 wrap/unwrap")

msg = MockMsg("Tony", "帮我调研一下AI芯片市场")
env = Envelope(
    msg_type=MsgType.TASK,
    priority=Priority.HIGH,
    ttl=300,
    payload_format=PayloadFormat.TEXT,
)
wrapped = env.wrap(msg)

check("wrap 返回原 msg 对象", wrapped is msg)
check("metadata 中存在 _protocol 键", "_protocol" in msg.metadata)
check("_protocol 是 dict 类型", isinstance(msg.metadata["_protocol"], dict))
check("msg_type 正确注入", msg.metadata["_protocol"]["msg_type"] == "task")
check("priority 正确注入", msg.metadata["_protocol"]["priority"] == "high")
check("ttl 正确注入", msg.metadata["_protocol"]["ttl"] == 300)
check("version 正确注入", msg.metadata["_protocol"]["version"] == "2.0")
check("msg_id 自动生成", len(msg.metadata["_protocol"]["msg_id"]) == 36)
check("HMAC 签名自动生成", "signature" in msg.metadata["_protocol"])

# 解析
parsed = Envelope.unwrap(msg)
check("unwrap 返回 Envelope 实例", isinstance(parsed, Envelope))
check("解析后 msg_type 一致", parsed.msg_type == MsgType.TASK)
check("解析后 priority 一致", parsed.priority == Priority.HIGH)
check("解析后 ttl 一致", parsed.ttl == 300)
check("解析后 msg_id 一致", parsed.msg_id == env.msg_id)

# 无协议信封的消息
plain_msg = MockMsg("Tony", "裸消息")
check("unwrap 裸消息返回 None", Envelope.unwrap(plain_msg) is None)


# ============================================================
# 测试 2: 四种消息类型工厂方法
# ============================================================

test_section("测试2: 四种消息类型工厂方法")

msg_task = MockMsg("Leader", "请调研AI芯片")
env_task = Envelope.task(priority=Priority.HIGH, ttl=3600)
env_task.wrap(msg_task)
check("Task 工厂: msg_type=task", Envelope.unwrap(msg_task).msg_type == MsgType.TASK)
check("Task 工厂: priority=high", Envelope.unwrap(msg_task).priority == Priority.HIGH)

msg_data = MockMsg("Researcher", "调研结果：市场规模500亿")
env_data = Envelope.data()
env_data.wrap(msg_data)
check("Data 工厂: msg_type=data", Envelope.unwrap(msg_data).msg_type == MsgType.DATA)

msg_ctrl = MockMsg("Leader", "创建3个研究员Agent")
env_ctrl = Envelope.control()
env_ctrl.wrap(msg_ctrl)
check("Control 工厂: msg_type=control", Envelope.unwrap(msg_ctrl).msg_type == MsgType.CONTROL)
check("Control 工厂: priority 自动设为 high", Envelope.unwrap(msg_ctrl).priority == Priority.HIGH)

msg_evt = MockMsg("Watchdog", "Agent3 心跳超时")
env_evt = Envelope.event()
env_evt.wrap(msg_evt)
check("Event 工厂: msg_type=event", Envelope.unwrap(msg_evt).msg_type == MsgType.EVENT)


# ============================================================
# 测试 3: 请求-响应链
# ============================================================

test_section("测试3: 请求-响应链（correlation_id）")

req_msg = MockMsg("Leader", "请调研")
req_env = Envelope.task(conversation_id="conv-001")
req_env.wrap(req_msg)
req_parsed = Envelope.unwrap(req_msg)

check("请求 conversation_id 正确", req_parsed.conversation_id == "conv-001")
check("请求 correlation_id 为 None", req_parsed.correlation_id is None)

reply_env = req_parsed.as_reply(in_reply_to=req_parsed.msg_id)
reply_msg = MockMsg("Researcher", "调研完成")
reply_env.wrap(reply_msg)
reply_parsed = Envelope.unwrap(reply_msg)

check("回复 msg_id 不同于请求", reply_parsed.msg_id != req_parsed.msg_id)
check("回复 correlation_id 指向请求", reply_parsed.correlation_id == req_parsed.msg_id)
check("回复 conversation_id 继承", reply_parsed.conversation_id == "conv-001")


# ============================================================
# 测试 4: TTL 过期检查
# ============================================================

test_section("测试4: TTL 过期检查")

env_never = Envelope(ttl=0)
check("TTL=0 永不过期", not env_never.is_expired())

env_future = Envelope(ttl=3600)
check("TTL=3600 未过期", not env_future.is_expired())

env_short = Envelope(ttl=1)
check("TTL=1 初始未过期", not env_short.is_expired())
time.sleep(1.2)
check("TTL=1 等待1.2秒后过期", env_short.is_expired())


# ============================================================
# 测试 5: JSON 序列化/反序列化
# ============================================================

test_section("测试5: JSON 序列化/反序列化（v2.0 RoutingHint）")

env_orig = Envelope(
    msg_type=MsgType.DATA,
    priority=Priority.NORMAL,
    conversation_id="json-test-001",
    routing=RoutingHint(addressing="multicast", visibility="group", distribution="fan_out"),
)

json_str = env_orig.model_dump_json()
check("model_dump_json 返回字符串", isinstance(json_str, str))

json_dict = json.loads(json_str)
env_restored = Envelope.model_validate(json_dict)
check("JSON 反序列化后 msg_type 一致", env_restored.msg_type == env_orig.msg_type)
check("JSON 反序列化后 conversation_id 一致", env_restored.conversation_id == "json-test-001")
check("JSON 反序列化后 routing.addressing 一致",
      env_restored.routing.addressing == "multicast")
check("JSON 反序列化后 routing.visibility 一致",
      env_restored.routing.visibility == "group")
check("JSON 反序列化后 routing.distribution 一致",
      env_restored.routing.distribution == "fan_out")

# 通过 msg.metadata 序列化
msg = MockMsg("sender", "hello")
env_orig.wrap(msg)
msg_json = json.dumps(msg.metadata)
msg_restored = json.loads(msg_json)
env_from_msg = Envelope.model_validate(msg_restored["_protocol"])
check("通过 msg.metadata 序列化后恢复成功", env_from_msg.msg_type == MsgType.DATA)


# ============================================================
# 测试 6: 与 AgentScope 原生 Msg 互不干扰
# ============================================================

test_section("测试6: 与 AgentScope 原生 Msg 互不干扰")

msg = MockMsg("user", "hello")
msg.metadata["custom_key"] = "custom_value"
msg.metadata["another"] = 123

env = Envelope(msg_type=MsgType.TASK)
env.wrap(msg)

check("原生 metadata 键保留", msg.metadata["custom_key"] == "custom_value")
check("原生 metadata 数值保留", msg.metadata["another"] == 123)
check("协议键 _protocol 存在", "_protocol" in msg.metadata)
check("协议键不影响原生键", "custom_key" in msg.metadata)

del msg.metadata["_protocol"]
check("删除协议键后，原生键仍存在", "custom_key" in msg.metadata)
check("删除协议键后，unwrap 返回 None", Envelope.unwrap(msg) is None)


# ============================================================
# 测试 7: HMAC 签名/验签/防篡改（v2.0新增）
# ============================================================

test_section("测试7: HMAC 签名/验签/防篡改")

# 设置密钥
Envelope.set_hmac_key("test-secret-key-123456")

# 签名
env_sig = Envelope(msg_type=MsgType.TASK, priority=Priority.HIGH, ttl=300)
env_sig.sign()
check("签名后 signature 不为空", env_sig.signature is not None)
check("签名长度为64字符（SHA256）", len(env_sig.signature) == 64)

# 验签
check("验签通过", env_sig.verify())

# 篡改检测
env_sig.ttl = 999
check("篡改后验签失败", not env_sig.verify())

# wrap 自动签名
msg_hmac = MockMsg("sender", "test hmac")
env_hmac = Envelope(msg_type=MsgType.TASK)
msg_hmac = env_hmac.wrap(msg_hmac)
check("wrap 自动签名", "signature" in msg_hmac.metadata["_protocol"])

# unwrap 自动验签
env_parsed = Envelope.unwrap(msg_hmac)
check("unwrap 验签通过（返回非None）", env_parsed is not None)

# 篡改metadata
msg_hmac.metadata["_protocol"]["ttl"] = 99999
env_tampered = Envelope.unwrap(msg_hmac)
check("篡改metadata后 unwrap 返回 None", env_tampered is None)

# 未设置密钥时自动生成
Envelope._hmac_key = None  # 重置密钥
env_auto = Envelope(msg_type=MsgType.TASK)
env_auto.sign()
check("未设置密钥时自动生成", env_auto.signature is not None)
check("自动生成密钥验签通过", env_auto.verify())


# ============================================================
# 测试 8: A2A 适配器（v2.0新增）
# ============================================================

test_section("测试8: A2A 适配器")

adapter = A2AAdapter()

# 元协议 → A2A Message
meta_env = Envelope(msg_type=MsgType.TASK, priority=Priority.HIGH, ttl=300)
a2a_msg = adapter.to_a2a_message(meta_env, content="调研任务", role="user")
check("A2A Message: message_id 一致", a2a_msg.message_id == meta_env.msg_id)
check("A2A Message: 有 parts", len(a2a_msg.parts) > 0)
check("A2A Message: 有 text part", any(p.type == A2APartType.TEXT for p in a2a_msg.parts))
check("A2A Message: 有 data part", any(p.type == A2APartType.DATA for p in a2a_msg.parts))
check("A2A Message: metadata 含 _meta_protocol", "_meta_protocol" in a2a_msg.metadata)

# A2A Message → 元协议
meta_restored = adapter.from_a2a_message(a2a_msg)
check("A2A→元协议: msg_type 一致", meta_restored.msg_type == MsgType.TASK)
check("A2A→元协议: priority 一致", meta_restored.priority == Priority.HIGH)

# 元协议 → A2A Task
a2a_task = adapter.to_a2a_task(meta_env, content="调研任务", session_id="session-001")
check("A2A Task: status=submitted", a2a_task.status == A2ATaskState.SUBMITTED)
check("A2A Task: 有 history", len(a2a_task.history) > 0)
check("A2A Task: session_id", a2a_task.session_id == "session-001")

# A2A Task → 元协议
meta_from_task = adapter.from_a2a_task(a2a_task)
check("A2A Task→元协议: 非None", meta_from_task is not None)

# 安全降级
plain_msg = MockMsg("plain", "hello")
env, is_fallback = adapter.safe_fallback_from_a2a(
    A2AMessage(message_id="test", role="user", parts=[])
)
check("安全降级: 返回 Envelope", isinstance(env, Envelope))
check("安全降级: is_fallback=True", is_fallback)

# 统计
check("adapter stats: to_a2a > 0", adapter.stats["to_a2a"] > 0)
check("adapter stats: from_a2a > 0", adapter.stats["from_a2a"] > 0)

# ============================================================
# 测试 9: 调研竞赛场景消息流模拟
# ============================================================

test_section("测试9: 调研竞赛场景消息流模拟")

conv_id = "research-competition-001"
researcher_ids = ["researcher-1", "researcher-2", "researcher-3"]

task_msgs = []
for rid in researcher_ids:
    msg = MockMsg("Leader", f"请调研AI芯片市场 - 分配给 {rid}")
    env = Envelope.task(conversation_id=conv_id, priority=Priority.HIGH, ttl=3600)
    env.wrap(msg)
    task_msgs.append(msg)

check("阶段1: 3条任务消息全部创建", len(task_msgs) == 3)
for i, m in enumerate(task_msgs):
    e = Envelope.unwrap(m)
    check(f"阶段1: 消息{i+1} 类型=task", e.msg_type == MsgType.TASK)
    check(f"阶段1: 消息{i+1} 会话ID一致", e.conversation_id == conv_id)
    check(f"阶段1: 消息{i+1} 有HMAC签名", e.signature is not None)

data_msgs = []
for i, task_msg in enumerate(task_msgs):
    task_env = Envelope.unwrap(task_msg)
    reply_msg = MockMsg(researcher_ids[i], f"调研结果: 市场数据{i+1}")
    reply_env = task_env.as_reply(in_reply_to=task_env.msg_id)
    reply_env.msg_type = MsgType.DATA
    reply_env.wrap(reply_msg)
    data_msgs.append(reply_msg)

check("阶段2: 3条数据消息全部创建", len(data_msgs) == 3)
for i, m in enumerate(data_msgs):
    e = Envelope.unwrap(m)
    task_e = Envelope.unwrap(task_msgs[i])
    check(f"阶段2: 消息{i+1} 类型=data", e.msg_type == MsgType.DATA)
    check(f"阶段2: 消息{i+1} correlation_id 指向任务", e.correlation_id == task_e.msg_id)

ctrl_msg = MockMsg("Leader", "创建3人专家评审团")
ctrl_env = Envelope.control(conversation_id=conv_id)
ctrl_env.wrap(ctrl_msg)
ctrl_parsed = Envelope.unwrap(ctrl_msg)
check("阶段3: 控制消息 msg_type=control", ctrl_parsed.msg_type == MsgType.CONTROL)

evt_msg = MockMsg("Leader", f"淘汰: {researcher_ids[2]} 排名末尾")
evt_env = Envelope.event(conversation_id=conv_id)
evt_env.wrap(evt_msg)
evt_parsed = Envelope.unwrap(evt_msg)
check("阶段4: 事件消息 msg_type=event", evt_parsed.msg_type == MsgType.EVENT)


# ============================================================
# 测试 10: 边界情况
# ============================================================

test_section("测试10: 边界情况")

msg_empty = MockMsg("test", "hello")
msg_empty.metadata = {}
env_empty = Envelope(msg_type=MsgType.TASK)
env_empty.wrap(msg_empty)
check("空 metadata 注入成功", "_protocol" in msg_empty.metadata)

env2 = Envelope(msg_type=MsgType.DATA)
env2.wrap(msg_empty)
check("重复 wrap 覆盖成功", Envelope.unwrap(msg_empty).msg_type == MsgType.DATA)

try:
    env.wrap("not a msg")
    check("非法类型应抛出异常", False, "应该抛出 TypeError 但没抛出")
except TypeError:
    check("非法类型抛出 TypeError", True)

big_content = "数据" * 10000
msg_big = MockMsg("sender", big_content)
env_big = Envelope(msg_type=MsgType.DATA)
env_big.wrap(msg_big)
check("大消息（2万字符）注入成功", "_protocol" in msg_big.metadata)
check("大消息原始内容未丢失", msg_big.content == big_content)

check("summary 包含版本号", "[v2.0]" in env.summary())
check("summary 包含类型", "type=data" in env_big.summary())

# ============================================================
# 结果汇总
# ============================================================

print(f"\n{'='*60}")
print(f"  验证结果汇总")
print(f"{'='*60}")
print(f"  ✅ 通过: {PASS}")
print(f"  ❌ 失败: {FAIL}")
print(f"  总计:   {PASS + FAIL}")

if FAIL == 0:
    print(f"\n  🎉 所有测试通过！消息契约（Envelope v2.0）设计验证完毕。")
    print(f"  可以直接复制 meta_protocol/ 到项目中使用。")
    sys.exit(0)
else:
    print(f"\n  ⚠️ 有 {FAIL} 个测试失败，请检查。")
    sys.exit(1)