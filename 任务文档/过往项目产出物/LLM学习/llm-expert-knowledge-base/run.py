#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Expert Knowledge Base - 统一入口
一站式管理所有Agent，驱动知识库持续进化
"""

import argparse
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_llm_info_radar(args):
    """运行大模型信息雷达"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "llm-info-radar" / "src" / "main.py")]
    if args.non_interactive:
        cmd.append("--non-interactive")
    subprocess.run(cmd, check=True)


def run_knowledge_distiller(args):
    """运行知识蒸馏器"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "knowledge-distiller" / "src" / "main.py")]
    if args.non_interactive:
        cmd.append("--non-interactive")
    subprocess.run(cmd, check=True)


def run_paper_reader(args):
    """运行论文精读师"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "paper-reader" / "src" / "main.py")]
    if args.weekly:
        cmd.append("--weekly-run")
    else:
        cmd.append("--manual")
        if args.arxiv_url:
            cmd.extend(["--arxiv-url", args.arxiv_url])
        if args.paper_title:
            cmd.extend(["--paper-title", args.paper_title])
        if args.count:
            cmd.extend(["--count", str(args.count)])
    subprocess.run(cmd, check=True)


def run_feedback_learner(args):
    """运行反馈学习器"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "feedback-learner" / "src" / "main.py")]
    if args.session_complete:
        cmd.append("--session-complete")
    elif args.weekly_report:
        cmd.append("--weekly-report")
    elif args.analyze_history:
        cmd.extend(["--analyze-history", args.analyze_history])
    if args.verbose:
        cmd.append("--verbose")
    subprocess.run(cmd, check=True)


def run_knowledge_auditor(args):
    """运行知识审计师"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "knowledge-auditor" / "src" / "main.py")]
    if args.full_audit:
        cmd.append("--full")
    subprocess.run(cmd, check=True)


