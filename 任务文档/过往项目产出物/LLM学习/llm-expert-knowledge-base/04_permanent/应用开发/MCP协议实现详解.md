
# MCP协议实现详解

## 概述

MCP（Model Context Protocol，模型上下文协议）是由Anthropic在2024年11月推出的开放标准协议，旨在解决AI大模型与外部数据源和工具之间的连接问题，使模型能够安全、灵活地访问文件、API、数据库等资源。

**一句话总结**：MCP将「上下文定义、工具注册、状态持久化、可插拔Agent」抽象成一套HTTP/SSE协议，让大模型与本地或远程"世界"无缝交互。写一次MCP Server，所有支持MCP的客户端都能用。

**定位**：AI时代的"USB-C接口"——统一的工具和数据源连接标准。

---

## 为什么需要MCP

### 工具调用的"巴别塔困境"

在MCP出现之前，让Agent调用外部工具是这样的：

- Agent A接入工具X → 自定义JSON格式
- Agent B接入工具Y → 另一种格式
- Agent C想同时用X和Y → 要写两个适配器
- 换个模型 → 全部重写

**问题**：每个工具都要写定制化集成，没有统一标准，生态碎片化。

### MCP的解决方案

MCP的核心理念很简单——**把工具调用标准化**。每个工具只需要暴露三样东西：

| 要素 | 说明 | 示例 |
|------|------|------|
| 工具名 | 唯一标识 | `get_userlist` |
| 参数定义 | JSON Schema格式 | name、department |
| 执行逻辑 | 实际业务代码 | 调用数据库查询 |

**价值**：写一次MCP Server，所有支持MCP的Host都能用，实现了真正的互操作。

---

## 整体架构

### 三大核心角色

```
┌──────────────────────────────────────────────────────┐
│                   MCP Host                           │
│  （Claude Desktop / Cursor / Zed / 自定义应用）      │
│                                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │            MCP Client（内置）                │     │
│  │  - 管理Server连接                            │     │
│  │  - 发送请求/处理响应                         │     │
│  │  - 维护工具/资源列表                         │     │
│  └──────────────┬──────────────────────────────┘     │
│                 │ JSON-RPC 2.0                       │
│                 │ （stdio / SSE / HTTP）             │
└─────────────────┼────────────────────────────────────┘
                  │
┌─────────────────┼────────────────────────────────────┐
│  MCP Server     │                                    │
│  （开发者实现）  │                                    │
│                 ▼                                    │
│  ┌───────────────────────────┐                      │
│  │  Tools（工具）            │                      │
│  │  - 可被LLM调用的函数       │                      │
│  │  - 名称+描述+参数Schema   │                      │
│  └───────────────────────────┘                      │
│  ┌───────────────────────────┐                      │
│  │  Resources（资源）        │                      │
│  │  - 可被LLM读取的数据       │                      │
│  │  - URI标识 + MIME类型     │                      │
│  └───────────────────────────┘                      │
│  ┌───────────────────────────┐                      │
│  │  Prompts（提示模板）      │                      │
│  │  - 预定义的交互模板        │                      │
│  │  - 可动态填充参数         │                      │
│  └───────────────────────────┘                      │
│                                                      │
│  ←→ REST API / 数据库 / 文件系统 / 浏览器...         │
└──────────────────────────────────────────────────────┘
```

### 角色说明

| 角色 | 说明 | 谁来实现 |
|------|------|---------|
| **MCP Host** | 用户直接交互的AI应用 | Anthropic、Cursor等 |
| **MCP Client** | 运行在Host内部，负责与Server通信 | 内置在Host中 |
| **MCP Server** | 封装具体的工具、数据源或服务 | 开发者实现 |

---

## 通信协议

### 两种传输方式

