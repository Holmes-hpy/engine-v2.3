#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回答质量评估模块
六维评分系统评估回答质量
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class QualityEvaluator:
    """质量评估器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.dimensions_config = self.config.get("quality_assessment", {}).get("dimensions", {})
        self.score_thresholds = self.config.get("quality_assessment", {}).get("score_thresholds", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def evaluate(self, user_query: str, assistant_response: str, conversation_data: Dict) -> Dict:
        """评估回答质量"""
        if not assistant_response:
            return {
                "overall_score": 0,
                "dimensions": {},
                "detailed_scores": {},
                "timestamp": datetime.now().isoformat()
            }

        dimension_scores = {}

        dimension_scores["accuracy"] = self._evaluate_accuracy(user_query, assistant_response)
        dimension_scores["completeness"] = self._evaluate_completeness(user_query, assistant_response, conversation_data)
        dimension_scores["relevance"] = self._evaluate_relevance(user_query, assistant_response)
        dimension_scores["clarity"] = self._evaluate_clarity(assistant_response)
        dimension_scores["practicality"] = self._evaluate_practicality(user_query, assistant_response)
        dimension_scores["timeliness"] = self._evaluate_timeliness(assistant_response)

        overall_score = self._calculate_overall_score(dimension_scores)

        detailed_scores = self._generate_detailed_scores(dimension_scores)

        quality_grade = self._assign_grade(overall_score)

        return {
            "overall_score": overall_score,
            "dimensions": dimension_scores,
            "detailed_scores": detailed_scores,
            "grade": quality_grade,
            "timestamp": datetime.now().isoformat()
        }

    def _evaluate_accuracy(self, user_query: str, response: str) -> float:
        """评估准确性"""
        score = 75.0

        if not response or len(response) < 10:
            return 30.0

        factual_indicators = ["根据", "研究表明", "实验证明", "数据显示", "typically", "usually"]
        if any(indicator in response for indicator in factual_indicators):
            score += 10.0

        uncertainty_indicators = ["可能", "也许", "不确定", "perhaps", "maybe", "possibly"]
        uncertainty_count = sum(1 for indicator in uncertainty_indicators if indicator in response)
        score -= uncertainty_count * 3.0

        contradiction_indicators = ["但是", "然而", "不过", "however", "but", "although"]
        if any(indicator in response for indicator in contradiction_indicators):
            score -= 5.0

        technical_terms = self._extract_technical_terms(response)
        if len(technical_terms) > 3:
            score += 5.0

        code_blocks = len(re.findall(r'```[\s\S]*?```', response))
        if code_blocks > 0:
            score += 5.0

        return min(100.0, max(0.0, score))

    def _evaluate_completeness(self, user_query: str, response: str, conversation_data: Dict) -> float:
        """评估完整性"""
        score = 70.0

        question_types = self._identify_question_types(user_query)

        response_length = len(response)
        query_length = len(user_query)
        length_ratio = response_length / query_length if query_length > 0 else 0

        if length_ratio > 5:
            score += 15.0
        elif length_ratio > 3:
            score += 10.0
        elif length_ratio < 1:
            score -= 20.0

        required_components = {
            "definition": ["是", "定义", "means", "refers to", "what is"],
            "explanation": ["因为", "由于", "通过", "原因", "because", "due to"],
            "steps": ["步骤", "首先", "然后", "最后", "step", "first", "then"],
            "examples": ["例如", "比如", "example", "for instance", "such as"],
            "conclusion": ["总之", "总结", "因此", "所以", "in conclusion", "therefore"]
        }

        matched_components = 0
        for component, keywords in required_components.items():
            if any(keyword in response.lower() for keyword in keywords):
                matched_components += 1

        score += matched_components * 5.0

        key_info = conversation_data.get("key_info", {})
        main_topic = key_info.get("main_topic", "")
        if main_topic and main_topic in response:
            score += 5.0

        return min(100.0, max(0.0, score))

    def _evaluate_relevance(self, user_query: str, response: str) -> float:
        """评估相关性"""
        score = 80.0

        query_words = set(self._tokenize(user_query))
        response_words = set(self._tokenize(response))

        overlap = query_words & response_words
        if len(query_words) > 0:
            relevance_ratio = len(overlap) / len(query_words)
            score = 60 + relevance_ratio * 40

        off_topic_indicators = ["顺便说一句", "另外", "顺便提一下", "by the way", "off topic"]
        off_topic_count = sum(1 for indicator in off_topic_indicators if indicator in response.lower())
        score -= off_topic_count * 15.0

        return min(100.0, max(0.0, score))

    def _evaluate_clarity(self, response: str) -> float:
        """评估清晰度"""
        score = 75.0

        if not response:
            return 30.0

        sentences = re.split(r'[。.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0

        if avg_sentence_length < 30:
            score += 10.0
        elif avg_sentence_length > 80:
            score -= 10.0

        structure_indicators = [
            "首先", "其次", "最后", "第一", "第二", "第三",
            "first", "second", "third", "finally", "additionally"
        ]
        structure_score = sum(1 for indicator in structure_indicators if indicator in response)
        score += min(structure_score * 5.0, 15.0)

        code_blocks = len(re.findall(r'```[\s\S]*?```', response))
        if code_blocks > 0:
            score += 5.0

        unclear_indicators = ["可能", "也许", "不太确定", "perhaps", "maybe", "unclear"]
        unclear_count = sum(1 for indicator in unclear_indicators if indicator in response)
        score -= unclear_count * 3.0

        return min(100.0, max(0.0, score))

    def _evaluate_practicality(self, user_query: str, response: str) -> float:
        """评估实用性"""
        score = 70.0

        action_keywords = ["可以", "应该", "建议", "尝试", "推荐", "can", "should", "recommend", "try"]
        if any(keyword in response for keyword in action_keywords):
            score += 10.0

        code_blocks = len(re.findall(r'```[\s\S]*?```', response))
        score += min(code_blocks * 7.0, 21.0)

        tool_mentions = ["使用", "借助", "通过", "using", "with", "via"]
        if any(keyword in response for keyword in tool_mentions):
            score += 5.0

        steps_indicators = ["步骤", "方法", "流程", "step", "method", "approach"]
        if any(keyword in response for keyword in steps_indicators):
            score += 5.0

        return min(100.0, max(0.0, score))

    def _evaluate_timeliness(self, response: str) -> float:
        """评估时效性"""
        score = 80.0

        recent_keywords = ["最新", "最近", "2024", "2025", "recently", "latest", "new"]
        if any(keyword in response for keyword in recent_keywords):
            score += 10.0

        old_keywords = ["早期", "过去", "传统", "older", "traditional", "past"]
        if any(keyword in response for keyword in old_keywords):
            score -= 5.0

        version_mentions = re.findall(r'(GPT-\d+|Claude-\d+|Llama-\d+)', response, re.IGNORECASE)
        if version_mentions:
            score += 5.0

        outdated_indicators = ["已过时", "不推荐", "deprecated", "outdated"]
        if any(indicator in response.lower() for indicator in outdated_indicators):
            score -= 10.0

        return min(100.0, max(0.0, score))

    def _calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """计算综合得分"""
        overall = 0.0

        for dimension_name, score in dimension_scores.items():
            if dimension_name in self.dimensions_config:
                weight = self.dimensions_config[dimension_name].get("weight", 0)
                overall += score * weight

        return round(overall, 2)

    def _identify_question_types(self, query: str) -> List[str]:
        """识别问题类型"""
        types = []

        if any(keyword in query for keyword in ["是什么", "什么是", "定义", "what is", "define"]):
            types.append("definition")
        if any(keyword in query for keyword in ["为什么", "原因", "why", "reason"]):
            types.append("reasoning")
        if any(keyword in query for keyword in ["如何", "怎么", "how", "方法"]):
            types.append("method")
        if any(keyword in query for keyword in ["比较", "对比", "difference", "compare"]):
            types.append("comparison")

        return types

    def _extract_technical_terms(self, text: str) -> List[str]:
        """提取技术术语"""
        terms = []

        technical_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'[\u4e00-\u9fa5]{2,}(?:机制|方法|模型|算法|技术|框架)'
        ]

        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)

        return list(set(terms))

    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        words = re.findall(r'[\w]+', text.lower())
        return words

    def _generate_detailed_scores(self, dimension_scores: Dict[str, float]) -> Dict:
        """生成详细评分说明"""
        detailed = {}

        for dimension_name, score in dimension_scores.items():
            dimension_info = self.dimensions_config.get(dimension_name, {})
            name = dimension_info.get("name", dimension_name)

            if score >= 85:
                level = "优秀"
            elif score >= 70:
                level = "良好"
            elif score >= 50:
                level = "一般"
            else:
                level = "较差"

            detailed[dimension_name] = {
                "name": name,
                "score": score,
                "level": level,
                "weight": dimension_info.get("weight", 0)
            }

        return detailed

    def _assign_grade(self, overall_score: float) -> str:
        """分配等级"""
        if overall_score >= self.score_thresholds.get("excellent", 85):
            return "A (优秀)"
        elif overall_score >= self.score_thresholds.get("good", 70):
            return "B (良好)"
        elif overall_score >= self.score_thresholds.get("needs_improvement", 50):
            return "C (需改进)"
        else:
            return "D (较差)"


def main():
    """测试函数"""
    evaluator = QualityEvaluator("config/config.json")

    test_query = "请解释一下Transformer的工作原理"
    test_response = "Transformer是一种基于注意力机制的模型架构..."

    result = evaluator.evaluate(test_query, test_response, {})

    print("质量评估结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
