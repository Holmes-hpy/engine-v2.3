#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习日志记录器
负责记录学习过程、保存日志文件、生成周度报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class LearningLogger:
    """学习日志记录器"""
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.base_path = self.config_path.parent.parent / self.config["general"]["base_path"]
        self.learning_logs_dir = self.base_path / self.config["general"]["learning_logs_dir"]
        self.weekly_report_dir = self.base_path / self.config["general"]["weekly_report_dir"]
        
        # 确保目录存在
        self.learning_logs_dir.mkdir(parents=True, exist_ok=True)
        self.weekly_report_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def log_learning(self, conversation_id, conversation_data, quality_scores, 
                    feedback_analysis, knowledge_gaps, optimization):
        """记录学习日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if not conversation_id:
            conversation_id = f"conv_{timestamp}"
        
        log_file = self.learning_logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}-{conversation_id}.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "conversation_data": conversation_data,
            "quality_scores": quality_scores,
            "feedback_analysis": feedback_analysis,
            "knowledge_gaps": knowledge_gaps,
            "optimization": optimization
        }
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "log_file": str(log_file)
        }
    
    def load_history(self, history_file):
        """加载历史记录"""
        if Path(history_file).exists():
            with open(history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"records": [], "average_score": 0}
    
    def _get_all_logs(self):
        """获取所有学习日志"""
        logs = []
        if self.learning_logs_dir.exists():
            for log_file in self.learning_logs_dir.glob("*.json"):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        log_data = json.load(f)
                        logs.append(log_data)
                except Exception:
                    pass
        return logs
    
    def _get_week_logs(self):
        """获取本周的学习日志"""
        all_logs = self._get_all_logs()
        week_ago = datetime.now() - timedelta(days=7)
        week_logs = []
        
        for log in all_logs:
            try:
                log_time = datetime.fromisoformat(log["timestamp"])
                if log_time >= week_ago:
                    week_logs.append(log)
            except Exception:
                pass
        
        return week_logs
    
    def generate_weekly_report(self):
        """生成周度学习报告"""
        week_logs = self._get_week_logs()
        all_logs = self._get_all_logs()
        
        # 统计本周数据
        conversation_count = len(week_logs)
        total_score = 0.0
        type_distribution = {}
        feedback_stats = {"positive": 0, "negative": 0, "followup": 0, "none": 0}
        knowledge_gap_types = {}
        scores_by_day = {}
        
        for log in week_logs:
            conv_type = log.get("conversation_data", {}).get("type", "unknown")
            type_distribution[conv_type] = type_distribution.get(conv_type, 0) + 1
            
            score = log.get("quality_scores", {}).get("overall_score", 0)
            total_score += score
            
            try:
                log_date = datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d")
                if log_date not in scores_by_day:
                    scores_by_day[log_date] = []
                scores_by_day[log_date].append(score)
            except Exception:
                pass
            
            feedback_type = log.get("feedback_analysis", {}).get("type", "none")
            feedback_stats[feedback_type] = feedback_stats.get(feedback_type, 0) + 1
            
            gaps = log.get("knowledge_gaps", [])
            for gap in gaps:
                gap_type = gap.get("type", "unknown")
                knowledge_gap_types[gap_type] = knowledge_gap_types.get(gap_type, 0) + 1
        
        average_score = total_score / conversation_count if conversation_count > 0 else 0
        
        daily_average = {}
        for date, scores in scores_by_day.items():
            daily_average[date] = sum(scores) / len(scores)
        
        # 统计历史数据（用于趋势分析）
        history_stats = self._calculate_history_stats(all_logs)
        
        # 生成报告内容
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_file = self.weekly_report_dir / f"{report_date}-周度学习报告.md"
        
        report_content = self._generate_report_markdown(
            conversation_count,
            average_score,
            type_distribution,
            feedback_stats,
            knowledge_gap_types,
            daily_average,
            week_logs,
            history_stats
        )
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        summary = self._generate_summary(
            conversation_count,
            average_score,
            type_distribution,
            feedback_stats,
            knowledge_gap_types,
            history_stats
        )
        
        return {
            "file": str(report_file),
            "period": f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')}",
            "conversation_count": conversation_count,
            "average_score": average_score,
            "summary": summary
        }
    
    def _calculate_history_stats(self, all_logs):
        """计算历史统计数据"""
        if not all_logs:
            return {
                "total_conversations": 0,
                "overall_average_score": 0,
                "type_distribution": {},
                "knowledge_gap_types": {},
                "feedback_stats": {"positive": 0, "negative": 0, "followup": 0, "none": 0},
                "weekly_trend": []
            }
        
        total_score = 0.0
        type_distribution = {}
        feedback_stats = {"positive": 0, "negative": 0, "followup": 0, "none": 0}
        knowledge_gap_types = {}
        weekly_scores = {}
        
        for log in all_logs:
            score = log.get("quality_scores", {}).get("overall_score", 0)
            total_score += score
            
            conv_type = log.get("conversation_data", {}).get("type", "unknown")
            type_distribution[conv_type] = type_distribution.get(conv_type, 0) + 1
            
            feedback_type = log.get("feedback_analysis", {}).get("type", "none")
            feedback_stats[feedback_type] = feedback_stats.get(feedback_type, 0) + 1
            
            gaps = log.get("knowledge_gaps", [])
            for gap in gaps:
                gap_type = gap.get("type", "unknown")
                knowledge_gap_types[gap_type] = knowledge_gap_types.get(gap_type, 0) + 1
            
            try:
                log_date = datetime.fromisoformat(log["timestamp"])
                week_key = log_date.strftime("%Y-%U")
                if week_key not in weekly_scores:
                    weekly_scores[week_key] = []
                weekly_scores[week_key].append(score)
            except Exception:
                pass
        
        weekly_trend = []
        for week_key in sorted(weekly_scores.keys()):
            week_scores = weekly_scores[week_key]
            weekly_trend.append({
                "week": week_key,
                "average_score": sum(week_scores) / len(week_scores),
                "count": len(week_scores)
            })
        
        return {
            "total_conversations": len(all_logs),
            "overall_average_score": total_score / len(all_logs),
            "type_distribution": type_distribution,
            "knowledge_gap_types": knowledge_gap_types,
            "feedback_stats": feedback_stats,
            "weekly_trend": weekly_trend[-4:]
        }
    
    def _generate_summary(self, conversation_count, average_score, type_distribution, 
                        feedback_stats, knowledge_gap_types, history_stats=None):
        """生成报告摘要"""
        summary_parts = []
        
        if conversation_count == 0:
            if history_stats and history_stats["total_conversations"] > 0:
                return f"本周暂无学习记录 | 历史累计 {history_stats['total_conversations']} 次对话 | 历史平均得分 {history_stats['overall_average_score']:.1f}/100"
            return "本周暂无学习记录"
        
        summary_parts.append(f"共处理 {conversation_count} 次对话")
        summary_parts.append(f"平均质量得分 {average_score:.1f}/100")
        
        if type_distribution:
            top_type = max(type_distribution.items(), key=lambda x: x[1])[0]
            summary_parts.append(f"主要对话类型: {top_type}")
        
        if knowledge_gap_types:
            top_gap = max(knowledge_gap_types.items(), key=lambda x: x[1])[0]
            summary_parts.append(f"主要知识缺口: {top_gap}")
        
        return " | ".join(summary_parts)
    
    def _generate_report_markdown(self, conversation_count, average_score, type_distribution,
                                feedback_stats, knowledge_gap_types, daily_average, week_logs,
                                history_stats=None):
        """生成Markdown格式的报告"""
        report_date = datetime.now().strftime("%Y年%m月%d日")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y年%m月%d日")
        
        markdown = f"""# 周度学习报告