| 方式 | 说明 | 适用场景 | 安全性 |
|------|------|---------|--------|
| **stdio** | 标准输入输出，Host将Server作为子进程启动 | 本地工具、最常用 | 最高，进程隔离 |
| **SSE** | Server-Sent Events，HTTP长连接 | 远程服务器 | 中，需网络权限 |
| **HTTP** | Streamable HTTP（新标准） | 远程服务 | 中 |

### 消息协议：JSON-RPC 2.0

无论哪种传输方式，MCP都使用JSON-RPC 2.0作为消息协议。

**请求格式**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_web",
    "arguments": {
      "query": "MCP协议",
      "limit": 5
    }
  }
}
```

**响应格式**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "搜索结果..."
      }
    ]
  }
}
```

**错误格式**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

---

## 三大核心原语

### 1. Tools（工具）

#### 什么是Tool

工具是可被模型调用的函数。每个工具有名称、描述和输入参数schema（JSON Schema格式）。模型通过LLM函数调用机制决定何时调用哪个工具，服务器执行后返回结果。

#### Tool定义结构

```
Tool = {
  name: string,           // 工具名（唯一标识）
  description: string,    // 工具描述（告诉LLM这个工具用来干什么）
  inputSchema: {          // 参数定义（JSON Schema）
    type: "object",
    properties: {
      param1: { type: "string", description: "..." },
      param2: { type: "integer", default: 5 }
    },
    required: ["param1"]
  }
}
```

#### 工具调用流程

```
LLM决定调用工具
    ↓
Client发送 tools/call 请求
    ↓
Server执行工具逻辑
    ↓
Server返回结果
    ↓
结果加入上下文
    ↓
LLM继续推理
```

#### 常用工具类型

| 类型 | 示例 | 说明 |
|------|------|------|
| 搜索工具 | search_web | 搜索互联网 |
| 文件操作 | read_file、write_file | 读写本地文件 |
| 数据库 | query_database | 执行SQL查询 |
| HTTP请求 | http_request | 调用外部API |
| 计算工具 | calculate | 数学计算 |
| 代码执行 | run_python | 运行Python代码 |

---

### 2. Resources（资源）

#### 什么是Resource

资源是可被模型读取的数据。类似RESTful中的资源概念，每个资源有URI标识符和MIME类型。服务器暴露资源列表，客户端按需获取。

#### Resource定义结构

```
Resource = {
  uri: string,           // URI标识符（如 file:///config/app.json）
  name: string,          // 资源名称
  description: string,   // 资源描述
  mimeType: string       // MIME类型（如 application/json）
}
```

#### Resource vs Tool的区别

| 维度 | Resource | Tool |
|------|----------|------|
| 方向性 | 只读（模型读取） | 可读写（模型调用执行） |
| 发现方式 | 列表浏览，按需读取 | LLM决策调用 |
| 类比 | 图书馆的书（你翻着看） | 图书馆管理员（你让他帮你找） |
| 适用场景 | 配置文件、数据集、文档 | 搜索、计算、API调用 |

#### 资源订阅（可选）

资源支持订阅更新——当资源内容变化时，服务器可以主动通知客户端。适用于实时数据场景。

---

### 3. Prompts（提示模板）

#### 什么是Prompt

提示是预定义的交互模板。包含可动态填充参数的消息模板，帮助模型理解如何使用特定工具或处理特定场景。

#### Prompt定义结构

```
Prompt = {
  name: string,              // 模板名称
  description: string,       // 模板描述
  arguments: [               // 可填充的参数
    {
      name: "topic",
      description: "文章主题",
      required: true
    }
  ],
  messages: [                // 模板消息
    {
      role: "user",
      content: "请写一篇关于{{topic}}的文章"
    }
  ]
}
```

#### Prompt的价值

- **标准化交互**：让用户和模型以一致的方式使用特定功能
- **降低使用门槛**：用户不需要知道怎么写Prompt，直接选模板
- **最佳实践沉淀**：把好用的Prompt封装成模板，团队共享

---

