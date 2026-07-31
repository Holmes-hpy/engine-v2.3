#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
对话历史获取与分析模块
从对话中提取关键信息并分类
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class ConversationAnalyzer:
    """对话分析器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.conversation_types = self.config.get("conversation_types", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def analyze(self, user_query: str, assistant_response: str, user_feedback: str = "") -> Dict:
        """分析对话"""
        if not user_query and not assistant_response:
            return {
                "type": "unknown",
                "key_info": {},
                "user_terms": [],
                "context": "",
                "timestamp": datetime.now().isoformat()
            }

        conversation_data = {
            "user_query": user_query,
            "assistant_response": assistant_response,
            "user_feedback": user_feedback,
            "type": self._classify_conversation(user_query),
            "key_info": self._extract_key_info(user_query, assistant_response),
            "user_terms": self._extract_user_terms(user_query),
            "context": self._analyze_context(user_query),
            "sentiment": self._analyze_sentiment(user_query),
            "complexity": self._assess_complexity(user_query),
            "timestamp": datetime.now().isoformat()
        }

        return conversation_data

    def _classify_conversation(self, user_query: str) -> str:
        """对话分类"""
        query_lower = user_query.lower()

        technical_keywords = [
            "原理", "机制", "是什么", "how", "what", "why",
            "算法", "模型", "架构", "实现", "原理", "概念",
            "transformer", "attention", "neural", "network"
        ]
        if any(keyword in query_lower for keyword in technical_keywords):
            return self.conversation_types.get("technical", "技术咨询类")

        problem_keywords = [
            "怎么", "如何", "怎么办", "solve", "fix", "解决",
            "问题", "错误", "bug", "issue", "error", "失败"
        ]
        if any(keyword in query_lower for keyword in problem_keywords):
            return self.conversation_types.get("problem_solving", "问题解决类")

        research_keywords = [
            "论文", "paper", "研究", "研究", "文献", "arxiv",
            "解读", "分析", "survey", "review"
        ]
        if any(keyword in query_lower for keyword in research_keywords):
            return self.conversation_types.get("research_support", "研究支持类")

        industry_keywords = [
            "趋势", "市场", "厂商", "行业", "动态", "前景",
            "趋势", "trends", "market", "industry", "company"
        ]
        if any(keyword in query_lower for keyword in industry_keywords):
            return self.conversation_types.get("industry_analysis", "行业分析类")

        return self.conversation_types.get("other", "其他类")

    def _extract_key_info(self, user_query: str, assistant_response: str) -> Dict:
        """提取关键信息"""
        key_info = {
            "main_topic": self._extract_main_topic(user_query),
            "technical_concepts": self._extract_technical_concepts(user_query + " " + assistant_response),
            "specific_technologies": self._extract_specific_technologies(user_query),
            "user_intent": self._extract_user_intent(user_query),
            "required_depth": self._assess_required_depth(user_query)
        }

        return key_info

    def _extract_main_topic(self, text: str) -> str:
        """提取主题"""
        topics = {
            "大语言模型": ["llm", "language model", "大模型", "gpt", "bert", "transformer"],
            "训练技术": ["training", "训练", "fine-tuning", "微调", "pre-training", "预训练"],
            "推理优化": ["inference", "推理", "deployment", "部署", "optimization", "优化"],
            "提示工程": ["prompt", "提示", "engineering", "工程", "few-shot", "fewshot"],
            "评估测试": ["evaluation", "评估", "benchmark", "测试", "metric", "指标"],
            "应用开发": ["application", "应用", "开发", "api", "implementation", "实现"]
        }

        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic

        return "其他"

    def _extract_technical_concepts(self, text: str) -> List[str]:
        """提取技术概念"""
        concepts = []
        technical_patterns = [
            r'\b(Transformer|Attention|Self-Attention|Multi-Head Attention)\b',
            r'\b(Large Language Model|LLM|GPT|BERT|Encoder|Decoder)\b',
            r'\b(Fine-tuning|Pre-training|RLHF|Instruction Tuning)\b',
            r'\b(Prompt Engineering|Few-shot|Zero-shot|CoT)\b',
            r'\b(RAG|Retrieval|Augmented|Generation)\b',
            r'\b(Quantization|Pruning|Knowledge Distillation)\b'
        ]

        text_combined = text + " " + self._extract_chinese_concepts(text)
        for pattern in technical_patterns:
            matches = re.findall(pattern, text_combined, re.IGNORECASE)
            concepts.extend([m.strip() for m in matches])

        return list(set(concepts))

    def _extract_chinese_concepts(self, text: str) -> str:
        """提取中文技术概念"""
        concepts = []
        chinese_concept_map = {
            "注意力机制": ["注意力", "attention"],
            "Transformer": ["transformer"],
            "大语言模型": ["大模型", "llm"],
            "微调": ["微调", "fine-tuning"],
            "预训练": ["预训练", "pre-training"],
            "提示工程": ["提示工程", "prompt"],
            "检索增强生成": ["rag", "检索增强"],
            "量化": ["量化", "quantization"]
        }

        for concept, keywords in chinese_concept_map.items():
            if any(keyword in text.lower() for keyword in keywords):
                concepts.append(concept)

        return " ".join(concepts)

    def _extract_specific_technologies(self, text: str) -> List[str]:
        """提取具体技术"""
        technologies = []

        tech_patterns = [
            (r'GPT-(\d)', r'GPT-\1'),
            (r'Claude-(\d)', r'Claude-\1'),
            (r'Llama-(\d)', r'Llama-\1'),
            (r'(\d+)B', r'\1B模型'),
            (r'(\d+)B参数', r'\1B参数模型')
        ]

        for pattern, replacement in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                tech = re.sub(pattern, replacement, match, flags=re.IGNORECASE)
                technologies.append(tech)

        return list(set(technologies))

    def _extract_user_intent(self, user_query: str) -> str:
        """提取用户意图"""
        query = user_query.strip()

        if query.startswith(("如何", "怎么", "怎样")):
            return "请求操作指导"
        elif "?" in query or "？" in query:
            if "为什么" in query:
                return "请求原因解释"
            elif "是什么" in query:
                return "请求定义解释"
            else:
                return "请求信息"
        elif any(keyword in query for keyword in ["请", "帮我", "想"]):
            return "请求帮助"
        elif any(keyword in query for keyword in ["比较", "对比"]):
            return "请求对比分析"
        elif any(keyword in query for keyword in ["推荐", "建议"]):
            return "请求推荐建议"

        return "其他意图"

    def _assess_required_depth(self, user_query: str) -> str:
        """评估所需深度"""
        query = user_query.lower()

        deep_keywords = ["详细", "深入", "全面", "具体", "详细解释", "thorough", "detailed"]
        if any(keyword in query for keyword in deep_keywords):
            return "深度"

        brief_keywords = ["简单", "简要", "概括", "大概", "brief", "summary"]
        if any(keyword in query for keyword in brief_keywords):
            return "浅显"

        if len(user_query) > 100:
            return "深度"

        return "中等"

    def _extract_user_terms(self, user_query: str) -> List[str]:
        """提取用户使用的专业术语"""
        terms = []

        chinese_terms = re.findall(r'[\u4e00-\u9fa5]{2,}', user_query)
        terms.extend([t for t in chinese_terms if len(t) >= 2])

        english_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', user_query)
        terms.extend(english_terms)

        return list(set(terms))[:10]

    def _analyze_context(self, user_query: str) -> str:
        """分析上下文"""
        context_markers = {
            "multi_turn": ["之前", "刚才", "继续", "还有", "另外", "previous", "continue"],
            "followup": ["追问", "为什么", "详细", "further", "more"],
            "context_dependent": ["这个", "那个", "它", "this", "that", "it"]
        }

        detected_context = []
        for context_type, markers in context_markers.items():
            if any(marker in user_query.lower() for marker in markers):
                detected_context.append(context_type)

        return ", ".join(detected_context) if detected_context else "single_turn"

    def _analyze_sentiment(self, text: str) -> str:
        """分析情感"""
        positive_markers = ["谢谢", "好", "棒", "不错", "感谢", "helpful", "good"]
        negative_markers = ["不对", "错误", "差", "不好", "糟糕", "wrong", "bad", "terrible"]

        text_lower = text.lower()
        if any(marker in text_lower for marker in positive_markers):
            return "positive"
        elif any(marker in text_lower for marker in negative_markers):
            return "negative"

        return "neutral"

    def _assess_complexity(self, text: str) -> str:
        """评估复杂度"""
        words = text.split()
        sentence_count = len(re.findall(r'[。.!?]', text))

        if len(words) > 50 or sentence_count > 3:
            return "high"
        elif len(words) > 20 or sentence_count > 1:
            return "medium"

        return "low"


def main():
    """测试函数"""
    analyzer = ConversationAnalyzer("config/config.json")

    test_query = "请详细解释一下Transformer的注意力机制是如何工作的"
    test_response = "Transformer使用自注意力机制..."

    result = analyzer.analyze(test_query, test_response)

    print("对话分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
