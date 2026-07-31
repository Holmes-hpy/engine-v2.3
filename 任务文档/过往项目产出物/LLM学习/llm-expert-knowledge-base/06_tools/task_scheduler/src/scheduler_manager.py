#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
定时任务管理器
用于管理知识质量审计的定时触发和事件触发
"""

import json
import os
import sys
import subprocess
import time
import traceback
from datetime import datetime
from pathlib import Path
import platform


class SchedulerManager:
    """定时任务管理器"""
    
    def __init__(self, config_path="config/scheduler_config.json"):
        self.base_path = Path(__file__).parent.parent
        self.config_path = self.base_path / config_path
        self.config = self.load_config()
        self.audit_script = self.base_path / "../knowledge-auditor/src/main.py"
        self.pipeline_script = self.base_path / "pipeline.py"
        
    def load_config(self):
        """加载配置"""
        default_config = {
            "full_audit_schedule": {
                "day_of_week": "sun",  # 周日
                "hour": 2,
                "minute": 0
            },
            "event_triggers": {
                "distillation_wait_minutes": 30
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败，使用默认配置: {e}")
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def is_macos(self):
        """判断是否为macOS系统"""
        return platform.system() == "Darwin"
    
    def get_cron_expression(self):
        """生成cron表达式 (每周日凌晨2:00)"""
        # cron格式: 分 时 日 月 周
        return "0 2 * * 0"
    
    def get_launchd_plist(self):
        """生成macOS launchd plist配置"""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llm-knowledge.full_audit</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{str(self.pipeline_script.absolute())}</string>
        <string>--full-audit</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{str(self.base_path / "logs" / "scheduler_stdout.log")}</string>
    <key>StandardErrorPath</key>
    <string>{str(self.base_path / "logs" / "scheduler_stderr.log")}</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>"""
        return plist_content
    
    def setup_macos_launchd(self):
        """设置macOS launchd定时任务"""
        print("设置 macOS launchd 定时任务...")
        
        plist_dir = Path.home() / "Library" / "LaunchAgents"
        plist_dir.mkdir(parents=True, exist_ok=True)
        
        plist_path = plist_dir / "com.llm-knowledge.full_audit.plist"
        plist_content = self.get_launchd_plist()
        
        plist_path.write_text(plist_content, encoding="utf-8")
        print(f"✓ 已创建 plist 文件: {plist_path}")
        
        # 加载任务
        try:
            subprocess.run(["launchctl", "unload", str(plist_path)], 
                         capture_output=True, text=True)
            result = subprocess.run(["launchctl", "load", "-w", str(plist_path)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ launchd 任务已加载")
                return True
            else:
                print(f"⚠️ launchd 加载警告: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 设置 launchd 失败: {e}")
            return False
    
    def setup_cron(self):
        """设置cron定时任务 (Linux/macOS)"""
        print("设置 cron 定时任务...")
        
        cron_expr = self.get_cron_expression()
        python_path = sys.executable
        script_path = str(self.pipeline_script.absolute())
        log_path = str(self.base_path / "logs" / "cron_audit.log")
        
        cron_job = f'{cron_expr} {python_path} {script_path} --full-audit >> {log_path} 2>&1'
        
        # 获取当前cron
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
        except:
            current_cron = ""
        
        # 检查是否已存在
        if "full-audit" in current_cron:
            print("⚠️ 定时任务已存在")
            return True
        
        # 添加新任务
        new_cron = current_cron + "\n" + cron_job + "\n" if current_cron else cron_job + "\n"
        
        try:
            subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
            print("✓ Cron 任务已添加")
            return True
        except Exception as e:
            print(f"❌ 设置 cron 失败: {e}")
            return False
    
    def setup_schedule(self):
        """设置定时任务"""
        print("=" * 60)
        print("📅 设置定时任务")
        print("=" * 60)
        
        # 确保日志目录存在
        (self.base_path / "logs").mkdir(exist_ok=True)
        
        success = False
        
        if self.is_macos():
            print("\n检测到 macOS 系统")
            print("\n选择定时任务方式:")
            print("1. 使用 launchd (推荐)")
            print("2. 使用 cron")
            
            choice = input("\n请选择 (1/2，默认为1): ").strip()
            
            if choice == "2":
                success = self.setup_cron()
            else:
                success = self.setup_macos_launchd()
        else:
            success = self.setup_cron()
        
        if success:
            print("\n✓ 定时任务设置完成！")
            print("  - 每周日凌晨 2:00 自动执行全面审计")
        else:
            print("\n⚠️ 定时任务设置失败，请手动配置")
        
        return success
    
    def remove_schedule(self):
        """移除定时任务"""
        print("=" * 60)
        print("🗑️  移除定时任务")
        print("=" * 60)
        
        if self.is_macos():
            # 移除 launchd
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.llm-knowledge.full_audit.plist"
            if plist_path.exists():
                try:
                    subprocess.run(["launchctl", "unload", str(plist_path)], 
                                 capture_output=True, text=True)
                    plist_path.unlink()
                    print("✓ 已移除 launchd 任务")
                except Exception as e:
                    print(f"⚠️ 移除 launchd 任务失败: {e}")
        
        # 移除 cron 任务
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                current_cron = result.stdout
                new_cron = "\n".join([line for line in current_cron.split("\n") 
                                     if "full-audit" not in line])
                
                if new_cron != current_cron:
                    subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
                    print("✓ 已移除 cron 任务")
        except:
            pass
        
        print("定时任务已移除")
    
    def show_schedule_status(self):
        """显示定时任务状态"""
        print("=" * 60)
        print("📋 定时任务状态")
        print("=" * 60)
        
        if self.is_macos():
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.llm-knowledge.full_audit.plist"
            if plist_path.exists():
                print("✓ launchd 任务: 已配置")
                try:
                    result = subprocess.run(["launchctl", "list", "com.llm-knowledge.full_audit"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and "com.llm-knowledge.full_audit" in result.stdout:
                        print("✓ launchd 任务: 已加载")
                    else:
                        print("⚠️ launchd 任务: 未加载")
                except:
                    pass
            else:
                print("✗ launchd 任务: 未配置")
        
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                if "full-audit" in result.stdout:
                    print("✓ cron 任务: 已配置")
                    print("\nCron 配置:")
                    for line in result.stdout.split("\n"):
                        if "full-audit" in line:
                            print(f"  {line.strip()}")
                else:
                    print("✗ cron 任务: 未配置")
        except:
            print("✗ cron 任务: 未配置")
        
        print("\n下次全面审计: 每周日凌晨 2:00")
    
    def trigger_audit_after_distillation(self, wait_minutes=None):
        """知识蒸馏完成后，等待指定时间触发审计"""
        if wait_minutes is None:
            wait_minutes = self.config["event_triggers"]["distillation_wait_minutes"]
        
        print("=" * 60)
        print(f"⏰ 知识蒸馏完成，将在 {wait_minutes} 分钟后执行审计")
        print("=" * 60)
        
        # 创建后台任务
        script_content = f'''#!/usr/bin/env python3
import time
import subprocess
import sys
from pathlib import Path

wait_minutes = {wait_minutes}
pipeline_script = Path("{self.pipeline_script.absolute()}")
python_exe = "{sys.executable}"

print(f"等待 {{wait_minutes}} 分钟...")
time.sleep(wait_minutes * 60)

print("开始执行知识审计...")
result = subprocess.run([python_exe, str(pipeline_script), "--full-audit"], capture_output=True, text=True)

if result.returncode == 0:
    print("知识审计执行成功")
else:
    print(f"知识审计执行失败: {{result.stderr}}")
'''
        
        trigger_script = self.base_path / "state" / "trigger_audit.py"
        trigger_script.parent.mkdir(exist_ok=True)
        trigger_script.write_text(script_content, encoding="utf-8")
        
        # 在后台运行
        try:
            subprocess.Popen([sys.executable, str(trigger_script)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           cwd=str(self.base_path))
            
            print(f"✓ 已设置延迟触发，{wait_minutes} 分钟后自动执行")
            return True
        except Exception as e:
            print(f"❌ 设置延迟触发失败: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="定时任务管理器")
    parser.add_argument("--setup", action="store_true", help="设置定时任务")
    parser.add_argument("--remove", action="store_true", help="移除定时任务")
    parser.add_argument("--status", action="store_true", help="查看定时任务状态")
    parser.add_argument("--trigger-after-distillation", type=int, metavar="MINUTES",
                       help="知识蒸馏后延迟触发审计（分钟）")
    
    args = parser.parse_args()
    
    manager = SchedulerManager()
    
    if args.setup:
        manager.setup_schedule()
    elif args.remove:
        manager.remove_schedule()
    elif args.status:
        manager.show_schedule_status()
    elif args.trigger_after_distillation is not None:
        manager.trigger_audit_after_distillation(args.trigger_after_distillation)
    else:
        print("定时任务管理器")
        print("\n使用方法:")
        print("  --setup              设置定时任务")
        print("  --remove             移除定时任务")
        print("  --status             查看任务状态")
        print("  --trigger-after-distillation MINUTES  知识蒸馏后延迟触发")
        print("\n定时规则:")
        print("  - 每周日凌晨 2:00 自动执行全面审计")
        print("  - 知识蒸馏完成后等待 30 分钟自动执行审计")


if __name__ == "__main__":
    main()
