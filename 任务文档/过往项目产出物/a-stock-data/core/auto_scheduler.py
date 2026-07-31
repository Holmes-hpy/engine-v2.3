#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化定时任务调度系统 - 完整版
支持配置文件管理多个定时任务
包括：
- 每日上午9:30: 科技前沿资讯分析
- 每日下午14:30: 科技前沿资讯分析
- 收盘后学习等
"""

import sys
import os
import json
import importlib
from pathlib import Path
from datetime import datetime
import time

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

def check_dependencies():
    """检查并安装必要的依赖"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        print("✓ APScheduler 已安装")
        return True
    except ImportError:
        print("⚠️  正在安装 APScheduler...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "apscheduler"])
            print("✓ APScheduler 安装成功")
            return True
        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False

def load_config():
    """加载调度配置"""
    config_file = PROJECT_DIR / "schedule_config.json"
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        return None
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

def get_function_from_path(function_path):
    """从路径字符串获取函数对象"""
    try:
        # 处理类似 "module.Class.method" 的路径
        parts = function_path.split('.')

        # 遍历所有可能的模块-分割点
        for i in range(1, len(parts) + 1):
            module_name = '.'.join(parts[:i])
            try:
                module = importlib.import_module(module_name)
                remaining = parts[i:]

                # 如果没有剩余部分，就是模块本身（不太可能是可调用的）
                if not remaining:
                    continue

                obj = module
                for part in remaining:
                    obj = getattr(obj, part)

                # 判断结果类型
                if callable(obj):
                    # 如果是类，实例化并返回run方法
                    if isinstance(obj, type):
                        instance = obj()
                        if hasattr(instance, 'run') and callable(getattr(instance, 'run')):
                            return instance.run
                        return instance
                    # 如果已是方法/函数，直接返回
                    return obj
            except (ImportError, AttributeError):
                continue

        # 兜底：尝试直接以 "模块.类" 的形式处理
        last_parts = function_path.rsplit('.', 2)
        if len(last_parts) >= 2:
            # 尝试 module.Class 形式
            module_name = '.'.join(last_parts[:-1])
            class_name = last_parts[-1]
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                if isinstance(cls, type):
                    instance = cls()
                    if hasattr(instance, 'run'):
                        return instance.run
            except (ImportError, AttributeError):
                pass

        raise ImportError(f"无法加载: {function_path}")

    except Exception as e:
        print(f"❌ 加载函数失败 {function_path}: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_task(task_name, function_path):
    """执行单个任务"""
    print("\n" + "="*80)
    print(f"🚀 定时任务触发 - {task_name}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    try:
        # 特殊处理常见任务
        if 'daily_tech_intel_system_v7' in function_path:
            from daily_tech_intel_system_v7 import DailyTechIntelSystemV7
            system = DailyTechIntelSystemV7()
            system.run()
            print("\n✅ 任务执行完成!")
            return

        if 'daily_tech_intel_system_v6' in function_path:
            from daily_tech_intel_system_v6 import DailyTechIntelSystemV6
            system = DailyTechIntelSystemV6()
            system.run()
            print("\n✅ 任务执行完成!")
            return

        if 'daily_tech_intel_system_v2' in function_path:
            from daily_tech_intel_system_v2 import DailyTechIntelSystemV2
            system = DailyTechIntelSystemV2()
            system.run()
            print("\n✅ 任务执行完成!")
            return

        if 'tech_news_crawler' in function_path:
            from tech_news_crawler import TechNewsCrawler
            crawler = TechNewsCrawler()
            crawler.run_crawl()
            print("\n✅ 任务执行完成!")
            return

        if 'autonomous_learning_system' in function_path:
            from autonomous_learning_system import AutonomousLearningSystem
            system = AutonomousLearningSystem()
            if 'run_daily_learning_cycle' in function_path:
                system.run_daily_learning_cycle()
            elif 'weekly_deep_learning' in function_path:
                system.weekly_deep_learning()
            elif 'monthly_evolution_report' in function_path:
                system.monthly_evolution_report()
            print("\n✅ 任务执行完成!")
            return

        # 通用处理
        func = get_function_from_path(function_path)
        if func:
            func()
            print("\n✅ 任务执行完成!")
        else:
            print(f"❌ 无法加载任务函数: {function_path}")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

def start_scheduler():
    """启动定时任务调度器"""
    print("⏰ 自动化定时任务调度系统启动")
    print("="*80)
    
    if not check_dependencies():
        print("❌ 依赖检查失败，请手动安装: pip install apscheduler")
        return
    
    config = load_config()
    if not config:
        return
    
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler()
    
    # 添加所有启用的任务
    tasks = config.get('tasks', [])
    added_count = 0

    for task in tasks:
        if not task.get('enabled', True):
            continue

        # 解析cron表达式
        cron_parts = task['cron'].split()
        if len(cron_parts) != 5:
            print(f"⚠️  跳过无效cron表达式: {task['name']} - {task['cron']}")
            continue

        minute, hour, day, month, day_of_week = cron_parts

        # 创建任务包装函数（使用默认参数正确捕获循环变量）
        task_name = task['name']
        func_path = task['function']

        def task_wrapper(tn=task_name, fp=func_path):
            run_task(tn, fp)

        # 构建cron参数（处理特殊值如'L'表示每月最后一天）
        cron_kwargs = {}
        if minute != '*':
            cron_kwargs['minute'] = int(minute)
        if hour != '*':
            cron_kwargs['hour'] = int(hour)
        if day != '*':
            if day == 'L':
                cron_kwargs['day'] = 'last'
            else:
                try:
                    cron_kwargs['day'] = int(day)
                except ValueError:
                    pass
        if month != '*':
            try:
                cron_kwargs['month'] = int(month)
            except ValueError:
                pass
        if day_of_week != '*':
            cron_kwargs['day_of_week'] = day_of_week

        try:
            scheduler.add_job(
                task_wrapper,
                trigger=CronTrigger(**cron_kwargs),
                id=task_name.replace(' ', '_'),
                name=task_name,
                replace_existing=True
            )
            added_count += 1
        except Exception as e:
            print(f"⚠️  任务 {task_name} 添加失败: {e}")
    
    if added_count == 0:
        print("❌ 没有启用的任务")
        return
    
    # 启动调度器
    scheduler.start()
    
    print("\n✅ 定时任务已配置:")
    print("-" * 80)
    for task in tasks:
        if task.get('enabled', True):
            status = "✅"
        else:
            status = "❌"
        print(f"   {status} {task['name']}")
        print(f"      时间: {task['cron']}")
        print(f"      描述: {task['description']}")
    
    print("\n💡 提示: 此程序将持续运行，按 Ctrl+C 停止\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止调度器...")
        scheduler.shutdown()
        print("✅ 调度器已停止")

def run_now():
    """立即执行一次科技前沿资讯分析任务（用于测试）"""
    print("🧪 立即执行一次科技前沿资讯分析任务...")
    run_task("科技资讯分析-测试", "daily_tech_intel_system_v7.DailyTechIntelSystemV7.run")


def show_help():
    """显示帮助信息"""
    print("""
科技前沿资讯自动化调度系统

用法:
    python auto_scheduler.py [命令]

命令:
    start    - 启动定时任务调度器（持续运行）
    now      - 立即执行一次科技资讯分析任务（测试用）
    help     - 显示此帮助信息

示例:
    python auto_scheduler.py start    # 启动定时调度
    python auto_scheduler.py now      # 立即执行一次测试

配置文件:
    schedule_config.json - 包含所有定时任务配置（上午9:30、下午14:30执行）
""")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_scheduler()
    elif command == 'now':
        run_now()
    else:
        show_help()

if __name__ == '__main__':
    main()
