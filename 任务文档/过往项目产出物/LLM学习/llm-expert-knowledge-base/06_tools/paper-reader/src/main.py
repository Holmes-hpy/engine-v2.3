#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
论文精读与复现Skill - 主入口
支持定时触发和手动触发
"""

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="论文精读与复现Skill")
    
    # 定时触发模式
    parser.add_argument("--weekly-run", action="store_true", 
                       help="执行每周定时任务（自动筛选并精读论文）")
    
    # 手动触发模式
    parser.add_argument("--manual", action="store_true", 
                       help="手动触发模式")
    parser.add_argument("--arxiv-url", type=str, 
                       help="指定arXiv论文链接进行精读")
    parser.add_argument("--paper-title", type=str, 
                       help="指定论文标题进行搜索和精读")
    parser.add_argument("--count", type=int, default=5, 
                       help="每周精读论文数量（默认5篇）")
    parser.add_argument("--priority", type=str, default="auto", 
                       choices=["auto", "conference", "institution", "code"],
                       help="论文筛选优先级")
    
    # 复现选项
    parser.add_argument("--reproduce", action="store_true", 
                       help="同时进行实验复现")
    parser.add_argument("--no-reproduce", action="store_true", 
                       help="不进行实验复现")
    
    # 知识整合选项
    parser.add_argument("--integrate", action="store_true", 
                       help="进行知识整合")
    parser.add_argument("--no-integrate", action="store_true", 
                       help="不进行知识整合")
    
    args = parser.parse_args()
    
    # 设置默认行为
    do_reproduce = args.reproduce or (not args.no_reproduce)
    do_integrate = args.integrate or (not args.no_integrate)
    
    try:
        config_path = Path(__file__).parent.parent / "config/config.json"
        
        # 从配置文件读取weekly_paper_count（定时任务模式优先使用配置文件）
        config_count = args.count
        if args.weekly_run:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    config_count = config_data.get("filtering", {}).get("weekly_paper_count", args.count)
            except Exception as e:
                print(f"读取配置文件失败，使用默认值 {args.count}")
        
        if args.weekly_run:
            # 定时触发：每周自动筛选并精读（使用配置文件中的数量）
            result = run_weekly_paper_reading(config_path, config_count, do_reproduce, do_integrate)
        elif args.manual:
            # 手动触发：指定论文（使用命令行参数）
            result = run_manual_reading(config_path, args.arxiv_url, args.paper_title, 
                                       args.count, args.priority, do_reproduce, do_integrate)
        else:
            print_usage()
            return
        
        if result["success"]:
            print(f"\n✅ {result['message']}")
            sys.exit(0)
        else:
            print(f"\n❌ {result['message']}")
            log_error(result.get("error", ""))
            sys.exit(1)
            
    except Exception as e:
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 执行失败: {str(e)}\n{traceback.format_exc()}\n"
        log_error(error_msg)
        print(f"\n❌ 执行失败！错误已记录到日志")
        sys.exit(1)


def run_weekly_paper_reading(config_path, count, do_reproduce, do_integrate):
    """执行每周定时论文精读任务"""
    print("=" * 60)
    print("📚 每周论文精读任务")
    print("=" * 60)
    
    from paper_filter import PaperFilter
    from paper_reader import PaperReader
    from paper_reproducer import PaperReproducer
    from knowledge_integrator import KnowledgeIntegrator
    
    try:
        # 1. 筛选论文
        print("\n🔍 步骤1/4: 筛选本周论文...")
        filter_module = PaperFilter(str(config_path))
        filter_module.config["filtering"]["weekly_paper_count"] = count
        selected_papers = filter_module.run_weekly_selection()
        
        if not selected_papers:
            return {"success": False, "message": "未筛选出论文"}
        
        print(f"\n📋 已筛选出 {len(selected_papers)} 篇论文")
        
        # 2. 精读论文
        print("\n📖 步骤2/4: 精读论文...")
        reader = PaperReader(str(config_path))
        analyses = reader.read_papers(selected_papers)
        
        if not analyses:
            return {"success": False, "message": "论文精读失败"}
        
        # 获取保存的文件路径
        paper_files = []
        for analysis in analyses:
            safe_title = analysis['title'][:50].replace('/', '_').replace('\\', '_')
            filename = f"{analysis['reading_date']}-{safe_title}.md"
            paper_files.append(Path(__file__).parent.parent.parent.parent / "05_papers" / filename)
        
        # 3. 实验复现（可选）
        if do_reproduce:
            print("\n🔬 步骤3/4: 实验复现...")
            reproducer = PaperReproducer(str(config_path))
            
            for i, paper in enumerate(selected_papers):
                if paper.get("github_url"):
                    print(f"\n复现 [{i+1}/{len(selected_papers)}]: {paper.get('title', '')[:30]}...")
                    repro_result = reproducer.reproduce(paper)
                    
                    # 将复现信息写入论文解读文件
                    if paper_files[i].exists():
                        content = paper_files[i].read_text(encoding='utf-8')
                        content += "\n" + repro_result["reproduction_report"]
                        paper_files[i].write_text(content, encoding='utf-8')
        
        # 4. 知识整合（可选）
        if do_integrate:
            print("\n🧠 步骤4/4: 知识整合...")
            integrator = KnowledgeIntegrator(str(config_path))
            
            for i, analysis in enumerate(analyses):
                if paper_files[i].exists():
                    integrator.integrate_knowledge(analysis, paper_files[i])
        
        return {
            "success": True,
            "message": f"每周论文精读完成！共精读 {len(analyses)} 篇论文",
            "paper_count": len(analyses)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"执行失败: {str(e)}",
            "error": traceback.format_exc()
        }


def run_manual_reading(config_path, arxiv_url, paper_title, count, priority, do_reproduce, do_integrate):
    """执行手动论文精读任务"""
    print("=" * 60)
    print("📚 手动论文精读任务")
    print("=" * 60)
    
    from paper_reader import PaperReader
    from paper_reproducer import PaperReproducer
    from knowledge_integrator import KnowledgeIntegrator
    
    try:
        papers_to_read = []
        
        if arxiv_url:
            print(f"\n🔗 指定arXiv链接: {arxiv_url}")
            papers_to_read.append({
                "arxiv_url": arxiv_url,
                "title": "从arXiv获取",
                "priority": priority
            })
        elif paper_title:
            print(f"\n🔍 搜索论文: {paper_title}")
            papers_to_read.append({
                "title": paper_title,
                "priority": priority
            })
        else:
            # 如果没有指定，从本地筛选
            from paper_filter import PaperFilter
            filter_module = PaperFilter(str(config_path))
            filter_module.config["filtering"]["weekly_paper_count"] = count
            
            print(f"\n🔍 筛选 {count} 篇论文，优先级: {priority}")
            papers_to_read = filter_module.run_weekly_selection()[:count]
        
        if not papers_to_read:
            return {"success": False, "message": "未找到指定的论文"}
        
        # 精读论文
        print(f"\n📖 开始精读 {len(papers_to_read)} 篇论文...")
        reader = PaperReader(str(config_path))
        analyses = reader.read_papers(papers_to_read)
        
        # 获取保存的文件路径
        paper_files = []
        for analysis in analyses:
            safe_title = analysis['title'][:50].replace('/', '_').replace('\\', '_')
            filename = f"{analysis['reading_date']}-{safe_title}.md"
            paper_files.append(Path(__file__).parent.parent.parent.parent / "05_papers" / filename)
        
        # 实验复现（可选）
        if do_reproduce:
            print("\n🔬 实验复现...")
            reproducer = PaperReproducer(str(config_path))
            
            for i, paper in enumerate(papers_to_read):
                if paper.get("github_url"):
                    print(f"\n复现 [{i+1}/{len(papers_to_read)}]: {paper.get('title', '')[:30]}...")
                    repro_result = reproducer.reproduce(paper)
                    
                    if paper_files[i].exists():
                        content = paper_files[i].read_text(encoding='utf-8')
                        content += "\n" + repro_result["reproduction_report"]
                        paper_files[i].write_text(content, encoding='utf-8')
        
        # 知识整合（可选）
        if do_integrate:
            print("\n🧠 知识整合...")
            integrator = KnowledgeIntegrator(str(config_path))
            
            for i, analysis in enumerate(analyses):
                if paper_files[i].exists():
                    integrator.integrate_knowledge(analysis, paper_files[i])
        
        return {
            "success": True,
            "message": f"手动论文精读完成！共精读 {len(analyses)} 篇论文",
            "paper_count": len(analyses)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"执行失败: {str(e)}",
            "error": traceback.format_exc()
        }


def log_error(error_msg):
    """记录错误日志"""
    error_dir = Path(__file__).parent.parent.parent.parent / "05_papers"
    error_dir.mkdir(parents=True, exist_ok=True)
    
    error_file = error_dir / "error.log"
    with open(error_file, "a", encoding="utf-8") as f:
        f.write(error_msg)
    
    print(f"\n⚠️ 错误已记录到: {error_file}")


def print_usage():
    """打印使用说明"""
    print("📚 论文精读与复现Skill")
    print("=" * 60)
    print("\n使用方法:")
    print("\n【定时触发模式】")
    print("  python3 main.py --weekly-run")
    print("    每周六凌晨1:00自动执行，筛选过去7天内最有价值的3-5篇论文")
    print("\n【手动触发模式】")
    print("  python3 main.py --manual --arxiv-url <arXiv链接>")
    print("    指定arXiv链接进行精读")
    print("  python3 main.py --manual --paper-title <标题>")
    print("    指定论文标题搜索并精读")
    print("\n【可选参数】")
    print("  --count N         指定精读论文数量（默认5篇）")
    print("  --priority auto|conference|institution|code")
    print("                    设置筛选优先级")
    print("  --reproduce       进行实验复现")
    print("  --no-reproduce    不进行实验复现")
    print("  --integrate       进行知识整合")
    print("  --no-integrate    不进行知识整合")
    print("\n【示例】")
    print("  # 每周定时任务")
    print("  python3 main.py --weekly-run")
    print("\n  # 手动精读指定论文")
    print("  python3 main.py --manual --arxiv-url https://arxiv.org/abs/2301.03724")
    print("\n  # 指定精读3篇，优先选择有代码的论文")
    print("  python3 main.py --manual --count 3 --priority code")


if __name__ == "__main__":
    main()
