"""步骤三+四 · 约束引擎 + 连接器 可用性验证 v2.0（8约束 + Connector兼容性 + applied_constraints）"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_protocol.constraint_engine import *
from meta_protocol.connector import *
from meta_protocol.port_contract import *
from meta_protocol.envelope import Envelope, MsgType, Priority

PASS = FAIL = 0
def check(desc, cond, detail=""):
    global PASS, FAIL
    if cond: print(f"  ✅ {desc}"); PASS += 1
    else: print(f"  ❌ {desc}  — {detail}"); FAIL += 1

def section(title):
    print(f"\n{'='*50}\n  {title}\n{'='*50}")

# ============================================================
# 约束引擎测试
# ============================================================
section("约束引擎: 硬约束 C1-C5")
engine = ConstraintEngine()

# C1: unicast → private
p = PortContract(addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.GLOBAL)
r = engine.validate(p)
check("C1: unicast+global 违反", not r.is_valid)
check("C1: 违规消息包含 C1", any("C1" in v.rule_id for v in r.violations))

# C2: exclusive → full
p = PortContract(memory_belonging=MemoryBelonging.EXCLUSIVE, context_isolation=ContextIsolation.NONE)
r = engine.validate(p)
check("C2: exclusive+none 违反", not r.is_valid)

# C3: fan_out → temporary
p = PortContract(distribution=Distribution.FAN_OUT, lifecycle=Lifecycle.PERMANENT)
r = engine.validate(p)
check("C3: fan_out+permanent 违反", not r.is_valid)
check("C3: 违规消息包含 C3", any("C3" in v.rule_id for v in r.violations))

p2 = PortContract(distribution=Distribution.FAN_OUT, lifecycle=Lifecycle.TEMPORARY)
r2 = engine.validate(p2)
check("C3: fan_out+temporary 通过", r2.is_valid)

# C4: sequential → unicast+private
p3 = PortContract(distribution=Distribution.SEQUENTIAL, addressing=AddressingMode.BROADCAST, visibility=VisibilityDomain.GLOBAL)
r3 = engine.validate(p3)
check("C4: sequential+broadcast+global 违反", not r3.is_valid)

p4 = PortContract(distribution=Distribution.SEQUENTIAL, addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE)
r4 = engine.validate(p4)
check("C4: sequential+unicast+private 通过", r4.is_valid)

# C5: broadcast → global
p5 = PortContract(addressing=AddressingMode.BROADCAST, visibility=VisibilityDomain.PRIVATE)
r5 = engine.validate(p5)
check("C5: broadcast+private 违反", not r5.is_valid)

section("约束引擎: 软约束 C6-C8")
# C6: unicast+private → 建议 exclusive
p6 = PortContract(addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE, memory_belonging=MemoryBelonging.SHARED)
r6 = engine.validate(p6)
check("C6: unicast+private+shared 触发警告", len(r6.warnings) > 0)
check("C6: 但整体仍有效", r6.is_valid)

# C7: shared → 建议 none
p7 = PortContract(memory_belonging=MemoryBelonging.SHARED, context_isolation=ContextIsolation.FULL)
r7 = engine.validate(p7)
check("C7: shared+full 触发警告", len(r7.warnings) > 0)

# C8: temporary → 建议 stateless
p8 = PortContract(lifecycle=Lifecycle.TEMPORARY, state_boundary=StateBoundary.STATEFUL)
r8 = engine.validate(p8)
check("C8: temporary+stateful 触发警告", len(r8.warnings) > 0)

section("约束引擎: applied_constraints")
pc = PortContract.isolated_worker()
r = engine.validate(pc)
check("isolated_worker: 记录了8条约束", len(r.applied_constraints) == 8)
check("isolated_worker: 包含 C1", "C1" in r.applied_constraints)
check("isolated_worker: 全部通过", r.is_valid)
check("summary 包含通过信息", "通过" in r.summary())

pc_violated = PortContract(addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.GLOBAL)
r_v = engine.validate(pc_violated)
check("violated: summary 包含违反", "违反" in r_v.summary())
check("violated: applied_constraints 包含 C1", "C1" in r_v.applied_constraints)

section("约束引擎: 切换校验")
old = PortContract.isolated_worker()
new = PortContract.hub_participant()
r_sw = engine.validate_switch(old, new)
check("切换: isolated→shared 触发警告", len(r_sw.warnings) > 0)

old2 = PortContract.fan_out_worker()
new2 = old2.override(lifecycle=Lifecycle.PERMANENT)
r_sw2 = engine.validate_switch(old2, new2)
check("切换: temporary→permanent 触发警告", any("SWITCH" in w.rule_id for w in r_sw2.warnings))

# visibility 升级警告
old3 = PortContract.isolated_worker()  # private
new3 = old3.override(visibility=VisibilityDomain.GLOBAL)
r_sw3 = engine.validate_switch(old3, new3)
check("切换: private→global 触发可见性警告", any("SWITCH-03" in w.rule_id for w in r_sw3.warnings))

section("约束引擎: Connector 兼容性校验")
pc_uni = PortContract(addressing=AddressingMode.UNICAST, distribution=Distribution.DIRECT)
r_conn1 = engine.validate_connector_compatibility(pc_uni, "Pipe")
check("unicast+direct → Pipe 兼容", r_conn1.is_valid)
r_conn2 = engine.validate_connector_compatibility(pc_uni, "Hub")
check("unicast+direct → Hub 不兼容", not r_conn2.is_valid)

pc_bc = PortContract(addressing=AddressingMode.BROADCAST, distribution=Distribution.DIRECT)
r_conn3 = engine.validate_connector_compatibility(pc_bc, "Hub")
check("broadcast+direct → Hub 兼容", r_conn3.is_valid)

# get_compatible_connectors
compat = engine.get_compatible_connectors(pc_uni)
check("unicast+direct 兼容列表非空", len(compat) > 0)
check("unicast+direct 兼容 Pipe", "Pipe" in compat)

# ============================================================
# 连接器测试
# ============================================================
async def connector_tests():
    section("连接器: Hub 广播")
    a1, a2, a3 = AgentRef("Leader"), AgentRef("Worker1"), AgentRef("Worker2")
    hub = Hub()
    hub.register(a1, a2, a3)

    msg = type("MockMsg", (), {"name": "Leader", "content": "hello", "metadata": {}, "id": "001"})()
    await hub.broadcast(sender=a1, msg=msg)
    check("Hub: a2收到消息", await a2.receive(timeout=1) is not None)
    check("Hub: a3收到消息", await a3.receive(timeout=1) is not None)
    check("Hub: a1未收到自己的消息", await a1.receive(timeout=0.3) is None)
    check("Hub: stats.sent=1", hub.stats["sent"] == 1)

    section("连接器: Hub 组播")
    msg2 = type("MockMsg", (), {"name": "Leader", "content": "secret", "metadata": {}, "id": "002"})()
    await hub.multicast(sender=a1, msg=msg2, targets=["Worker1"])
    check("Hub组播: a2收到", await a2.receive(timeout=1) is not None)
    check("Hub组播: a3未收到", await a3.receive(timeout=0.3) is None)

    section("连接器: Pipe 点对点")
    a4, a5 = AgentRef("AgentA"), AgentRef("AgentB")
    pipe = Pipe(a4, a5)
    msg3 = type("MockMsg", (), {"name": "AgentA", "content": "ping", "metadata": {}, "id": "003"})()
    await pipe.send(msg3, sender=a4)
    check("Pipe: a5收到", await a5.receive(timeout=1) is not None)
    check("Pipe: a4未收到", await a4.receive(timeout=0.3) is None)

    msg4 = type("MockMsg", (), {"name": "AgentB", "content": "pong", "metadata": {}, "id": "004"})()
    await pipe.send(msg4, sender=a5)
    check("Pipe: a4收到回复", await a4.receive(timeout=1) is not None)

    section("连接器: Router 路由（v2.0 addressing+visibility）")
    router = Router()
    a6, a7, a8 = AgentRef("R1"), AgentRef("R2"), AgentRef("R3")
    router.add_route(a6, addressing="unicast", visibility="private", priority=1)
    router.add_route(a7, addressing="multicast", visibility="group", priority=2)
    router.add_route(a8, addressing="multicast", visibility="group", priority=1)
    targets = router.resolve(addressing="multicast", visibility="group")
    check("Router: multicast+group匹配2个", len(targets) == 2)
    check("Router: 优先级排序 a7在前", targets[0].name == "R2")
    msg5 = type("MockMsg", (), {"name": "sender", "content": "routed", "metadata": {}, "id": "005"})()
    await router.route(msg5, target=a6)
    check("Router: 直接路由到a6", await a6.receive(timeout=1) is not None)
    # resolve_address 兼容旧版格式
    targets2 = router.resolve_address("unicast+private")
    check("Router: resolve_address兼容", len(targets2) == 1)

    section("连接器: Broker 发布订阅")
    broker = Broker(max_retries=2)
    a9, a10 = AgentRef("Sub1"), AgentRef("Sub2")
    broker.subscribe("research-001", a9)
    broker.subscribe("research-001", a10)
    msg6 = type("MockMsg", (), {"name": "publisher", "content": "update", "metadata": {}, "id": "006"})()
    await broker.publish("research-001", msg6)
    check("Broker: a9收到", await a9.receive(timeout=1) is not None)
    check("Broker: a10收到", await a10.receive(timeout=1) is not None)

    # 无订阅者
    msg7 = type("MockMsg", (), {"name": "p", "content": "nobody", "metadata": {}, "id": "007"})()
    await broker.publish("no-subscribers", msg7)
    check("Broker: 无订阅者不报错", True)

asyncio.run(connector_tests())

# 结果
print(f"\n{'='*50}\n  ✅ 通过: {PASS}  ❌ 失败: {FAIL}  总计: {PASS+FAIL}\n{'='*50}")
sys.exit(0 if FAIL == 0 else 1)