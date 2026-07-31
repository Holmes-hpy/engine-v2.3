# 输出管理规范

> **项目**: v1.3.0 (v1.3.0)
> **输出根目录**: /Users/houpengyuan/Documents/trae_projects/临时使用/output/v1.3.0/output
> **生成时间**: 2026-07-16T07:00:00+08:00
> **启动包版本**: 1.3.0

## 1. 概述

本规则定义项目所有输出文件的管理规范，包括输出目录结构、文件命名、格式标准和生命周期管理。

## 2. 输出目录结构

```
/Users/houpengyuan/Documents/trae_projects/临时使用/output/v1.3.0/output/
├── deliverables/           # 最终交付物
│   └── README.md
├── drafts/                 # 草稿文件
│   └── README.md
├── archives/               # 归档文件
│   └── README.md
└── index.md                # 输出索引
```

## 3. 输出状态与任务状态映射

输出文件状态与任务状态（参见规则 T1）存在以下映射关系：

| 输出状态 | 对应任务状态 | 说明 |
|----------|-------------|------|
| draft | in_progress | 任务执行中，产出物为草稿 |
| review | reviewing | 任务评审中，产出物待审查 |
| final | completed | 任务已完成，产出物正式发布 |
| archived | archived | 任务已归档，产出物归档保存 |

**联动规则**：
- 任务状态变更时，自动更新相关输出文件的 `status` 字段
- 任务切换到 `archived` 时，对应输出文件自动移动到 `archives/`
- 任务从 `blocked` 恢复为 `in_progress` 时，对应输出文件保持 `draft` 状态

## 4. 文件命名规范

### 4.1 交付物命名

```
{项目标识}-{交付物类型}-{版本}-{日期}.{扩展名}
```

示例：
- `v1.3.0-design-doc-v1.0-20260715.md`
- `v1.3.0-api-spec-v0.5-20260715.yaml`

### 4.2 草稿命名

```
DRAFT-{交付物类型}-{序号}-{日期}.{扩展名}
```

示例：
- `DRAFT-design-doc-01-20260715.md`

### 4.3 归档命名

```
ARCHIVE-{原文件名}-{归档日期}.{扩展名}
```

## 5. 输出格式标准

### 5.1 Markdown 交付物

所有 Markdown 交付物必须包含以下头部：

```markdown
---
title: 文档标题
project: v1.3.0
type: 交付物类型
version: 1.0.0
created: YYYY-MM-DD
author: unknown
status: draft / review / final
---
```

### 5.2 JSON 交付物

所有 JSON 交付物必须包含以下元数据：

```json
{
  "_meta": {
    "project": "v1.3.0",
    "type": "交付物类型",
    "version": "1.0.0",
    "created": "YYYY-MM-DD"
  },
  "data": { }
}
```

## 6. 输出生命周期

```
草稿 (drafts/) → 评审 → 交付物 (deliverables/) → 归档 (archives/)
```

### 6.1 状态流转

| 状态 | 位置 | 说明 |
|------|------|------|
| draft | drafts/ | 初步生成，待完善 |
| review | drafts/ | 已完成，待评审 |
| final | deliverables/ | 已通过评审，正式发布 |
| archived | archives/ | 已过时，保留备查 |

### 6.2 自动归档规则

- 交付物更新后，旧版本自动移动到 archives/
- 草稿超过 30 天未更新，触发归档通知（写入 logs/ 并通知相关 agent）
- 归档通知发出 7 天后，如无确认延期，自动移动到 archives/
- 用户可在 `index.md` 中标记 `keep: true` 来跳过自动归档

**归档执行者**：由 T2 生命周期的**执行阶段中的监控子阶段**定期检查归档到期项（建议每小时一次）。

### 6.3 归档恢复机制

如需恢复已归档的文件：
1. 从 `archives/` 复制回 `deliverables/`
2. 在 `index.md` 中增加"恢复记录"章节
3. 恢复后状态更新为 `draft`（需重新评审）
4. 恢复操作记录到 `logs/lifecycle.log`

## 7. 敏感数据检查

所有输出文件在写入前必须通过敏感数据过滤（参见规则 G2）。

## 8. 索引维护

每次新增或更新输出文件后，必须更新 `/Users/houpengyuan/Documents/trae_projects/临时使用/output/v1.3.0/output/index.md`：

```markdown
# 输出索引

## 最新交付物
- [文档标题](deliverables/文件名) - 版本 v1.0.0 - 状态: final

## 进行中草稿
- [草稿标题](drafts/文件名) - 状态: draft

## 最近归档
- [归档标题](archives/文件名) - 归档日期: YYYY-MM-DD
```

**自动化**：可通过 `scripts/update-output-index.sh` 自动扫描 deliverables/ 目录并更新 index.md，建议每次任务完成时运行。