## MCP Server开发（Python）

### 项目初始化

```bash
# 创建项目
mkdir my-mcp-server
cd my-mcp-server

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装 MCP SDK
pip install mcp
```

**项目结构**：
```
my-mcp-server/
├── src/
│   └── my_server/
│       ├── __init__.py
│       ├── server.py      # 主Server实现
│       ├── tools.py       # 工具定义
│       ├── resources.py   # 资源定义
│       └── prompts.py     # Prompt定义
├── pyproject.toml
└── README.md
```

### 主Server实现

```python
# src/my_server/server.py
"""
MCP Server 主实现
"""
import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

# 导入各个组件
from .tools import list_tools, call_tool
from .resources import list_resources, read_resource
from .prompts import list_prompts, get_prompt

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Server 实例
server = Server("my-mcp-server")

# ======== 注册工具 ========
@server.list_tools()
async def handle_list_tools() -> list:
    """列出所有可用工具"""
    return await list_tools()

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list:
    """处理工具调用"""
    logger.info(f"Tool called: {name} with args: {arguments}")
    return await call_tool(name, arguments)

# ======== 注册资源 ========
@server.list_resources()
async def handle_list_resources() -> list:
    """列出所有可用资源"""
    return await list_resources()

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    logger.info(f"Resource read: {uri}")
    return await read_resource(uri)

# ======== 注册 Prompts ========
@server.list_prompts()
async def handle_list_prompts() -> list:
    """列出所有可用 Prompts"""
    return await list_prompts()

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict) -> list:
    """获取 Prompt 内容"""
    logger.info(f"Prompt requested: {name} with args: {arguments}")
    return await get_prompt(name, arguments)

# ======== 主入口 ========
async def run():
    """运行 Server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

def main():
    """CLI 入口"""
    asyncio.run(run())

if __name__ == "__main__":
    main()
```

### 工具实现

```python
# src/my_server/tools.py
"""
工具定义与实现
"""
import json
import httpx
from typing import Any, List
from mcp.types import Tool, TextContent

# ======== 工具列表 ========
async def list_tools() -> List[Tool]:
    """返回所有可用工具"""
    return [
        # 搜索工具
        Tool(
            name="search_web",
            description="搜索互联网信息。返回相关网页标题、链接和摘要。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        # 文件操作
        Tool(
            name="read_file",
            description="读取本地文件内容。支持文本文件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件路径（绝对路径）"
                    }
                },
                "required": ["path"]
            }
        ),
        # 数据库查询
        Tool(
            name="query_database",
            description="执行 SQL 查询。只支持 SELECT 语句。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL 查询语句（仅 SELECT）"
                    },
                    "database": {
                        "type": "string",
                        "description": "数据库名称",
                        "enum": ["main", "analytics", "logs"]
                    }
                },
                "required": ["sql"]
            }
        ),
        # 计算器
        Tool(
            name="calculate",
            description="执行数学计算表达式。",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如：2+3*4"
                    }
                },
                "required": ["expression"]
            }
        )
    ]

# ======== 工具调用处理 ========
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """执行工具调用"""
    
    if name == "search_web":
        return await _search_web(arguments["query"], arguments.get("limit", 5))
    elif name == "read_file":
        return await _read_file(arguments["path"])
    elif name == "query_database":
        return await _query_database(arguments["sql"], arguments.get("database", "main"))
    elif name == "calculate":
        return await _calculate(arguments["expression"])
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

# ======== 具体工具实现 ========
async def _search_web(query: str, limit: int) -> List[TextContent]:
    """搜索网络"""
    async with httpx.AsyncClient() as client:
        # 实际实现中替换为真实 API
        results = [
            {"title": f"Result {i}", "url": f"https://example.com/{i}", "snippet": f"...{query}..."}
            for i in range(limit)
        ]
    
    return [TextContent(
        type="text",
        text=json.dumps(results, ensure_ascii=False, indent=2)
    )]

async def _read_file(path: str) -> List[TextContent]:
    """读取文件"""
    import os
    
    # 安全检查：防止路径遍历
    if ".." in path:
        return [TextContent(type="text", text="Error: Path traversal not allowed")]
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return [TextContent(type="text", text=content)]
    except FileNotFoundError:
        return [TextContent(type="text", text=f"Error: File not found: {path}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _calculate(expression: str) -> List[TextContent]:
    """安全计算数学表达式"""
    try:
        import ast
        import operator
        
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }
        
        def safe_eval(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                op = allowed_operators.get(type(node.op))
                if op:
                    return op(left, right)
            raise ValueError("Unsupported expression")
        
        tree = ast.parse(expression, mode='eval')
        result = safe_eval(tree.body)
        
        return [TextContent(type="text", text=f"Result: {result}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]
```

