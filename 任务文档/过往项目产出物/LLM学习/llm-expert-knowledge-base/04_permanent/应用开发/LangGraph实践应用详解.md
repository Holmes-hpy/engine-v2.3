
# LangGraph实践应用详解

## 概述

LangGraph是LangChain团队推出的底层工作流引擎，专门用于构建有状态、循环式的AI Agent工作流。它将Agent的执行过程建模为有向图（DAG），每个节点是一个处理步骤，边是条件跳转逻辑。

**核心定位**：2026年构建生产级AI Agent的首选框架，从原型迈向生产的关键工具。

---

## 为什么选择LangGraph

### 传统Agent循环的问题

很多团队初期用"while循环 + 工具调用"实现Agent，够用但难以维护：

| 问题 | 说明 |
|------|------|
| 状态混乱 | 隐式状态传递，调试困难 |
| 无法中断 | 不支持暂停/恢复 |
| 难以并行 | 手动管理并发复杂 |
| 不可观测 | 执行路径不透明 |
| 扩展性差 | 复杂流程越写越乱 |

### LangGraph的六大核心优势

1. **状态机语义**：工作流的每个状态都是显式定义的，便于调试和测试
2. **条件分支**：可以根据LLM输出或外部条件动态决定下一步
3. **并行执行**：支持多个节点同时执行，然后聚合结果
4. **持久化**：内置checkpointing，工作流可以暂停、恢复，支持Human-in-the-Loop
5. **可视化**：图结构可以直接渲染为流程图，方便团队协作
6. **生产就绪**：LangGraph Platform提供从开发到部署的一站式支持

---

## 三大核心概念

### 1. State（状态）：工作流的共享数据

#### 什么是State

State是Agent在整个执行过程中共享和更新的数据。它通常是一个字典或自定义的TypedDict，包含了Agent当前所需的所有信息。

#### 状态定义示例

```python
from typing import TypedDict, Annotated, List
from operator import add
from langgraph.graph import StateGraph

class WorkflowState(TypedDict):
    """工作流的共享状态定义"""
    # 用户输入
    user_query: str
    
    # 中间结果（使用add操作符：新值追加而非覆盖）
    search_results: Annotated[list[str], add]
    
    # 最终输出
    final_answer: str
    
    # 控制流
    iteration_count: int
    should_continue: bool
    
    # 工具调用历史
    tool_calls: Annotated[list[dict], add]
    
    # 错误信息
    errors: Annotated[list[str], add]
```

#### 状态更新的三种模式

| 模式 | 语法 | 适用场景 | 说明 |
|------|------|---------|------|
| 追加模式 | `Annotated[list[str], add]` | 引用来源、日志记录 | 多个Agent都可以append，不会覆盖 |
| 覆盖模式 | 普通字段（如`draft: str`） | 当前版本类数据 | 后写入的覆盖先写入的 |
| 合并模式 | `Annotated[dict, or_]` | 信息收集场景 | 字典自动合并，新旧值都保留 |

**关键直觉**：State就像团队的"公共白板"，所有Agent都在上面读写信息。

---

### 2. Node（节点）：处理步骤

#### 什么是Node

每个节点是一个接受State、返回State更新的函数。节点是工作流的基本处理单元。

#### 节点定义示例

```python
import anthropic
from langgraph.graph import StateGraph

client = anthropic.Anthropic()

def analyze_query_node(state: WorkflowState) -> dict:
    """分析用户查询，确定搜索策略"""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""分析这个查询，输出JSON：
查询：{state['user_query']}
输出格式：{{
  "query_type": "factual|analytical|creative",
  "search_keywords": ["关键词1", "关键词2"],
  "complexity": "simple|medium|complex",
  "requires_calculation": true|false
}}"""
        }]
    )
    
    import json
    try:
        analysis = json.loads(response.content[0].text)
    except:
        analysis = {
            "query_type": "factual",
            "search_keywords": [state['user_query']],
            "complexity": "simple"
        }
    
    return {
        "search_keywords": analysis.get("search_keywords", []),
        "query_analysis": analysis
    }

def synthesis_node(state: WorkflowState) -> dict:
    """综合搜索结果生成最终回答"""
    context = "\n\n".join(state.get("search_results", [])[:5])
    
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""基于以下搜索结果，回答用户问题。
问题：{state['user_query']}
搜索结果：{context}
请给出准确、全面的回答。"""
        }]
    )
    
    return {
        "final_answer": response.content[0].text,
        "should_continue": False
    }
```

