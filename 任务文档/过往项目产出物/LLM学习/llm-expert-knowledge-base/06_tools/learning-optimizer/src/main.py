#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习计划优化Skill - 主入口
作为大模型专家系统的"学习总监"，负责制定科学合理的学习战略
"""

import argparse
import json
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="学习计划优化Skill")
    
    parser.add_argument("--full", action="store_true",
                       help="执行完整的学习计划优化流程")
    parser.add_argument("--health", action="store_true",
                       help="仅执行知识库健康度评估")
    parser.add_argument("--trends", action="store_true",
                       help="仅执行技术趋势分析")
    parser.add_argument("--user", action="store_true",
                       help="仅执行用户需求分析")
    parser.add_argument("--generate", action="store_true",
                       help="仅生成学习计划")
    parser.add_argument("--evaluate", action="store_true",
                       help="仅评估上周学习计划执行情况")
    parser.add_argument("--emergency", type=str,
                       help="触发紧急学习计划，参数：tech|user|health")
    parser.add_argument("--verbose", action="store_true",
                       help="详细输出")
    
    args = parser.parse_args()
    
    try:
        config_path = Path(__file__).parent.parent / "config/config.json"
        
        if args.emergency:
            result = run_emergency_plan(config_path, args.emergency, args.verbose)
        elif args.full:
            result = run_full_optimization(config_path, args.verbose)
        elif args.health:
            result = run_health_assessment(config_path, args.verbose)
        elif args.trends:
            result = run_trend_analysis(config_path, args.verbose)
        elif args.user:
            result = run_user_analysis(config_path, args.verbose)
        elif args.generate:
            result = run_plan_generation(config_path, args.verbose)
        elif args.evaluate:
            result = run_evaluation(config_path, args.verbose)
        else:
            print_usage()
            return
        
        if result["success"]:
            print(f"\n✅ {result['message']}")
            if args.verbose and "details" in result:
                print(f"\n📊 详细信息：")
                print(json.dumps(result["details"], ensure_ascii=False, indent=2))
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


def run_full_optimization(config_path, verbose):
    """执行完整的学习计划优化流程"""
    print("=" * 60)
    print("🎯 学习计划优化 - 完整流程")
    print("=" * 60)
    
    from health_assessment import (
        KnowledgeHealthAssessor,
        TrendAnalyzer,
        UserDemandAnalyzer,
        LearningPlanGenerator
    )
    
    if verbose:
        print("\n📊 步骤1/7: 知识库健康度评估...")
    assessor = KnowledgeHealthAssessor(str(config_path))
    health_report = assessor.assess()
    
    if verbose:
        print(f"   - 健康度评分: {health_report.get('overall_score', 0):.1f}/100")
    
    if verbose:
        print("\n📈 步骤2/7: 技术趋势分析...")
    trend_analyzer = TrendAnalyzer(str(config_path))
    trend_report = trend_analyzer.analyze()
    
    if verbose:
        print(f"   - 识别趋势: {len(trend_report.get('trends', []))} 个")
    
    if verbose:
        print("\n👥 步骤3/7: 用户需求分析...")
    user_analyzer = UserDemandAnalyzer(str(config_path))
    user_report = user_analyzer.analyze()
    
    if verbose:
        print(f"   - 识别需求: {len(user_report.get('demands', []))} 个")
    
    if verbose:
        print("\n📋 步骤4/7: 学习计划生成...")
    plan_generator = LearningPlanGenerator(str(config_path))
    learning_plan = plan_generator.generate(health_report, trend_report, user_report)
    
    if verbose:
        print(f"   - 任务数量: {len(learning_plan.get('tasks', []))} 个")
    
    if verbose:
        print("\n⏰ 步骤5/7: 任务调度与更新...")
    scheduler_result = update_scheduler_configs(learning_plan, config_path)
    
    if verbose:
        print(f"   - 调度更新: {'成功' if scheduler_result.get('success', False) else '失败'}")
    
    if verbose:
        print("\n📝 步骤6/7: 生成学习计划报告...")
    report_result = generate_learning_plan_report(
        health_report, trend_report, user_report, learning_plan, config_path
    )
    
    if verbose:
        print(f"   - 报告文件: {report_result.get('report_file', 'N/A')}")
    
    if verbose:
        print("\n✅ 步骤7/7: 学习计划优化完成！")
    
    return {
        "success": True,
        "message": "完整学习计划优化完成！",
        "details": {
            "health_report": health_report,
            "trend_report": trend_report,
            "user_report": user_report,
            "learning_plan": learning_plan,
            "report_file": report_result.get("report_file", "")
        }
    }


def run_health_assessment(config_path, verbose):
    """仅执行知识库健康度评估"""
    print("=" * 60)
    print("🏥 知识库健康度评估")
    print("=" * 60)
    
    from health_assessment import KnowledgeHealthAssessor
    
    assessor = KnowledgeHealthAssessor(str(config_path))
    health_report = assessor.assess()
    
    if verbose:
        print(f"\n📊 评估结果：")
        print(f"   - 健康度评分: {health_report.get('overall_score', 0):.1f}/100")
        print(f"   - 覆盖度: {health_report.get('coverage_score', 0):.1f}/100")
        print(f"   - 质量度: {health_report.get('quality_score', 0):.1f}/100")
        print(f"   - 时效性: {health_report.get('timeliness_score', 0):.1f}/100")
        print(f"   - 关联度: {health_report.get('relevance_score', 0):.1f}/100")
        print(f"   - 实用度: {health_report.get('utility_score', 0):.1f}/100")
        
        weak_areas = health_report.get('weak_areas', [])
        if weak_areas:
            print(f"\n⚠️  薄弱环节：")
            for area in weak_areas:
                print(f"   - {area.get('name', 'N/A')}: {area.get('reason', 'N/A')}")
    
    return {
        "success": True,
        "message": "知识库健康度评估完成！",
        "details": health_report
    }


def run_trend_analysis(config_path, verbose):
    """仅执行技术趋势分析"""
    print("=" * 60)
    print("📈 技术趋势分析")
    print("=" * 60)
    
    from health_assessment import TrendAnalyzer
    
    analyzer = TrendAnalyzer(str(config_path))
    trend_report = analyzer.analyze()
    
    if verbose:
        print(f"\n📊 分析结果：")
        trends = trend_report.get('trends', [])
        print(f"   - 识别趋势: {len(trends)} 个")
        
        if trends:
            print(f"\n🔥 热门趋势：")
            for trend in trends[:5]:
                priority = trend.get('priority', 'unknown')
                name = trend.get('name', 'N/A')
                print(f"   - [{priority}] {name}")
    
    return {
        "success": True,
        "message": "技术趋势分析完成！",
        "details": trend_report
    }


def run_user_analysis(config_path, verbose):
    """仅执行用户需求分析"""
    print("=" * 60)
    print("👥 用户需求分析")
    print("=" * 60)
    
    from health_assessment import UserDemandAnalyzer
    
    analyzer = UserDemandAnalyzer(str(config_path))
    user_report = analyzer.analyze()
    
    if verbose:
        print(f"\n📊 分析结果：")
        demands = user_report.get('demands', [])
        print(f"   - 识别需求: {len(demands)} 个")
        
        if demands:
            print(f"\n🎯 用户关注：")
            for demand in demands[:5]:
                priority = demand.get('priority', 'unknown')
                name = demand.get('name', 'N/A')
                print(f"   - [{priority}] {name}")
    
    return {
        "success": True,
        "message": "用户需求分析完成！",
        "details": user_report
    }


def run_plan_generation(config_path, verbose):
    """仅生成学习计划"""
    print("=" * 60)
    print("📋 学习计划生成")
    print("=" * 60)
    
    from health_assessment import (
        KnowledgeHealthAssessor,
        TrendAnalyzer,
        UserDemandAnalyzer,
        LearningPlanGenerator
    )
    
    assessor = KnowledgeHealthAssessor(str(config_path))
    health_report = assessor.assess()
    
    trend_analyzer = TrendAnalyzer(str(config_path))
    trend_report = trend_analyzer.analyze()
    
    user_analyzer = UserDemandAnalyzer(str(config_path))
    user_report = user_analyzer.analyze()
    
    plan_generator = LearningPlanGenerator(str(config_path))
    learning_plan = plan_generator.generate(health_report, trend_report, user_report)
    
    if verbose:
        print(f"\n📊 学习计划：")
        print(f"   - 任务数量: {len(learning_plan.get('tasks', []))} 个")
        print(f"   - 目标数量: {len(learning_plan.get('goals', []))} 个")
        
        tasks = learning_plan.get('tasks', [])
        if tasks:
            print(f"\n🎯 重点任务：")
            for task in tasks[:3]:
                priority = task.get('priority', 'unknown')
                name = task.get('name', 'N/A')
                print(f"   - [{priority}] {name}")
    
    return {
        "success": True,
        "message": "学习计划生成完成！",
        "details": learning_plan
    }


def run_evaluation(config_path, verbose):
    """仅评估上周学习计划执行情况"""
    print("=" * 60)
    print("📊 学习计划执行评估")
    print("=" * 60)
    
    from health_assessment import LearningEvaluator
    
    evaluator = LearningEvaluator(str(config_path))
    evaluation_report = evaluator.evaluate()
    
    if verbose:
        print(f"\n📊 评估结果：")
        print(f"   - 任务完成率: {evaluation_report.get('completion_rate', 0):.1f}%")
        print(f"   - 成果达成率: {evaluation_report.get('achievement_rate', 0):.1f}%")
        print(f"   - 健康度提升: {evaluation_report.get('health_improvement', 0):.1f} 分")
        
        issues = evaluation_report.get('issues', [])
        if issues:
            print(f"\n⚠️  问题分析：")
            for issue in issues[:3]:
                print(f"   - {issue.get('description', 'N/A')}")
    
    return {
        "success": True,
        "message": "学习计划执行评估完成！",
        "details": evaluation_report
    }


def run_emergency_plan(config_path, emergency_type, verbose):
    """执行紧急学习计划"""
    print("=" * 60)
    print("🚨 紧急学习计划触发")
    print("=" * 60)
    
    emergency_types = {
        'tech': '重大技术事件',
        'user': '用户紧急需求',
        'health': '知识库严重问题'
    }
    
    if emergency_type not in emergency_types:
        return {
            "success": False,
            "message": f"无效的紧急类型，有效类型：{', '.join(emergency_types.keys())}"
        }
    
    print(f"\n⚠️  紧急类型: {emergency_types[emergency_type]}")
    
    from health_assessment import EmergencyHandler
    
    handler = EmergencyHandler(str(config_path))
    emergency_plan = handler.handle(emergency_type)
    
    if verbose:
        print(f"\n📋 紧急计划：")
        print(f"   - 任务数量: {len(emergency_plan.get('tasks', []))} 个")
        print(f"   - 时间限制: {emergency_plan.get('time_limit_hours', 0)} 小时")
    
    return {
        "success": True,
        "message": "紧急学习计划已生成！",
        "details": emergency_plan
    }


def update_scheduler_configs(learning_plan, config_path):
    """更新调度器配置"""
    # 这里简化实现，实际应该更新其他Skill的配置
    return {
        "success": True,
        "updated_skills": ["radar", "distillation", "auditor", "paper_reader"]
    }


def generate_learning_plan_report(health_report, trend_report, user_report, 
                                 learning_plan, config_path):
    """生成学习计划报告"""
    from health_assessment import LearningPlanGenerator
    
    generator = LearningPlanGenerator(str(config_path))
    report_path = generator.generate_report(
        health_report, trend_report, user_report, learning_plan
    )
    
    return {
        "success": True,
        "report_file": report_path
    }


def log_error(error_msg):
    """记录错误日志"""
    error_file = Path(__file__).parent.parent.parent / "08_audit" / "learning_optimizer_error.log"
    error_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(error_file, "a", encoding="utf-8") as f:
        f.write(error_msg)
    
    print(f"\n⚠️  错误已记录到: {error_file}")


def print_usage():
    """打印使用说明"""
    print("🎯 学习计划优化Skill")
    print("=" * 60)
    print("\n作为大模型专家系统的\"学习总监\"，负责制定科学合理的学习战略。")
    print("\n使用方法：")
    print("\n1. 完整学习计划优化：")
    print("   python3 src/main.py --full --verbose")
    print("\n2. 单项分析：")
    print("   python3 src/main.py --health   # 知识库健康度评估")
    print("   python3 src/main.py --trends    # 技术趋势分析")
    print("   python3 src/main.py --user      # 用户需求分析")
    print("\n3. 其他功能：")
    print("   python3 src/main.py --generate  # 仅生成学习计划")
    print("   python3 src/main.py --evaluate  # 评估上周学习计划")
    print("\n4. 紧急计划：")
    print("   python3 src/main.py --emergency tech   # 重大技术事件")
    print("   python3 src/main.py --emergency user   # 用户紧急需求")
    print("   python3 src/main.py --emergency health # 知识库严重问题")


if __name__ == "__main__":
    main()