**生成时间**: {report_date}
**统计周期**: {start_date} 至 {report_date}

---

## 1. 本周概览

| 指标 | 数值 |
|------|------|
| 对话总数 | {conversation_count} |
| 平均质量得分 | {average_score:.1f}/100 |
| 知识缺口识别 | {sum(knowledge_gap_types.values())} 个 |

"""
        
        if conversation_count == 0:
            markdown += """**说明**: 本周没有新的对话记录，以下分析基于历史数据进行回顾。

"""
        
        if average_score >= 85:
            quality_comment = "🎉 表现优秀！继续保持！"
        elif average_score >= 70:
            quality_comment = "👍 表现良好，还有提升空间"
        elif average_score >= 50:
            quality_comment = "⚠️ 需要改进，建议关注重点问题"
        elif conversation_count == 0:
            quality_comment = "📊 本周无新数据，显示历史趋势"
        else:
            quality_comment = "🔴 表现不佳，需要重点优化"
        
        markdown += f"**质量评价**: {quality_comment}\n"
        
        if history_stats and history_stats["total_conversations"] > 0:
            markdown += f"""

**历史数据概览**:
- 历史累计对话: {history_stats['total_conversations']} 次
- 历史平均得分: {history_stats['overall_average_score']:.1f}/100

"""
        
        # 2. 对话类型分布
        markdown += "\n---\n\n## 2. 对话类型分布\n\n"
        
        display_distribution = type_distribution if conversation_count > 0 else (history_stats.get("type_distribution", {}) if history_stats else {})
        display_count = conversation_count if conversation_count > 0 else (history_stats.get("total_conversations", 0) if history_stats else 0)
        
        if display_distribution:
            markdown += "| 类型 | 数量 | 占比 |\n"
            markdown += "|------|------|------|\n"
            for conv_type, count in sorted(display_distribution.items(), key=lambda x: -x[1]):
                percentage = (count / display_count * 100) if display_count > 0 else 0
                markdown += f"| {conv_type} | {count} | {percentage:.1f}% |\n"
            if conversation_count == 0:
                markdown += "\n*注: 以上为历史累计数据*\n"
        else:
            markdown += "暂无数据\n"
        
        # 3. 回答质量分析
        markdown += "\n---\n\n## 3. 回答质量分析\n\n"
        
        if daily_average:
            markdown += "### 3.1 每日平均得分趋势\n\n"
            markdown += "| 日期 | 平均得分 |\n"
            markdown += "|------|----------|\n"
            for date in sorted(daily_average.keys()):
                markdown += f"| {date} | {daily_average[date]:.1f}/100 |\n"
        elif history_stats and history_stats["weekly_trend"]:
            markdown += "### 3.1 历史周度趋势（最近4周）\n\n"
            markdown += "| 周次 | 对话数 | 平均得分 |\n"
            markdown += "|------|--------|----------|\n"
            for trend in history_stats["weekly_trend"]:
                year, week_num = trend["week"].split("-")
                markdown += f"| {year}年第{week_num}周 | {trend['count']} | {trend['average_score']:.1f}/100 |\n"
        
        if week_logs:
            latest_log = week_logs[-1]
            dimensions = latest_log.get("quality_scores", {}).get("dimensions", {})
            if dimensions:
                markdown += "\n### 3.2 各维度质量得分（最近一次）\n\n"
                markdown += "| 维度 | 得分 |\n"
                markdown += "|------|------|\n"
                for dim_name, score in dimensions.items():
                    markdown += f"| {dim_name} | {score:.1f}/100 |\n"
        
        # 4. 用户反馈统计
        markdown += "\n---\n\n## 4. 用户反馈统计\n\n"
        markdown += "| 反馈类型 | 数量 | 占比 |\n"
        markdown += "|----------|------|------|\n"
        
        display_feedback = feedback_stats if conversation_count > 0 else (history_stats.get("feedback_stats", {}) if history_stats else {})
        total_feedback = sum(display_feedback.values())
        
        for feedback_type, count in display_feedback.items():
            percentage = (count / total_feedback * 100) if total_feedback > 0 else 0
            markdown += f"| {feedback_type} | {count} | {percentage:.1f}% |\n"
        
        if conversation_count == 0 and total_feedback > 0:
            markdown += "\n*注: 以上为历史累计数据*\n"
        
        # 5. 知识缺口分析
        markdown += "\n---\n\n## 5. 知识缺口分析\n\n"
        
        display_gaps = knowledge_gap_types if conversation_count > 0 else (history_stats.get("knowledge_gap_types", {}) if history_stats else {})
        
        if display_gaps:
            markdown += "| 缺口类型 | 数量 |\n"
            markdown += "|----------|------|\n"
            for gap_type, count in sorted(display_gaps.items(), key=lambda x: -x[1]):
                markdown += f"| {gap_type} | {count} |\n"
            if conversation_count == 0:
                markdown += "\n*注: 以上为历史累计数据*\n"
        else:
            markdown += "未识别到知识缺口\n"
        
        # 6. 系统优化措施
        markdown += "\n---\n\n## 6. 系统优化措施\n\n"
        
        optimizations = []
        
        if conversation_count > 0:
            if average_score < 70:
                optimizations.append("- 加强知识采集，提升回答准确性")
            if sum(knowledge_gap_types.values()) > 5:
                optimizations.append("- 优化知识库结构，减少知识缺口")
            if feedback_stats.get("negative", 0) > feedback_stats.get("positive", 0):
                optimizations.append("- 分析负面反馈，改进回答质量")
        else:
            if history_stats:
                hist_score = history_stats.get("overall_average_score", 0)
                hist_gaps = sum(history_stats.get("knowledge_gap_types", {}).values())
                hist_feedback = history_stats.get("feedback_stats", {})
                
                if hist_score < 70:
                    optimizations.append("- 基于历史数据分析，回答准确性需要提升")
                if hist_gaps > 5:
                    optimizations.append("- 历史知识缺口较多，建议系统性补充")
                if hist_feedback.get("negative", 0) > hist_feedback.get("positive", 0):
                    optimizations.append("- 历史负面反馈较多，需重点改进回答质量")
                if hist_score >= 70 and hist_gaps <= 5:
                    optimizations.append("- 历史表现良好，建议继续保持学习节奏")
        
        if optimizations:
            for opt in optimizations:
                markdown += f"{opt}\n"
        else:
            markdown += "系统运行良好，暂无特别优化建议\n"
        
        # 7. 下周学习重点
        markdown += "\n---\n\n## 7. 下周学习重点\n\n"
        
        priorities = []
        
        display_gaps_for_priority = display_gaps
        display_dist_for_priority = display_distribution
        
        if display_gaps_for_priority:
            top_gaps = sorted(display_gaps_for_priority.items(), key=lambda x: -x[1])[:3]
            for gap_type, count in top_gaps:
                priorities.append(f"- 补充 {gap_type} 类型的知识 (共 {count} 次)")
        
        if display_dist_for_priority:
            top_types = sorted(display_dist_for_priority.items(), key=lambda x: -x[1])[:2]
            for conv_type, count in top_types:
                priorities.append(f"- 深入学习 {conv_type} 领域的知识")
        
        if conversation_count == 0:
            priorities.append("- 增加对话活跃度，收集更多学习数据")
            priorities.append("- 定期检查知识更新情况")
        
        if priorities:
            for p in priorities:
                markdown += f"{p}\n"
        else:
            markdown += "继续保持当前学习节奏\n"
        
        # 8. 详细记录
        markdown += "\n---\n\n## 8. 详细学习记录\n\n"
        if week_logs:
            for i, log in enumerate(week_logs[-10:], 1):
                conv_id = log.get("conversation_id", f"记录{i}")
                score = log.get("quality_scores", {}).get("overall_score", 0)
                conv_type = log.get("conversation_data", {}).get("type", "unknown")
                timestamp = log.get("timestamp", "")
                
                markdown += f"### {i}. {conv_id}\n"
                markdown += f"- 时间: {timestamp}\n"
                markdown += f"- 类型: {conv_type}\n"
                markdown += f"- 得分: {score:.1f}/100\n\n"
        elif history_stats and history_stats["total_conversations"] > 0:
            markdown += f"本周无新记录，历史累计 {history_stats['total_conversations']} 条学习记录。\n"
            markdown += "建议查看历史报告了解详细情况。\n"
        else:
            markdown += "暂无详细记录\n"
        
        markdown += "\n---\n\n*报告生成完毕*"
        
        return markdown
