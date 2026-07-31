# 第1轮：初始需求 — 深度调研Agent系统与知识体系构建

## 用户提问

我需要相关领域专家帮我完成以下内容：

1. 深度调研现有的智能体系统；发现几家后跟我确认范围。
2. 为我讲解通用智能体系统基本架构；
3. 为我讲解各家智能体系统的特点、区别；
4. 为我讲解单智能体工作、多智能体工作、智能体编排的详细原理以及各家特色；
5. Harness engineering 是什么？怎么用？

如果可以我希望能够有一个html的基础结构图，然后每多一个新的知识点，结构图中对应部分就会发生变化，然后不断扩充。这样能帮我快速建立学习的知识体系，能够让我很好的结构化，这样我学的快。

## 专家回答

### 调研执行

启动了3个并行Explore子代理进行深度调研：
- **市场调研**：覆盖20+ Agent系统的分类（开源、商业、新兴）
- **架构调研**：通用Agent架构、各框架差异
- **Harness Engineering调研**：2026年新范式

### 核心框架确认（7大核心框架）

| 框架 | 类型 | 核心特点 |
|------|------|----------|
| LangGraph | 开源 | 有向图抽象，State管理 |
| OpenAI Agents SDK | 开源 | OpenAI官方，Function Calling原生 |
| Google ADK | 开源 | Google官方，A2A协议 |
| AutoGen/MAF | 开源 | 微软，对话驱动多Agent |
| CrewAI | 开源 | 角色驱动，Crew+Process |
| Dify | 开源/商业 | 低代码，可视化编排 |
| Anthropic MCP | 协议 | 工具交互标准 |

### 5大核心模块架构

```
感知 → 大脑/推理 → 规划 → 记忆 → 工具/行动
```

- **感知(Perception)**：接收用户输入、环境反馈、其他Agent消息
- **大脑(Brain/Reasoning)**：LLM推理核心，ReAct/Plan-and-Execute/Reflexion
- **规划(Planning)**：任务分解、步骤规划、动态调整
- **记忆(Memory)**：短期记忆(对话历史)、长期记忆(向量数据库)、工作记忆
- **工具(Tools/Action)**：函数调用、API调用、文件操作、MCP工具

### 单Agent模式

- **ReAct**：Thought→Action→Observation循环，最基础模式
- **Plan-and-Execute**：先规划再执行，适合复杂任务
- **Reflexion**：生成→反思→修正，自我改进
- **生产级混合**：外层Plan-and-Execute + 内层ReAct + 最终Reflection

### 多Agent拓扑

- **层级式(Hierarchical)**：主管+工人，自上而下分配
- **对等式(Peer-to-Peer)**：平等协作，对话驱动
- **网络式(Network)**：动态连接，按需通信

### 2026"协议年"三大协议

- **MCP**（Anthropic）：工具交互协议
- **A2A**（Google）：Agent间通信协议
- **AG-UI**：用户交互协议

### Harness Engineering（2026新范式）

OpenAI提出的新范式，公式：**Agent = Model × Harness**

四大组件：
1. **Context Management**：AGENTS.md等上下文管理
2. **Architecture Constraints**：Linter/CI架构约束
3. **Feedback Loops**：强制验证反馈环
4. **Entropy Management**：技术债务预防

AI工程演化：Prompt Engineering(2023) → Context Engineering(2025) → Harness Engineering(2026)

### 渐进式知识结构图

创建了v1、v2、v3三版渐进式SVG知识结构图，v3确认为知识体系骨架。

## 本轮核心知识点

- Agent系统全景：7大核心框架 + 20+系统分类
- 通用架构：5大模块（感知→大脑→规划→记忆→工具）
- 单Agent：ReAct/Plan-and-Execute/Reflexion三种模式
- 多Agent：层级/对等/网络三种拓扑
- 编排：工作流编排vs动态编排，2026融合趋势
- 三大协议：MCP/A2A/AG-UI
- Harness Engineering：Agent = Model × Harness