#### 节点的返回值

节点返回的是**部分State更新**，不是完整的State。框架会自动将返回值合并到当前State中。

---

### 3. Edge（边）：连接关系

#### 三种边类型

| 类型 | 用途 | 语法 |
|------|------|------|
| 顺序边 | 固定的下一步 | `add_edge("A", "B")` |
| 条件边 | 动态决定下一步 | `add_conditional_edges(source, router, mapping)` |
| 入口边 | 起始节点 | `set_entry_point("start")` |

#### 顺序边示例

```python
from langgraph.graph import StateGraph, END

def build_simple_workflow():
    """简单的线性工作流"""
    workflow = StateGraph(WorkflowState)
    
    # 添加节点
    workflow.add_node("analyze", analyze_query_node)
    workflow.add_node("search", web_search_node)
    workflow.add_node("synthesize", synthesis_node)
    
    # 设置起始节点
    workflow.set_entry_point("analyze")
    
    # 顺序边
    workflow.add_edge("analyze", "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", END)  # END是特殊的结束节点
    
    return workflow.compile()
```

#### 条件边示例

条件边是LangGraph最强大的特性之一，允许基于状态动态决定执行流。

```python
def build_research_workflow():
    """带质量检查和重试的研究型工作流"""
    workflow = StateGraph(WorkflowState)
    
    # 添加节点
    workflow.add_node("analyze", analyze_query_node)
    workflow.add_node("search", web_search_node)
    workflow.add_node("synthesize", synthesis_node)
    workflow.add_node("quality_check", quality_check_node)
    
    # 设置起始节点
    workflow.set_entry_point("analyze")
    
    # 顺序边
    workflow.add_edge("analyze", "search")
    workflow.add_edge("search", "synthesize")
    workflow.add_edge("synthesize", "quality_check")
    
    # 条件边：质量检查后决定是否重试
    def should_retry(state: WorkflowState) -> str:
        if state.get("quality_passed", True):
            return "done"
        elif state.get("iteration_count", 0) >= 2:
            return "done"  # 最多重试2次
        else:
            return "retry"
    
    workflow.add_conditional_edges(
        "quality_check",
        should_retry,
        {
            "done": END,
            "retry": "search"  # 重新搜索
        }
    )
    
    return workflow.compile()
```

**关键直觉**：条件边就像程序中的if-else，但判断逻辑可以是LLM的决策。

---

## 完整的工作流搭建流程

### 第一步：定义State

先想清楚工作流需要共享哪些数据。

### 第二步：创建节点

把每个处理步骤封装成函数。

### 第三步：编排图

用边把节点连起来，确定执行顺序和条件分支。

### 第四步：编译运行

调用`.compile()`得到可执行的app，然后用`.invoke()`执行。

### 完整示例

```python
# 使用工作流
app = build_research_workflow()

result = app.invoke({
    "user_query": "2026年AI Agent的最新技术进展",
    "search_results": [],
    "tool_calls": [],
    "errors": [],
    "iteration_count": 0,
    "should_continue": True
})

print(result["final_answer"])
```

---

## 高级特性

### 1. 并行节点：提升多任务效率

当多个步骤互不依赖时，可以并行执行提高效率。

```python
def build_parallel_research_workflow():
    """并行搜索多个来源，提高效率"""
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("decompose", decompose_query_node)
    # 三个并行搜索节点
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("db_search", database_search_node)
    workflow.add_node("docs_search", docs_search_node)
    workflow.add_node("merge_results", merge_results_node)
    workflow.add_node("synthesize", synthesis_node)
    
    workflow.set_entry_point("decompose")
    
    # 分解后并行执行三个搜索
    # LangGraph自动并行处理同一源节点的多条边
    workflow.add_edge("decompose", "web_search")
    workflow.add_edge("decompose", "db_search")
    workflow.add_edge("decompose", "docs_search")
    
    # 三个节点都完成后才到merge_results
    workflow.add_edge("web_search", "merge_results")
    workflow.add_edge("db_search", "merge_results")
    workflow.add_edge("docs_search", "merge_results")
    
    workflow.add_edge("merge_results", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()
```

