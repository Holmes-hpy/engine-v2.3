# 通用职场专家库 (agency-agents-zh)

> **项目**: {{PROJECT_NAME}} ({{PROJECT_SLUG}})
> **生成时间**: {{INIT_TIMESTAMP}}
> **启动包版本**: {{BOOTSTRAP_VERSION}}

## 概述

本目录包含 **215+ 位通用职场专家定义**，覆盖 20 个部门/领域。每位专家是一个独立的 Markdown 文件，包含角色定义、能力范围和使用场景。

## 目录结构

```
agency-agents-zh/
├── academic/              # 学术研究专家 (6位)
├── ai/                    # AI 系统与记忆银行文档
├── design/                # 设计专家 (8位)
├── engineering/           # 工程技术专家 (35位)
├── examples/              # 工作流示例 (6个)
├── finance/               # 财务专家 (8位)
├── game-development/      # 游戏开发专家 (20位)
│   ├── blender/
│   ├── godot/
│   ├── roblox-studio/
│   ├── unity/
│   └── unreal-engine/
├── hr/                    # 人力资源专家 (2位)
├── legal/                 # 法务专家 (2位)
├── marketing/             # 市场营销专家 (~40位)
├── paid-media/            # 付费媒体专家 (8位)
├── product/               # 产品专家 (5位)
├── project-management/    # 项目管理专家 (6位)
├── sales/                 # 销售专家 (8位)
├── spatial-computing/     # 空间计算专家 (6位)
├── specialized/           # 专业/特殊领域专家 (~45位)
├── strategy/              # 战略与策略文档
│   ├── coordination/      # 专家激活提示词与交接模板
│   ├── playbooks/         # 7阶段战略手册
│   └── runbooks/          # 场景运行手册
├── supply-chain/          # 供应链专家 (4位)
├── support/               # 支持/运维专家 (8位)
├── testing/               # 测试/QA专家 (9位)
├── AGENT-LIST.md          # 专家完整清单
├── CATALOG.md             # 专家分类目录
└── README.md              # 本文件
```

## 专家分类速查

### 工程技术 (engineering/) — 35 位

| 专家文件名 | 角色 |
|-----------|------|
| `engineering-software-architect.md` | 软件架构师 |
| `engineering-backend-architect.md` | 后端架构师 |
| `engineering-autonomous-optimization-architect.md` | 自主优化架构师 |
| `engineering-frontend-developer.md` | 前端开发 |
| `engineering-ai-engineer.md` | AI 工程师 |
| `engineering-data-engineer.md` | 数据工程师 |
| `engineering-security-engineer.md` | 安全工程师 |
| `engineering-devops-automator.md` | DevOps |
| `engineering-sre.md` | SRE |
| `engineering-code-reviewer.md` | 代码审查 |
| `engineering-database-optimizer.md` | 数据库优化 |
| `engineering-embedded-firmware-engineer.md` | 嵌入式固件 |
| `engineering-iot-solution-architect.md` | IoT 方案架构 |
| `engineering-mobile-app-builder.md` | 移动应用 |
| `engineering-solidity-smart-contract-engineer.md` | 智能合约 |
| `engineering-technical-writer.md` | 技术文档 |
| ... 等 35 位 |

### 市场营销 (marketing/) — ~40 位

覆盖抖音、小红书、快手、B站、知乎、微博、微信、LinkedIn、Twitter、TikTok、Instagram、Reddit 等全平台。

### 专业/特殊领域 (specialized/) — ~45 位

| 专家文件名 | 角色 |
|-----------|------|
| `specialized-workflow-architect.md` | 工作流架构师 |
| `specialized-salesforce-architect.md` | Salesforce 架构师 |
| `automation-governance-architect.md` | 自动化治理架构师 |
| `agentic-identity-trust.md` | 身份信任架构师 |
| `blockchain-security-auditor.md` | 区块链安全审计 |
| `prompt-engineer.md` | 提示词工程师 |
| `specialized-mcp-builder.md` | MCP 构建器 |
| `specialized-chief-of-staff.md` | 参谋长 |
| `specialized-civil-engineer.md` | 土木工程师 |
| ... 等 45 位 |

### 游戏开发 (game-development/) — 20 位

覆盖 Unity、Unreal Engine、Godot、Roblox、Blender 五大引擎/平台。

### 战略手册 (strategy/playbooks/) — 7 份

- Phase 0: 发现 (Discovery)
- Phase 1: 策略 (Strategy)
- Phase 2: 基础 (Foundation)
- Phase 3: 构建 (Build)
- Phase 4: 加固 (Hardening)
- Phase 5: 发布 (Launch)
- Phase 6: 运营 (Operate)

## 文件命名规范

```
{领域}-{专家角色}.md
```

示例：
- `product-product-manager.md`
- `engineering-backend-architect.md`
- `design-ux-architect.md`

## 专家定义模板

每个专家文件遵循以下结构：

```markdown
# {专家角色名称}

## 角色定义
{一句话描述该专家的角色}

## 能力范围
- {能力 1}
- {能力 2}
- ...

## 使用场景
1. {场景 1}
2. {场景 2}

## 输出格式
{该专家产生输出的标准格式}

## 约束条件
- {约束 1}
- {约束 2}
```

## 使用方式

大模型在需要特定领域知识时，读取对应的专家文件，按照其中的角色定义和能力范围执行任务。

## 零API依赖声明

所有专家定义均为本地 Markdown 文件，不依赖任何外部 API。
