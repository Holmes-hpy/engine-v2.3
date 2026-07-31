# 第9轮：架构组合模式分类 + AgentScope改造方案

## 用户提问

我有2个问题：
1，这种架构组合目前有多少种？分别怎么实现的？主要场景有哪些？
2，以agentscope为例，meshub是他在架构层就支持，那么我要在agentscope中实现Claude的创建子agent模式，或者组合其他模式，是不是需要在代码层对架构进行改造来实现？这块你要分两部分讲明。1，不动用代码如何实现的，2，如果我希望平台底层就要支持这种默认能力，要怎么做？

## 专家回答

### 问题1：架构组合模式分类

多Agent架构模式本质上有4种"原子模式"，它们的组合产生了各种变体：

**4种原子模式**：
1. **MsgHub（广播模式）**：AgentScope原生，微信群式共享
2. **Isolated Rooms（隔离房间）**：Claude Code模式，独立上下文
3. **Sequential Pipeline（串行流水线）**：A→B→C线性传递
4. **Fan-out/Fan-in（扇入扇出）**：主Agent分发→并行执行→汇总

**主要组合方式**：
- 2层MsgHub+Isolated（公司架构）
- Sequential+Isolated（流水线中某步并行处理）
- MsgHub+Fan-out（群聊中某人发起并行任务）
- 3层：MsgHub(L1)→Isolated(L2)→Fan-out(L3)（部门内再分工）

### 问题2-A：不动代码如何实现（方案A：Pipeline嵌套模拟）

在AgentScope 2.0中，不修改框架源码，可以通过以下方式模拟Claude模式：

**核心思路**：
- 第一层用MsgHub让部门经理共享信息
- 每个部门经理内部用SequentialPipeline顺序调用"虚拟子Agent"
- 关键：虚拟子Agent之间不共享MsgHub，信息只通过经理传递

**具体方法**：
1. 部门经理Agent收到任务后，不通过`AgentCreate`创建Worker，而是在自己的ReAct循环中，通过Tool Call调用一个"子任务执行器"
2. 子任务执行器内部维护自己的独立状态（但实际上还是在经理的上下文中，只是通过提示词隔离）
3. 子任务执行器返回摘要结果，经理将摘要广播到MsgHub

**局限性（本质是模拟）**：
- 所有"子Agent"仍然共享经理的上下文窗口（因为都在同一个LLM调用链中）
- 不是真正的独立Session，没有真正的上下文隔离
- 经理的上下文会随着子任务执行不断膨胀
- 子Agent之间无法真正并行（在同一个ReAct循环里是串行的）

### 问题2-B：底层支持需要5层改造（方案B：真正实现）

如果希望AgentScope平台底层原生支持，需要改造5个层面：

**第1层：Agent基类层 — 加Agent工厂**
- 现在所有Agent都是代码里new出来的
- 需要加`AgentFactory`，根据LLM输出自动创建对应类型Agent
- 类比：给经理配HR部门，经理说"招个前端"，HR自动创建

**第2层：Session/状态管理层 — 加独立子会话**
每个动态创建的子Agent必须有三个独立：
- 独立Memory：子Agent不读父Agent记忆
- 独立Toolkit：子Agent只拿到自己需要的工具
- 独立权限控制：子Agent不能操作父Agent的文件系统

**第3层：Pipeline编排层 — 加SpawnPipeline**
封装完整生命周期：创建子Agent→执行→返回结果→清理
类比Docker：`docker run ... && docker rm`，容器跑完自动销毁

**第4层：消息/通信层 — 扩展MsgHub**
原始MsgHub是扁平广播域，需要支持**作用域化**：
- 每个SpawnPipeline内部创建自己的小型MsgHub
- 子Agent间消息不泄露到外层跨部门MsgHub
- 支持跨层消息路由

**第5层：工具层 — 给Agent"招人权"**
把上述能力封装成内置工具：
- `SpawnAgent(name, task, tools, model)` — 招人干活
- `SendMessage(target, content)` — 发消息
- `CollectResult(agent_name)` — 收集结果

**绝对不能省略的防线：递归防护**
Anthropic的血泪教训：不加防护，子Agent会为简单查询创建50个孙Agent，瞬间烧光API额度。
- 静态过滤：子Agent的工具列表里直接不包含SpawnAgent
- 运行时Guard：检查当前嵌套深度>=最大深度则拒绝

### 选型建议

| 需求 | 推荐方案 |
|------|----------|
| 学习理解原理 | AgentScope 1.0 + Pipeline嵌套模拟 |
| 快速实现双层架构 | AgentScope 2.0 Agent Team原生支持 |
| 构建自有平台 | 5层蓝图，重点实现SpawnPipeline+递归防护 |

## 本轮核心知识点

- 4种原子模式：MsgHub/Isolated/Sequential/Fan-out
- 组合方式是原子模式的嵌套和叠加
- 方案A（不动代码）：Pipeline嵌套模拟，本质上仍是共享上下文
- 方案B（底层改造）：5层改造（基类/Session/Pipeline/通信/工具）+递归防护
- 递归防护是生死线：静态过滤+运行时Guard双层保护
