#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户反馈分析模块
分析用户反馈并进行深入分析
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class FeedbackAnalyzer:
    """反馈分析器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.feedback_config = self.config.get("feedback_analysis", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def analyze(self, feedback: str, quality_scores: Dict) -> Dict:
        """分析用户反馈"""
        if not feedback:
            return {
                "type": "none",
                "sentiment": "neutral",
                "details": {},
                "timestamp": datetime.now().isoformat()
            }

        feedback_type = self._identify_feedback_type(feedback)
        sentiment = self._analyze_sentiment(feedback)
        details = self._analyze_details(feedback, feedback_type, quality_scores)

        return {
            "type": feedback_type,
            "sentiment": sentiment,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

    def _identify_feedback_type(self, feedback: str) -> str:
        """识别反馈类型"""
        feedback_lower = feedback.lower()

        positive_keywords = self.feedback_config.get("positive_keywords", [])
        if any(keyword in feedback_lower for keyword in positive_keywords):
            return "positive"

        correction_keywords = self.feedback_config.get("correction_keywords", [])
        if any(keyword in feedback_lower for keyword in correction_keywords):
            return "correction"

        negative_keywords = self.feedback_config.get("negative_keywords", [])
        if any(keyword in feedback_lower for keyword in negative_keywords):
            return "negative"

        followup_keywords = self.feedback_config.get("followup_keywords", [])
        if any(keyword in feedback_lower for keyword in followup_keywords):
            return "followup"

        return "neutral"

    def _analyze_sentiment(self, feedback: str) -> str:
        """分析情感"""
        feedback_lower = feedback.lower()

        positive_indicators = ["很好", "棒", "不错", "优秀", "helpful", "good", "great", "excellent"]
        negative_indicators = ["不好", "差", "糟糕", "不对", "bad", "poor", "wrong", "terrible"]

        positive_count = sum(1 for indicator in positive_indicators if indicator in feedback_lower)
        negative_count = sum(1 for indicator in negative_indicators if indicator in feedback_lower)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"

        return "neutral"

    def _analyze_details(self, feedback: str, feedback_type: str, quality_scores: Dict) -> Dict:
        """分析详情"""
        details = {
            "feedback_text": feedback,
            "key_points": [],
            "action_required": False,
            "priority": "normal"
        }

        if feedback_type == "positive":
            details["key_points"] = self._extract_positive_points(feedback)
            details["action_required"] = False
            details["priority"] = "low"

        elif feedback_type == "negative":
            details["key_points"] = self._extract_negative_points(feedback)
            details["action_required"] = True
            details["priority"] = "high"
            details["error_analysis"] = self._analyze_errors(feedback, quality_scores)

        elif feedback_type == "correction":
            details["key_points"] = self._extract_correction_points(feedback)
            details["action_required"] = True
            details["priority"] = "high"
            details["correction_info"] = self._extract_correction_info(feedback)

        elif feedback_type == "followup":
            details["key_points"] = self._extract_followup_points(feedback)
            details["action_required"] = True
            details["priority"] = "medium"
            details["followup_reason"] = self._analyze_followup_reason(feedback)

        return details

    def _extract_positive_points(self, feedback: str) -> List[str]:
        """提取正面反馈要点"""
        points = []

        positive_patterns = {
            "内容准确": ["准确", "正确", "accurate", "correct"],
            "讲解清晰": ["清晰", "清楚", "clear", "understandable"],
            "很有帮助": ["有帮助", "有用", "helpful", "useful"],
            "回答全面": ["全面", "完整", "comprehensive", "complete"]
        }

        for category, keywords in positive_patterns.items():
            if any(keyword in feedback.lower() for keyword in keywords):
                points.append(category)

        return points if points else ["整体满意"]

    def _extract_negative_points(self, feedback: str) -> List[str]:
        """提取负面反馈要点"""
        points = []

        negative_patterns = {
            "内容不准确": ["不对", "不准确", "错误", "wrong", "incorrect"],
            "信息不完整": ["不完整", "缺少", "incomplete", "missing"],
            "表述不清楚": ["不清楚", "模糊", "unclear", "confusing"],
            "缺乏实用性": ["没用", "不实用", "not practical", "unhelpful"]
        }

        for category, keywords in negative_patterns.items():
            if any(keyword in feedback.lower() for keyword in keywords):
                points.append(category)

        return points if points else ["存在不足"]

    def _extract_correction_points(self, feedback: str) -> List[str]:
        """提取修正反馈要点"""
        points = []

        correction_patterns = [
            r'应该是[""""](.+?)[""""]',
            r'实际上[""""](.+?)["""]',
            r'应该是(.+?)[，,]',
            r'实际上(.+?)[，,]'
        ]

        for pattern in correction_patterns:
            matches = re.findall(pattern, feedback)
            points.extend(matches)

        return points if points else ["用户提供修正"]

    def _extract_followup_points(self, feedback: str) -> List[str]:
        """提取追问要点"""
        points = []

        followup_patterns = {
            "需要更详细": ["详细", "具体", "详细解释", "detailed"],
            "需要原因": ["为什么", "原因", "why", "reason"],
            "需要例子": ["例子", "示例", "example", "instance"],
            "继续追问": ["还有", "另外", "also", "more"]
        }

        for category, keywords in followup_patterns.items():
            if any(keyword in feedback.lower() for keyword in keywords):
                points.append(category)

        return points if points else ["需要更多信息"]

    def _analyze_errors(self, feedback: str, quality_scores: Dict) -> Dict:
        """分析错误"""
        error_analysis = {
            "probable_causes": [],
            "affected_dimensions": []
        }

        feedback_lower = feedback.lower()

        if any(keyword in feedback_lower for keyword in ["不对", "错误", "wrong"]):
            error_analysis["probable_causes"].append("知识库中缺少相关知识")
            error_analysis["affected_dimensions"].append("accuracy")

        if any(keyword in feedback_lower for keyword in ["不完整", "缺少", "missing"]):
            error_analysis["probable_causes"].append("知识整合不完整")
            error_analysis["affected_dimensions"].append("completeness")

        if any(keyword in feedback_lower for keyword in ["不清楚", "模糊"]):
            error_analysis["probable_causes"].append("表述不清晰")
            error_analysis["affected_dimensions"].append("clarity")

        if quality_scores.get("dimensions", {}):
            low_scores = {
                dim: score for dim, score in quality_scores["dimensions"].items()
                if score < 70
            }
            for dim in low_scores:
                if dim not in error_analysis["affected_dimensions"]:
                    error_analysis["affected_dimensions"].append(dim)

        return error_analysis

    def _extract_correction_info(self, feedback: str) -> Dict:
        """提取修正信息"""
        correction_info = {
            "correct_value": "",
            "source": "user",
            "needs_verification": True
        }

        patterns = [
            (r'应该是[""""](.+?)["""]', 1),
            (r'实际上[""""](.+?)["""]', 1),
            (r'应该是(.+?)[，。]', 1)
        ]

        for pattern, group in patterns:
            match = re.search(pattern, feedback)
            if match:
                correction_info["correct_value"] = match.group(group)
                break

        return correction_info

    def _analyze_followup_reason(self, feedback: str) -> str:
        """分析追问原因"""
        feedback_lower = feedback.lower()

        if any(keyword in feedback_lower for keyword in ["详细", "具体", "detailed"]):
            return "原回答不够详细"
        elif any(keyword in feedback_lower for keyword in ["为什么", "原因", "why"]):
            return "用户有更深层次的需求"
        elif any(keyword in feedback_lower for keyword in ["还有", "另外", "also"]):
            return "用户有其他相关问题"

        return "需要更多信息"


def main():
    """测试函数"""
    analyzer = FeedbackAnalyzer("config/config.json")

    test_feedback = "回答得很好，很有帮助！"

    result = analyzer.analyze(test_feedback, {})

    print("反馈分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