**执行流程**：
```
        → web_search  →
decompose → db_search   → merge → synthesize → END
        → docs_search  →
```

---

### 2. Human-in-the-Loop：工作流暂停与恢复

LangGraph内置了检查点机制，支持在关键步骤暂停等待人工确认。

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END

# 使用SQLite持久化检查点
memory = SqliteSaver.from_conn_string("checkpoints.db")

def build_approval_workflow():
    """需要人工审批的工作流"""
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("draft_response", draft_response_node)
    workflow.add_node("human_review", human_review_node)  # 等待人工
    workflow.add_node("finalize", finalize_node)
    
    workflow.set_entry_point("draft_response")
    workflow.add_edge("draft_response", "human_review")
    
    # human_review节点会在此处暂停，等待人工输入
    workflow.add_conditional_edges(
        "human_review",
        lambda state: "approve" if state.get("approved") else "revise",
        {
            "approve": "finalize",
            "revise": "draft_response"
        }
    )
    
    workflow.add_edge("finalize", END)
    
    # 编译时注入检查点
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]  # 在此节点前暂停
    )

# 第一次运行：会在human_review前暂停
app = build_approval_workflow()
thread_config = {"configurable": {"thread_id": "task_001"}}

result = app.invoke(
    {"user_query": "起草给客户的季度报告"},
    config=thread_config
)
print("草稿已生成，等待审批：", result.get("draft"))

# 人工审查后，继续运行（注入审批状态）
app.update_state(
    thread_config,
    {"approved": True, "human_feedback": "很好，可以发送"}
)

final_result = app.invoke(None, config=thread_config)
print("最终结果：", final_result.get("final_answer"))
```

**应用场景**：
- 高风险操作需要人工确认
- 审批流程
- 数据标注
- 人工审核生成内容

---

### 3. 流式输出与实时进度

```python
async def run_with_streaming(user_query: str):
    """流式执行工作流，实时显示进度"""
    app = build_research_workflow()
    
    async for event in app.astream_events(
        {
            "user_query": user_query,
            "search_results": [],
            "tool_calls": [],
            "errors": [],
            "iteration_count": 0
        },
        version="v1"
    ):
        kind = event["event"]
        
        if kind == "on_chain_start":
            node_name = event["name"]
            if node_name in ["analyze", "search", "synthesize", "quality_check"]:
                print(f"🔄 执行节点: {node_name}")
                
        elif kind == "on_chain_end":
            node_name = event["name"]
            if node_name == "synthesize":
                output = event["data"].get("output", {})
                if "final_answer" in output:
                    print(f"✅ 生成回答完成")
                    
        elif kind == "on_llm_stream":
            # 实时输出LLM生成的文字
            chunk = event["data"].get("chunk", "")
            if hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
```

---

## 多Agent协作模式

### 模式一：Supervisor（主管调度）

这是LangGraph最推荐的模式，适合90%的生产场景。

#### 架构

```
用户 → 主管 → Researcher → 返回结果 
     → 主管 → Writer → 返回结果 
     → 主管 → Editor → 返回结果 
     → 主管 → Publisher → 返回结果 
     → 主管 → 最终答案
```

#### 特点

- 星型拓扑：中间一个主管Agent，周围一圈专业Agent
- 主管负责：接收任务、拆分子任务、分配、收集结果、决定下一步
- 主管不干活，只调度

#### 优势与劣势

| 优势 | 劣势 |
|------|------|
| 可控性强，所有路由决策集中在一个点 | 主管可能成为瓶颈 |
| 调试简单，只需要看主管的日志 | 频繁切换Agent时，主管LLM调用次数多 |

#### 完整实现示例

```python
from typing import TypedDict, Annotated, List
from operator import add
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# ===== 第一步：定义共享状态 =====
class ContentTeamState(MessagesState):
    """内容创作团队的共享状态"""
    topic: str                    # 文章主题
    research_notes: str           # 调研笔记
    draft: str                    # 初稿
    edit_feedback: str            # 编辑意见
    final_article: str            # 终稿
    citations: Annotated[List[str], add]  # 引用来源
    status: str                   # 当前状态

# ===== 第二步：创建专业Agent =====
llm = ChatOpenAI(model="gpt-4o", temperature=0)

@tool
def web_search(query: str) -> str:
    """搜索互联网获取最新信息"""
    return f"搜索结果：关于'{query}'的最新资料……"

