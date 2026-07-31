# 任务状态机规范

> **项目**: v1.3.0 (v1.3.0)
> **生成时间**: 2026-07-16T07:00:00+08:00
> **启动包版本**: 1.3.0

## 1. 概述

本规则定义项目中任务的状态定义、状态流转规则和并发控制策略。所有任务必须遵循本状态机进行管理。

## 2. 状态定义

### 2.1 核心状态

| 状态 | 代号 | 说明 |
|------|------|------|
| pending | 待处理 | 任务已创建，等待执行 |
| in_progress | 进行中 | 任务正在执行 |
| completed | 已完成 | 任务成功完成 |
| failed | 失败 | 任务执行失败 |
| blocked | 阻塞 | 任务因依赖未满足而暂停 |

### 2.2 扩展状态

| 状态 | 代号 | 说明 |
|------|------|------|
| reviewing | 评审中 | 任务产物待评审 |
| handoff_incomplete | 交接不完整 | 任务完成但交接报告缺失 |
| archived | 已归档 | 任务已归档，不再活跃 |

## 3. 状态流转图

```
                        ┌─────────────┐
             ┌─────────►│   pending   │◄──────────┐
             │          └──────┬──────┘           │
             │                 │ start            │ retry
             │                 ▼                  │
             │          ┌─────────────┐           │
             │    block │  in_progress│           │
             │◄─────────┤             ├─────┐     │
             │          └──────┬──────┘     │     │
             │                 │            │     │
             │          submit │        fail │     │
             │                 ▼            │     │
             │          ┌───────────┐        │     │
             │          │ reviewing │◄───┐   │     │
             │          └─────┬─────┘    │   │     │
             │         pass  │ reject    │   │     │
             │               │       ┌───┘   │     │
             │               ▼       ▼       │     │
        ┌────┴────┐    ┌─────────┐  ┌───────┴──┐   │
        │ blocked │    │completed│  │  failed  │───┘
        └────┬────┘    └────┬────┘  └──────────┘
             │              │
             │        ┌─────┴──────────┐
             │        │                │
             │   archive│  handoff_fail │
             │        ▼                ▼
             │   ┌──────────┐  ┌──────────────────────┐
             │   │ archived │  │ handoff_incomplete    │
             │   └──────────┘  └──────────┬───────────┘
             │                            │ fix
             │                            ▼
             │                     ┌─────────┐
             └─────────────────────│completed│
                                   └─────────┘
```

### 3.1 合法流转

| 从状态 | 到状态 | 触发条件 |
|--------|--------|----------|
| pending | in_progress | 任务开始执行 |
| pending | blocked | 依赖任务未完成 |
| in_progress | reviewing | 任务完成，提交评审 |
| in_progress | failed | 任务执行出错 |
| in_progress | blocked | 执行中发现新依赖 |
| reviewing | completed | 评审通过 |
| reviewing | in_progress | 评审不通过，返回修改 |
| reviewing | failed | 评审发现严重问题 |
| blocked | in_progress | 依赖已满足 |
| failed | pending | 重置任务，准备重试 |
| completed | archived | 任务归档 |
| completed | handoff_incomplete | 交接报告缺失 |
| handoff_incomplete | completed | 补充交接报告 |

### 3.2 非法流转

以下状态流转被禁止：

| 从状态 | 到状态 | 原因 |
|--------|--------|------|
| completed | failed | 已完成任务不应回退 |
| archived | * | 已归档任务不可变更 |
| failed | completed | 必须先经过 pending |

## 4. 并发控制

### 4.1 最大活跃任务数

```
MAX_ACTIVE_TASKS = 10
```

默认值为 10。当活跃任务数达到上限时，新任务自动进入 `blocked` 状态，等待资源。

### 4.2 任务优先级

| 优先级 | 数值 | 说明 |
|--------|------|------|
| critical | 1 | 阻塞其他任务的关键路径任务 |
| high | 2 | 重要任务 |
| normal | 3 | 普通任务（默认） |
| low | 4 | 可延后处理的任务 |

### 4.3 资源分配策略

当活跃任务数达到上限时，按以下策略分配：

1. 高优先级任务优先获得执行权
2. 同优先级任务按创建时间 FIFO
3. 被抢占的低优先级任务转为 `blocked` 状态

## 5. 状态持久化

### 5.1 存储位置

```
tasks/active/     — 存储 in_progress, blocked 状态的任务
tasks/reviewing/  — 存储 reviewing 状态的任务
tasks/handoff/    — 存储 handoff_incomplete 状态的任务
tasks/completed/  — 存储 completed, failed, archived 状态的任务
```

### 5.2 文件格式

```json
{
  "task_id": "TASK-0001",
  "title": "任务标题",
  "status": "in_progress",
  "priority": "normal",
  "version": 1,
  "retry_count": 0,
  "max_retry_count": 3,
  "review_result": null,
  "review_comment": null,
  "output_status": null,
  "checkpoint_count": 0,
  "in_progress_seconds": 0,
  "max_execution_seconds": 604800,
  "created_at": "2026-07-15T10:00:00Z",
  "started_at": "2026-07-15T10:05:00Z",
  "completed_at": null,
  "assigned_agent": "agent-id",
  "parent_task": null,
  "subtasks": [],
  "dependencies": [],
  "outputs": [],
  "transitions": [
    {"from": "pending", "to": "in_progress", "at": "2026-07-15T10:05:00Z"}
  ]
}
```

### 5.3 output_status 更新规则

任务 JSON 中的 `output_status` 字段与输出文件的 `status` 保持同步更新（参见规则 O1 第 3 节映射表）。更新方向为：**任务状态变更 → 同时更新任务 JSON 的 `output_status` 和输出文件的 `status`**。

## 6. 状态变更日志

每次状态变更记录到 `tasks/state-change.log`：

```
[2026-07-15 10:05:00] TASK-0001: pending → in_progress (by: agent-id)
[2026-07-15 10:30:00] TASK-0001: in_progress → completed (by: agent-id)
```

## 7. 并发一致性保证

### 7.1 乐观锁机制

状态持久化 JSON 中的 `version` 字段作为乐观锁版本号。每次状态变更时：
1. 读取当前任务的 `version`
2. 执行状态变更逻辑
3. 写入时检查 `version` 是否与读取时一致
4. 如一致 → 更新状态并将 `version + 1`
5. 如不一致 → 拒绝变更，返回冲突错误

**原子写入保障**：状态变更写入时，建议使用"写入临时文件 + 重命名"模式确保原子性：
1. 将更新后的 JSON 写入 `tasks/active/{TASK_ID}.tmp`
2. 验证临时文件格式正确
3. 原子重命名：`{TASK_ID}.tmp` → `{TASK_ID}.json`

### 7.2 冲突处理流程

当检测到并发冲突时：
1. 回滚当前操作
2. 记录冲突日志到 `tasks/state-change.log`：`[CONFLICT] TASK-NNNN: 并发冲突，version 不一致`
3. 等待 3 秒后自动重试
4. 如连续 3 次冲突，标记任务为 `blocked` 并通知用户
