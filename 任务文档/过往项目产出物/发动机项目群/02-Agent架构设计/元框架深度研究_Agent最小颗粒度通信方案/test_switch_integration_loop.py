"""步骤五+六+七 · 动态切换 + 集成 + Loop工程 可用性验证 v2.0（频率限制 + 文件锁 + StorageBackend）"""
import sys, os, asyncio, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_protocol.dynamic_switch import *
from meta_protocol.integration import *
from meta_protocol.loop_engineering import *
from meta_protocol.port_contract import *
from meta_protocol.constraint_engine import *
from meta_protocol.connector import *
from meta_protocol.envelope import Envelope, MsgType, Priority

PASS = FAIL = 0
def check(desc, cond, detail=""):
    global PASS, FAIL
    if cond: print(f"  ✅ {desc}"); PASS += 1
    else: print(f"  ❌ {desc}  — {detail}"); FAIL += 1
def section(title):
    print(f"\n{'='*50}\n  {title}\n{'='*50}")

# ============================================================
# 动态切换控制器
# ============================================================
async def dynamic_switch_tests():
    section("动态切换: 规则分析")
    agent = AgentRef("Leader")
    port = PortContract.fan_out_worker()
    ctrl = DynamicSwitchController(agent, port)

    # 控制消息 → 扇出
    ctrl_msg = type("MockMsg",(),{"name":"s","content":"创建","metadata":{},"id":"c1"})()
    Envelope.control().wrap(ctrl_msg)
    rec = ctrl.analyze(ctrl_msg)
    check("控制消息→推荐扇出", rec.new_port.distribution == Distribution.FAN_OUT)
    check("控制消息→高置信度", rec.confidence >= 0.8)

    # 普通消息 → 不切换
    plain = type("MockMsg",(),{"name":"s","content":"hi","metadata":{},"id":"p1"})()
    rec2 = ctrl.analyze(plain)
    check("无信封消息→低置信度", rec2.confidence < 0.6)

    section("动态切换: 执行切换")
    port2 = PortContract.agent_scope_default()
    ctrl2 = DynamicSwitchController(agent, port2)
    rec3 = SwitchRecommendation("测试",
        port2.override(addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE))
    result = await ctrl2.switch(rec3)
    check("合法切换通过", result.is_valid)
    check("切换后 addressing 更新", ctrl2.port.addressing == AddressingMode.UNICAST)
    check("切换后 visibility 更新", ctrl2.port.visibility == VisibilityDomain.PRIVATE)
    check("历史记录", len(ctrl2.history) == 1)

    # 非法切换（fan_out + permanent）
    rec4 = SwitchRecommendation("非法", port2.override(distribution=Distribution.FAN_OUT, lifecycle=Lifecycle.PERMANENT))
    result4 = await ctrl2.switch(rec4)
    check("非法切换被拒绝", not result4.is_valid)

    section("动态切换: 频率限制")
    ctrl3 = DynamicSwitchController(agent, PortContract.agent_scope_default(),
        min_switch_interval=0.02, max_switches_per_minute=100)
    # 快速连续切换应全部通过（加微小延迟避开频率限制）
    for i in range(5):
        await asyncio.sleep(0.03)
        rec = SwitchRecommendation(f"test{i}", ctrl3.port.override(
            addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE))
        result = await ctrl3.switch(rec)
        check(f"快速切换{i+1}通过", result.is_valid)
    check("switch_stats 有记录", ctrl3.switch_stats["total_switches"] == 5)
    check("switch_stats switches_last_minute", ctrl3.switch_stats["switches_last_minute"] == 5)

    # 频率限制：设置极低上限
    ctrl4 = DynamicSwitchController(agent, PortContract.agent_scope_default(),
        min_switch_interval=0.01, max_switches_per_minute=2)
    for i in range(2):
        rec = SwitchRecommendation(f"test{i}", ctrl4.port.override(
            addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE))
        await ctrl4.switch(rec)
    # 第3次应被拒绝
    rec_over = SwitchRecommendation("over", ctrl4.port.override(
        addressing=AddressingMode.BROADCAST, visibility=VisibilityDomain.GLOBAL))
    result_over = await ctrl4.switch(rec_over)
    check("频率超限被拒绝", not result_over.is_valid)

    section("动态切换: Prompt注入")
    prompt = ctrl2.get_system_prompt_appendix()
    check("Prompt包含寻址方式", "unicast" in prompt)
    check("Prompt包含可见性域", "private" in prompt)
    check("Prompt包含分发策略", "direct" in prompt)
    check("Prompt包含10要素说明", "Memory归属" in prompt)