### 资源实现

```python
# src/my_server/resources.py
"""
资源定义与实现
"""
import os
from typing import List
from mcp.types import Resource

# ======== 资源列表 ========
async def list_resources() -> List[Resource]:
    """列出所有可用资源"""
    return [
        # 静态资源
        Resource(
            uri="file:///config/app.json",
            name="应用配置",
            description="应用配置文件",
            mimeType="application/json"
        ),
        Resource(
            uri="file:///data/users.csv",
            name="用户数据",
            description="用户信息 CSV",
            mimeType="text/csv"
        ),
    ]

# ======== 资源读取 ========
async def read_resource(uri: str) -> str:
    """读取资源内容"""
    
    if uri.startswith("file:///"):
        path = uri[8:]  # 移除 "file:///"
        return await _read_file_resource(path)
    elif uri.startswith("db://"):
        table = uri[5:]
        return await _read_database_resource(table)
    else:
        raise ValueError(f"Unsupported resource URI: {uri}")

async def _read_file_resource(path: str) -> str:
    """读取文件资源"""
    # 安全检查
    if ".." in path:
        raise ValueError("Path traversal not allowed")
    
    # 实际路径映射
    base_dir = "/data"
    full_path = os.path.join(base_dir, path)
    
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Resource not found: {uri}")
```

---

## 完整通信流程

### 连接生命周期

```
初始化阶段
    ↓
客户端 → initialize 请求（协议版本、能力协商）
服务器 → initialize 响应（支持的能力）
    ↓
客户端 → notifications/initialized 通知
    ↓
操作阶段
    ↓
工具调用 / 资源读取 / Prompt获取
    ↓
关闭阶段
    ↓
优雅断开连接
```

### 一次工具调用的完整过程

```
1. 用户提问
    ↓
2. LLM判断需要调用工具
    ↓
3. Client发送 tools/call 请求
   └─ method: "tools/call"
   └─ params: { name: "search_web", arguments: {...} }
    ↓
4. Server执行工具逻辑
    ↓
5. Server返回结果
   └─ result: { content: [{ type: "text", text: "..." }] }
    ↓
6. Client将结果加入上下文
    ↓
7. LLM基于结果继续推理
    ↓
8. 返回最终答案给用户
```

---

## 安全模型

### 三层安全防护

| 层级 | 防护措施 | 说明 |
|------|---------|------|
| **第一层：用户授权** | 工具调用需用户确认 | 防止LLM擅自调用危险工具 |
| **第二层：沙箱隔离** | stdio传输：进程隔离 | Server运行在独立进程，无网络暴露 |
| **第三层：权限控制** | Host控制哪些工具可用 | Server可定义只读工具等 |

### 常见安全实践

1. **路径遍历防护**：检查文件路径中是否包含`..`
2. **SQL注入防护**：只允许SELECT语句，使用参数化查询
3. **代码执行沙箱**：使用受限的执行环境
4. **API密钥管理**：不要在工具描述中暴露敏感信息
5. **速率限制**：防止频繁调用消耗资源