def run_learning_optimizer(args):
    """运行学习总监"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "learning-optimizer" / "src" / "main.py")]
    if args.full:
        cmd.append("--full")
    elif args.health:
        cmd.append("--health")
    elif args.trends:
        cmd.append("--trends")
    elif args.user:
        cmd.append("--user")
    elif args.generate:
        cmd.append("--generate")
    elif args.evaluate:
        cmd.append("--evaluate")
    elif args.emergency:
        cmd.extend(["--emergency", args.emergency])
    if args.verbose:
        cmd.append("--verbose")
    subprocess.run(cmd, check=True)


def run_self_driven_agent(args):
    """运行自主学习智能体"""
    cmd = ["python3", str(PROJECT_ROOT / "06_tools" / "self-driven-agent" / "src" / "main.py")]
    subprocess.run(cmd, check=True)


def run_full_pipeline(args):
    """运行完整知识管理流程"""
    print("=" * 70)
    print("🚀 LLM Expert Knowledge Base - 完整知识管理流程")
    print("=" * 70)
    
    try:
        print("\n📡 步骤1/5: 信息采集 (LLM信息雷达)")
        run_llm_info_radar(args)
        
        print("\n🔬 步骤2/5: 知识蒸馏 (知识蒸馏器)")
        run_knowledge_distiller(args)
        
        print("\n📚 步骤3/5: 论文精读 (论文精读师)")
        run_paper_reader(args)
        
        print("\n🔍 步骤4/5: 质量审计 (知识审计师)")
        run_knowledge_auditor(args)
        
        print("\n🎯 步骤5/5: 学习优化 (学习总监)")
        run_learning_optimizer(args)
        
        print("\n" + "=" * 70)
        print("✅ 完整知识管理流程执行完成！")
        print("=" * 70)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 流程执行失败: {e}")
        sys.exit(1)


def show_status():
    """显示系统状态"""
    print("=" * 70)
    print("📊 LLM Expert Knowledge Base - 系统状态")
    print("=" * 70)
    
    directories = [
        ("01_inbox", "待处理信息"),
        ("02_raw", "原始数据"),
        ("03_ai_wiki", "结构化知识"),
        ("04_permanent", "永久知识库"),
        ("05_papers", "论文库"),
        ("06_tools", "工具模块"),
        ("07_case_studies", "案例研究"),
        ("08_audit", "审计报告"),
        ("99_archive", "归档"),
    ]
    
    print("\n📁 目录状态:")
    for dir_name, desc in directories:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.rglob("*.md")))
            print(f"   ✅ {dir_name:15s} - {desc} ({file_count} 篇文档)")
        else:
            print(f"   ❌ {dir_name:15s} - {desc} (目录不存在)")
    
    print("\n🤖 Agent状态:")
    agents = [
        ("llm-info-radar", "大模型信息雷达", "信息采集"),
        ("knowledge-distiller", "知识蒸馏器", "知识提炼"),
        ("paper-reader", "论文精读师", "论文分析"),
        ("feedback-learner", "反馈学习器", "反馈学习"),
        ("knowledge-auditor", "知识审计师", "质量审计"),
        ("learning-optimizer", "学习总监", "学习规划"),
        ("self-driven-agent", "自主学习智能体", "自主学习"),
    ]
    
    for agent_name, agent_title, agent_desc in agents:
        agent_path = PROJECT_ROOT / "06_tools" / agent_name
        prompt_path = agent_path / "prompt" / "agent_prompt.txt"
        if agent_path.exists():
            status = "✅" if prompt_path.exists() else "⚠️"
            prompt_status = "已配置" if prompt_path.exists() else "未配置"
            print(f"   {status} {agent_name:20s} - {agent_title} ({agent_desc}, {prompt_status})")
        else:
            print(f"   ❌ {agent_name:20s} - {agent_title} ({agent_desc}, 模块缺失)")
    
    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="LLM Expert Knowledge Base - 统一入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 运行完整知识管理流程
  python3 run.py --pipeline
  
  # 运行单个Agent
  python3 run.py --radar              # 信息采集
  python3 run.py --distill            # 知识蒸馏
  python3 run.py --paper              # 论文精读
  python3 run.py --feedback           # 反馈学习
  python3 run.py --audit              # 知识审计
  python3 run.py --optimizer          # 学习优化
  python3 run.py --autonomous         # 自主学习
  
  # 查看系统状态
  python3 run.py --status
        """
    )
    
    # 整体流程
    parser.add_argument("--pipeline", action="store_true", help="运行完整知识管理流程")
    parser.add_argument("--status", action="store_true", help="显示系统状态")
    parser.add_argument("--non-interactive", action="store_true", help="非交互模式")
    
    # 单个Agent
    parser.add_argument("--radar", action="store_true", help="运行大模型信息雷达")
    parser.add_argument("--distill", action="store_true", help="运行知识蒸馏器")
    parser.add_argument("--paper", action="store_true", help="运行论文精读师")
    parser.add_argument("--feedback", action="store_true", help="运行反馈学习器")
    parser.add_argument("--audit", action="store_true", help="运行知识审计师")
    parser.add_argument("--optimizer", action="store_true", help="运行学习总监")
    parser.add_argument("--autonomous", action="store_true", help="运行自主学习智能体")
    
    # 论文精读师参数
    parser.add_argument("--weekly", action="store_true", help="论文精读：每周模式")
    parser.add_argument("--arxiv-url", type=str, help="论文精读：指定arXiv链接")
    parser.add_argument("--paper-title", type=str, help="论文精读：指定论文标题")
    parser.add_argument("--count", type=int, default=5, help="论文精读：论文数量")
    
    # 反馈学习器参数
    parser.add_argument("--session-complete", action="store_true", help="反馈学习：会话结束")
    parser.add_argument("--weekly-report", action="store_true", help="反馈学习：周度报告")
    parser.add_argument("--analyze-history", type=str, help="反馈学习：分析历史文件")
    
    # 知识审计师参数
    parser.add_argument("--full-audit", action="store_true", help="知识审计：全面审计")
    
    # 学习总监参数
    parser.add_argument("--full", action="store_true", help="学习优化：完整流程")
    parser.add_argument("--health", action="store_true", help="学习优化：健康度评估")
    parser.add_argument("--trends", action="store_true", help="学习优化：趋势分析")
    parser.add_argument("--user", action="store_true", help="学习优化：用户分析")
    parser.add_argument("--generate", action="store_true", help="学习优化：生成计划")
    parser.add_argument("--evaluate", action="store_true", help="学习优化：评估执行")
    parser.add_argument("--emergency", type=str, help="学习优化：紧急计划(tech/user/health)")
    
    # 通用参数
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.pipeline:
        run_full_pipeline(args)
        return
    
    if args.radar:
        run_llm_info_radar(args)
    elif args.distill:
        run_knowledge_distiller(args)
    elif args.paper:
        run_paper_reader(args)
    elif args.feedback:
        run_feedback_learner(args)
    elif args.audit:
        run_knowledge_auditor(args)
    elif args.optimizer:
        run_learning_optimizer(args)
    elif args.autonomous:
        run_self_driven_agent(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()