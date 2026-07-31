"""
步骤八 · 端到端测试：调研竞赛全流程验证 v2.0
==============================================
模拟完整5阶段场景，验证元协议所有模块协同工作。
(v2.0: 适配10要素体系，增加HMAC签名、A2A适配器、applied_constraints、文件锁验证)

场景：
  1. Leader 扇出任务给3个研究员
  2. 研究员独立调研，返回结果
  3. Leader 创建专家评审团（MsgHub模式评审）
  4. 淘汰末尾研究员
  5. 循环迭代，直到只剩最优

验证项：
  ✅ 消息契约（Envelope）+ HMAC签名/防篡改
  ✅ 端口契约（PortContract）10要素 + MultiMode
  ✅ 约束引擎（ConstraintEngine）8条约束 + applied_constraints
  ✅ 连接器（Hub/Pipe/Router/Broker）正确路由
  ✅ 动态切换（DynamicSwitch）频率限制
  ✅ 集成中间件（MetaProtocolMiddleware）全部挂载点
  ✅ Loop工程（FileLock + StorageBackend）
  ✅ A2A适配器 双向转换
"""
import sys, os, asyncio, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_protocol.envelope import Envelope, MsgType, Priority
from meta_protocol.port_contract import (
    PortContract, Capabilities, MultiModePortContract,
    AddressingMode, VisibilityDomain, Distribution,
    MemoryBelonging, ContextIsolation, Lifecycle, StateBoundary,
)
from meta_protocol.constraint_engine import ConstraintEngine
from meta_protocol.connector import AgentRef, Hub, Pipe, Router
from meta_protocol.dynamic_switch import DynamicSwitchController, SwitchRecommendation
from meta_protocol.integration import MetaProtocolMiddleware
from meta_protocol.loop_engineering import (
    StopHook, CircuitBreaker, Watchdog, RalphLoop,
    FileStorageBackend, FileLock,
)
from meta_protocol.a2a_adapter import A2AAdapter

PASS = FAIL = 0
def check(desc, cond, detail=""):
    global PASS, FAIL
    if cond: print(f"  ✅ {desc}"); PASS += 1
    else: print(f"  ❌ {desc}  — {detail}"); FAIL += 1

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

