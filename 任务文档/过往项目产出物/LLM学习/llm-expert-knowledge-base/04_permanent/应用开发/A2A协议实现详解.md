
# A2A协议实现详解

## 概述

A2A（Agent-to-Agent Protocol，智能体间通信协议）是由Google Cloud在2025年4月推出的开放协议，旨在为不同框架或厂商构建的AI Agent提供统一协作标准，实现Agent之间的互联互通与任务协商。

**一句话总结**：A2A是Agent时代的"外交协议"——让不同公司、不同框架开发的AI Agent能像人类团队一样互相沟通、协作完成任务。

**地位**：2025年6月贡献至Linux Foundation成为开源协议，联合SAP、ServiceNow、LangChain、MongoDB等超过50家企业共同开发。

---

## 为什么需要A2A

### 多Agent的"巴别塔困境"

在A2A出现之前，多Agent协作出了名的难：

- Agent A用LangChain开发，Agent B用AutoGen开发，它们之间怎么通信？
- 公司采购了客服Agent，想让它调用数据分析Agent的能力，要写多少定制代码？
- 不同厂商的Agent各说各话，没有统一的"外交语言"

**问题本质**：缺乏Agent间互操作的开放标准，每个协作场景都要做定制化集成。

### A2A的解决方案

A2A为异构Agent系统提供了一套统一的交互规范：

| 规范要素 | 作用 |
|---------|------|
| Agent Card | Agent的"数字名片"，声明能力、接口、认证方式 |
| Task（任务） | 标准化的工作单元，有明确的生命周期 |
| Message（消息） | Agent间通信的统一格式 |
| Artifact（工件） | 任务产出物的标准表示 |

**价值**：写一次Agent，所有支持A2A的Agent都能和你协作。

---

## 设计原则

Google在设计A2A协议时遵循五大核心原则：

| 原则 | 说明 |
|------|------|
| **以Agent为中心** | 强调Agent自主性和多Agent协作能力，不局限于工具调用角色 |
| **基于现有标准** | 建立在HTTP、JSON-RPC和SSE等业界通用协议之上 |
| **默认安全** | 支持企业级认证授权（JWT、OIDC、签名的Agent Card） |
| **支持长任务** | 灵活支持从快速任务到复杂研究的多种场景，支持实时进度更新 |
| **模态无关** | 支持文本、音频、视频、表单、iframe等多种交互形式 |

---

## 三大参与角色

```
┌──────────┐     发起任务      ┌──────────┐
│   User   │ ───────────────→ │  Client  │
│ （用户）  │                  │ （客户端） │
└──────────┘                  └────┬─────┘
                                   │
                            HTTP / SSE
                            JSON-RPC
                                   │
                              ┌────▼─────┐
                              │  Server  │
                              │ （服务端） │
                              │  = Agent │
                              └──────────┘
```

| 角色 | 说明 |
|------|------|
| **User（用户）** | 使用Agent系统完成任务的人或服务 |
| **Client（客户端）** | 代表用户向远程Agent发起请求的实体 |
| **Server（服务端）** | 不透明（黑盒）的远程Agent，即A2A服务器 |

**注意**：与MCP不同，A2A没有Host的概念——设计上更开放，不绑定特定的宿主应用。

---

## 四大核心概念

### 1. Agent Card（智能体名片）

#### 什么是Agent Card

Agent Card是一个JSON文件，描述了Agent提供了什么样的功能。官方建议托管在 `https://base-url/.well-known/agent.json`，这样就可以直接通过HTTP GET获取。

**类比**：就像网站的`robots.txt`或`favicon.ico`，是Agent的"标准名片位置"。

#### Agent Card完整结构

```json
{
  "name": "Coder Agent",
  "description": "An agent that generates code based on natural language instructions.",
  "url": "https://coder-agent.example.com",
  "version": "1.0.0",
  "provider": {
    "organization": "Example Corp",
    "url": "https://example.com"
  },
  "documentationUrl": "https://coder-agent.example.com/docs",
  
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": true
  },
  
  "authentication": {
    "type": "http",
    "scheme": "bearer"
  },
  
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain", "application/json"],
  
  "skills": [
    {
      "id": "generate-code",
      "name": "Generate Code",
      "description": "Generate code based on natural language descriptions",
      "tags": ["coding", "software development"],
      "examples": [
        "Implement binary search in Python",
        "Create a React component for a todo list"
      ],
      "inputModes": ["text/plain"],
      "outputModes": ["text/plain", "application/json"]
    }
  ]
}
```

