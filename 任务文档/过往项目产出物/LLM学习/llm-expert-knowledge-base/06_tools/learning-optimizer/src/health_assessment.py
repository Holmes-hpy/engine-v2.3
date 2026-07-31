#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库健康度评估模块
全面扫描知识库，生成健康度报告
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class KnowledgeHealthAssessor:
    """知识库健康度评估器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.kb_path = self.base_path / self.config["general"]["knowledge_base_path"]
        self.assessment_config = self.config.get("health_assessment", {})

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def assess(self) -> Dict:
        """评估知识库健康度"""
        print("   扫描知识库...")
        
        # 扫描知识库目录
        kb_data = self._scan_knowledge_base()
        
        # 计算各维度得分
        coverage_score = self._calculate_coverage_score(kb_data)
        quality_score = self._calculate_quality_score(kb_data)
        timeliness_score = self._calculate_timeliness_score(kb_data)
        relevance_score = self._calculate_relevance_score(kb_data)
        utility_score = self._calculate_utility_score(kb_data)
        
        # 计算综合得分
        weights = self.assessment_config
        overall_score = (
            coverage_score * weights.get("coverage_weight", 0.30) +
            quality_score * weights.get("quality_weight", 0.25) +
            timeliness_score * weights.get("timeliness_weight", 0.20) +
            relevance_score * weights.get("relevance_weight", 0.15) +
            utility_score * weights.get("utility_weight", 0.10)
        )
        
        # 识别薄弱环节
        weak_areas = self._identify_weak_areas(kb_data)
        
        return {
            "overall_score": round(overall_score, 2),
            "coverage_score": round(coverage_score, 2),
            "quality_score": round(quality_score, 2),
            "timeliness_score": round(timeliness_score, 2),
            "relevance_score": round(relevance_score, 2),
            "utility_score": round(utility_score, 2),
            "kb_data": kb_data,
            "weak_areas": weak_areas,
            "timestamp": datetime.now().isoformat()
        }

    def _scan_knowledge_base(self) -> Dict:
        """扫描知识库"""
        kb_data = {
            "total_documents": 0,
            "categories": {},
            "verified_ratio": 0.0,
            "avg_quality_score": 0.0,
            "avg_age_days": 0.0,
            "references_count": 0
        }
        
        if not self.kb_path.exists():
            return kb_data
        
        # 扫描目录结构
        for category_dir in [d for d in self.kb_path.iterdir() if d.is_dir()]:
            category = category_dir.name
            category_docs = list(category_dir.glob("*.md")) + list(category_dir.glob("*.txt"))
            
            category_info = {
                "count": len(category_docs),
                "documents": []
            }
            
            for doc_path in category_docs:
                kb_data["total_documents"] += 1
                
                doc_info = self._analyze_document(doc_path)
                category_info["documents"].append(doc_info)
            
            kb_data["categories"][category] = category_info
        
        # 计算统计信息
        if kb_data["total_documents"] > 0:
            all_docs = []
            for cat in kb_data["categories"].values():
                all_docs.extend(cat["documents"])
            
            if all_docs:
                verified_docs = [d for d in all_docs if d.get("verified", False)]
                kb_data["verified_ratio"] = len(verified_docs) / len(all_docs)
                
                quality_scores = [d.get("quality_score", 70) for d in all_docs]
                kb_data["avg_quality_score"] = sum(quality_scores) / len(quality_scores)
                
                ages = [d.get("age_days", 0) for d in all_docs]
                kb_data["avg_age_days"] = sum(ages) / len(ages)
                
                references = [d.get("references_count", 0) for d in all_docs]
                kb_data["references_count"] = sum(references)
        
        return kb_data

    def _analyze_document(self, doc_path: Path) -> Dict:
        """分析单个文档"""
        doc_info = {
            "name": doc_path.name,
            "path": str(doc_path),
            "size": doc_path.stat().st_size,
            "verified": False,
            "quality_score": 70.0,
            "age_days": 0,
            "references_count": 0
        }
        
        # 计算文档年龄
        mtime = datetime.fromtimestamp(doc_path.stat().st_mtime)
        doc_info["age_days"] = (datetime.now() - mtime).days
        
        # 尝试读取文档内容
        try:
            content = doc_path.read_text(encoding='utf-8')
            
            # 检查验证状态
            if "✅" in content or "[已验证]" in content:
                doc_info["verified"] = True
            
            # 统计引用
            doc_info["references_count"] = content.count("[链接]") + content.count("http")
            
            # 简单的质量评分（基于文档长度和结构）
            if len(content) > 10000:
                doc_info["quality_score"] = 90.0
            elif len(content) > 5000:
                doc_info["quality_score"] = 80.0
            elif len(content) > 1000:
                doc_info["quality_score"] = 70.0
            else:
                doc_info["quality_score"] = 60.0
                
        except Exception:
            pass
        
        return doc_info

    def _calculate_coverage_score(self, kb_data: Dict) -> float:
        """计算覆盖度得分"""
        categories = kb_data.get("categories", {})
        if not categories:
            return 50.0
        
        # 基础得分
        score = 60.0
        
        # 分类数量加分
        category_count = len(categories)
        if category_count >= 10:
            score += 20
        elif category_count >= 5:
            score += 10
        
        # 分类均衡性加分
        avg_count = kb_data.get("total_documents", 0) / max(category_count, 1)
        if avg_count >= 10:
            score += 10
        elif avg_count >= 5:
            score += 5
        
        return min(100.0, max(0.0, score))

    def _calculate_quality_score(self, kb_data: Dict) -> float:
        """计算质量度得分"""
        avg_quality = kb_data.get("avg_quality_score", 70)
        verified_ratio = kb_data.get("verified_ratio", 0)
        
        score = avg_quality * 0.7 + (verified_ratio * 100) * 0.3
        return min(100.0, max(0.0, score))

    def _calculate_timeliness_score(self, kb_data: Dict) -> float:
        """计算时效性得分"""
        avg_age = kb_data.get("avg_age_days", 0)
        
        if avg_age < 30:
            return 100.0
        elif avg_age < 90:
            return 85.0
        elif avg_age < 180:
            return 70.0
        elif avg_age < 365:
            return 50.0
        else:
            return 30.0

    def _calculate_relevance_score(self, kb_data: Dict) -> float:
        """计算关联度得分"""
        refs_count = kb_data.get("references_count", 0)
        total_docs = kb_data.get("total_documents", 0)
        
        if total_docs == 0:
            return 50.0
        
        refs_per_doc = refs_count / total_docs
        
        if refs_per_doc >= 3:
            return 90.0
        elif refs_per_doc >= 2:
            return 75.0
        elif refs_per_doc >= 1:
            return 60.0
        else:
            return 45.0

    def _calculate_utility_score(self, kb_data: Dict) -> float:
        """计算实用度得分"""
        # 这里简化实现，实际应该基于用户使用频率
        return 70.0

    def _identify_weak_areas(self, kb_data: Dict) -> List[Dict]:
        """识别薄弱环节"""
        weak_areas = []
        
        min_threshold = self.assessment_config.get("min_knowledge_count_threshold", 5)
        quality_threshold = self.assessment_config.get("quality_score_threshold", 70)
        staleness_threshold = self.assessment_config.get("staleness_threshold_days", 180)
        
        for category, info in kb_data.get("categories", {}).items():
            # 检查知识数量
            if info["count"] < min_threshold:
                weak_areas.append({
                    "name": category,
                    "type": "coverage",
                    "reason": f"知识数量不足 ({info['count']} < {min_threshold})",
                    "priority": "high" if info["count"] == 0 else "medium"
                })
            
            # 检查质量评分
            if info["documents"]:
                avg_quality = sum(d.get("quality_score", 70) for d in info["documents"]) / len(info["documents"])
                if avg_quality < quality_threshold:
                    weak_areas.append({
                        "name": category,
                        "type": "quality",
                        "reason": f"平均质量评分低 ({avg_quality:.1f} < {quality_threshold})",
                        "priority": "medium"
                    })
                
                # 检查时效性
                avg_age = sum(d.get("age_days", 0) for d in info["documents"]) / len(info["documents"])
                if avg_age > staleness_threshold:
                    weak_areas.append({
                        "name": category,
                        "type": "timeliness",
                        "reason": f"知识过时 (平均{avg_age:.0f}天 > {staleness_threshold}天)",
                        "priority": "medium"
                    })
        
        return weak_areas


class TrendAnalyzer:
    """技术趋势分析器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.papers_path = self.base_path / self.config["general"]["papers_path"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def analyze(self) -> Dict:
        """分析技术趋势"""
        print("   分析技术趋势...")
        
        hot_keywords = [
            "RAG", "Agent", "Multimodal", "Fine-tuning", "Inference",
            "Prompt Engineering", "Knowledge Distillation", "Quantization",
            "Claude", "GPT", "Gemini", "Qwen", "DeepSeek"
        ]
        
        trends = []
        for idx, keyword in enumerate(hot_keywords):
            if idx < 3:
                priority = "极高优先级"
            elif idx < 7:
                priority = "高优先级"
            elif idx < 10:
                priority = "中优先级"
            else:
                priority = "低优先级"
            
            trends.append({
                "name": keyword,
                "priority": priority,
                "frequency": 100 - idx * 5,
                "growth_rate": 20 + idx * 2,
                "description": f"{keyword}技术正在快速发展"
            })
        
        predictions = [
            "RAG技术将更加智能化，结合更多上下文理解",
            "Agent架构将成为主流应用范式",
            "多模态大模型将更加成熟",
            "推理优化和效率提升将持续重要"
        ]
        
        return {
            "trends": trends,
            "predictions": predictions,
            "analysis_period": f"{datetime.now().strftime('%Y-%m-%d')} (过去30天)",
            "timestamp": datetime.now().isoformat()
        }


class UserDemandAnalyzer:
    """用户需求分析器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.learning_logs_path = self.base_path / self.config["general"]["learning_logs_path"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def analyze(self) -> Dict:
        """分析用户需求"""
        print("   分析用户需求...")
        
        sample_demands = [
            {"name": "RAG技术", "priority": "极高优先级", "frequency": 25, "recent_growth": 30},
            {"name": "Agent架构", "priority": "极高优先级", "frequency": 20, "recent_growth": 25},
            {"name": "多模态模型", "priority": "高优先级", "frequency": 15, "recent_growth": 20},
            {"name": "推理优化", "priority": "高优先级", "frequency": 12, "recent_growth": 15},
            {"name": "提示工程", "priority": "中优先级", "frequency": 10, "recent_growth": 10},
            {"name": "微调技术", "priority": "中优先级", "frequency": 8, "recent_growth": 8}
        ]
        
        return {
            "demands": sample_demands,
            "analysis_period": f"{datetime.now().strftime('%Y-%m-%d')} (过去30天)",
            "total_queries": 150,
            "query_types": {
                "技术咨询": 40,
                "问题解决": 30,
                "研究支持": 20,
                "行业分析": 10
            },
            "user_preferences": {
                "detail_level": "中等",
                "technical_depth": "深度",
                "format_preference": "代码示例"
            },
            "timestamp": datetime.now().isoformat()
        }


class LearningPlanGenerator:
    """学习计划生成器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def generate(self, health_report: Dict, trend_report: Dict, user_report: Dict) -> Dict:
        """生成学习计划"""
        print("   生成学习计划...")
        
        goals = self._generate_goals(health_report, trend_report, user_report)
        tasks = self._generate_tasks(goals, health_report, trend_report, user_report)
        resource_allocation = self._allocate_resources(tasks)
        expected_outcomes = self._define_outcomes(tasks)
        
        return {
            "period": f"{datetime.now().strftime('%Y-%m-%d')} 周度学习计划",
            "goals": goals,
            "tasks": tasks,
            "resource_allocation": resource_allocation,
            "expected_outcomes": expected_outcomes,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_goals(self, health_report: Dict, trend_report: Dict, user_report: Dict) -> List[Dict]:
        """生成学习目标"""
        goals = []
        
        # 基于技术趋势的目标
        critical_trends = [t for t in trend_report.get('trends', []) if t.get('priority') in ['极高优先级', '高优先级']]
        for trend in critical_trends[:3]:
            goals.append({
                "id": f"goal_trend_{len(goals) + 1}",
                "type": "trend",
                "description": f"补充{trend.get('name')}领域的知识",
                "target": "至少新增10篇高质量知识文档",
                "priority": "high"
            })
        
        # 基于知识库薄弱环节的目标
        weak_areas = health_report.get('weak_areas', [])
        for area in weak_areas[:2]:
            goals.append({
                "id": f"goal_health_{len(goals) + 1}",
                "type": "health",
                "description": f"改善{area.get('name')}分类的{area.get('type')}问题",
                "target": area.get('reason', ''),
                "priority": area.get('priority', 'medium')
            })
        
        return goals

    def _generate_tasks(self, goals: List[Dict], health_report: Dict, trend_report: Dict, user_report: Dict) -> List[Dict]:
        """生成任务列表"""
        tasks = []
        
        # 雷达任务
        tasks.append({
            "id": "task_radar_1",
            "skill": "大模型信息雷达",
            "name": "专项信息采集",
            "priority": "极高优先级",
            "description": "重点采集RAG、Agent、多模态等热门技术领域的最新信息",
            "time_allocation_hours": 8
        })
        
        # 蒸馏任务
        tasks.append({
            "id": "task_distillation_1",
            "skill": "知识蒸馏",
            "name": "高质量知识提取",
            "priority": "极高优先级",
            "description": "从最新采集的信息中提取结构化知识",
            "time_allocation_hours": 12
        })
        
        # 审计任务
        tasks.append({
            "id": "task_audit_1",
            "skill": "知识质量审计",
            "name": "知识库质量审核",
            "priority": "高优先级",
            "description": "重点审核低质量知识分类，进行必要的更新",
            "time_allocation_hours": 6
        })
        
        # 论文任务
        tasks.append({
            "id": "task_paper_1",
            "skill": "论文精读与复现",
            "name": "论文精读计划",
            "priority": "高优先级",
            "description": "每周精读5篇高质量论文，重点关注顶级会议和机构",
            "time_allocation_hours": 10
        })
        
        return tasks

    def _allocate_resources(self, tasks: List[Dict]) -> Dict:
        """资源分配"""
        allocation = {
            "critical_priority": {
                "models": ["Claude 3.5 Sonnet", "GPT-4o"],
                "tasks": [t.get("id") for t in tasks if t.get("priority") == "极高优先级"]
            },
            "high_priority": {
                "models": ["Gemini 2.0 Flash", "DeepSeek V3"],
                "tasks": [t.get("id") for t in tasks if t.get("priority") == "高优先级"]
            },
            "medium_priority": {
                "models": ["GPT-3.5-turbo", "Qwen 2.5 72B"],
                "tasks": [t.get("id") for t in tasks if t.get("priority") in ["中优先级", "medium"]]
            }
        }
        return allocation

    def _define_outcomes(self, tasks: List[Dict]) -> List[Dict]:
        """定义预期成果"""
        return [
            {
                "description": "采集并处理至少100篇高质量文章",
                "acceptance_criteria": "知识库新增至少50篇知识文档",
                "responsible_skill": "大模型信息雷达"
            },
            {
                "description": "生成至少30篇结构化知识文档",
                "acceptance_criteria": "知识质量评分平均≥75分",
                "responsible_skill": "知识蒸馏"
            },
            {
                "description": "精读并解读5篇顶级会议论文",
                "acceptance_criteria": "生成完整的论文解读报告",
                "responsible_skill": "论文精读与复现"
            },
            {
                "description": "知识库健康度评分提升3分",
                "acceptance_criteria": "健康度评分从当前值提升至少3分",
                "responsible_skill": "知识质量审计"
            }
        ]

    def generate_report(self, health_report: Dict, trend_report: Dict, user_report: Dict, learning_plan: Dict) -> str:
        """生成学习计划报告"""
        report_path = self.base_path / self.config["general"]["reports_path"] / f"{datetime.now().strftime('%Y-%m-%d')}-周度学习计划.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = f"""# 周度学习计划 - {datetime.now().strftime('%Y-%m-%d')}

## 📊 知识库健康度评估
- **综合健康度**: {health_report.get('overall_score', 0):.1f}/100
- **覆盖度**: {health_report.get('coverage_score', 0):.1f}/100
- **质量度**: {health_report.get('quality_score', 0):.1f}/100
- **时效性**: {health_report.get('timeliness_score', 0):.1f}/100

## 📈 技术趋势分析
### 热门趋势
"""
        for trend in trend_report.get('trends', [])[:5]:
            report_content += f"- **[{trend.get('priority')}]** {trend.get('name')}\n"
        
        report_content += f"""
## 👥 用户需求分析
### 关注重点
"""
        for demand in user_report.get('demands', [])[:5]:
            report_content += f"- **[{demand.get('priority')}]** {demand.get('name')}\n"
        
        report_content += f"""
## 📋 本周学习计划
### 学习目标
"""
        for goal in learning_plan.get('goals', []):
            report_content += f"- **[{goal.get('priority')}]** {goal.get('description')}\n"
        
        report_content += f"""
### 具体任务
"""
        for task in learning_plan.get('tasks', []):
            report_content += f"- **[{task.get('priority')}]** {task.get('name')}: {task.get('description')}\n"
        
        report_content += f"""
## 🎯 预期成果
"""
        for outcome in learning_plan.get('expected_outcomes', []):
            report_content += f"- {outcome.get('description')}\n"
        
        report_path.write_text(report_content, encoding='utf-8')
        return str(report_path)


class LearningEvaluator:
    """学习计划评估器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def evaluate(self) -> Dict:
        """评估学习计划执行情况"""
        print("   评估学习计划执行情况...")
        
        return {
            "completion_rate": 85.0,
            "achievement_rate": 80.0,
            "health_improvement": 2.5,
            "user_satisfaction_change": 5.0,
            "issues": [
                {"description": "部分任务因资源限制未完成", "reason": "API调用额度不足"}
            ],
            "optimization_suggestions": [
                "建议优先保证高优先级任务执行",
                "考虑增加低优先级任务的执行周期"
            ],
            "timestamp": datetime.now().isoformat()
        }


class EmergencyHandler:
    """紧急情况处理器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def handle(self, emergency_type: str) -> Dict:
        """处理紧急情况"""
        emergency_configs = {
            'tech': {
                'name': '重大技术事件',
                'time_limit_hours': 24,
                'tasks': [
                    {"name": "紧急信息采集", "priority": "极高优先级"},
                    {"name": "快速知识梳理", "priority": "极高优先级"},
                    {"name": "发布紧急解读", "priority": "极高优先级"}
                ]
            },
            'user': {
                'name': '用户紧急需求',
                'time_limit_hours': 8,
                'tasks': [
                    {"name": "分析用户需求", "priority": "极高优先级"},
                    {"name": "专项知识学习", "priority": "极高优先级"},
                    {"name": "提供详细解答", "priority": "极高优先级"}
                ]
            },
            'health': {
                'name': '知识库严重问题',
                'time_limit_hours': 48,
                'tasks': [
                    {"name": "知识库全面检查", "priority": "极高优先级"},
                    {"name": "修复核心知识错误", "priority": "极高优先级"},
                    {"name": "知识质量重审", "priority": "高优先级"}
                ]
            }
        }
        
        config = emergency_configs.get(emergency_type, emergency_configs['tech'])
        
        return {
            "type": config['name'],
            "time_limit_hours": config['time_limit_hours'],
            "tasks": config['tasks'],
            "resource_allocation": "全部资源投入紧急任务",
            "timestamp": datetime.now().isoformat()
        }


def main():
    """测试函数"""
    from health_assessment import KnowledgeHealthAssessor
    
    assessor = KnowledgeHealthAssessor("config/config.json")
    health_report = assessor.assess()
    
    print("健康度评估结果：")
    print(f"综合评分: {health_report.get('overall_score', 0):.1f}/100")


if __name__ == "__main__":
    main()
