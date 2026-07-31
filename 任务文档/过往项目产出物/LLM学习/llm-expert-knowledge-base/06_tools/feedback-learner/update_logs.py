
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 设置日志目录
logs_dir = Path(__file__).parent.parent / "08_audit" / "learning_logs"

# 定义新的时间戳（最近7天）
new_dates = [
    datetime.now() - timedelta(days=6),
    datetime.now() - timedelta(days=5),
    datetime.now() - timedelta(days=4),
    datetime.now() - timedelta(days=3),
    datetime.now() - timedelta(days=1),
]

# 读取旧的日志文件
old_logs = []
for i in range(1, 6):
    log_file = logs_dir / f"2026-05-2{19+i}-conv_00{i}.json"
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            old_logs.append(json.load(f))

# 创建新的日志文件
for i, log_data in enumerate(old_logs):
    new_date = new_dates[i]
    new_timestamp = new_date.isoformat()
    new_date_str = new_date.strftime("%Y-%m-%d")
    
    # 修改时间戳
    log_data["timestamp"] = new_timestamp
    
    # 创建新文件名
    new_log_file = logs_dir / f"{new_date_str}-conv_00{i+1}_updated.json"
    
    # 保存新日志
    with open(new_log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已创建更新后的日志: {new_log_file.name}")

print("\n✅ 所有日志更新完成！")
