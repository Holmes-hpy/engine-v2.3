# 外部系统集成（Plane MCP）

> **版本**: v2.4.0
> **优先级**: P8
> **说明**: 本文件定义项目与外部系统的集成方式，重点是 Plane 项目管理系统。所有与 Plane 的交互必须遵守本文件。

---

## 1. Plane MCP 总览

Plane 是项目的外部项目管理系统，用于团队协作和任务追踪。本项目通过 Plane MCP Server 与 Plane 进行程序化交互。

### 1.1 基本信息

| 项 | 值 |
|----|-----|
| Plane Web UI | `https://plane.mas.aicookbook.site/mas/` |
| MCP Server | `https://mcp-plane.mas.aicookbook.site/http/api-key/mcp` |
| 工作区 | `mas` |
| 认证方式 | API Key（Bearer Token） |
| 凭证存储 | `plane_mcp/.env`（git 忽略） |

### 1.2 客户端位置

```
plane_mcp/
├── client.py              # 核心 Python 客户端（HTTP SSE 协议）
├── __init__.py            # 模块导出
├── .env.example           # 凭证模板
├── .env                   # 实际凭证（git 忽略，不要提交！）
└── tools/*.json           # 177 个工具描述文件
```

### 1.3 快速验证

```python
from plane_mcp import PlaneMCPClient
client = PlaneMCPClient()
me = client.get_me()
print(me)  # 应该返回当前用户信息
```

或命令行：
```bash
cd plane_mcp && python3 client.py get_me
```

---

## 2. 关键 ID 速查表

> **重要**：这些 ID 是项目的"坐标"，新任务直接查此表，不要每次都遍历。

### 2.1 项目（Projects）

| 项目名称 | 标识 | ID | 说明 |
|---------|------|----|------|
| 产品交付 | SHIP | `458341b9-94b6-4419-97b9-5d5f8073d6d1` | 对外交付物管理 |
| 智驭研发 | ZHIYU | `1f03bf83-4999-4299-b8e0-f05ba4cf7465` | 内部研发管理 |

### 2.2 模块（Modules）- 产品交付项目

| 模块名称 | ID | 说明 |
|---------|----|------|
| 科技快报 | `1cd55d8a-8c64-4450-bd54-9446ed3f577c` | 每日 AI 行业动态快报 |
| 【智能体2.0】【自动编排】 | `c78a9669-ecfb-4816-aa40-ff5a3d124e95` | 自动编排功能模块 |
| 【智能体2.0】【任务总览】 | `d69c8e7c-6a4e-4cb2-98f4-bd4b76424902` | 任务总览模块 |

> 新增模块时，必须更新此表。查询模块列表：`python3 plane_mcp/client.py list_modules project_id=xxx`

### 2.3 常用工具

| 工具名 | 用途 | 必填参数 |
|--------|------|----------|
| `list_projects` | 列出所有项目 | - |
| `list_work_items` | 列出工作项 | `project_id` |
| `create_work_item` | 创建工作项 | `project_id`, `name` |
| `update_work_item` | 更新工作项 | `project_id`, `work_item_id` |
| `list_modules` | 列出模块 | `project_id` |
| `create_module` | 创建模块 | `project_id`, `name` |
| `manage_module_work_items` | 管理模块工作项关联 | `project_id`, `module_id` |
| `list_module_work_items` | 列出模块下的工作项 | `project_id`, `module_id` |
| `list_pages` | 列出页面 | `project_id` |
| `create_page` | 创建页面 | `name`, `description_html` |
| `get_me` | 获取当前用户 | - |

> 完整工具列表：`python3 plane_mcp/client.py` 不带参数会列出所有工具，共 177 个。

---

## 3. 每日快报上传流程

### 3.1 一键上传脚本

脚本位置：`任务文档/20260731-同行发展情况/产出物/每日快报/upload_to_plane.py`