#### 字段详解

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | Agent的可读名称（如"Recipe Agent"） |
| `description` | string | Agent的描述，帮助其他Agent理解它能做什么 |
| `url` | string | Agent的服务地址 |
| `version` | string | 版本号（格式由提供方决定） |
| `provider` | object | 服务提供商信息 |
| `capabilities` | object | 支持的能力（流式、推送、状态历史等） |
| `authentication` | object | 认证要求（匹配OpenAPI认证结构） |
| `skills` | array | Agent能执行的能力单元 |
| `skills[].id` | string | Skill的唯一标识 |
| `skills[].tags` | array | 描述能力类别的标签（如"cooking"） |
| `skills[].examples` | array | 示例场景，帮助理解如何使用 |

#### Agent Card的引申：Agent注册表

自然的延伸是需要Agent注册表——无论是公开的还是私有的，方便查找需要的Agent。甚至可以设想去中心化的场景：

- 每个网站都有自己的`/.well-known/agent.json`
- 在P2P网络中广播自己的Agent Card
- Agent Card存放在IPFS或以太坊上
- Agent的协作关系构成自组织的Agent网络

---

### 2. Task（任务）

#### 什么是Task

任务是一个有状态的实体，允许客户端与远程Agent协作以达成特定的结果并生成相应的输出。在任务内，客户端与远程Agent之间交换消息，远程Agent生成工件作为结果。

**关键特性**：
- 任务始终由客户端创建
- 任务状态由远程Agent决定
- 多个任务可以归属于同一个会话（sessionId）
- 同一个任务上下文中可以进行多轮对话

#### 任务生命周期

```
submitted（已提交）
    ↓
working（处理中）
    ↓
    ├──→ input-required（需要输入）
    │        ↓（用户补充信息）
    │      working
    │
    ├──→ completed（已完成）
    │
    ├──→ canceled（已取消）
    │
    └──→ failed（失败）
```

**TaskState枚举值**：

| 状态 | 说明 |
|------|------|
| `submitted` | 任务已提交，等待处理 |
| `working` | Agent正在处理任务 |
| `input-required` | Agent需要更多信息才能继续 |
| `completed` | 任务成功完成 |
| `canceled` | 任务被取消 |
| `failed` | 任务失败 |
| `unknown` | 状态未知 |

#### Task完整结构

```typescript
interface Task {
  id: string;                    // 任务唯一标识
  sessionId?: string;            // 会话ID（客户端生成，可选）
  status: TaskStatus;            // 当前状态
  history?: Message[];           // 消息历史（可选）
  artifacts?: Artifact[];        // 生成的工件集合
  metadata?: Record<string, any>; // 扩展元数据
}

interface TaskStatus {
  state: TaskState;              // 状态值
  message?: Message;             // 状态更新的附加消息
  timestamp?: string;            // ISO格式时间戳
}
```

#### Agent收到请求后的行动选择

Agent收到任务请求后，可以采取以下行动：
- 立即满足请求
- 安排稍后执行
- 拒绝请求
- 协商不同的执行方式
- 向客户端索要更多信息
- 委派给其他Agent或系统

**重要设计**：即使任务完成后，客户端仍然可以请求更多信息或在同一任务上下文中进行更改。比如：
- 客户端："画一只兔子的图片"
- Agent：`<图片>`
- 客户端："把它画成红色"

---

### 3. Artifact（工件）

#### 什么是Artifact

工件是Agent作为任务最终结果生成的输出。工件具有不可变性，可以被命名，并且可以包含多个部分。通过流式响应，可以将新部分附加到现有的工件中。

**类比**：就像设计师交付设计稿——可能包含PSD文件、说明文档、切图资源，这些都是"工件"。

**特点**：
- 一个任务可以生成多个工件
- 例如"创建一个网页"任务，可能产生HTML工件和图像工件
- 支持流式输出（新部分可以追加）

#### Artifact结构

```typescript
interface Artifact {
  name?: string;                           // 工件名称
  description?: string;                    // 描述
  parts: Part[];                           // 内容片段
  metadata?: Record<string, any>;          // 元数据
  index: number;                           // 序号
  append?: boolean;                        // 是否追加模式
  lastChunk?: boolean;                     // 是否最后一块
}
```

---

### 4. Message & Part（消息与片段）

#### Message（消息）

消息是包含任何非工件内容的实体。这些内容可以包括Agent的思考、用户的上下文、指令、错误信息、状态更新或元数据。

**规则**：
- 所有来自客户端的内容均以消息形式发送
- Agent通过消息传达状态或提供指令
- 生成的结果以工件形式发送

```typescript
interface Message {
  role: "user" | "agent";           // 角色
  parts: Part[];                    // 内容片段
  metadata?: Record<string, any>;   // 元数据
}
```

