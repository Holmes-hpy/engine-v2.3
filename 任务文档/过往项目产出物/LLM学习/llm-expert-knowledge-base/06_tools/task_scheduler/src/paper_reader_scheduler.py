#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
论文精读定时任务管理器
用于管理论文精读与复现Skill的定时触发和手动触发
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import platform


class PaperReaderScheduler:
    """论文精读定时任务管理器"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.paper_reader_script = self.base_path / "../paper-reader/src/main.py"
        self.config_path = self.base_path / "config/paper_reader_schedule.json"
        self.paper_reader_config_path = self.base_path / "../paper-reader/config/config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置（优先从paper-reader的config读取weekly_paper_count）"""
        # 先读取paper-reader的配置
        paper_reader_config = {}
        if self.paper_reader_config_path.exists():
            try:
                with open(self.paper_reader_config_path, "r", encoding="utf-8") as f:
                    paper_reader_config = json.load(f)
            except Exception as e:
                print(f"加载paper-reader配置失败: {e}")
        
        # 获取weekly_paper_count（优先从paper-reader配置读取）
        weekly_count = paper_reader_config.get("filtering", {}).get("weekly_paper_count", 5)
        
        default_config = {
            "paper_reading_schedule": {
                "day_of_week": "sat",
                "hour": 1,
                "minute": 0,
                "weekly_paper_count": weekly_count
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败，使用默认配置: {e}")
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def is_macos(self):
        """判断是否为macOS系统"""
        return platform.system() == "Darwin"
    
    def get_cron_expression(self):
        """生成论文精读的cron表达式 (每周六凌晨1:00)"""
        # cron格式: 分 时 日 月 周
        # 周六是6
        return "0 1 * * 6"
    
    def get_launchd_plist(self):
        """生成macOS launchd plist配置"""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llm-knowledge.paper_reader</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{str(self.paper_reader_script.absolute())}</string>
        <string>--weekly-run</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>6</integer>
        <key>Hour</key>
        <integer>1</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{str(self.base_path / "logs" / "paper_reader_stdout.log")}</string>
    <key>StandardErrorPath</key>
    <string>{str(self.base_path / "logs" / "paper_reader_stderr.log")}</string>
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
        
        plist_path = plist_dir / "com.llm-knowledge.paper_reader.plist"
        plist_content = self.get_launchd_plist()
        
        plist_path.write_text(plist_content, encoding="utf-8")
        print(f"✓ 已创建 plist 文件: {plist_path}")
        
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
        """设置cron定时任务"""
        print("设置 cron 定时任务...")
        
        cron_expr = self.get_cron_expression()
        python_path = sys.executable
        script_path = str(self.paper_reader_script.absolute())
        log_path = str(self.base_path / "logs" / "paper_reader_cron.log")
        
        cron_job = f'{cron_expr} {python_path} {script_path} --weekly-run >> {log_path} 2>&1'
        
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
        except:
            current_cron = ""
        
        if "paper_reader" in current_cron or "--weekly-run" in current_cron:
            print("⚠️ 论文精读定时任务已存在")
            return True
        
        new_cron = current_cron + "\n" + cron_job + "\n" if current_cron else cron_job + "\n"
        
        try:
            subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
            print("✓ Cron 任务已添加")
            return True
        except Exception as e:
            print(f"❌ 设置 cron 失败: {e}")
            return False
    
    def setup_schedule(self, method=None):
        """设置定时任务"""
        print("=" * 60)
        print("📅 设置论文精读定时任务")
        print("=" * 60)
        
        (self.base_path / "logs").mkdir(exist_ok=True)
        
        success = False
        
        if self.is_macos():
            print("\n检测到 macOS 系统")
            
            if method == "cron":
                print("使用 cron")
                success = self.setup_cron()
            else:
                print("使用 launchd (推荐)")
                success = self.setup_macos_launchd()
        else:
            print("\n使用 cron")
            success = self.setup_cron()
        
        if success:
            print("\n✓ 定时任务设置完成！")
            print(f"  - 每周六凌晨 {self.config['paper_reading_schedule']['hour']}:00 自动执行论文精读")
            print(f"  - 每次精读 {self.config['paper_reading_schedule']['weekly_paper_count']} 篇论文")
        else:
            print("\n⚠️ 定时任务设置失败，请手动配置")
        
        return success
    
    def remove_schedule(self):
        """移除定时任务"""
        print("=" * 60)
        print("🗑️  移除论文精读定时任务")
        print("=" * 60)
        
        if self.is_macos():
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.llm-knowledge.paper_reader.plist"
            if plist_path.exists():
                try:
                    subprocess.run(["launchctl", "unload", str(plist_path)], 
                                 capture_output=True, text=True)
                    plist_path.unlink()
                    print("✓ 已移除 launchd 任务")
                except Exception as e:
                    print(f"⚠️ 移除 launchd 任务失败: {e}")
        
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                current_cron = result.stdout
                new_cron = "\n".join([line for line in current_cron.split("\n") 
                                     if "--weekly-run" not in line and "paper_reader" not in line])
                
                if new_cron != current_cron:
                    subprocess.run(["crontab", "-"], input=new_cron, text=True, capture_output=True)
                    print("✓ 已移除 cron 任务")
        except:
            pass
        
        print("论文精读定时任务已移除")
    
    def show_schedule_status(self):
        """显示定时任务状态"""
        print("=" * 60)
        print("📋 论文精读定时任务状态")
        print("=" * 60)
        
        if self.is_macos():
            plist_path = Path.home() / "Library" / "LaunchAgents" / "com.llm-knowledge.paper_reader.plist"
            if plist_path.exists():
                print("✓ launchd 任务: 已配置")
                try:
                    result = subprocess.run(["launchctl", "list", "com.llm-knowledge.paper_reader"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and "com.llm-knowledge.paper_reader" in result.stdout:
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
                if "--weekly-run" in result.stdout or "paper_reader" in result.stdout:
                    print("✓ cron 任务: 已配置")
                    print("\nCron 配置:")
                    for line in result.stdout.split("\n"):
                        if "--weekly-run" in line or "paper_reader" in line:
                            print(f"  {line.strip()}")
                else:
                    print("✗ cron 任务: 未配置")
        except:
            print("✗ cron 任务: 未配置")
        
        print(f"\n下次论文精读: 每周六凌晨 {self.config['paper_reading_schedule']['hour']}:00")
        print(f"每次精读论文数: {self.config['paper_reading_schedule']['weekly_paper_count']}")
    
    def run_manual(self, arxiv_url=None, paper_title=None, count=5, priority="auto"):
        """手动触发论文精读"""
        print("=" * 60)
        print("📚 手动触发论文精读")
        print("=" * 60)
        
        args = ["--manual"]
        
        if arxiv_url:
            args.extend(["--arxiv-url", arxiv_url])
            print(f"\n🔗 指定arXiv链接: {arxiv_url}")
        elif paper_title:
            args.extend(["--paper-title", paper_title])
            print(f"\n🔍 搜索论文: {paper_title}")
        
        args.extend(["--count", str(count)])
        args.extend(["--priority", priority])
        
        print(f"\n📋 参数: {args}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.paper_reader_script)] + args,
                capture_output=True,
                text=True,
                cwd=str(self.base_path)
            )
            
            print("\n📝 执行结果:")
            print(result.stdout)
            
            if result.stderr:
                print("\n⚠️ 警告/错误:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"\n❌ 执行失败: {e}")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="论文精读定时任务管理器")
    parser.add_argument("--setup", action="store_true", help="设置定时任务")
    parser.add_argument("--remove", action="store_true", help="移除定时任务")
    parser.add_argument("--status", action="store_true", help="查看定时任务状态")
    parser.add_argument("--manual", action="store_true", help="手动触发论文精读")
    parser.add_argument("--arxiv-url", type=str, help="指定arXiv链接")
    parser.add_argument("--paper-title", type=str, help="指定论文标题")
    parser.add_argument("--count", type=int, default=5, help="精读论文数量")
    parser.add_argument("--priority", type=str, default="auto", 
                       choices=["auto", "conference", "institution", "code"],
                       help="筛选优先级")
    parser.add_argument("--method", type=str, default="launchd", 
                       choices=["launchd", "cron"],
                       help="定时任务方式 (macOS: launchd/cron, Linux: cron)")
    
    args = parser.parse_args()
    
    scheduler = PaperReaderScheduler()
    
    if args.setup:
        scheduler.setup_schedule(args.method)
    elif args.remove:
        scheduler.remove_schedule()
    elif args.status:
        scheduler.show_schedule_status()
    elif args.manual:
        success = scheduler.run_manual(args.arxiv_url, args.paper_title, args.count, args.priority)
        if success:
            print("\n✅ 手动触发成功！")
        else:
            print("\n❌ 手动触发失败！")
    else:
        print("📚 论文精读定时任务管理器")
        print("\n使用方法:")
        print("  --setup              设置定时任务")
        print("  --method launchd|cron  指定定时任务方式")
        print("  --remove             移除定时任务")
        print("  --status             查看任务状态")
        print("  --manual             手动触发论文精读")
        print("  --arxiv-url URL      指定arXiv链接")
        print("  --paper-title TITLE  指定论文标题")
        print("  --count N            指定精读数量")
        print("  --priority TYPE      设置筛选优先级")
        print("\n定时规则:")
        print("  - 每周六凌晨 1:00 自动执行论文精读")
        print("  - 每次自动筛选并精读 3-5 篇高质量论文")


if __name__ == "__main__":
    main()
