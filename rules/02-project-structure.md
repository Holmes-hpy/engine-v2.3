# 项目结构与命名规则

> **版本**: v2.3.0
> **优先级**: P2
> **说明**: 本文件定义项目的目录结构、命名规范和路径引用规则。所有文件和目录操作必须遵守本文件。

---

## 1. 完整目录结构

v2.3.0 项目初始化后的标准目录结构：

```
{项目根目录}/
├── README.md                        # 项目说明
├── .gitignore                       # Git忽略规则
├── .bootstrap-complete              # 初始化完成标记（自动生成）
├── 项目使用指南.md                   # [NEW] 项目级使用指南（LLM必读）
│
├── rules/                           # 规则体系（核心）
│   ├── 00-meta.md                   # 元规则
│   ├── 01-llm-behavior.md           # LLM行为约束
│   ├── 02-project-structure.md      # 本文件
│   ├── 03-task-execution.md         # 任务执行流程
│   ├── 04-knowledge.md              # 知识管理与沉淀
│   ├── 05-output.md                 # 产出物管理
│   ├── _registry.yaml               # 规则注册表
│   └── README.md
│
├── 任务文档/                         # [NEW] 任务工作区（核心）
│   ├── _template/                   # 任务文件夹模板
│   │   ├── 任务启动清单.md
│   │   ├── 对话记录.md
│   │   ├── 沉淀日志.md
│   │   ├── 产出物/
│   │   │   └── .gitkeep
│   │   └── .meta/
│   │       ├── task-state.json
│   │       └── versions.yaml
│   ├── _archive/                    # 已归档任务（超过90天）
│   │   └── .gitkeep
│   ├── _index.md                    # 任务索引（自动生成）
│   └── {YYYYMMDD}-{任务主题}/        # 每个任务一个文件夹
│       ├── 任务启动清单.md
│       ├── 任务描述.md
│       ├── 对话记录.md              # 结构化摘要
│       ├── 沉淀日志.md
│       ├── 交接报告.md
│       ├── 产出物/
│       │   ├── v{major}.{minor}-{YYYYMMDD}-{描述}.md
│       │   └── .versions/
│       │       └── manifest.yaml
│       └── .meta/
│           ├── task-state.json
│           ├── versions.yaml
│           └── session-log.yaml
│
├── 捡破烂/                           # [NEW] 原始对话档案与挖掘区
│   ├── _buffer/                     # 挖掘缓冲区（待审查的挖掘报告）
│   │   └── .gitkeep
│   ├── _archive/                    # 超过4周的原始对话归档
│   │   └── .gitkeep
│   ├── _mining-reports/             # 已审查通过的挖掘报告
│   │   └── .gitkeep
│   └── {YYYYMMDD}-{任务主题}/        # 与任务文档同名的原始对话
│       ├── .meta.yaml               # 任务元数据
│       ├── round-01.md              # 第一轮（原始完整对话）
│       ├── round-02.md              # 第二轮
│       └── ...
│
├── memory/                          # 认知闭环 - Markdown存储
│   ├── sessions/                    # 会话归档（提炼后）
│   ├── episodes/                    # 情景记忆
│   ├── facts/                       # 原子事实
│   ├── profiles/                    # Agent/用户画像
│   ├── principles/                  # 原则
│   ├── patterns/                    # 模式
│   ├── decisions/                   # 决策记录
│   ├── index/                       # 索引文件
│   └── _schema.sql
│
├── .memory/                         # 认知闭环 - SQLite数据库
│   └── knowledge.db                 # 本地知识库（零API依赖，FTS5）
│
├── expert-library/                  # 专家库
│   ├── agency-agents-zh/            # 通用领域专家（251位）
│   ├── financial-services/          # 金融服务专家（10 Agent + 55技能模板）
│   ├── agency-orchestrator/         # 工作流模板专家（51个）
│   └── README.md
│
├── 产出物/                           # [已废弃 v2.3.0] 产出物统一在任务文档/{任务}/产出物/
│
├── tasks/                           # 任务状态存储（JSON）
│   ├── active/                      # 进行中任务
│   ├── completed/                   # 已完成任务
│   ├── checkpoints/                 # 检查点
│   ├── state-machine-config.json
│   ├── lifecycle.log
│   └── state-change.log
│
├── docs/                            # 项目文档
│   └── decisions/                   # 架构决策记录(ADR)
│
├── scripts/                         # 自动化脚本
│   ├── health_check.py
│   ├── init_memory.py
│   ├── validate_rules.py
│   ├── sensitive_scan.py
│   └── archive_expired.py
│
├── logs/                            # 运行日志
│   ├── bootstrap/
│   ├── cognitive/                   # 认知沉淀日志
│   ├── sensitive-filter.log
│   ├── fault-recovery.log
│   └── timeout/
│
├── agents/                          # Agent配置
│   ├── README.md
│   └── _index.yaml
│
├── .meta/                           # 项目元数据
│   ├── bootstrap-state.json
│   └── task-registry.yaml
│
└── cognitive-closure/               # 认知闭环Schema
    ├── schema/
    │   ├── 01-core-schema.sql
    │   ├── 02-fts5-config.sql
    │   └── 03-seed-data.sql
    └── curator-agent-prompt.md
```