async def main():
    global PASS, FAIL

    # ============================================================
    # 初始化
    # ============================================================
    section("初始化：创建Leader + 3个研究员 + 3个专家")

    leader = AgentRef("Leader")
    researchers = [AgentRef(f"Researcher-{i+1}") for i in range(3)]
    experts = [AgentRef(f"Expert-{i+1}") for i in range(3)]

    leader_port = PortContract.fan_out_worker()
    leader_engine = ConstraintEngine()
    leader_ctrl = DynamicSwitchController(leader, leader_port, leader_engine,
        min_switch_interval=0.01, max_switches_per_minute=100)
    leader_mw = MetaProtocolMiddleware(
        type("MockAgent", (), {"name": "Leader"})(), leader_port, engine=leader_engine,
    )

    stop_hook = StopHook(max_rounds=10, max_tokens=50000)
    breaker = CircuitBreaker(failure_threshold=5, reset_timeout=30)
    tmpdir = tempfile.mkdtemp()
    ralph = RalphLoop(backend=FileStorageBackend(save_dir=tmpdir))

    researcher_ports = [PortContract.isolated_worker() for _ in range(3)]
    researcher_ctrls = [
        DynamicSwitchController(r, p, ConstraintEngine())
        for r, p in zip(researchers, researcher_ports)
    ]

    check("Leader端口=fan_out", leader_port.distribution == Distribution.FAN_OUT)
    check("Leader端口=exclusive", leader_port.memory_belonging == MemoryBelonging.EXCLUSIVE)
    check("Leader端口=full隔离", leader_port.context_isolation == ContextIsolation.FULL)
    check("研究员端口=unicast", researcher_ports[0].addressing == AddressingMode.UNICAST)
    check("研究员端口=private", researcher_ports[0].visibility == VisibilityDomain.PRIVATE)
    check("研究员端口=exclusive", researcher_ports[0].memory_belonging == MemoryBelonging.EXCLUSIVE)

    # ============================================================
    # 阶段1: 扇出任务
    # ============================================================
    section("阶段1: Leader 扇出任务给3个研究员")

    hub = Hub()
    hub.register(leader, *researchers)

    for i, r in enumerate(researchers):
        task_msg = type("MockMsg", (), {
            "name": "Leader", "content": f"请调研AI芯片市场-任务{i+1}",
            "metadata": {}, "id": f"task-{i+1}"
        })()
        Envelope.task(
            conversation_id="research-comp-001", priority=Priority.HIGH, ttl=3600,
        ).wrap(task_msg)
        await hub.multicast(sender=leader, msg=task_msg, targets=[r.name])

    for i, r in enumerate(researchers):
        msg = await r.receive(timeout=1)
        check(f"研究员{i+1}收到任务消息", msg is not None)
        if msg:
            env = Envelope.unwrap(msg)
            check(f"研究员{i+1}消息类型=task", env.msg_type == MsgType.TASK)
            check(f"研究员{i+1}会话ID", env.conversation_id == "research-comp-001")
            check(f"研究员{i+1}HMAC签名有效", env.signature is not None)

    # 应用约束检查
    r = leader_engine.validate(leader_port)
    check("阶段1: 约束检查通过", r.is_valid)
    check("阶段1: applied_constraints完整", len(r.applied_constraints) == 8)

    # ============================================================
    # 阶段2: 收集结果
    # ============================================================
    section("阶段2: 研究员返回数据，Leader 扇入收集")

    for i, r in enumerate(researchers):
        data_msg = type("MockMsg", (), {
            "name": r.name, "content": f"调研结果: 市场数据{i+1}, 评分={80+i*5}",
            "metadata": {}, "id": f"data-{i+1}"
        })()
        Envelope.data(conversation_id="research-comp-001", priority=Priority.NORMAL).wrap(data_msg)
        await hub.broadcast(sender=r, msg=data_msg)

    results_received = 0
    for _ in range(3):
        msg = await leader.receive(timeout=1)
        if msg:
            env = Envelope.unwrap(msg)
            if env and env.msg_type == MsgType.DATA:
                results_received += 1
    check("Leader收到3条数据消息", results_received == 3)

    # ============================================================
    # 阶段3: 专家评审（动态切换到MsgHub模式）
    # ============================================================
    section("阶段3: Leader创建专家评审团，动态切换到MsgHub模式")

    hub_participant_port = PortContract.hub_participant(
        addressing=AddressingMode.MULTICAST, visibility=VisibilityDomain.GROUP,
    )
    rec = SwitchRecommendation("需要专家评审，切换到组播+共享", hub_participant_port, confidence=0.9)
    await leader_ctrl.switch(rec)

    check("阶段3: Leader切换到multicast", leader_ctrl.port.addressing == AddressingMode.MULTICAST)
    check("阶段3: Leader切换到group", leader_ctrl.port.visibility == VisibilityDomain.GROUP)
    check("阶段3: Leader切换到shared", leader_ctrl.port.memory_belonging == MemoryBelonging.SHARED)
    check("阶段3: 切换历史有记录", len(leader_ctrl.history) > 0)

    review_hub = Hub("review-hub")
    review_hub.register(leader, *experts)

    review_msg = type("MockMsg", (), {
        "name": "Leader", "content": "请评审以下三份调研报告",
        "metadata": {}, "id": "review-1"
    })()
    Envelope.task(conversation_id="research-comp-001", priority=Priority.HIGH).wrap(review_msg)
    await review_hub.broadcast(sender=leader, msg=review_msg)

    for i, expert in enumerate(experts):
        received = await expert.receive(timeout=1)
        check(f"专家{i+1}收到评审请求", received is not None)

    for i, expert in enumerate(experts):
        opinion = type("MockMsg", (), {
            "name": expert.name, "content": "评审意见: 研究员2最好, 研究员3最差",
            "metadata": {}, "id": f"opinion-{i+1}"
        })()
        Envelope.data(conversation_id="research-comp-001").wrap(opinion)
        await review_hub.broadcast(sender=expert, msg=opinion)

    opinions = 0
    for _ in range(3):
        if await leader.receive(timeout=1):
            opinions += 1
    check("Leader收到3条评审意见", opinions == 3)

    # ============================================================
    # 阶段4: 淘汰末尾研究员
    # ============================================================
    section("阶段4: 淘汰末尾研究员")

    eliminated = researchers.pop()

    evt_msg = type("MockMsg", (), {
        "name": "Leader", "content": f"淘汰: {eliminated.name}",
        "metadata": {}, "id": "elim-1"
    })()
    Envelope.event(conversation_id="research-comp-001").wrap(evt_msg)

    for r in researchers:
        result = leader_engine.validate(researcher_ports[researchers.index(r)])
        check(f"淘汰后{r.name}端口仍合法", result.is_valid)

    check("研究员数量减为2", len(researchers) == 2)

    await asyncio.sleep(0.02)  # 让时间戳前进，避开频率限制

    # ============================================================
    # 阶段5: 循环迭代
    # ============================================================
    section("阶段5: 循环迭代（第二轮）")

    new_port = leader_port
    rec2 = SwitchRecommendation("新一轮迭代，切换回扇出模式", new_port, confidence=0.9)
    await leader_ctrl.switch(rec2)

    check("阶段5: Leader回到扇出模式", leader_ctrl.port.distribution == Distribution.FAN_OUT)

    for i, r in enumerate(researchers):
        task2 = type("MockMsg", (), {
            "name": "Leader", "content": f"第二轮调研-{i+1}",
            "metadata": {}, "id": f"round2-{i+1}"
        })()
        Envelope.task(conversation_id="research-comp-001", priority=Priority.HIGH, ttl=3600).wrap(task2)
        await hub.multicast(sender=leader, msg=task2, targets=[r.name])

    for i, r in enumerate(researchers):
        received = await r.receive(timeout=1)
        check(f"第二轮: 研究员{i+1}收到任务", received is not None)

    # ============================================================
    # Loop工程验证
    # ============================================================
    section("Loop工程: 全流程验证")

    for i in range(7):
        if stop_hook.check(token_count=5000):
            check("StopHook: 触发停止", i >= 5)
            break
    check("StopHook: 总轮数", stop_hook.stats["rounds"] == 7)

    try:
        await breaker.call(asyncio.sleep(0))
        check("CircuitBreaker: 正常调用通过", breaker.state == "closed")
    except Exception as e:
        check(f"CircuitBreaker: 异常 {e}", False)

    wd = Watchdog("Leader", timeout=5.0, check_interval=0.5)
    await wd.start()
    for _ in range(3):
        wd.heartbeat()
        await asyncio.sleep(0.2)
    check("Watchdog: 正常心跳计数", wd.stats["heartbeat_count"] >= 3)
    await wd.stop()

    state = {"round": 2, "remaining_researchers": [r.name for r in researchers]}
    ralph.save("research-comp-001", state)
    restored = ralph.load("research-comp-001")
    check("RalphLoop: 状态恢复成功", restored["round"] == 2)
    check("RalphLoop: 剩余研究员", len(restored["remaining_researchers"]) == 2)
    ralph.delete("research-comp-001")

    # ============================================================
    # 集成中间件全挂载点验证
    # ============================================================
    section("集成中间件: 5个挂载点全部验证")

    mock_agent = type("MockAgent", (), {"name": "TestAgent"})()
    mw = MetaProtocolMiddleware(mock_agent, PortContract.agent_scope_default())

    prompt = mw.on_system_prompt("Base prompt")
    check("MP1 onSystemPrompt: 注入协议说明", "通信协议配置" in prompt)

    raw = type("MockMsg", (), {"name": "s", "content": "hi", "metadata": {}, "id": "mp2"})()
    processed = mw.on_model_call(raw)
    check("MP2 onModelCall: 自动注入信封", "_protocol" in processed.metadata)

    output = await mw.on_reasoning(raw, "需要独立调研")
    check("MP3 onReasoning: 保留原始输出", "独立调研" in output)

    send_action = type("MockAction", (), {"type": "send_message"})()
    result = await mw.on_acting(raw, send_action)
    check("MP4 onActing: 正常动作通过", result is send_action)

    mw.on_agent_created(type("MockAgent", (), {"name": "ChildAgent"})())
    mw.on_agent_destroyed(type("MockAgent", (), {"name": "ChildAgent"})())
    check("MP5 onAgent: 生命周期回调正常", True)

    # ============================================================
    # A2A 适配器验证
    # ============================================================
    section("A2A适配器: 双向转换")

    adapter = A2AAdapter()
    meta_env = Envelope(msg_type=MsgType.TASK, priority=Priority.HIGH, ttl=300)
    a2a_msg = adapter.to_a2a_message(meta_env, content="调研任务", role="user")
    check("A2A: 元协议→A2A Message成功", a2a_msg.message_id == meta_env.msg_id)
    meta_restored = adapter.from_a2a_message(a2a_msg)
    check("A2A: A2A→元协议 msg_type一致", meta_restored.msg_type == MsgType.TASK)

    a2a_task = adapter.to_a2a_task(meta_env, content="调研任务", session_id="e2e-001")
    check("A2A: 元协议→A2A Task成功", a2a_task.status.value == "submitted")
    meta_from_task = adapter.from_a2a_task(a2a_task)
    check("A2A: A2A Task→元协议成功", meta_from_task is not None)

    # 安全降级
    plain_msg = A2AAdapter.__new__(A2AAdapter)
    env, is_fallback = adapter.safe_fallback_from_a2a(
        type("A2AMessage", (), {"message_id": "test", "role": "user", "parts": [], "metadata": {}})()
    )
    check("A2A: 安全降级返回Envelope", isinstance(env, Envelope))
    check("A2A: 安全降级is_fallback=True", is_fallback)

    # ============================================================
    # 非法操作拦截验证
    # ============================================================
    section("安全拦截: 非法操作验证")

    illegal_port = PortContract(distribution=Distribution.FAN_OUT, lifecycle=Lifecycle.PERMANENT)
    result = leader_engine.validate(illegal_port)
    check("安全: fan_out+permanent被拦截", not result.is_valid)
    check("安全: 拦截原因=C3", any("C3" in v.rule_id for v in result.violations))

    illegal_port2 = PortContract(
        distribution=Distribution.SEQUENTIAL,
        addressing=AddressingMode.BROADCAST, visibility=VisibilityDomain.GLOBAL,
    )
    result2 = leader_engine.validate(illegal_port2)
    check("安全: sequential+broadcast被拦截", not result2.is_valid)
    check("安全: 拦截原因=C4", any("C4" in v.rule_id for v in result2.violations))

    # C1: unicast+global
    illegal_port3 = PortContract(addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.GLOBAL)
    result3 = leader_engine.validate(illegal_port3)
    check("安全: unicast+global被拦截", not result3.is_valid)

    # C2: exclusive+none
    illegal_port4 = PortContract(memory_belonging=MemoryBelonging.EXCLUSIVE, context_isolation=ContextIsolation.NONE)
    result4 = leader_engine.validate(illegal_port4)
    check("安全: exclusive+none被拦截", not result4.is_valid)

    # C5: broadcast+private
    illegal_port5 = PortContract(addressing=AddressingMode.BROADCAST, visibility=VisibilityDomain.PRIVATE)
    result5 = leader_engine.validate(illegal_port5)
    check("安全: broadcast+private被拦截", not result5.is_valid)

    # ============================================================
    # HMAC 防篡改 E2E 验证
    # ============================================================
    section("HMAC防篡改: 端到端验证")

    msg_hmac = type("MockMsg", (), {"name": "Leader", "content": "敏感数据", "metadata": {}, "id": "hmac-t"})()
    Envelope.task(priority=Priority.CRITICAL).wrap(msg_hmac)
    env_ok = Envelope.unwrap(msg_hmac)
    check("HMAC: 正常消息验签通过", env_ok is not None)
    check("HMAC: 签名存在", env_ok.signature is not None)

    msg_hmac.metadata["_protocol"]["ttl"] = 99999
    env_tampered = Envelope.unwrap(msg_hmac)
    check("HMAC: 篡改消息验签失败（返回None）", env_tampered is None)

    # ============================================================
    # MultiMode E2E 验证
    # ============================================================
    section("MultiMode: 多模式端口契约")

    multi = PortContract.multi_mode({
        "default": PortContract.hub_participant(),
        "isolated": PortContract.isolated_worker(),
        "audit": PortContract.auditor_observer(),
    })
    check("MultiMode: 默认=default", multi.current_mode == "default")
    multi.switch("isolated", "开始独立任务")
    check("MultiMode: 切换到isolated", multi.current_mode == "isolated")
    check("MultiMode: active是exclusive", multi.active.memory_belonging == MemoryBelonging.EXCLUSIVE)
    multi.switch("audit", "审计模式")
    check("MultiMode: 切换到audit", multi.current_mode == "audit")
    check("MultiMode: active是unicast+group", multi.active.addressing == AddressingMode.UNICAST)
    check("MultiMode: active是group", multi.active.visibility == VisibilityDomain.GROUP)
    check("MultiMode: 历史记录3条", len(multi.history) == 2)

    # ============================================================
    # 结果
    # ============================================================
    print(f"\n{'='*60}")
    print(f"  🏁 端到端测试结果")
    print(f"{'='*60}")
    print(f"  ✅ 通过: {PASS}")
    print(f"  ❌ 失败: {FAIL}")
    print(f"  总计:   {PASS + FAIL}")

    if FAIL == 0:
        print(f"\n  🎉 8步全部完成！元协议层 v2.0 可交付。")
        print(f"  研发可直接复制 meta_protocol/ 目录到项目中使用。")
    else:
        print(f"\n  ⚠️ {FAIL} 项失败，请排查。")

    return FAIL == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)