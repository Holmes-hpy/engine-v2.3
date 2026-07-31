"""步骤二 · 端口契约 IDL 可用性验证 v2.0（10要素 + MultiMode + SafeFallback）"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meta_protocol.port_contract import *

PASS = FAIL = 0
def check(desc, cond, detail=""):
    global PASS, FAIL
    if cond: print(f"  ✅ {desc}"); PASS += 1
    else: print(f"  ❌ {desc}  — {detail}"); FAIL += 1

def section(title):
    print(f"\n{'='*50}\n  {title}\n{'='*50}")

# 测试1: 7种预设模板
section("测试1: 7种预设模板")
for name, factory, exp_addr, exp_vis, exp_mem, exp_ctx, exp_life in [
    ("isolated_worker", PortContract.isolated_worker, "unicast", "private", "exclusive", "full", "temporary"),
    ("hub_participant", PortContract.hub_participant, "broadcast", "global", "shared", "none", "permanent"),
    ("pipeline_stage", PortContract.pipeline_stage, "unicast", "private", "inherited", "partial", "permanent"),
    ("fan_out_worker", PortContract.fan_out_worker, "unicast", "private", "exclusive", "full", "temporary"),
    ("agent_scope_default", PortContract.agent_scope_default, "broadcast", "global", "shared", "none", "permanent"),
    ("auditor_observer", PortContract.auditor_observer, "unicast", "group", "shared", "partial", "permanent"),
    ("expert_consultation", PortContract.expert_consultation, "multicast", "group", "exclusive", "partial", "temporary"),
]:
    p = factory()
    check(f"{name}: addressing", p.addressing.value == exp_addr)
    check(f"{name}: visibility", p.visibility.value == exp_vis)
    check(f"{name}: memory_belonging", p.memory_belonging.value == exp_mem)
    check(f"{name}: context_isolation", p.context_isolation.value == exp_ctx)
    check(f"{name}: lifecycle", p.lifecycle.value == exp_life)

# 测试2: 自定义声明
section("测试2: 自定义声明")
p = PortContract(
    addressing=AddressingMode.UNICAST, visibility=VisibilityDomain.PRIVATE,
    memory_belonging=MemoryBelonging.EXCLUSIVE, context_isolation=ContextIsolation.FULL,
    distribution=Distribution.FAN_OUT, lifecycle=Lifecycle.TEMPORARY,
    state_boundary=StateBoundary.STATELESS,
)
check("自定义 addressing", p.addressing == AddressingMode.UNICAST)
check("自定义 visibility", p.visibility == VisibilityDomain.PRIVATE)
check("自定义 lifecycle", p.lifecycle == Lifecycle.TEMPORARY)
check("默认 reliability", p.reliability == Reliability.AT_LEAST_ONCE)

# 测试3: override 方法
section("测试3: override 不可变语义")
orig = PortContract.isolated_worker()
switched = orig.override(
    addressing=AddressingMode.MULTICAST, visibility=VisibilityDomain.GROUP,
    memory_belonging=MemoryBelonging.SHARED, context_isolation=ContextIsolation.NONE,
)
check("切换后 addressing 变了", switched.addressing == AddressingMode.MULTICAST)
check("切换后 visibility 变了", switched.visibility == VisibilityDomain.GROUP)
check("切换后 memory_belonging 变了", switched.memory_belonging == MemoryBelonging.SHARED)
check("原对象 addressing 未变", orig.addressing == AddressingMode.UNICAST)
check("原对象 visibility 未变", orig.visibility == VisibilityDomain.PRIVATE)
check("其他字段继承", switched.distribution == orig.distribution)

# 测试4: 装饰器
section("测试4: port_override 装饰器")
@port_override(addressing=AddressingMode.MULTICAST, visibility=VisibilityDomain.GROUP)
def expert_review(): pass
check("装饰器存储 _port_overrides", hasattr(expert_review, "_port_overrides"))
check("覆盖 addressing 正确", expert_review._port_overrides["addressing"] == AddressingMode.MULTICAST)
check("覆盖 visibility 正确", expert_review._port_overrides["visibility"] == VisibilityDomain.GROUP)

# 测试5: 序列化
section("测试5: 序列化/反序列化")
p = PortContract.fan_out_worker()
d = p.to_dict()
check("to_dict 返回 dict", isinstance(d, dict))
p2 = PortContract.from_dict(d)
check("反序列化 addressing 一致", p2.addressing == p.addressing)
check("反序列化 visibility 一致", p2.visibility == p.visibility)
check("反序列化 memory_belonging 一致", p2.memory_belonging == p.memory_belonging)
check("反序列化 context_isolation 一致", p2.context_isolation == p.context_isolation)

# 测试6: YAML 读写
section("测试6: YAML 读写")
with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False, encoding="utf-8") as f:
    tmp = f.name
p = PortContract.fan_out_worker()
p.to_yaml(tmp)
p2 = PortContract.from_yaml(tmp)
os.unlink(tmp)
check("YAML 往返 addressing", p2.addressing == p.addressing)
check("YAML 往返 visibility", p2.visibility == p.visibility)
check("YAML 往返 lifecycle", p2.lifecycle == p.lifecycle)
check("YAML 往返 capabilities", p2.capabilities.can_create_agent == p.capabilities.can_create_agent)

# 测试7: 调研竞赛场景配置
section("测试7: 调研竞赛场景配置")
p1 = PortContract.fan_out_worker()  # 阶段1: 扇出独立研究员
p2 = p1.override(distribution=Distribution.FAN_IN)  # 阶段2: 收集
p3 = PortContract.hub_participant(
    addressing=AddressingMode.MULTICAST, visibility=VisibilityDomain.GROUP
)  # 阶段3: 专家评审
p4 = p1.override(lifecycle=Lifecycle.CONDITIONAL, capabilities=Capabilities(can_destroy=True))  # 阶段4: 淘汰
check("阶段1: fan_out addressing", p1.addressing == AddressingMode.UNICAST)
check("阶段1: fan_out visibility", p1.visibility == VisibilityDomain.PRIVATE)
check("阶段2: 切换到 fan_in", p2.distribution == Distribution.FAN_IN)
check("阶段3: 切换到 multicast", p3.addressing == AddressingMode.MULTICAST)
check("阶段3: 切换到 group", p3.visibility == VisibilityDomain.GROUP)
check("阶段3: 切换到 shared", p3.memory_belonging == MemoryBelonging.SHARED)
check("阶段4: 条件销毁", p4.lifecycle == Lifecycle.CONDITIONAL)
check("阶段4: 可销毁", p4.capabilities.can_destroy == True)

# 测试8: SafeFallbackContract
section("测试8: SafeFallbackContract")
p = PortContract.safe_fallback()
check("safe_fallback addressing", p.addressing == AddressingMode.UNICAST)
check("safe_fallback visibility", p.visibility == VisibilityDomain.PRIVATE)
check("safe_fallback memory", p.memory_belonging == MemoryBelonging.EXCLUSIVE)
check("safe_fallback context", p.context_isolation == ContextIsolation.FULL)
check("safe_fallback 不能创建Agent", p.capabilities.can_create_agent == False)
check("safe_fallback recursion_depth=0", p.capabilities.max_recursion_depth == 0)

# 测试9: MultiModePortContract
section("测试9: MultiModePortContract")
multi = PortContract.multi_mode({
    "default": PortContract.hub_participant(),
    "isolated": PortContract.isolated_worker(),
    "audit": PortContract.auditor_observer(),
})
check("当前模式=default", multi.current_mode == "default")
check("active 是 hub_participant", multi.active.addressing == AddressingMode.BROADCAST)
check("模式列表有3个", len(multi.modes) == 3)
switched = multi.switch("isolated", "需要独立调研")
check("切换后模式=isolated", multi.current_mode == "isolated")
check("active 是 isolated_worker", multi.active.memory_belonging == MemoryBelonging.EXCLUSIVE)
check("历史记录有1条", len(multi.history) == 1)
check("history 包含原因", "独立调研" in multi.history[0][1])
# 切换回 default
multi.switch("default")
check("历史记录有2条", len(multi.history) == 2)
# 获取不切换
check("get 不切换", multi.get("audit").addressing == AddressingMode.UNICAST)
check("当前模式仍是 default", multi.current_mode == "default")
# 非法模式
try:
    multi.switch("不存在的模式")
    check("非法模式应抛异常", False)
except ValueError:
    check("非法模式正确抛异常", True)

# 测试10: extensions 扩展字段
section("测试10: extensions 扩展字段")
p = PortContract(extensions={"custom_tool": "web_search", "max_context": 4096})
check("extensions 有自定义字段", p.extensions["custom_tool"] == "web_search")
check("extensions max_context", p.extensions["max_context"] == 4096)
d = p.to_dict()
p2 = PortContract.from_dict(d)
check("extensions 往返一致", p2.extensions["custom_tool"] == "web_search")

# 测试11: is_compatible_with
section("测试11: is_compatible_with")
pc_a = PortContract.isolated_worker()   # unicast+private
pc_b = PortContract.auditor_observer()  # unicast+group
pc_c = PortContract.hub_participant()   # broadcast+global
check("unicast-private vs unicast-group → 不兼容", not pc_a.is_compatible_with(pc_b))
check("unicast-private vs unicast-private → 兼容", pc_a.is_compatible_with(pc_a))
check("unicast-private vs broadcast-global → 不兼容", not pc_a.is_compatible_with(pc_c))

# 测试12: 旧版 YAML 兼容迁移
section("测试12: 旧版 YAML 兼容迁移")
data = {"reachability": "unicast+private", "data_isolation": "isolated", "distribution": "fan_out"}
p = PortContract.from_dict(data)
check("旧版 reachability→addressing", p.addressing == AddressingMode.UNICAST)
check("旧版 reachability→visibility", p.visibility == VisibilityDomain.PRIVATE)
check("旧版 data_isolation→memory", p.memory_belonging == MemoryBelonging.EXCLUSIVE)
check("旧版 data_isolation→context", p.context_isolation == ContextIsolation.FULL)

# 结果
print(f"\n{'='*50}\n  ✅ 通过: {PASS}  ❌ 失败: {FAIL}  总计: {PASS+FAIL}\n{'='*50}")
sys.exit(0 if FAIL == 0 else 1)