> **路径基准点**：本规则中所有相对路径，基准点为项目根目录（即 `.memory/` 所在目录）。

---

## 2. 目录管理规则

### 2.1 禁止修改结构的目录

以下目录由启动包自动生成，非必要不得手动修改结构：
- `rules/` — 规则体系完整性依赖固定结构
- `.memory/` — 认知闭环数据库位置固定
- `tasks/` — 任务状态存储结构依赖状态机定义
- `expert-library/` — 专家库结构固定
- `cognitive-closure/` — Schema文件位置固定
- `捡破烂/_buffer/`、`捡破烂/_archive/`、`捡破烂/_mining-reports/` — 挖掘工作区结构固定

### 2.2 允许扩展的目录

以下目录鼓励根据项目需求扩展：
- `docs/decisions/` — 添加新的ADR文件
- `memory/` — 添加新的知识条目
- `任务文档/` — 创建新的任务文件夹（产出物自动在任务目录下）
- `logs/` — 添加新的日志分类子目录
- `任务文档/` — 创建新的任务文件夹

### 2.3 用户自定义目录

用户可在项目根目录下创建自定义目录（如 `src/`、`tests/`、`data/` 等），规则不限制项目特定目录的创建。

---

## 3. 命名规范

### 3.1 通用命名规则

- 文件和目录名使用中文或英文，禁止使用空格（空格替换为 `-`）
- 中文目录/文件名可以正常使用
- 避免特殊字符：`/ \ : * ? " < > |`

### 3.2 任务文件夹命名

```
任务文档/{YYYYMMDD}-{任务主题}/
捡破烂/{YYYYMMDD}-{任务主题}/
```

- 日期格式：`YYYYMMDD`（如 `20260718`）
- 任务主题：2-20个字符，允许中文、英文、数字、连字符、下划线
- 同一天内不允许重复主题（重复时自动追加序号 `-01`、`-02`）

### 3.3 捡破烂轮次文件命名

```
round-{NN}.md
```

- 使用阿拉伯数字两位数编号（01、02、03...99）
- 超过99轮时使用三位数（100、101...）
- 文件内部标题使用中文"第N轮对话"
- 文件排序天然正确（01 < 02 < ... < 10 < 11）

### 3.4 产出物命名

详见 `05-output.md` 中的版本管理规则。基本格式：
```
v{major}.{minor}-{YYYYMMDD}-{描述}.{ext}
```

### 3.5 任务ID命名

```
TASK-{NNNN}
```

- 4位数字序列，从0001开始递增
- 全局唯一，不复用

### 3.6 用户自定义命名规则 [场景: Agent/Skill创建]

当用户为项目定义了特定的命名前缀或格式要求时（如 `howe-` 前缀），相关命名必须遵守。具体规则由用户在项目中通过追加规则或直接指令定义。

### 3.7 Skill文件命名规范 [场景: Skill创建]

- 每个Skill是一个独立文件夹，文件夹名称即为Skill名称
- Skill文件夹内的主文件名必须为 `SKILL.md`（全大写）
- 禁止使用 `skill.md`、`Skill.md` 等其他大小写形式

---

## 4. 路径引用规范

项目内所有路径引用必须使用相对路径（相对于项目根目录）：

```markdown
<!-- 正确 -->
参见 [项目结构规范](rules/02-project-structure.md)

<!-- 错误 -->
参见 /Users/dev/project/rules/02-project-structure.md
```

在规则文件中引用其他规则时，使用 `[L{N}: {章节号}]` 格式（详见 `00-meta.md` 4.3节）。

---

## 5. 目录初始化时机

| 目录 | 创建时机 | 创建者 |
|------|----------|--------|
| 所有标准目录（rules/、memory/、tasks/等） | 项目初始化（bootstrap） | 初始化Agent |
| `任务文档/{任务}/` | 第一次任务对话结束后 | 任务初始化Agent |
| `捡破烂/{任务}/` | 第一次任务对话结束后（与任务文档同步创建） | LLM自动 |
| `捡破烂/{任务}/round-NN.md` | 每轮对话结束后 | LLM自动 |
| `捡破烂/_buffer/` | 项目初始化时 | 初始化Agent |
| `memory/{principles,patterns,decisions}/` | 项目初始化时 | 初始化Agent |

---

## 6. 隐藏文件与元数据

### 6.1 允许的隐藏文件/目录

| 路径 | 用途 |
|------|------|
| `.memory/` | SQLite数据库目录 |
| `.meta/` | 项目元数据目录 |
| `.gitignore` | Git忽略规则 |
| `.bootstrap-complete` | 初始化完成标记 |
| `.gitkeep` | Git保留空目录的占位文件 |

### 6.2 任务文件夹内的.meta/

每个任务文件夹下的 `.meta/` 目录存放任务元数据：
- `task-state.json`：任务状态快照
- `versions.yaml`：产出物版本清单
- `session-log.yaml`：会话日志（可选）

### 6.3 捡破烂文件夹内的.meta.yaml

每个捡破烂任务文件夹根目录放 `.meta.yaml`（不是目录，是文件），记录任务元数据，用于周度扫描时快速识别。
