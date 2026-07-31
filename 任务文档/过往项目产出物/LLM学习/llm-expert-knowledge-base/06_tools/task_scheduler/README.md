
# 任务调度器

协调大模型信息雷达和知识蒸馏的执行。

## 功能

- 按顺序执行大模型信息雷达和知识蒸馏
- 在两个任务间等待15分钟
- 如果雷达失败时跳过知识蒸馏
- 记录执行状态和日志

## 使用方法

### 单次执行

```bash
cd task_scheduler
python src/pipeline.py
```

### 设置定时任务（使用 crontab（macOS/Linux）

```bash
crontab -e
```

添加以下内容（例如每天早上9点执行）：

```
0 9 * * * cd /path/to/task_scheduler && python src/pipeline.py >> logs/cron.log 2>&1
```

## 事件触发规则

1. 执行大模型信息雷达
2. **成功 → 等待15分钟
3. 执行知识蒸馏
4. **失败 → 跳过知识蒸馏

## 目录结构

```
task_scheduler/
├── config/
│   └── pipeline_config.json  # 配置文件
├── logs/                   # 日志目录
├── state/                  # 状态文件目录
├── src/
│   └── pipeline.py       # 主程序
└── README.md
```

## 配置说明

编辑 `config/pipeline_config.json`:

```json
{
  "radar_wait_minutes": 15,        // 雷达执行后等待时间
  "radar_script": "src/main.py",     // 雷达脚本路径
  "distiller_script": "src/main.py", // 蒸馏脚本路径
  "python_command": "python3"      // Python命令
}
```

## 状态文件

程序会在 `state/pipeline_state.json` 中记录执行状态：

```json
{
  "last_radar_run": "2024-01-01T09:00:00",
  "last_radar_success": true,
  "last_distiller_run": "2024-01-01T09:15:00",
  "last_distiller_success": true
}
```

## 输出日志

运行日志保存在:
- `logs/task_scheduler-YYYYMMDD.log`

