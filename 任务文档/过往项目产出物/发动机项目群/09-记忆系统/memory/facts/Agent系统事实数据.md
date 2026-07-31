# Agent系统事实数据

> 沉淀时间：2026-07-26
> 来源：0-A-V8.1发动机/memory/ 知识迁移 + 自学.md 补充
> 置信度：高

---

## 关键时间线

| 时间 | 事件 | 意义 |
|------|------|------|
| 2022 | CoT（思维链）提出 | 让LLM"想清楚" |
| 2023.06 | Function Calling发布 | **真正转折点**，让LLM"能行动" |
| 2023.11 | OpenAI Assistants API | 官方Agent雏形 |
| 2024 | Agent框架爆发 | LangGraph/CrewAI/AutoGen/AgentScope等涌现 |
| 2025 | 多Agent协作主流化 | Context Engineering成为焦点 |
| 2026 | 协议年+Harness Engineering | MCP/A2A/AG-UI三大协议，Agent = Model × Harness |

---

## 7大核心框架对比

| 框架 | 出品方 | 类型 | 核心特点 | 信息流模式 |
|------|--------|------|----------|-----------|
| LangGraph | LangChain | 开源 | 有向图抽象，State管理 | 图驱动，可模拟任意拓扑 |
| OpenAI Agents SDK | OpenAI | 开源 | OpenAI官方，Function Calling原生 | 隔离式SubAgent |
| Google ADK | Google | 开源 | Google官方，A2A协议 | 支持A2A互操作 |
| AutoGen/MAF | 微软 | 开源 | 对话驱动多Agent | GroupChat对话式 |
| CrewAI | 开源社区 | 开源 | 角色驱动，Crew+Process | 层级+流程 |
| Dify | 开源/商业 | 低代码 | 可视化编排 | 可视化工作流 |
| AgentScope | 阿里通义实验室 | 开源 | MsgHub哲学，6大抽象 | MsgHub广播原生 |
| Anthropic MCP | Anthropic | 协议 | 工具交互标准 | 协议层，非框架 |

---

## AgentScope 6大核心抽象

1. **Message（消息）**：血液/载体，一切信息传递的基本单位
2. **Agent（智能体）**：具备observe/reply/print三个核心能力
3. **Model（模型）**：统一接口层，支持多模型切换
4. **Memory（记忆）**：4种后端 + Mark标签 + 压缩机制
5. **Tool（工具）**：任何可调用对象都是工具
6. **Pipeline（编排）**：MsgHub + Sequential + Fanout

---

## AgentScope 6大差异化特性
- MCP + A2A双协议原生支持
- 内置RL（Trinity-RFT）强化学习
- 实时语音Agent支持
- 分布式部署原生支持
- 内置多种Pipeline模式
- 丰富的Agent模板库

---

## 2026协议年三大协议
- **MCP**（Anthropic）：工具交互协议（Model Context Protocol）
- **A2A**（Google）：Agent间通信协议（Agent-to-Agent）
- **AG-UI**：用户交互协议

---

## Harness Engineering四大组件
OpenAI提出的2026新范式，公式：Agent = Model × Harness
1. **Context Management**：AGENTS.md等上下文管理
2. **Architecture Constraints**：Linter/CI架构约束
3. **Feedback Loops**：强制验证反馈环
4. **Entropy Management**：技术债务预防

---

## 递归6大挑战
1. 上下文爆炸（Context Explosion）
2. 成本爆炸（Cost Explosion）
3. 通信噪音（Communication Noise）
4. 协调损耗（Coordination Loss）
5. 递归陷阱（Recursive Trap）
6. 质量退化（Quality Degradation）

---

## 记忆三层结构
1. **短期记忆（工作记忆）**：当前对话历史，在LLM上下文窗口内
2. **长期记忆（经验记忆）**：向量数据库，存储历史经验，语义检索召回
3. **实体记忆（知识记忆）**：结构化存储的实体关系知识

---

## 可研报告案例Token数据（参考）
| Step | Agent | Token数 | 说明 |
|------|-------|---------|------|
| 0 | Leader初始加载 | ~7.5K | System+SKILL+Tools+用户输入 |
| 3 | Parser-A开始 | ~4K | 全新Session，上下文隔离 |
| 5 | Leader检查信息表 | ~15.5K | Leader开始感到窗口压力 |
| 8 | Writer-9写结论 | ~33.1K | 读前8章，全方案最大单次消耗 |
| 9 | Integrator整合 | ~37.3K | 全流程峰值，占128K窗口29.1% |

---

## RAG技术演进（来自自学.md）

| 阶段 | 技术 | 核心能力 | 局限性 |
|------|------|----------|--------|
| 第一代 RAG | 向量检索 | 语义相似度匹配 | 无法分析关系，只能匹配语义相近内容 |
| 第二代 RAG | 向量 + 知识图谱 | 支持实体关系查询 | 人工维护成本高 |
| Agentic RAG | Agent自主决策 | Agent自己判断找什么、怎么找 | 技术复杂度高 |

---

## 侯鹏远关键洞察（来自自学.md）

### 洞察1：Agent/Memory是"剥离"而非"诞生"
Agent和Memory不是凭空出现的新概念，而是把原来一体化Prompt+上下文的功能做了拆分——Memory存上下文，Agent = 固化的工作流程 + 思维链加强。

### 洞察2：工程化本质是抑制幻觉
大模型幻觉一部分来自智力限制，一部分来自上下文太小记不住。所有工程化手段（工作流、SKILL、MCP、约束）本质上是在用各种方式约束大模型输出。

### 洞察3：大模型应用演进 = 上下文窗口放大
Chat → Copilot → LangChain → Agent → 低代码平台，每一步演进都是上下文窗口变大的结果。

### 洞察4：Transformer自注意力机制是涌现的根源
Transformer架构核心是自注意力机制，无论后续怎么改造（取消解码器、增加隐层），自注意力机制至今未被颠覆。

### 洞察5：模型蒸馏的"孔乙己"视角
蒸馏本质上是把别人家模型当老师给自己孩子讲东西，从社会学角度看与盗窃无异，但从"读书人的事"角度看——这是行业默认操作。