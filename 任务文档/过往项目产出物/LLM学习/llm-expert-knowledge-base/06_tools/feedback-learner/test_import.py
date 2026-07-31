#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# 添加 src 目录到路径
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

print(f"Python path: {sys.path}")
print(f"src_dir exists: {src_dir.exists()}")
print(f"Files in src_dir: {list(src_dir.glob('*.py'))}")

try:
    from learning_logger import LearningLogger
    print("✅ 成功导入 LearningLogger")
    
    # 测试初始化
    config_path = src_dir.parent / "config" / "config.json"
    logger = LearningLogger(str(config_path))
    print("✅ 成功初始化 LearningLogger")
    
    # 测试生成报告
    report = logger.generate_weekly_report()
    print(f"✅ 报告生成成功！")
    print(f"   报告文件: {report['file']}")
    print(f"   对话总数: {report['conversation_count']}")
    print(f"   平均得分: {report['average_score']}")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
