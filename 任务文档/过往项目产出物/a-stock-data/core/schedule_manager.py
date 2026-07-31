#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度管理模块
管理自主学习系统的定时任务
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

def create_schedule_config():
    """创建定时任务配置文件"""
    config_file = PROJECT_DIR / "schedule_config.json"
    
    config = {
        "tasks": [
            {
                "name": "每日学习-收盘后",
                "description": "收盘后学习并生成每日简报",
                "cron": "30 15 * * 1-5",
                "function": "autonomous_learning_system.AutonomousLearningSystem.run_daily_learning_cycle",
                "enabled": True
            },
            {
                "name": "科技资讯爬取-上午",
                "description": "每日上午9:30爬取科技前沿资讯，关注十五五规划相关产业",
                "cron": "30 9 * * 1-5",
                "function": "tech_news_crawler.TechNewsCrawler.run_crawl",
                "enabled": True
            },
            {
                "name": "科技资讯爬取-下午",
                "description": "每日下午14:30爬取科技前沿资讯，关注十五五规划相关产业",
                "cron": "30 14 * * 1-5",
                "function": "tech_news_crawler.TechNewsCrawler.run_crawl",
                "enabled": True
            },
            {
                "name": "每周深度学习",
                "description": "每周日进行深度学习并生成周度报告",
                "cron": "0 20 * * 0",
                "function": "autonomous_learning_system.AutonomousLearningSystem.weekly_deep_learning",
                "enabled": True
            },
            {
                "name": "月度进化报告",
                "description": "每月最后一天生成进化报告",
                "cron": "0 20 L * *",
                "function": "autonomous_learning_system.AutonomousLearningSystem.monthly_evolution_report",
                "enabled": True
            }
        ],
        "created_at": datetime.now().isoformat(),
        "version": "1.1"
    }
    
    import json
    config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2))
    print(f"✓ 配置文件创建: {config_file}")
    return config_file

def show_schedule():
    """显示定时任务列表"""
    print("=" * 70)
    print("⏰ 定时任务配置")
    print("=" * 70)
    print()
    
    config_file = PROJECT_DIR / "schedule_config.json"
    
    if config_file.exists():
        import json
        config = json.loads(config_file.read_text())
        
        print(f"配置版本: {config.get('version', '1.0')}")
        print(f"创建时间: {config.get('created_at', '')}")
        print()
        print("-" * 70)
        print("任务列表:")
        print("-" * 70)
        
        for i, task in enumerate(config.get('tasks', []), 1):
            status = "✅ 启用" if task.get('enabled', True) else "❌ 禁用"
            print(f"{i}. {task['name']}")
            print(f"   描述: {task['description']}")
            print(f"   时间: {task['cron']}")
            print(f"   状态: {status}")
            print()
    else:
        print("未找到配置文件，正在创建...")
        create_schedule_config()
        show_schedule()

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自主学习系统 - 定时任务管理")
    parser.add_argument('command', choices=['init', 'show', 'test'], 
                       help="命令: init=初始化, show=显示任务, test=测试")
    parser.add_argument('--now', action='store_true', 
                       help="立即测试每日学习流程")
    
    args = parser.parse_args()
    
    if args.command == 'init':
        print("🚀 初始化定时任务配置...")
        create_schedule_config()
        print()
        show_schedule()
    
    elif args.command == 'show':
        show_schedule()
    
    elif args.command == 'test':
        print("🧪 测试自主学习系统...")
        print()
        
        from autonomous_learning_system import AutonomousLearningSystem
        
        system = AutonomousLearningSystem()
        
        if args.now:
            print("⏰ 立即运行每日学习流程...")
            print()
            system.run_daily_learning_cycle()
        else:
            print("📋 可用测试命令:")
            print("   python schedule_manager.py test --now  (立即运行每日学习)")
            print("   python autonomous_learning_system.py     (运行完整流程)")
            print()
            show_schedule()

if __name__ == '__main__':
    main()