---

## MCP vs A2A：区别与联系

### 快速对比

| 维度 | MCP | A2A |
|------|-----|-----|
| **解决的问题** | Agent ↔ 工具/数据源 | Agent ↔ Agent |
| **架构** | Client-Server | Peer-to-Peer |
| **核心抽象** | Tools、Resources、Prompts | Agent Card、Task、Message |
| **类比** | 工具箱（给AI一把扳手） | 团队协作（AI找另一个AI帮忙） |
| **谁发起** | 模型主动调用工具 | Agent之间互相委托 |

### 生活比喻

**MCP = 工具箱**
- 就像你的工具箱里有扳手、螺丝刀、电钻
- 你（AI）需要的时候自己拿出来用
- 工具不会自己干活，得你操作

**A2A = 团队协作**
- 就像你有一个团队，有设计师、程序员、产品经理
- 你（Agent）把任务分给专业的人做
- 他们做完了把结果汇报给你

### 两者关系

MCP和A2A不是竞争关系，而是互补关系：

```
Agent A ──A2A── Agent B
  │                │
  MCP              MCP
  │                │
工具/资源       工具/资源
```

一个Agent可以同时：
- 通过MCP使用工具
- 通过A2A和其他Agent协作

---

## 生态与应用

### 支持MCP的Host

| Host | 类型 | 说明 |
|------|------|------|
| Claude Desktop | AI助手 | Anthropic官方桌面应用 |
| Cursor | IDE | AI编程编辑器 |
| Zed | IDE | 高性能代码编辑器 |
| Trae | IDE | 国产AI编程工具 |
| 自定义应用 | - | 任何集成MCP Client的应用 |

### 常见MCP Server类型

| 类型 | 用途 | 示例 |
|------|------|------|
| 文件系统 | 读写本地文件 | filesystem MCP |
| 浏览器控制 | 网页操作 | Puppeteer MCP |
| 数据库 | 数据查询 | PostgreSQL MCP |
| 搜索 | 网络搜索 | Tavily MCP |
| 代码仓库 | 代码分析 | GitHub MCP |
| 生产力工具 | 日历、邮件 | Google Workspace MCP |

---

## 最佳实践

### Server开发最佳实践

1. **好的工具描述**：description要写清楚工具是干什么的，LLM才能正确判断什么时候调用
2. **明确的参数Schema**：用JSON Schema严格定义参数类型、描述、默认值
3. **安全第一**：所有涉及文件、网络、数据库的操作都要有安全检查
4. **友好的错误信息**：工具出错时返回清晰的错误描述，方便LLM理解和重试
5. **适度的工具粒度**：不要太细（太碎了LLM不知道用哪个），也不要太粗（不灵活）

### 生产环境建议

1. **使用SSE传输**：远程服务用SSE，本地工具用stdio
2. **实现健康检查**：定期检查Server是否正常运行
3. **日志记录**：记录所有工具调用，便于调试和审计
4. **认证授权**：远程Server要实现API Key等认证机制
5. **版本管理**：Server升级时注意向后兼容

---

## 总结

MCP协议是AI Agent生态的关键基础设施，它为AI模型与外部工具、数据源的交互提供了统一的标准接口。

**核心价值**：
- **标准化**：结束工具调用的"巴别塔困境"
- **互操作性**：写一次Server，所有支持MCP的Host都能用
- **安全性**：多层安全防护，用户可控
- **生态繁荣**：统一标准促进工具生态快速发展

**发展趋势**：MCP正在成为AI Agent工具调用的"HTTP协议"——就像HTTP统一了Web通信，MCP正在统一AI与外部世界的连接方式。

---

## 相关知识

- [Agents技术](../模型架构/Agents技术.md)
- [Agentic RAG技术详解](../模型架构/Agentic%20RAG技术详解.md)
- [A2A协议详解](./A2A协议详解.md)

