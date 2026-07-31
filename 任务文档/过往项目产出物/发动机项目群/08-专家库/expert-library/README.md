# 工作流编排器 (agency-orchestrator)

> **项目**: {{PROJECT_NAME}} ({{PROJECT_SLUG}})
> **生成时间**: {{INIT_TIMESTAMP}}
> **启动包版本**: {{BOOTSTRAP_VERSION}}

## 概述

本目录包含 **agency-orchestrator 工作流编排引擎** 及其配套资源。编排引擎是一个 YAML 驱动的工作流执行系统，能够按预定义步骤自动调用多个专家协同完成任务。

**配套资源包括**：
- **~20 个 YAML 工作流模板**（产品开发、部门协作、数据分析等）
- **agency-agents/ 专家副本**（agency-agents-zh 的镜像，~150 位专家）
- **12 种 IDE 集成配置**（TRAE、Cursor、Copilot、Claude Code 等）

## 目录结构

```
agency-orchestrator/
├── agency-agents/           # 专家副本（agency-agents-zh 镜像）
│   ├── academic/
│   ├── design/
│   ├── engineering/
│   ├── finance/
│   ├── game-development/
│   ├── marketing/
│   ├── paid-media/
│   ├── product/
│   ├── project-management/
│   ├── sales/
│   ├── spatial-computing/
│   ├── specialized/
│   ├── strategy/
│   ├── support/
│   └── testing/
│
├── docs/                    # 设计文档与 PRD
│   ├── superpowers/         # 能力规划（条件循环、MCP 服务器等）
│   └── PRD.md
│
├── integrations/            # IDE 集成配置
│   ├── aider/               # Aider AI 助手
│   ├── antigravity/         # Antigravity
│   ├── claude-code/         # Claude Code CLI
│   ├── codex/               # OpenAI Codex CLI
│   ├── copilot/             # GitHub Copilot
│   ├── cursor/              # Cursor IDE
│   ├── gemini-cli/          # Google Gemini CLI
│   ├── kiro/                # Kiro
│   ├── openclaw/            # OpenClaw
│   ├── opencode/            # OpenCode
│   ├── qwen/                # 通义千问
│   ├── trae/                # TRAE IDE ⭐
│   └── windsurf/            # Windsurf
│
├── src/                     # TypeScript 源代码（核心编排引擎）
│   ├── agents/              # 代理加载器
│   ├── cli/                 # 命令行工具
│   ├── connectors/          # IDE 连接器
│   ├── core/                # 核心引擎（DAG、条件、执行器）
│   ├── mcp/                 # MCP 服务器
│   ├── output/              # 报告生成
│   └── utils/               # 工具函数
│
├── workflows/               # YAML 工作流模板 (~20个)
│   ├── data/                # 数据类工作流
│   ├── department-collab/   # 部门协作工作流
│   ├── academic-paper-outline.yaml
│   ├── ai-opinion-article.yaml
│   ├── ai-startup-launch.yaml
│   ├── codex-cc-loop.yaml
│   ├── codex-cc-simple.yaml
│   ├── content-pipeline.yaml
│   └── ...
│
├── examples/                # 示例文件
├── test/                    # 测试套件
└── README.md
```

## 核心能力

### 1. YAML 工作流定义

工作流使用 YAML 文件定义，包含步骤、条件、循环和专家调用：

```yaml
name: 代码审查工作流
description: 自动执行代码审查流程
steps:
  - name: 静态分析
    agent: engineering-code-reviewer
    input: "{{PR_DIFF}}"
    output: static_analysis_report

  - name: 安全扫描
    agent: engineering-security-engineer
    input: "{{PR_DIFF}}"
    output: security_report
    condition: "{{ENABLE_SECURITY_SCAN}} == true"

  - name: 综合评审
    agent: engineering-software-architect
    input:
      - "{{static_analysis_report}}"
      - "{{security_report}}"
    output: final_review
```

### 2. 条件与循环

支持在工作流中定义条件和循环：
- **条件步骤**：根据输入条件决定是否执行某一步
- **循环步骤**：对列表中的每个元素重复执行
- **并行步骤**：多个步骤同时执行

### 3. 多 IDE 集成

已预配置以下 IDE/工具的集成：

| IDE/工具 | 配置文件 | 说明 |
|----------|----------|------|
| TRAE | `integrations/trae/ao-workflow-runner.md` | 当前环境 |
| Cursor | `integrations/cursor/workflow-runner.mdc` | Cursor IDE |
| GitHub Copilot | `integrations/copilot/copilot-instructions.md` | Copilot CLI |
| Claude Code | `integrations/claude-code/README.md` | Claude Code |
| OpenAI Codex | `integrations/codex/instructions.md` | Codex CLI |
| Gemini CLI | `integrations/gemini-cli/GEMINI.md` | Gemini |
| Windsurf | `integrations/windsurf/.windsurfrules` | Windsurf |
| ... | ... | ... |

## 工作流模板清单

| 工作流 | 文件 | 场景 |
|--------|------|------|
| 仪表盘设计 | `workflows/data/dashboard-design.yaml` | 数据可视化 |
| 数据管道审阅 | `workflows/data/data-pipeline-review.yaml` | 数据工程 |
| CEO 组织委派 | `workflows/department-collab/ceo-org-delegation.yaml` | 高层管理 |
| 代码审查 | `workflows/department-collab/code-review.yaml` | 工程协作 |
| 内容发布 | `workflows/department-collab/content-publish.yaml` | 内容运营 |
| 学术论文大纲 | `workflows/academic-paper-outline.yaml` | 学术研究 |
| AI 观点文章 | `workflows/ai-opinion-article.yaml` | 内容创作 |
| AI 创业启动 | `workflows/ai-startup-launch.yaml` | 创业 |
| Codex 循环 | `workflows/codex-cc-loop.yaml` | 代码迭代 |
| 内容管道 | `workflows/content-pipeline.yaml` | 内容生产 |

## agency-agents/ 说明

`agency-agents/` 目录是 `agency-agents-zh/` 的一个镜像副本，包含相同的专家定义但可能版本略有差异。建议以 `agency-agents-zh/` 为主要参考，本目录下的副本用于编排引擎内部引用。

## 使用方式

1. **直接使用工作流模板**：在 `workflows/` 目录中选择合适的 YAML 模板，按需修改后执行
2. **集成到 IDE**：将 `integrations/trae/` 下的配置复制到 TRAE 配置目录，启用工作流运行器
3. **自定义工作流**：参考现有 YAML 模板，创建符合项目需求的新工作流

## 零API依赖声明

工作流模板和专家定义均为本地文件，不依赖外部 API。编排引擎本身需要 Node.js 运行时（如需执行 `src/` 中的 TypeScript 代码），但工作流定义文件可直接被大模型读取和执行。