#### Part（片段）

Part是客户端与远程Agent之间作为消息或工件一部分交换的完整内容。每个Part有其独特的内容类型和元数据。

**三种Part类型**：

| 类型 | 接口 | 用途 |
|------|------|------|
| **TextPart** | `{ type: "text", text: string }` | 文本内容 |
| **FilePart** | `{ type: "file", file: { name, mimeType, bytes/uri } }` | 文件内容 |
| **DataPart** | `{ type: "data", data: Record<string, any> }` | 结构化数据 |

```typescript
type Part = (TextPart | FilePart | DataPart) & {
  metadata: Record<string, any>;
};
```

---

## 通信机制

### 传输协议

| 方式 | 说明 | 适用场景 |
|------|------|---------|
| **HTTP + JSON-RPC** | 标准请求/响应模式 | 简单任务、同步调用 |
| **SSE（Server-Sent Events）** | 服务器推送事件流 | 长任务、流式输出、实时进度 |
| **Push Notifications** | 推送通知（Webhook） | 离线场景、异步回调 |

### 标准API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/.well-known/agent.json` | GET | 获取Agent Card |
| `/tasks/send` | POST | 发送任务（请求/响应模式） |
| `/tasks/sendSubscribe` | POST | 发送任务（SSE流式模式） |
| `/tasks/{id}/status` | GET | 查询任务状态 |
| `/tasks/{id}/subscribe` | GET | 订阅任务更新（SSE） |
| `/tasks/{id}/cancel` | POST | 取消任务 |

### 任务发送示例（Request/Response模式）

**请求**：
```json
POST /tasks/send
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tasks/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "用Python实现二分查找算法"
        }
      ]
    }
  }
}
```

**响应**：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "task": {
      "id": "task-12345",
      "status": {
        "state": "completed",
        "timestamp": "2025-06-01T12:00:00Z"
      },
      "artifacts": [
        {
          "name": "binary_search.py",
          "parts": [
            {
              "type": "text",
              "text": "def binary_search(arr, target):\n    ..."
            }
          ]
        }
      ]
    }
  }
}
```

### 流式任务（SSE模式）

对于长任务，使用`sendSubscribe`端点通过SSE推送实时更新：

```
任务提交 → 状态：submitted
    ↓
状态更新：working（附带进度信息）
    ↓
工件更新：Part 1（代码文件第一段）
    ↓
工件更新：Part 2（代码文件第二段）
    ↓
状态更新：completed
    ↓
流结束
```

**事件类型**：

| 事件 | 说明 |
|------|------|
| `TaskStatusUpdateEvent` | 任务状态更新 |
| `TaskArtifactUpdateEvent` | 工件更新（流式输出） |

### 推送通知

对于不需要保持连接的场景，Agent可以通过Webhook向客户端推送通知：

```typescript
interface PushNotificationConfig {
  url: string;                           // Webhook地址
  token?: string;                        // 任务/会话唯一token
  authentication?: {
    schemes: string;
    credentials?: string;
  };
}
```

---

## 错误处理

### 错误消息格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Task not found"
  }
}
```

### 标准错误码

| 错误码 | 信息 | 描述 |
|--------|------|------|
| -32700 | JSON parse error | 无效的JSON |
| -32600 | Invalid Request | 请求负载验证错误 |
| -32601 | Method not found | 非法方法 |
| -32602 | Invalid params | 无效的方法参数 |
| -32603 | Internal error | 内部JSON-RPC错误 |
| -32000 ~ -32099 | Server error | 保留给实现特定错误 |
| -32001 | Task not found | 找不到任务 |
| -32002 | Task cannot be canceled | 无法取消任务 |
| -32003 | Push notifications not supported | 不支持推送通知 |
| -32004 | Unsupported operation | 操作不支持 |
| -32005 | Incompatible content types | 内容类型不兼容 |

---

## Python实现示例

### A2A Server（Flask实现）