**功能**：读取本地 Markdown 快报 → 转 HTML → 创建 Plane 工作项 → 关联到"科技快报"模块

**用法**：

```bash
# 上传今天的快报（自动识别日期）
cd 任务文档/20260731-同行发展情况/产出物/每日快报
python3 upload_to_plane.py

# 上传指定日期的快报
python3 upload_to_plane.py --date 2026-08-04

# 预览模式（不上传，只检查内容）
python3 upload_to_plane.py --date 2026-08-04 --dry-run

# 上传后验证
python3 upload_to_plane.py --date 2026-08-04 --verify

# 自定义标题
python3 upload_to_plane.py --date 2026-08-04 --title "【特刊】AI行业重大事件汇总"
```

### 3.2 手动上传（Python 方式）

如果需要更灵活的控制（如批量上传、附带附件等），使用 Python API：

```python
import sys
sys.path.insert(0, "plane_mcp")
from client import PlaneMCPClient
import markdown

client = PlaneMCPClient()

project_id = "458341b9-94b6-4419-97b9-5d5f8073d6d1"  # 产品交付
module_id = "1cd55d8a-8c64-4450-bd54-9446ed3f577c"   # 科技快报

# 1. 读取 Markdown
md_content = open("path/to/file.md", encoding="utf-8").read()
html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

# 2. 创建工作项
result = client.create_work_item(
    project_id=project_id,
    name="工作项标题",
    description_html=html_content,
    priority="high",  # urgent / high / medium / low / none
)
work_item_id = result["id"]

# 3. 关联到模块
client.call_tool("manage_module_work_items", {
    "project_id": project_id,
    "module_id": module_id,
    "add_ids": [work_item_id],
})
```

### 3.3 注意事项

1. **Pages API 不可用**：Plane Pages 在本项目中返回 404（未启用），内容直接放在工作项的 `description_html` 字段中
2. **内容长度限制**：`description_html` 建议不超过 10 万字符，超长内容会被自动截断
3. **Markdown 转 HTML**：必须使用 `markdown` 库，支持表格、代码块、目录等扩展
4. **凭证安全**：`.env` 文件已在 `.gitignore` 中，**严禁提交到 GitHub**

---

## 4. 常见任务速查

### 4.1 查询产品交付项目下有哪些模块

```bash
cd plane_mcp
python3 client.py list_modules project_id=458341b9-94b6-4419-97b9-5d5f8073d6d1
```

### 4.2 查看科技快报模块下的工作项

```bash
cd plane_mcp
python3 client.py list_module_work_items \
  project_id=458341b9-94b6-4419-97b9-5d5f8073d6d1 \
  module_id=1cd55d8a-8c64-4450-bd54-9446ed3f577c
```

### 4.3 创建新模块

```bash
cd plane_mcp
python3 client.py create_module \
  project_id=458341b9-94b6-4419-97b9-5d5f8073d6d1 \
  name="模块名称" \
  description="模块描述"
```

> 创建后**必须**更新本文件 2.2 节的模块速查表。

### 4.4 查看所有可用工具

```bash
cd plane_mcp
python3 -c "from client import PlaneMCPClient; c=PlaneMCPClient(); [print(t['name']) for t in c.list_tools()]"
```

---

## 5. 已知限制与 Pitfall

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Pages API 返回 404 | 项目未启用 Pages 功能 | 使用工作项 `description_html` 承载内容 |
| `create_work_item` 不支持 `module_id` 参数 | Plane API 设计如此 | 先创建工作项，再用 `manage_module_work_items` 关联 |
| 大段 Markdown 表格渲染异常 | Plane 的 HTML 渲染对复杂表格支持有限 | 简化表格结构，或拆分为多个段落 |
| 凭证丢失 | `.env` 被误删或未配置 | 从 `.env.example` 复制，填入 API Key |

---

## 6. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.4.0 | 2026-08-04 | 新增本规则文件；Plane MCP 集成文档；每日快报上传脚本；关键 ID 速查表 |