# ============================================================
# 集成中间件
# ============================================================
async def integration_tests():
    section("集成中间件: SystemPrompt")
    mock_agent = type("MockAgent",(),{"name":"TestAgent"})()
    mw = MetaProtocolMiddleware(mock_agent, PortContract.isolated_worker())
    result = mw.on_system_prompt("You are a helpful assistant.")
    check("SystemPrompt包含协议说明", "通信协议配置" in result)
    check("SystemPrompt保留原始内容", "You are a helpful assistant." in result)

    section("集成中间件: ModelCall")
    raw = type("MockMsg",(),{"name":"s","content":"hi","metadata":{},"id":"mc1"})()
    processed = mw.on_model_call(raw)
    check("无信封消息自动注入", "_protocol" in processed.metadata)

    section("集成中间件: Reasoning")
    output = "我需要进行独立调研，这是最合适的方案。"
    result = await mw.on_reasoning(raw, output)
    check("onReasoning不修改输出", result == output)
    check("检测到'独立'关键词后切换为exclusive", mw.port.memory_belonging == MemoryBelonging.EXCLUSIVE)
    check("检测到'独立'关键词后切换为full隔离", mw.port.context_isolation == ContextIsolation.FULL)

    section("集成中间件: Acting")
    mw2 = MetaProtocolMiddleware(mock_agent,
        PortContract.isolated_worker().override(
            capabilities=Capabilities(can_create_agent=False, can_send=True, can_receive=True)
        )
    )
    create_action = type("MockAction",(),{"type":"create_agent"})()
    try:
        await mw2.on_acting(raw, create_action)
        check("无创建权限应拦截", False, "应抛出PermissionError")
    except PermissionError:
        check("无创建权限正确拦截", True)

    section("集成中间件: 状态查询")
    status = mw.status()
    check("状态包含agent名", status["agent"] == "TestAgent")
    check("状态包含port", "addressing" in status["port"])
    check("状态包含visibility", "visibility" in status["port"])
    check("状态包含switch_stats", "switch_stats" in status)

# ============================================================
# Loop工程
# ============================================================
async def loop_engineering_tests():
    section("Loop工程: StopHook")
    hook = StopHook(max_rounds=5, max_tokens=1000, max_seconds=3600)
    for i in range(6):
        if hook.check(token_count=100):
            break
    check("StopHook: 5轮后停止", hook.stats["rounds"] == 5)
    check("StopHook: stop_reason", "最大轮数" in hook.stop_reason)

    hook2 = StopHook(max_rounds=100, max_tokens=500, max_seconds=3600)
    for i in range(10):
        if hook2.check(token_count=100):
            break
    check("StopHook: Token超限停止", hook2.stats["total_tokens"] >= 500)

    # 自定义条件
    flag = [False]
    hook3 = StopHook(max_rounds=100, custom_condition=lambda: flag[0])
    flag[0] = True
    check("StopHook: 自定义条件", hook3.check())

    section("Loop工程: CircuitBreaker")
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60)
    for i in range(3):
        try:
            await breaker.call(asyncio.sleep(0))
        except:
            pass
    check("CircuitBreaker: 3次成功不触发", breaker.state == "closed")

    b2 = CircuitBreaker(failure_threshold=2, reset_timeout=60)
    for i in range(2):
        try:
            async def fail(): raise RuntimeError("fail")
            await b2.call(fail())
        except RuntimeError:
            pass
    check("CircuitBreaker: 2次失败打开", b2.state == "open")
    try:
        await b2.call(asyncio.sleep(0))
        check("CircuitBreaker: 打开后拒绝", False, "应抛出CircuitBreakerOpen")
    except CircuitBreakerOpen:
        check("CircuitBreaker: 打开后正确抛出", True)

    section("Loop工程: Watchdog")
    wd = Watchdog("TestAgent", timeout=2.0, check_interval=0.5)
    await wd.start()
    wd.heartbeat()
    await asyncio.sleep(0.6)
    check("Watchdog: 正常心跳未超时", wd.stats["timeout_count"] == 0)
    await wd.stop()
    check("Watchdog: 停止后 running=False", not wd.stats["running"])

    section("Loop工程: RalphLoop + FileStorageBackend")
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = FileStorageBackend(save_dir=tmpdir)
        ralph = RalphLoop(backend=backend)
        state = {"round": 5, "tokens": 5000, "context": ["msg1", "msg2"]}
        ralph.save("test_agent", state)
        loaded = ralph.load("test_agent")
        check("RalphLoop: 保存+加载 round", loaded["round"] == 5)
        check("RalphLoop: 保存+加载 tokens", loaded["tokens"] == 5000)
        check("RalphLoop: 保存+加载 context", loaded["context"] == ["msg1", "msg2"])
        ralph.delete("test_agent")
        check("RalphLoop: 删除后load返回None", ralph.load("test_agent") is None)

    section("Loop工程: FileLock")
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = os.path.join(tmpdir, "test.lock")
        lock = FileLock(lock_path)
        check("FileLock: acquire成功", lock.acquire())
        lock.release()
        check("FileLock: release后可重新acquire", lock.acquire())
        lock.release()

        # 上下文管理器
        with FileLock(lock_path):
            check("FileLock: 上下文管理器进入", True)
        check("FileLock: 上下文管理器退出", True)

        # 超时测试
        lock2 = FileLock(lock_path)
        lock2.acquire()
        lock3 = FileLock(lock_path, timeout=0.5)
        check("FileLock: 超时返回False", not lock3.acquire())
        lock2.release()

asyncio.run(dynamic_switch_tests())
asyncio.run(integration_tests())
asyncio.run(loop_engineering_tests())

print(f"\n{'='*50}\n  ✅ 通过: {PASS}  ❌ 失败: {FAIL}  总计: {PASS+FAIL}\n{'='*50}")
sys.exit(0 if FAIL == 0 else 1)