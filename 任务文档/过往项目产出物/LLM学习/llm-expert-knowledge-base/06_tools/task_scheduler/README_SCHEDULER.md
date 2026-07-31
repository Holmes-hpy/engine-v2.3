# 知识质量审计触发规则配置

## 概述

本系统为"知识质量审计"Skill 实现了以下触发规则：

1. **事件触发**：当"知识蒸馏"Skill 执行完成后，等待30分钟，自动执行"知识质量审计"
   - 如果"知识蒸馏"执行失败，则不执行"知识质量审计"
   
2. **定时触发**：每周日凌晨2:00 自动执行一次全面审计
   - 全面审计会扫描 `../03_ai_wiki/` 和 `../04_permanent/` 目录中的所有知识文档

3. **错误处理**：如果执行过程中出现错误，将错误信息保存到 `../08_audit/error.log` 文件，并通知用户审计失败

---

## 目录结构

```
task_scheduler/
├── config/
│   ├── pipeline_config.json
│   └── scheduler_config.json (自动生成)
├── src/
│   ├── pipeline.py          # 完整流程调度
│   └── scheduler_manager.py # 定时任务管理器
├── logs/
│   ├── pipeline.log
│   ├── scheduler_stdout.log
│   ├── scheduler_stderr.log
│   └── cron_audit.log
├── state/
│   ├── pipeline_state.json
│   └── trigger_audit.py (自动生成)
└── README_SCHEDULER.md
```

---

## 使用方法

### 1. 设置定时任务（每周日凌晨2:00全面审计）

在 macOS 上运行：

```bash
cd llm-expert-knowledge-base/06_tools/task_scheduler
python3 src/scheduler_manager.py --setup
```

会提示选择使用 launchd（推荐）或 cron。

在 Linux 上会自动使用 cron。

### 2. 查看定时任务状态

```bash
python3 src/scheduler_manager.py --status
```

### 3. 移除定时任务

```bash
python3 src/scheduler_manager.py --remove
```

### 4. 运行完整知识流水线

```bash
python3 src/pipeline.py --full-pipeline
```

### 5. 手动运行全面审计

```bash
python3 src/pipeline.py --full-audit
```

---

## 功能说明

### 事件触发：知识蒸馏 → 知识审计

当运行完整流水线时，系统会自动：
1. 执行信息雷达（可选）
2. 执行知识蒸馏
3. 如果蒸馏成功，设置30分钟后自动运行审计
4. 同时也会立即执行一次审计

如果知识蒸馏失败，系统会终止流程并不设置延迟审计。

### 定时触发：每周日凌晨2:00全面审计

定时任务会执行 `pipeline.py --full-audit`，该命令会：
- 扫描 `03_ai_wiki/` 目录
- 扫描 `04_permanent/` 目录
- 对所有文档执行六维质量评分
- 生成审计报告到 `08_audit/` 目录
- 按质量分类处理文档

### 错误处理

如果任何环节出错：
- 错误信息会记录到 `08_audit/error.log`
- 流程日志会记录到 `task_scheduler/logs/pipeline.log`
- Cron/launchd 日志会记录到各自的日志文件

---

## 配置说明

### scheduler_config.json

自动生成的配置文件：

```json
{
  "full_audit_schedule": {
    "day_of_week": "sun",
    "hour": 2,
    "minute": 0
  },
  "event_triggers": {
    "distillation_wait_minutes": 30
  }
}
```

---

## 注意事项

1. 确保 Python 解释器路径正确
2. 确保文件权限允许执行定时任务
3. 在 macOS 上，launchd 可能需要完整磁盘权限
4. 定时任务不会重复设置（运行 --setup 会检查是否已存在）

---

## 故障排查

### 查看任务状态

```bash
# macOS launchd
launchctl list | grep llm-knowledge

# Cron
crontab -l
```

### 查看日志

```bash
# 流程日志
cat logs/pipeline.log

# 审计错误日志
cat ../../08_audit/error.log
```