researcher = create_react_agent(
    model=llm,
    tools=[web_search],
    name="researcher",
    prompt=(
        "你是一位资深调研员。你的职责是搜集与主题相关的权威资料，"
        "整理关键信息，并列出所有引用来源。"
        "不要写文章，只输出结构化的调研笔记。"
    ),
)

writer = create_react_agent(
    model=llm,
    tools=[],
    name="writer",
    prompt=(
        "你是一位资深科技撰稿人。根据提供的调研笔记撰写初稿。"
        "要求：逻辑清晰、段落过渡自然、语言通俗易懂。"
    ),
)

# ===== 第三步：创建主管Agent =====
from langgraph_supervisor import create_supervisor

supervisor = create_supervisor(
    agents=[researcher, writer, editor, publisher],
    model=llm,
    prompt=(
        "你是一位内容创作团队的主管。你的职责是："
        "1. 接收用户的创作需求，拆解成子任务"
        "2. 每次只分配一个子任务给一个专业Agent"
        "3. 收集Agent的返回结果，决定下一步行动"
        "分配规则："
        "- 需要搜集资料 → researcher"
        "- 需要撰写文章 → writer"
        "禁止：不要自己做专业工作。"
    ),
    output_mode="last_message",  # 生产级优化：控制上下文窗口
).compile(name="content_team")

# ===== 第四步：运行 =====
from langchain_core.messages import HumanMessage

result = supervisor.invoke({
    "messages": [
        HumanMessage(content="写一篇关于'AI智能体在企业办公中的应用'的公众号文章")
    ]
}, config={"recursion_limit": 25})

print(result["messages"][-1].content)
```

---

### 模式二：Swarm（去中心化协商）

没有主管，Agent之间直接移交控制权。

#### 架构

```
用户 → Researcher → "这个话题需要写作专家" 
     → handoff → Writer → "写完了，需要编辑审核" 
     → handoff → Editor → "审核通过，可以排版" 
     → handoff → Publisher → 最终答案
```

#### Handoff实现

```python
from langchain_core.tools import tool
from langgraph.types import Command

# 创建handoff工具工厂
def make_handoff_tool(target_agent: str, description: str):
    @tool(f"transfer_to_{target_agent}")
    def handoff(reason: str) -> Command:
        """移交任务给另一个Agent"""
        return Command(
            goto=target_agent,
            update={"current_agent": target_agent},
            graph=Command.PARENT,
        )
    handoff.__doc__ = description
    return handoff

# 为每个Agent创建handoff工具
transfer_to_writer = make_handoff_tool(
    "writer",
    "当调研完成，需要撰写文章时，移交给撰稿人。"
)

# 给Researcher配handoff工具
researcher_with_handoff = create_react_agent(
    model=llm,
    tools=[web_search, transfer_to_writer],
    name="researcher",
    prompt="你是一位调研员。调研完成后，调用transfer_to_writer移交任务。",
)
```

#### 优势与劣势

| 优势 | 劣势 |
|------|------|
| 灵活性高，协作更自然 | 调试困难，决策不透明 |
| 无主管开销，成本低 | 可靠性稍低，依赖模型判断 |
| Agent直接移交，延迟低 | 可能出现"踢皮球"死循环 |

---

### 两种模式对比

| 维度 | Supervisor（主管调度） | Swarm（去中心化协商） |
|------|----------------------|---------------------|
| 控制权 | 集中，主管决定一切 | 分散，Agent自主协商 |
| 调试难度 | 低，看主管日志即可 | 高，需追踪每个Agent的决策 |
| 适用场景 | 任务类型明确、流程可控 | 任务模糊、需要频繁协作 |
| 延迟 | 较高（每次切换都经主管） | 较低（Agent直接移交） |
| 成本 | 较高（主管额外LLM调用） | 较低（无主管开销） |
| 可靠性 | 高（规则硬编码） | 中（依赖模型判断） |

**生产经验建议**：先用Supervisor跑通流程，积累足够数据和日志后，再逐步把高频协作路径改成Swarm的handoff。

---

## 生产级优化技巧

### 1. 递归限制防死循环

```python
result = supervisor.invoke(
    {"messages": [HumanMessage(content="...")]},
    config={"recursion_limit": 25}  # 最多25轮，超限强制终止
)
```

多Agent系统最容易出现的bug是"踢皮球"：AgentA说"给AgentB"，AgentB说"给AgentA"，无限循环。`recursion_limit`是保险丝。

### 2. 分层模型策略降低成本

```python
supervisor_llm = ChatOpenAI(model="gpt-4o", temperature=0)  # 主管用大脑
worker_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # 工人用眼睛
```

主管需要推理能力，用强模型。专业Agent只需要执行能力，用小模型。这种分层策略可以降低成本60-70%，且不影响调度可靠性。

### 3. 生产环境检查点

```python
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg2

