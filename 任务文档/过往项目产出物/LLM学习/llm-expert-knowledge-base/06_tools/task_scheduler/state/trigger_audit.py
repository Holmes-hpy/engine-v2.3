#!/usr/bin/env python3
import time
import subprocess
import sys
from pathlib import Path

wait_minutes = 30
pipeline_script = Path("/Users/houpengyuan/Documents/trae_projects/LLM学习/llm-expert-knowledge-base/06_tools/task_scheduler/pipeline.py")
python_exe = "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"

print(f"等待 {wait_minutes} 分钟...")
time.sleep(wait_minutes * 60)

print("开始执行知识审计...")
result = subprocess.run([python_exe, str(pipeline_script), "--full-audit"], capture_output=True, text=True)

if result.returncode == 0:
    print("知识审计执行成功")
else:
    print(f"知识审计执行失败: {result.stderr}")