```python
"""
简单的A2A Server实现示例
"""
from flask import Flask, request, jsonify, Response
import json
import uuid
from dataclasses import dataclass, field
from typing import Optional, List

app = Flask(__name__)

# 内存存储（生产环境用数据库）
tasks = {}

@dataclass
class Task:
    id: str
    status: str = "submitted"
    result: Optional[str] = None

# ===== Agent Card =====
@app.route('/.well-known/agent.json')
def agent_card():
    return jsonify({
        "name": "Calculation Agent",
        "description": "一个执行数学计算的Agent",
        "url": "http://localhost:8000",
        "version": "1.0.0",
        "capabilities": {
            "streaming": False,
            "stateTransitionHistory": True
        },
        "authentication": {
            "type": "none"
        },
        "skills": [
            {
                "id": "calculate",
                "name": "数学计算",
                "description": "执行数学表达式计算",
                "tags": ["math", "calculation"],
                "examples": ["计算 2 + 3 * 4"]
            }
        ]
    })

# ===== 任务发送 =====
@app.route('/tasks/send', methods=['POST'])
def send_task():
    data = request.json
    task_id = str(uuid.uuid4())
    
    # 提取用户消息
    message_text = ""
    for part in data.get('params', {}).get('message', {}).get('parts', []):
        if part.get('type') == 'text':
            message_text = part.get('text', '')
    
    # 处理任务（这里简化为计算）
    try:
        import ast
        import operator
        
        allowed_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        
        def safe_eval(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                left = safe_eval(node.left)
                right = safe_eval(node.right)
                op = allowed_ops.get(type(node.op))
                if op:
                    return op(left, right)
            raise ValueError("不支持的表达式")
        
        tree = ast.parse(message_text, mode='eval')
        result = str(safe_eval(tree.body))
        
        status = "completed"
        artifacts = [{
            "name": "result.txt",
            "parts": [{"type": "text", "text": f"计算结果: {result}"}]
        }]
    except Exception as e:
        status = "failed"
        artifacts = []
    
    tasks[task_id] = Task(id=task_id, status=status, result=result if status == "completed" else str(e))
    
    return jsonify({
        "jsonrpc": "2.0",
        "id": data.get('id'),
        "result": {
            "task": {
                "id": task_id,
                "status": {
                    "state": status
                },
                "artifacts": artifacts
            }
        }
    })

# ===== 查询状态 =====
@app.route('/tasks/<task_id>/status')
def get_task_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {"code": -32001, "message": "Task not found"}
        }), 404
    
    return jsonify({
        "jsonrpc": "2.0",
        "result": {
            "task": {
                "id": task.id,
                "status": {"state": task.status}
            }
        }
    })

if __name__ == '__main__':
    app.run(port=8000, debug=True)
```

### A2A Client实现

```python
"""
简单的A2A Client实现示例
"""
import requests
import json

class A2AClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.agent_card = None
    
    def get_agent_card(self) -> dict:
        """获取Agent Card"""
        if not self.agent_card:
            resp = requests.get(f"{self.base_url}/.well-known/agent.json")
            resp.raise_for_status()
            self.agent_card = resp.json()
        return self.agent_card
    
    def send_task(self, message_text: str) -> dict:
        """发送任务"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tasks/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {"type": "text", "text": message_text}
                    ]
                }
            }
        }
        
        resp = requests.post(
            f"{self.base_url}/tasks/send",
            json=payload
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_task_status(self, task_id: str) -> dict:
        """查询任务状态"""
        resp = requests.get(f"{self.base_url}/tasks/{task_id}/status")
        resp.raise_for_status()
        return resp.json()

# 使用示例
if __name__ == '__main__':
    client = A2AClient("http://localhost:8000")
    
    # 1. 获取Agent Card
    card = client.get_agent_card()
    print(f"Agent名称: {card['name']}")
    print(f"描述: {card['description']}")
    
    # 2. 发送任务
    result = client.send_task("2 + 3 * 4")
    task = result['result']['task']
    
    print(f"\n任务ID: {task['id']}")
    print(f"状态: {task['status']['state']}")
    
    if task['status']['state'] == 'completed':
        for artifact in task.get('artifacts', []):
            print(f"\n工件: {artifact['name']}")
            for part in artifact['parts']:
                if part['type'] == 'text':
                    print(f"内容: {part['text']}")
```

---

## A2A vs MCP：深入对比

### 核心差异

| 维度 | MCP | A2A |
|------|-----|-----|
| **主要用途** | Agent与工具/数据源的连接 | Agent与Agent之间的通信协作 |
| **核心架构** | Client-Host-Server（三层） | Client-Server（两层，对等） |
| **核心抽象** | Tools、Resources、Prompts | Agent Card、Task、Message、Artifact |
| **通信对象** | 模型 ↔ 工具 | Agent ↔ Agent |
| **典型场景** | 数据库查询、文件处理、API调用 | 跨平台任务分配、复杂流程编排 |
| **性能优势** | 低延迟工具调用 | 长任务异步处理 |
| **控制权** | Host控制（中心化） | Agent自主协商（去中心化） |
| **生态成熟度** | 广泛采用，社区快速增长 | 初期，行业支持良好 |

### 生活比喻

