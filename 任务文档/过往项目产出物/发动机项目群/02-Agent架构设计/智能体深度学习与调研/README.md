# 智能体深度学习与调研 — 对话全记录

> 记录时间：2026-07-17 至 2026-07-19
> 学习路径：非开发者视角，理解框架/结构/机制/原理/特性
> 核心目标：建立Agent系统的结构化知识体系

---

## 目录结构

```
智能体深度学习与调研/
├── README.md                              ← 本文件（索引）
├── conversations/                         ← 每轮对话一个md文件
│   ├── 第01轮_初始需求_深度调研Agent系统与知识体系.md
│   ├── 第02轮_AgentScope深度解析与学习路径.md
│   ├── 第03轮_认知校准_ChatBot到Agent的进化真相.md
│   ├── 第04轮_五大模块深度协作原理.md
│   ├── 第05轮_递归多Agent架构的想法与挑战.md
│   ├── 第06轮_四种工业级多Agent策略深度解析.md
│   ├── 第07轮_AgentScope_Fanout_vs_Claude子Agent本质区别.md
│   ├── 第08轮_混合架构构想_MsgHub加Claude双层模式.md
│   ├── 第09轮_架构组合模式分类与AgentScope改造方案.md
│   ├── 第10轮_AgentScope2.0实战_子Agent创建子Agent.md
│   ├── 第11轮_元框架问题_架构组合的本质困难.md
│   ├── 第12轮_上下文窗口深度解析_可研报告案例.md
│   ├── 第13轮_上下文窗口演化可视化_第一版.md
│   └── 第14轮_可视化修复与排版重构_第二版.md
└── visuals/                               ← 可视化文件
    └── 上下文窗口演化演示.html            ← 交互式HTML（浏览器打开）
```

---

## 对话轮次索引

| 轮次 | 主题 | 核心知识点 |
|------|------|-----------|
| 01 | 初始需求 | Agent系统全景调研、7大核心框架、5大模块架构、Harness Engineering、渐进式知识结构图 |
| 02 | AgentScope深度 | 6大核心抽象、MsgHub哲学、5阶段非开发者学习路径 |
| 03 | 认知校准 | 纠正4个误区、Function Calling是真正转折点（2023.06）、AI工程三代演化 |
| 04 | 5大模块协作 | 闭环控制系统、真实场景ReAct循环演示、Memory三层结构、向量搜索必要性 |
| 05 | 递归Agent军团 | 6大现实挑战（上下文/成本爆炸、通信噪音、协调损耗、递归陷阱、质量退化） |
| 06 | 4种工业策略 | 预设层级/有限扇出/上下文压缩/动态子Agent，策略组合使用 |
| 07 | Fan-out vs Claude | 本质区别是信息流：微信群vs独立房间，6维对比 |
| 08 | 混合架构构想 | MsgHub(L1)+Isolated(L2)=公司组织架构，3优势4挑战，最多两层 |
| 09 | 组合与改造 | 4种原子模式组合、方案A模拟vs方案B五层改造、递归防护双层防线 |
| 10 | AS2.0实战 | permission_context+SubAgentTemplate、create_app嵌套、三种角色模板 |
| 11 | **元框架** | 架构组合本质困难、4个冲突维度、元框架是前沿研究问题（待深入研究）|
| 12 | 上下文窗口 | messages数组构成、可研报告10步Token演化、4条上下文管理法则 |
| 13-14 | 可视化 | 交互式HTML演示，Token累计消耗追踪，Session切换现象 |

---

## 核心知识体系骨架

### 一、基础公式
```
Agent = LLM + Tools + Memory + Autonomy（自主性）
Agent = Model × Harness（2026新范式）
```

### 二、5大核心模块
```
感知(Perception) → 大脑/推理(Reasoning) → 规划(Planning) → 记忆(Memory) → 工具/行动(Tools)
```
Agent本质是**闭环控制系统**，核心循环是ReAct：Thought→Action→Observation→...

### 三、关键时间线
```
2022     CoT（思维链）— 让LLM"想清楚"
2023.06  Function Calling — 真正转折点！让LLM"能行动"
2023.11  OpenAI Assistants API
2024     Agent框架爆发（LangGraph/CrewAI/AutoGen/AgentScope）
2025     多Agent协作主流化、Context Engineering
2026     协议年（MCP/A2A/AG-UI）、Harness Engineering
```

### 四、多Agent拓扑与模式
| 模式 | 信息流 | 类比 | 代表 |
|------|--------|------|------|
| MsgHub广播 | all-to-all | 微信群 | AgentScope |
| Isolated隔离 | tree (parent-child) | 独立办公室 | Claude Code |
| Sequential流水线 | linear A→B→C | 工厂流水线 | 各框架Pipeline |
| Fan-out扇入扇出 | map-reduce | 项目经理分发任务 | LangGraph/AgentScope |

### 五、4种工业策略
1. **预设层级**：固定角色，可预测不灵活
2. **有限扇出**：动态创建但不递归，天然并行
3. **上下文压缩**：3级压缩（摘要/结构化/标签化）
4. **动态子Agent**：允许递归但有3层硬限制（深度/数量/步骤）

### 六、上下文窗口管理法则
1. 按需加载SKILL
2. 信息压缩传递（原始→精炼）
3. 并行隔离（独立Session）
4. 终态依赖显式化

### 七、AI工程三代演化
```
Prompt Engineering (2023) → Context Engineering (2025) → Harness Engineering (2026)
```

### 八、三大协议（2026协议年）
- **MCP**（Anthropic）：工具交互协议
- **A2A**（Google）：Agent间通信协议
- **AG-UI**：用户交互协议

---

## 待深入研究

- [ ] **元框架（Meta-Framework）问题**：能否构建不绑定任何具体架构模式、允许自由组合嵌套的通用Agent框架？这是多Agent系统架构描述语言（ADL for MAS）的前沿研究方向。待基础内容吃透后深入研究。

---

## 可视化工具使用说明

打开 `visuals/上下文窗口演化演示.html`（浏览器直接打开）：

- **中间区域**（核心）：当前Agent窗口占用堆叠条、全局累计统计（本步新增/累计总消耗/API调用/预计成本）、每步Token消耗柱状图、本步关键变化
- **左栏**：执行流程导航
- **右栏**：消息内容详情（默认折叠，点击展开）
- **操作**：点击"下一步/上一步"或键盘←→方向键切换Step，点击柱状图或流程节点可直接跳转
- **重点观察**：Step 3切换Parser-A时"当前窗口重置但全局累计不重置"的现象