# 生产环境使用PostgreSQL持久化检查点
conn = psycopg2.connect(os.environ["DATABASE_URL"])
checkpointer = PostgresSaver(conn)
checkpointer.setup()

production_app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_approval"],
)
```

### 4. 监控与调试（LangSmith集成）

```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_key"
os.environ["LANGCHAIN_PROJECT"] = "production-agent"
```

之后所有工作流执行都会自动发送到LangSmith，可以看到：
- 完整的执行路径（哪些节点被执行了）
- 每个节点的输入/输出
- Token消耗和延迟
- 失败节点和错误信息

### 5. 评估Pipeline

多Agent系统比单Agent更容易出错，需要更完善的评估：

| 评估指标 | 说明 |
|---------|------|
| 路由准确率 | 主管每次分配是否正确 |
| 工具调用效率 | 完成任务用了多少次工具调用 |
| 端到端成功率 | 最终输出是否满足用户需求 |

---

## LangGraph Platform部署

### 配置文件（langgraph.json）

```json
{
  "dependencies": ["./my_agent"],
  "graphs": {
    "research_agent": "./my_agent/workflow.py:app",
    "code_agent": "./my_agent/code_workflow.py:app"
  },
  "env": {
    "ANTHROPIC_API_KEY": "env:ANTHROPIC_API_KEY"
  }
}
```

### 部署命令

```bash
# 本地开发服务器
langgraph dev

# 构建Docker镜像
langgraph build -t my-agent:latest

# 部署到云（LangSmith托管）
langgraph up
```

---

## StateGraph vs DAG：如何选择

| 维度 | StateGraph | DAG |
|------|-----------|-----|
| 模式 | 状态机模式 | 依赖图模式 |
| 循环支持 | 支持（条件边） | 不支持（有向无环） |
| 并行支持 | 支持 | 支持 |
| 适用场景 | 复杂交互、需要循环 | 数据处理、依赖明确 |
| 灵活性 | 高 | 中 |

- 需要循环 → StateGraph
- 需要并行 → DAG
- 分支复杂 → StateGraph
- 依赖明确 → DAG

---

## 最佳实践总结

### 设计原则

1. **状态先行**：先设计好State，再考虑节点和边
2. **职责单一**：每个节点只做一件事
3. **显式优于隐式**：所有状态都要明确定义在State里
4. **渐进式复杂度**：先做线性流程，再加条件边，最后加并行

### 常见坑

1. **状态字段过多**：State不是万能垃圾桶，只放真正需要共享的数据
2. **节点粒度过细**：不要每个操作都做一个节点，适当聚合
3. **条件边过多**：图太复杂难以调试，优先用线性流程
4. **忘记递归限制**：多Agent系统一定要设recursion_limit

---

## 总结

LangGraph是构建生产级AI工作流的工程利器：

1. **StateGraph**：显式的状态管理，避免隐式状态传递的混乱
2. **条件边**：基于LLM输出或外部条件的动态路由
3. **并行节点**：自动并行化无依赖的处理步骤
4. **Checkpointing**：工作流暂停/恢复，支持Human-in-the-Loop
5. **流式执行**：实时输出中间结果，提升用户体验
6. **Platform部署**：从本地开发到生产的一站式支持

相比简单的Agent循环，LangGraph提供了工业级的可靠性、可调试性和可扩展性——这正是从原型迈向生产的关键差距。

**核心认知转变**：未来的AI系统不是"一个超级聪明的个体"，而是"一个协作高效的团队"。多Agent系统的价值不在于每个Agent有多强，而在于它们之间的协作有多顺畅。

---

## 相关知识

- [Agents技术](../模型架构/Agents技术.md)
- [Agentic RAG技术详解](../模型架构/Agentic%20RAG技术详解.md)
- [提示工程](../模型架构/提示工程.md)

