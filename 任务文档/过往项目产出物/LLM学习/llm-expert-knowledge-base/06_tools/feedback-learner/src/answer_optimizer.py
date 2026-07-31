#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
回答优化器
根据质量评估和用户反馈，优化回答策略
"""

import json
from pathlib import Path


class AnswerOptimizer:
    """回答优化器"""
    
    def __init__(self, config_path):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def optimize(self, user_query, assistant_response, quality_scores, 
                feedback_analysis, conversation_data):
        """优化回答"""
        suggestions = []
        preference_update = False
        
        # 根据质量得分生成优化建议
        dimensions = quality_scores.get("dimensions", {})
        
        if dimensions.get("accuracy", 100) < 70:
            suggestions.append("提高回答准确性，验证关键信息")
        
        if dimensions.get("completeness", 100) < 70:
            suggestions.append("增加回答完整性，覆盖更多相关方面")
        
        if dimensions.get("clarity", 100) < 70:
            suggestions.append("优化表述清晰度，改善逻辑结构")
        
        if dimensions.get("practicality", 100) < 70:
            suggestions.append("增强实用性，提供可操作建议")
        
        # 根据用户反馈生成建议
        feedback_type = feedback_analysis.get("type", "none")
        if feedback_type == "negative":
            suggestions.append("分析负面反馈原因，改进回答策略")
        elif feedback_type == "followup":
            suggestions.append("增加回答深度，提供更详细的解释")
        
        return {
            "suggestions": suggestions,
            "preference_update": preference_update,
            "optimization_notes": "根据质量评估和反馈生成优化建议"
        }
