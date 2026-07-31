#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识应用与反馈学习Skill - 主入口
从每一次与用户的交互中提取有价值的信息，评估回答质量，发现系统不足，自动触发知识补充和能力优化
"""

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

# 添加当前目录到模块搜索路径
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def main():
    parser = argparse.ArgumentParser(description="知识应用与反馈学习Skill")
    
    # 被动触发模式 - 当对话结束时自动调用
    parser.add_argument("--session-complete", action="store_true",
                       help="会话结束，触发反馈学习流程")
    
    # 手动指定对话内容
    parser.add_argument("--user-query", type=str,
                       help="用户问题")
    parser.add_argument("--assistant-response", type=str,
                       help="助手回答")
    parser.add_argument("--user-feedback", type=str,
                       help="用户反馈（如有）")
    
    # 分析现有对话历史
    parser.add_argument("--analyze-history", type=str,
                       help="分析指定的对话历史文件")
    
    # 生成报告
    parser.add_argument("--weekly-report", action="store_true",
                       help="生成周度学习报告")
    
    # 参数
    parser.add_argument("--conversation-id", type=str,
                       help="对话ID")
    parser.add_argument("--verbose", action="store_true",
                       help="详细输出")
    
    args = parser.parse_args()
    
    try:
        config_path = Path(__file__).parent.parent / "config/config.json"
        
        if args.session_complete or args.user_query:
            # 执行反馈学习流程
            result = run_feedback_learning(
                config_path,
                args.user_query,
                args.assistant_response,
                args.user_feedback,
                args.conversation_id,
                args.verbose
            )
        elif args.analyze_history:
            # 分析历史对话
            result = analyze_history(config_path, args.analyze_history, args.verbose)
        elif args.weekly_report:
            # 生成周度报告
            result = generate_weekly_report(config_path, args.verbose)
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


def run_feedback_learning(config_path, user_query, assistant_response, user_feedback, conversation_id, verbose):
    """执行反馈学习流程"""
    print("=" * 60)
    print("🧠 知识应用与反馈学习")
    print("=" * 60)
    
    from conversation_analyzer import ConversationAnalyzer
    from quality_evaluator import QualityEvaluator
    from feedback_analyzer import FeedbackAnalyzer
    from knowledge_gap_identifier import KnowledgeGapIdentifier
    from answer_optimizer import AnswerOptimizer
    from learning_logger import LearningLogger
    
    try:
        if verbose:
            print(f"\n📝 处理对话: {conversation_id or '新对话'}")
        
        # 1. 对话历史获取与分析
        print("\n📊 步骤1/7: 对话历史获取与分析...")
        analyzer = ConversationAnalyzer(str(config_path))
        conversation_data = analyzer.analyze(
            user_query or "",
            assistant_response or "",
            user_feedback or ""
        )
        
        if verbose:
            print(f"   - 对话类型: {conversation_data.get('type', 'unknown')}")
            print(f"   - 关键信息: {len(conversation_data.get('key_info', {}))} 项")
        
        # 2. 回答质量评估
        print("\n📈 步骤2/7: 回答质量评估...")
        evaluator = QualityEvaluator(str(config_path))
        quality_scores = evaluator.evaluate(
            user_query or "",
            assistant_response or "",
            conversation_data
        )
        
        if verbose:
            print(f"   - 综合得分: {quality_scores.get('overall_score', 0):.1f}/100")
            print(f"   - 准确性: {quality_scores.get('dimensions', {}).get('accuracy', 0):.1f}/100")
            print(f"   - 完整性: {quality_scores.get('dimensions', {}).get('completeness', 0):.1f}/100")
        
        # 3. 用户反馈分析
        feedback_analysis = {}
        if user_feedback:
            print("\n💬 步骤3/7: 用户反馈分析...")
            feedback_analyzer = FeedbackAnalyzer(str(config_path))
            feedback_analysis = feedback_analyzer.analyze(user_feedback, quality_scores)
            
            if verbose:
                print(f"   - 反馈类型: {feedback_analysis.get('type', 'unknown')}")
                print(f"   - 反馈情感: {feedback_analysis.get('sentiment', 'neutral')}")
        
        # 4. 知识缺口识别与自动补充
        print("\n🔍 步骤4/7: 知识缺口识别...")
        gap_identifier = KnowledgeGapIdentifier(str(config_path))
        knowledge_gaps = gap_identifier.identify(
            user_query or "",
            conversation_data,
            quality_scores,
            feedback_analysis
        )
        
        if verbose:
            print(f"   - 识别缺口: {len(knowledge_gaps)} 个")
            for gap in knowledge_gaps:
                print(f"     - {gap.get('type', 'unknown')}: {gap.get('description', 'N/A')}")
        
        # 5. 回答优化与风格调整
        print("\n✨ 步骤5/7: 回答优化...")
        optimizer = AnswerOptimizer(str(config_path))
        optimization = optimizer.optimize(
            user_query or "",
            assistant_response or "",
            quality_scores,
            feedback_analysis,
            conversation_data
        )
        
        if verbose:
            print(f"   - 优化建议: {len(optimization.get('suggestions', []))} 项")
            print(f"   - 用户偏好更新: {optimization.get('preference_update', False)}")
        
        # 6. 学习记录与报告生成
        print("\n📝 步骤6/7: 学习记录...")
        logger = LearningLogger(str(config_path))
        log_result = logger.log_learning(
            conversation_id,
            conversation_data,
            quality_scores,
            feedback_analysis,
            knowledge_gaps,
            optimization
        )
        
        if verbose:
            print(f"   - 学习日志: {log_result.get('log_file', 'N/A')}")
        
        # 7. 系统自我改进
        print("\n🔧 步骤7/7: 系统自我改进...")
        system_improvements = []
        if quality_scores.get('overall_score', 0) < 70:
            system_improvements.append("回答质量偏低，建议增加相关知识采集")
        if len(knowledge_gaps) > 2:
            system_improvements.append("知识缺口较多，建议优化知识库结构")
        
        if verbose and system_improvements:
            print(f"   - 系统改进建议:")
            for improvement in system_improvements:
                print(f"     - {improvement}")
        
        return {
            "success": True,
            "message": "反馈学习完成！",
            "details": {
                "conversation_type": conversation_data.get('type', 'unknown'),
                "quality_score": quality_scores,
                "feedback_type": feedback_analysis.get('type', 'none'),
                "knowledge_gaps": knowledge_gaps,
                "optimization": optimization,
                "log_file": log_result.get('log_file', ''),
                "system_improvements": system_improvements
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"反馈学习失败: {str(e)}",
            "error": traceback.format_exc()
        }


def analyze_history(config_path, history_file, verbose):
    """分析历史对话"""
    print("=" * 60)
    print("📚 历史对话分析")
    print("=" * 60)
    
    from learning_logger import LearningLogger
    
    try:
        logger = LearningLogger(str(config_path))
        history = logger.load_history(history_file)
        
        print(f"\n📊 历史记录统计:")
        print(f"   - 记录总数: {len(history.get('records', []))}")
        print(f"   - 平均质量得分: {history.get('average_score', 0):.1f}/100")
        
        if verbose:
            print(f"\n📋 详细信息:")
            print(json.dumps(history, ensure_ascii=False, indent=2))
        
        return {
            "success": True,
            "message": "历史分析完成！",
            "details": history
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"历史分析失败: {str(e)}",
            "error": traceback.format_exc()
        }


def generate_weekly_report(config_path, verbose):
    """生成周度学习报告"""
    print("=" * 60)
    print("📊 周度学习报告生成")
    print("=" * 60)
    
    from learning_logger import LearningLogger
    
    try:
        logger = LearningLogger(str(config_path))
        report = logger.generate_weekly_report()
        
        print(f"\n✅ 周度报告已生成!")
        print(f"   - 报告文件: {report.get('file', 'N/A')}")
        print(f"   - 统计周期: {report.get('period', 'N/A')}")
        print(f"   - 对话总数: {report.get('conversation_count', 0)}")
        print(f"   - 平均质量: {report.get('average_score', 0):.1f}/100")
        
        if verbose:
            print(f"\n📄 报告摘要:")
            print(report.get('summary', 'N/A'))
        
        return {
            "success": True,
            "message": "周度报告生成完成！",
            "details": report
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"报告生成失败: {str(e)}",
            "error": traceback.format_exc()
        }


def log_error(error_msg):
    """记录错误日志"""
    error_file = Path(__file__).parent.parent.parent / "08_audit" / "feedback_learner_error.log"
    error_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(error_file, "a", encoding="utf-8") as f:
        f.write(error_msg)
    
    print(f"\n⚠️ 错误已记录到: {error_file}")


def print_usage():
    """打印使用说明"""
    print("🧠 知识应用与反馈学习Skill")
    print("=" * 60)
    print("\n这是一个被动触发的事件驱动型Skill")
    print("通常在大模型对话结束后自动调用")
    print("\n使用场景:")
    print("\n1. 会话结束触发:")
    print("   python3 main.py --session-complete --user-query '...' --assistant-response '...'")
    print("\n2. 手动指定对话:")
    print("   python3 main.py --user-query '用户问题' --assistant-response '回答' --user-feedback '反馈'")
    print("\n3. 分析历史:")
    print("   python3 main.py --analyze-history <日志文件>")
    print("\n4. 生成周度报告:")
    print("   python3 main.py --weekly-report")
    print("\n参数说明:")
    print("   --conversation-id    对话ID")
    print("   --verbose           详细输出")


if __name__ == "__main__":
    main()
