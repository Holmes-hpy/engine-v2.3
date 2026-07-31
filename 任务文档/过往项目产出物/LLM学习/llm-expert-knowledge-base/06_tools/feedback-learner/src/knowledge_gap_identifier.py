#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识缺口识别与自动补充模块
识别知识缺口并触发相应的补充流程
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class KnowledgeGapIdentifier:
    """知识缺口识别器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.gap_config = self.config.get("knowledge_gap", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def identify(self, user_query: str, conversation_data: Dict, 
                quality_scores: Dict, feedback_analysis: Dict) -> List[Dict]:
        """识别知识缺口"""
        gaps = []

        gap_types = self.gap_config.get("types", {})
        trigger_actions = self.gap_config.get("trigger_actions", {})

        if quality_scores.get("overall_score", 0) < 70:
            gaps.append({
                "type": gap_types.get("missing", "完全缺失"),
                "description": "回答质量偏低，可能存在知识缺口",
                "trigger_action": trigger_actions.get("missing", ""),
                "priority": "high"
            })

        if feedback_analysis.get("type") == "negative":
            gaps.append({
                "type": gap_types.get("incomplete", "不完整或不准确"),
                "description": "用户反馈存在不足，需要补充相关知识",
                "trigger_action": trigger_actions.get("incomplete", ""),
                "priority": "high",
                "details": feedback_analysis.get("details", {})
            })

        key_info = conversation_data.get("key_info", {})
        technical_concepts = key_info.get("technical_concepts", [])
        
        if len(technical_concepts) > 0:
            gaps.append({
                "type": gap_types.get("incomplete", "不完整或不准确"),
                "description": f"涉及的技术概念: {', '.join(technical_concepts[:3])}",
                "trigger_action": trigger_actions.get("incomplete", ""),
                "priority": "medium",
                "concepts": technical_concepts[:5]
            })

        conversation_type = conversation_data.get("type", "")
        if "research" in conversation_type.lower():
            gaps.append({
                "type": gap_types.get("missing", "完全缺失"),
                "description": "研究支持类对话，可能需要更多研究资料",
                "trigger_action": trigger_actions.get("missing", ""),
                "priority": "medium"
            })

        low_dimensions = [
            dim for dim, score in quality_scores.get("dimensions", {}).items()
            if score < 60
        ]
        if low_dimensions:
            gaps.append({
                "type": gap_types.get("incomplete", "不完整或不准确"),
                "description": f"低分维度: {', '.join(low_dimensions)}",
                "trigger_action": trigger_actions.get("incomplete", ""),
                "priority": "medium",
                "low_dimensions": low_dimensions
            })

        return gaps

    def get_trigger_command(self, gap_type: str) -> str:
        """获取触发命令"""
        trigger_actions = self.gap_config.get("trigger_actions", {})
        action = trigger_actions.get(gap_type, "")

        if action == "trigger_radar":
            return "trigger_radar"
        elif action == "trigger_distillation":
            return "trigger_distillation"
        elif action == "update_index":
            return "update_index"
        elif action == "mark_for_update":
            return "mark_for_update"

        return ""


class AnswerOptimizer:
    """回答优化器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.learning_config = self.config.get("learning", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def optimize(self, user_query: str, response: str, quality_scores: Dict,
                 feedback_analysis: Dict, conversation_data: Dict) -> Dict:
        """优化回答"""
        suggestions = []
        preference_update = False

        if quality_scores.get("overall_score", 0) < 70:
            suggestions.append("需要增加相关背景知识的介绍")
            suggestions.append("建议补充更详细的解释和例子")

        low_dimensions = [
            dim for dim, score in quality_scores.get("dimensions", {}).items()
            if score < 70
        ]
        for dim in low_dimensions:
            suggestions.append(f"优化{self._get_dimension_name(dim)}维度的表现")

        if feedback_analysis.get("type") == "followup":
            suggestions.append("增加回答的详细程度")
            suggestions.append("预判用户可能的追问并提前准备")

        if feedback_analysis.get("type") == "positive":
            suggestions.append("总结本次成功回答的特点，应用到未来")
            preference_update = True

        required_depth = conversation_data.get("key_info", {}).get("required_depth", "中等")
        if required_depth == "深度":
            suggestions.append("用户需要深度解答，应提供更全面的分析")

        user_intent = conversation_data.get("key_info", {}).get("user_intent", "")
        if "比较" in user_intent or "对比" in user_intent:
            suggestions.append("使用表格或对比结构展示信息")

        return {
            "suggestions": suggestions,
            "preference_update": preference_update,
            "timestamp": datetime.now().isoformat()
        }

    def _get_dimension_name(self, dimension: str) -> str:
        """获取维度名称"""
        dimension_names = {
            "accuracy": "准确性",
            "completeness": "完整性",
            "relevance": "相关性",
            "clarity": "清晰度",
            "practicality": "实用性",
            "timeliness": "时效性"
        }
        return dimension_names.get(dimension, dimension)


class LearningLogger:
    """学习记录器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.logs_dir = self.base_path / self.config["general"]["learning_logs_dir"]
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def log_learning(self, conversation_id: str, conversation_data: Dict,
                    quality_scores: Dict, feedback_analysis: Dict,
                    knowledge_gaps: List[Dict], optimization: Dict) -> Dict:
        """记录学习"""
        if not conversation_id:
            conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        log_data = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_data": conversation_data,
            "quality_scores": quality_scores,
            "feedback_analysis": feedback_analysis,
            "knowledge_gaps": knowledge_gaps,
            "optimization": optimization
        }

        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}-{conversation_id}.md"
        
        log_content = self._generate_log_content(log_data)
        log_file.write_text(log_content, encoding='utf-8')

        return {
            "success": True,
            "log_file": str(log_file)
        }

    def _generate_log_content(self, log_data: Dict) -> str:
        """生成日志内容"""
        content = f"# 学习日志 - {log_data['conversation_id']}\n\n"
        content += f"**时间**: {log_data['timestamp']}\n\n"
        content += "---\n\n"

        content += "## 对话基本信息\n\n"
        content += f"- **用户问题**: {log_data['conversation_data'].get('user_query', 'N/A')}\n"
        content += f"- **对话类型**: {log_data['conversation_data'].get('type', 'unknown')}\n"
        content += f"- **用户意图**: {log_data['conversation_data'].get('key_info', {}).get('user_intent', 'N/A')}\n\n"

        content += "## 回答质量评估\n\n"
        quality_scores = log_data['quality_scores']
        content += f"- **综合得分**: {quality_scores.get('overall_score', 0):.1f}/100\n"
        content += f"- **质量等级**: {quality_scores.get('grade', 'N/A')}\n\n"

        content += "### 各维度得分\n\n"
        for dim, score in quality_scores.get('dimensions', {}).items():
            content += f"- **{dim}**: {score:.1f}/100\n"
        content += "\n"

        content += "## 用户反馈分析\n\n"
        feedback = log_data['feedback_analysis']
        content += f"- **反馈类型**: {feedback.get('type', 'none')}\n"
        content += f"- **反馈情感**: {feedback.get('sentiment', 'neutral')}\n"
        if feedback.get('details', {}).get('key_points'):
            content += f"- **关键要点**: {', '.join(feedback['details']['key_points'])}\n"
        content += "\n"

        content += "## 知识缺口识别\n\n"
        gaps = log_data['knowledge_gaps']
        if gaps:
            for i, gap in enumerate(gaps, 1):
                content += f"{i}. **[{gap.get('type', 'unknown')}]** {gap.get('description', 'N/A')}\n"
                content += f"   - 优先级: {gap.get('priority', 'normal')}\n"
                content += f"   - 触发动作: {gap.get('trigger_action', 'N/A')}\n\n"
        else:
            content += "未发现明显知识缺口\n\n"

        content += "## 优化建议\n\n"
        optimization = log_data['optimization']
        suggestions = optimization.get('suggestions', [])
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                content += f"{i}. {suggestion}\n"
        else:
            content += "无优化建议\n"
        content += "\n"

        return content

    def load_history(self, log_file: str) -> Dict:
        """加载历史记录"""
        if not Path(log_file).exists():
            return {"records": [], "average_score": 0}

        history = json.loads(Path(log_file).read_text(encoding='utf-8'))
        return history

    def generate_weekly_report(self) -> Dict:
        """生成周度报告"""
        report_date = datetime.now()
        report_file = self.base_path / self.config["general"]["weekly_report_dir"] / \
                     f"{report_date.strftime('%Y-%m-%d')}-周度学习报告.md"

        report_file.parent.mkdir(parents=True, exist_ok=True)

        report_content = self._generate_weekly_report_content(report_date)
        report_file.write_text(report_content, encoding='utf-8')

        return {
            "success": True,
            "file": str(report_file),
            "period": f"{report_date.strftime('%Y-%m-%d')} (本周)",
            "conversation_count": 0,
            "average_score": 0,
            "summary": "周度学习报告已生成"
        }

    def _generate_weekly_report_content(self, report_date: datetime) -> str:
        """生成周度报告内容"""
        content = f"# 周度学习报告 - {report_date.strftime('%Y-%m-%d')}\n\n"
        content += "---\n\n"

        content += "## 本周学习统计\n\n"
        content += "- 对话总数: 待统计\n"
        content += "- 平均质量得分: 待统计\n"
        content += "- 知识缺口数: 待统计\n"
        content += "- 用户反馈数: 待统计\n\n"

        content += "## 主要发现\n\n"
        content += "本周学习报告正在完善中...\n\n"

        content += "## 下周计划\n\n"
        content += "- 继续优化知识库\n"
        content += "- 提升回答质量\n"
        content += "- 关注用户反馈\n\n"

        return content


def main():
    """测试函数"""
    gap_identifier = KnowledgeGapIdentifier("config/config.json")
    gaps = gap_identifier.identify("测试问题", {}, {"overall_score": 65}, {})

    print("识别到的知识缺口:")
    print(json.dumps(gaps, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
