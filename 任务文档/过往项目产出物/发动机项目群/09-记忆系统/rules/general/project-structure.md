# 项目结构规范

> **项目**: v1.3.0 (v1.3.0)
> **类型**: generic
> **生成时间**: 2026-07-16T07:00:00+08:00
> **启动包版本**: 1.3.0

## 1. 目录结构总览

```
v1.3.0/
├── README.md                     # 项目说明文档
├── .gitignore                    # Git 忽略规则
├── .bootstrap-complete           # 初始化完成标记（自动生成）
│
├── docs/                         # 项目文档
│   ├── decisions/                # 架构决策记录 (ADR)
│   │   └── README.md             # ADR 索引
│   └── guides/                   # 操作指南
│
├── rules/                        # 规则体系（核心）
│   ├── general/                  # 通用规则
│   │   ├── project-structure.md  # 本文件
│   │   ├── rule-registry.md      # 规则注册表
│   │   └── sensitive-data-filter.md
│   ├── output/                   # 输出管理规则
│   │   ├── output-management.md
│   │   └── handoff-contract.md
│   └── task/                     # 任务管理规则
│       ├── task-state-machine.md
│       ├── task-lifecycle.md
│       └── fault-recovery.md
│
├── memory/                       # 认知闭环 - Markdown 存储
│   ├── sessions/                 # 会话归档
│   │   └── README.md
│   ├── knowledge/                # 知识沉淀
│   │   └── README.md
│   └── index/                    # 索引文件
│       ├── knowledge-index.md
│       └── session-index.md
│
├── .memory/                      # 认知闭环 - SQLite 数据库
│   └── knowledge.db              # 本地知识库（零API依赖）
│
├── experts/                      # 专家库
│   ├── agency-agents-zh/         # 通用职场专家（215位）
│   ├── financial-services/       # 金融服务专家（10位）
│   └── agency-orchestrator/      # 工作流模板（51个）
│
├── tasks/                        # 任务状态存储
│   ├── active/                   # 进行中任务 (in_progress, blocked)
│   ├── reviewing/                # 评审中任务 (reviewing)
│   ├── handoff/                  # 交接中任务 (handoff_incomplete)
│   ├── completed/                # 已完成任务 (completed, failed, archived)
│   ├── checkpoints/              # 检查点
│   │   └── bootstrap/            # 初始化检查点
│   ├── state-machine-config.json # 状态机配置
│   ├── lifecycle.log             # 生命周期日志
│   └── state-change.log          # 状态变更日志
│
├── output/                       # 输出根目录 (参见规则 O1)
│   ├── deliverables/             # 最终交付物
│   │   └── README.md
│   ├── drafts/                   # 草稿文件
│   │   └── README.md
│   ├── archives/                 # 归档文件
│   │   └── README.md
│   └── index.md                  # 输出索引
│
└── logs/                         # 运行日志
    ├── bootstrap/                # 初始化日志
    │   ├── bootstrap-2026-07-16T07:00:00+08:00.log
    │   └── handoff-report.md
    ├── sensitive-filter.log      # 敏感数据过滤日志
    ├── fault-recovery.log        # 故障恢复日志
    ├── timeout/                  # 超时记录
    ├── fault/                    # 故障现场数据
    │   └── scenes/               # 故障场景快照
    └── drills/                   # 故障恢复演练记录
```

> **路径基准点**：本规则中所有相对路径，基准点为项目根目录（即 `.memory/` 所在的目录）。

> **自动化初始化**：项目初始化时运行 `scripts/init_project.sh --type generic` 可自动创建上述目录结构。脚本会检查目录完整性并生成 `.bootstrap-complete` 标记文件。

## 2. 类型特定扩展目录

基于项目类型 `generic`，可额外创建以下目录：

### 2.1 web 类型扩展

```
src/                # 源代码
public/             # 静态资源
tests/              # 测试文件
config/             # 配置文件
```

### 2.2 data 类型扩展

```
data/               # 数据集
notebooks/          # Jupyter 笔记本
models/             # 数据模型
scripts/            # 处理脚本
```

### 2.3 ai 类型扩展

```
prompts/            # 提示词模板
models/             # AI 模型
datasets/           # 训练数据
experiments/        # 实验记录
```

### 2.4 mobile 类型扩展

```
src/                # 源代码
assets/             # 资源文件
platforms/          # 平台特定代码
tests/              # 测试文件
```

### 2.5 generic 类型扩展

```
src/                # 源代码
tests/              # 测试文件
assets/             # 通用资源
```

## 3. 目录管理规则

### 3.1 禁止修改的目录

以下目录由启动包自动生成，非必要不得手动修改结构：

- `rules/` — 规则体系完整性依赖固定结构
- `.memory/` — 认知闭环数据库位置固定
- `tasks/` — 任务状态存储结构依赖状态机定义（含 active/、reviewing/、handoff/、completed/、checkpoints/ 等子目录）
- `output/` — 输出目录结构依赖 O1 规则定义
- `logs/` — 日志目录结构含预定义的日志文件和子目录

### 3.2 用户可扩展目录

以下目录鼓励用户根据项目需求扩展：

- `docs/decisions/` — 添加新的 ADR 文件
- `memory/sessions/` — 添加新的会话归档
- `memory/knowledge/` — 添加新的知识条目
- `logs/` — 添加新的日志分类子目录

### 3.3 文件命名规范

| 目录 | 命名规范 | 示例 |
|------|----------|------|
| docs/decisions/ | `ADR-NNNN-短标题.md` | `ADR-0001-选择-react.md` |
| memory/sessions/ | `YYYY-MM-DD-会话主题.md` | `2026-07-15-架构评审.md` |
| memory/knowledge/ | `领域-知识点.md` | `frontend-state-management.md` |
| tasks/active/ | `TASK-NNNN-描述.json` | `TASK-0001-设计数据库.json` |

## 4. 路径引用规范

项目内所有路径引用必须使用相对路径（相对于项目根目录）：

```markdown
<!-- 正确 -->
参见 [项目结构规范](rules/general/project-structure.md)

<!-- 错误 -->
参见 /Users/dev/project/rules/general/project-structure.md
```

## 5. 项目标识

本项目的唯一标识为 `v1.3.0`，在所有配置、日志、数据库记录中统一使用此标识。