| MCP = 工具箱 | A2A = 团队协作 |
|-------------|--------------|
| 工具箱里有扳手、螺丝刀、电钻 | 团队里有设计师、程序员、产品经理 |
| 你（AI）需要的时候自己拿出来用 | 你（Agent）把任务分给专业的人做 |
| 工具不会自己干活，得你操作 | 他们做完了把结果汇报给你 |
| 工具是被动的、无生命的 | 每个Agent都是主动的、有"大脑"的 |

### 两者关系：互补而非竞争

MCP和A2A不是竞争关系，而是互补关系：

```
┌──────────┐           ┌──────────┐
│ Agent A  │ ──A2A──→ │ Agent B  │
└────┬─────┘           └────┬─────┘
     │                      │
     MCP                    MCP
     │                      │
  工具/资源               工具/资源
```

一个Agent可以同时：
- 通过MCP使用外部工具
- 通过A2A和其他Agent协作

**场景示例（电商客服）**：
```
客服Agent通过MCP调用订单数据库查询订单
    ↓
发现需要修改配送地址
    ↓
通过A2A请求物流Agent修改配送地址
```

### 技术上的边界：Agent vs Tool

一个有意思的思考：Agent和工具有没有绝对的边界？

- 从技术上看，A2A能覆盖的场景似乎更多，包括MCP的场景
- 但工具是"被动调用"的，Agent是"主动协作"的
- 从架构上看，MCP更倾向于中心化管理，A2A更倾向于分散自治

---

## 产业现状与应用

### 生态参与者

**联合发起方**：Google、SAP、ServiceNow、LangChain、MongoDB等50+企业

**已部署企业**：Adobe、ServiceNow、S&P Global等

**贡献给Linux Foundation**：2025年6月，成为真正的开源社区项目

### 应用场景

| 场景 | 说明 |
|------|------|
| **企业跨系统协作** | 客服Agent、数据分析Agent、合同生成Agent跨系统协作 |
| **AI Agent市场** | Agent Marketplace发布与交易 |
| **消费级应用** | 手机助手通过A2A操作微信等App |
| **旅行规划** | 主Agent分解任务给机票、酒店、景点Agent |
| **供应链管理** | 采购Agent与库存Agent实时同步 |

### 产业动态

2026年6月，微信开始向手机厂商开放A2A能力，荣耀率先落地。用户只需对YOYO说一句话，就可以直接发送微信消息、发起微信语音或视频通话。华为、小米、OPPO、vivo等厂商也已宣布接入计划。

**意义**：这标志着A2A协议正在从企业级走向消费级，成为智能设备间的"通用交互语言"。

---

## 最佳实践

### Server开发最佳实践

1. **完善的Agent Card**：description和examples要写清楚，其他Agent才知道怎么和你协作
2. **正确的状态管理**：严格遵循TaskState的状态转换规则
3. **支持流式输出**：长任务一定要支持SSE，用户体验好很多
4. **错误处理友好**：错误信息要具体，让调用方知道怎么处理
5. **认证与安全**：生产环境一定要加认证（Bearer Token等）

### 架构选择建议

| 场景 | 选MCP | 选A2A | 都用 |
|------|-------|-------|------|
| 调用一个API接口 | ✅ | | |
| 需要AI帮你写代码 | | ✅ | |
| 读取数据库 | ✅ | | |
| 多步骤复杂任务 | | ✅ | |
| 工具调用 | ✅ | | |
| Agent间协商 | | ✅ | |
| 企业级复杂系统 | | | ✅ |

---

## 总结

A2A协议是多Agent协作时代的关键基础设施，它为异构Agent系统提供了统一的"外交语言"。

**核心价值**：
- **互操作性**：结束Agent间的"巴别塔困境"
- **可组合性**：像搭积木一样组合不同Agent的能力
- **去中心化**：Agent自主协商，不需要中心化的调度器
- **生态繁荣**：统一标准促进Agent市场快速发展

**发展趋势**：
- 从企业级走向消费级（微信A2A就是信号）
- 从简单协作走向复杂协商（议价、合同、争议解决）
- 从单体Agent走向Agent网络（自组织的协作生态）

**未来畅想**：当每个网站、每个服务都有自己的Agent Card，当Agent之间可以自主发现、协商、协作时，我们将进入一个真正的"Agent互联网"时代——不是人在使用App，而是Agent在为人类跑腿办事。

---

## 相关知识

- [MCP协议实现详解](./MCP协议实现详解.md)
- [Agents技术](../模型架构/Agents技术.md)
- [LangGraph实践应用详解](./LangGraph实践应用详解.md)

