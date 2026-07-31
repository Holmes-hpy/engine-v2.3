"""
Serenity瓶颈投资 - 公告深度解读模块
专业的上市公司公告解读与证据验证

功能：
1. 公告分类与重要性评级
2. 订单/合同/合作深度解析
3. 资本开支/产能扩张验证
4. 客户认证/定点验证
5. 业绩预告/经营数据验证
6. 股权激励/管理层信心验证

证据等级：
- 强证据：正式订单合同、定点函、量产协议
- 中证据：送样验证、小批量试产、客户考察
- 弱证据：战略规划、媒体报道、券商研报
"""

import sys
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.stock_data import cninfo_announcements
    ANNOUNCEMENT_AVAILABLE = True
except ImportError:
    ANNOUNCEMENT_AVAILABLE = False


class AnnouncementCategory(Enum):
    """公告类别"""
    ORDER_CONTRACT = "订单合同"
    COOPERATION = "合作协议"
    CAPEX_EXPANSION = "资本开支/产能扩张"
    CUSTOMER_CERTIFICATION = "客户认证/定点"
    PERFORMANCE = "业绩预告/经营数据"
    EQUITY_INCENTIVE = "股权激励"
    INDUSTRY_POLICY = "行业政策"
    MATERIAL_PROGRESS = "重大事项进展"
    OTHER = "其他"


class EvidenceStrength(Enum):
    """证据强度"""
    STRONG = "强"
    MEDIUM = "中"
    WEAK = "弱"


@dataclass
class AnnouncementAnalysis:
    """单条公告分析结果"""
    title: str
    category: AnnouncementCategory
    date: str
    evidence_strength: EvidenceStrength
    importance_score: int  # 0-100
    key_info: Dict = field(default_factory=dict)
    summary: str = ""


@dataclass
class EvidenceVerificationResult:
    """证据验证综合结果"""
    stock_code: str
    stock_name: str
    total_announcements: int = 0
    strong_evidence_count: int = 0
    medium_evidence_count: int = 0
    weak_evidence_count: int = 0
    evidence_level: str = "弱"
    overall_score: int = 0  # 0-100
    key_announcements: List[AnnouncementAnalysis] = field(default_factory=list)
    verification_summary: str = ""
    key_findings: List[str] = field(default_factory=list)


# ============================================================
# 公告关键词库
# ============================================================

ANNOUNCEMENT_KEYWORDS = {
    AnnouncementCategory.ORDER_CONTRACT: {
        "keywords": [
            "签订合同", "签署合同", "重大合同", "日常经营合同",
            "中标", "中标通知书", "订单", "大额订单",
            "供货协议", "采购协议", "销售合同",
            "框架协议", "战略合作协议",
        ],
        "strength_patterns": [
            (r"金额[约]?\s*[\d.]+\s*[万亿]", 10),
            (r"占.*营收.*?\s*[\d.]+%", 15),
            (r"客户名称.*(英伟达|华为|特斯拉|苹果|三星|台积电)", 20),
        ],
        "importance": 80,
    },
    AnnouncementCategory.COOPERATION: {
        "keywords": [
            "战略合作", "合作协议", "签署协议",
            "联合研发", "技术合作", "产学研",
            "战略合作框架", "产业合作",
        ],
        "strength_patterns": [
            (r"合资公司", 10),
            (r"深度合作", 5),
        ],
        "importance": 60,
    },
    AnnouncementCategory.CAPEX_EXPANSION: {
        "keywords": [
            "扩产", "产能扩张", "新建产能", "扩产项目",
            "投资建设", "固定资产投资", "项目投资",
            "产能建设", "增产", "产能释放",
            "资本开支", "募投项目",
        ],
        "strength_patterns": [
            (r"投资.*金额.*[\d.]+\s*[万亿]", 15),
            (r"产能.*增加", 10),
            (r"建设期.*\d+\s*月", 5),
        ],
        "importance": 70,
    },
    AnnouncementCategory.CUSTOMER_CERTIFICATION: {
        "keywords": [
            "通过认证", "客户认证", "供应商认证",
            "定点", "入选供应商", "合格供应商",
            "送样", "验证通过", "小批量供货",
            "量产", "批量供货",
        ],
        "strength_patterns": [
            (r"国际.*客户", 20),
            (r"通过.*认证", 15),
            (r"正式供货", 10),
            (r"小批量", 5),
        ],
        "importance": 75,
    },
    AnnouncementCategory.PERFORMANCE: {
        "keywords": [
            "业绩预告", "业绩快报", "业绩预告",
            "经营数据", "月度经营", "季度业绩",
            "营收", "净利润",
        ],
        "strength_patterns": [
            (r"增长.*\s*[\d.]+%", 15),
            (r"超预期", 10),
            (r"扭亏为盈", 10),
        ],
        "importance": 65,
    },
    AnnouncementCategory.EQUITY_INCENTIVE: {
        "keywords": [
            "股权激励", "员工持股", "股票期权", "限制性股票",
            "增持", "回购",
        ],
        "strength_patterns": [
            (r"业绩考核.*\d+%", 10),
            (r"行权价格", 5),
        ],
        "importance": 50,
    },
    AnnouncementCategory.INDUSTRY_POLICY: {
        "keywords": [
            "政策", "补贴", "扶持", "产业政策",
            "行业标准",
        ],
        "strength_patterns": [],
        "importance": 40,
    },
    AnnouncementCategory.MATERIAL_PROGRESS: {
        "keywords": [
            "重大事项进展", "重组进展", "项目进展",
            "技术突破", "新产品", "研发进展",
        ],
        "strength_patterns": [
            (r"技术突破", 10),
            (r"填补.*空白", 15),
        ],
        "importance": 55,
    },
}


# ============================================================
# 公告解读引擎
# ============================================================

class AnnouncementDeepAnalyzer:
    """
    公告深度解读引擎

    专业分析上市公司公告，提取关键证据信息
    """

    def __init__(self):
        self.category_keywords = ANNOUNCEMENT_KEYWORDS

    def analyze_announcements(
        self,
        stock_code: str,
        stock_name: str = "",
        days: int = 180,
    ) -> EvidenceVerificationResult:
        """
        分析指定股票的公告，验证商业化证据

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            days: 分析天数

        Returns:
            EvidenceVerificationResult: 证据验证结果
        """
        result = EvidenceVerificationResult(
            stock_code=stock_code,
            stock_name=stock_name,
        )

        if not ANNOUNCEMENT_AVAILABLE:
            result.verification_summary = "公告数据接口不可用"
            return result

        try:
            # 获取公告
            announcements = cninfo_announcements(stock_code, days=days)
            result.total_announcements = len(announcements)

            if not announcements:
                result.verification_summary = "未找到相关公告"
                return result

            # 逐条分析
            for ann in announcements[:50]:  # 最多分析50条
                analysis = self._analyze_single_announcement(ann)
                if analysis:
                    result.key_announcements.append(analysis)

            # 统计证据强度
            for analysis in result.key_announcements:
                if analysis.evidence_strength == EvidenceStrength.STRONG:
                    result.strong_evidence_count += 1
                elif analysis.evidence_strength == EvidenceStrength.MEDIUM:
                    result.medium_evidence_count += 1
                else:
                    result.weak_evidence_count += 1

            # 计算综合评分
            result.overall_score = self._calculate_evidence_score(result)

            # 确定证据等级
            if result.strong_evidence_count >= 2:
                result.evidence_level = "强"
            elif result.strong_evidence_count >= 1 or result.medium_evidence_count >= 3:
                result.evidence_level = "中"
            else:
                result.evidence_level = "弱"

            # 生成摘要
            result.verification_summary = self._generate_summary(result)
            result.key_findings = self._extract_key_findings(result)

            # 按重要性排序
            result.key_announcements.sort(key=lambda x: x.importance_score, reverse=True)

        except Exception as e:
            result.verification_summary = f"公告分析出错: {str(e)}"

        return result

    def _analyze_single_announcement(self, ann: Dict) -> Optional[AnnouncementAnalysis]:
        """分析单条公告"""
        title = str(
            ann.get("announcementTitle", "")
            or ann.get("ann_title", "")
            or ann.get("title", "")
        )
        date = str(
            ann.get("announcementTime", "")
            or ann.get("ann_date", "")
            or ann.get("publish_time", "")
        )[:10]

        if not title:
            return None

        # 匹配分类
        best_category = AnnouncementCategory.OTHER
        best_score = 0
        best_config = None

        for category, config in self.category_keywords.items():
            score = 0
            for kw in config["keywords"]:
                if kw in title:
                    score += 10

            if score > best_score:
                best_score = score
                best_category = category
                best_config = config

        if best_category == AnnouncementCategory.OTHER:
            return None

        # 计算重要性评分
        importance = best_config["importance"] if best_config else 30

        # 强度模式匹配（需要摘要文本）
        summary = title
        strength_bonus = 0
        key_info = {}

        for pattern, bonus in best_config.get("strength_patterns", []):
            if re.search(pattern, title):
                strength_bonus += bonus
                match = re.search(pattern, title)
                if match:
                    key_info[pattern] = match.group(0)

        importance += strength_bonus
        importance = min(100, importance)

        # 确定证据强度
        if importance >= 80:
            strength = EvidenceStrength.STRONG
        elif importance >= 50:
            strength = EvidenceStrength.MEDIUM
        else:
            strength = EvidenceStrength.WEAK

        return AnnouncementAnalysis(
            title=title,
            category=best_category,
            date=date,
            evidence_strength=strength,
            importance_score=importance,
            key_info=key_info,
            summary=self._generate_announcement_summary(title, best_category, key_info),
        )

    def _generate_announcement_summary(
        self, title: str, category: AnnouncementCategory, key_info: Dict
    ) -> str:
        """生成公告摘要"""
        if category == AnnouncementCategory.ORDER_CONTRACT:
            return f"订单合同类公告：可能涉及重要客户或大额订单"
        elif category == AnnouncementCategory.CUSTOMER_CERTIFICATION:
            return f"客户认证类公告：验证客户拓展进展"
        elif category == AnnouncementCategory.CAPEX_EXPANSION:
            return f"产能扩张类公告：验证供给端增长动力"
        elif category == AnnouncementCategory.COOPERATION:
            return f"战略合作类公告：验证行业地位"
        elif category == AnnouncementCategory.PERFORMANCE:
            return f"业绩类公告：验证业绩兑现能力"
        elif category == AnnouncementCategory.EQUITY_INCENTIVE:
            return f"股权激励：验证管理层信心"
        else:
            return f"其他重要公告"

    def _calculate_evidence_score(self, result: EvidenceVerificationResult) -> int:
        """计算证据综合评分"""
        score = 0
        score += result.strong_evidence_count * 30
        score += result.medium_evidence_count * 15
        score += result.weak_evidence_count * 5

        # 时间衰减：近期公告权重更高
        # （简化处理，实际应该按时间加权）

        return min(100, score)

    def _generate_summary(self, result: EvidenceVerificationResult) -> str:
        """生成验证摘要"""
        parts = []
        parts.append(f"近180天共{result.total_announcements}条公告")
        parts.append(f"强证据{result.strong_evidence_count}条")
        parts.append(f"中证据{result.medium_evidence_count}条")

        if result.evidence_level == "强":
            parts.append("商业化验证充分")
        elif result.evidence_level == "中":
            parts.append("商业化验证中等")
        else:
            parts.append("商业化验证不足，需持续跟踪")

        return "，".join(parts)

    def _extract_key_findings(self, result: EvidenceVerificationResult) -> List[str]:
        """提取关键发现"""
        findings = []

        # 按类别统计
        category_count = {}
        for ann in result.key_announcements:
            cat = ann.category.value
            category_count[cat] = category_count.get(cat, 0) + 1

        for cat, count in sorted(category_count.items(), key=lambda x: -x[1]):
            findings.append(f"{cat}: {count}条")

        # 最强证据
        strong_anns = [a for a in result.key_announcements if a.evidence_strength == EvidenceStrength.STRONG]
        if strong_anns:
            findings.append(f"最强证据: {strong_anns[0].title[:30]}...")

        return findings


# ============================================================
# 多维度证据验证器
# ============================================================

class MultiDimensionalEvidenceVerifier:
    """
    多维度证据验证器

    从多个维度交叉验证瓶颈投资逻辑：
    1. 公告维度
    2. 财务维度
    3. 研报维度
    4. 资金维度
    """

    def __init__(self):
        self.announcement_analyzer = AnnouncementDeepAnalyzer()

    def verify(
        self,
        stock_code: str,
        stock_name: str = "",
        stock_data=None,
    ) -> Dict:
        """
        多维度验证

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            stock_data: 股票数据对象

        Returns:
            Dict: 验证结果
        """
        result = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "overall_evidence_level": "弱",
            "overall_score": 0,
            "dimensions": {},
            "key_verification_points": [],
        }

        # 1. 公告维度
        try:
            ann_result = self.announcement_analyzer.analyze_announcements(
                stock_code, stock_name
            )
            result["dimensions"]["announcement"] = {
                "level": ann_result.evidence_level,
                "score": ann_result.overall_score,
                "strong_count": ann_result.strong_evidence_count,
                "medium_count": ann_result.medium_evidence_count,
                "summary": ann_result.verification_summary,
            }
            if ann_result.key_findings:
                result["key_verification_points"].extend(ann_result.key_findings[:3])
        except Exception as e:
            result["dimensions"]["announcement"] = {
                "level": "待验证",
                "score": 0,
                "error": str(e),
            }

        # 2. 财务维度
        if stock_data and stock_data.financial:
            fin_score = 0
            fin_findings = []
            fin = stock_data.financial

            if fin.profit_growth > 50:
                fin_score += 25
                fin_findings.append(f"净利润增速{fin.profit_growth:.1f}%")
            elif fin.profit_growth > 20:
                fin_score += 15
                fin_findings.append(f"净利润增速{fin.profit_growth:.1f}%")

            if fin.revenue_growth > 30:
                fin_score += 20
                fin_findings.append(f"营收增速{fin.revenue_growth:.1f}%")

            if fin.gross_margin > 40:
                fin_score += 15
                fin_findings.append(f"毛利率{fin.gross_margin:.1f}%")

            fin_level = "强" if fin_score >= 50 else "中" if fin_score >= 25 else "弱"
            result["dimensions"]["financial"] = {
                "level": fin_level,
                "score": fin_score,
                "findings": fin_findings,
            }
            result["key_verification_points"].extend(fin_findings[:2])

        # 3. 研报维度
        if stock_data and stock_data.research:
            res_score = 0
            res = stock_data
            if res.research.report_count_3m > 20:
                res_score += 10
            elif res.research.covered_brokers > 10:
                res_score += 10

            res_level = "中" if res_score >= 15 else "弱"
            result["dimensions"]["research"] = {
                "level": res_level,
                "score": res_score,
                "report_count": res.research.report_count_3m,
                "broker_count": res.research.covered_brokers,
            }

        # 计算综合评分和等级
        dim_scores = [
            d.get("score", 0) for d in result["dimensions"].values()
        ]
        if dim_scores:
            result["overall_score"] = sum(dim_scores) / len(dim_scores)
        result["overall_score"] = min(100, result["overall_score"])

        # 综合证据等级
        strong_dims = sum(
            1 for d in result["dimensions"].values() if d.get("level") == "强"
        )
        medium_dims = sum(
            1 for d in result["dimensions"].values() if d.get("level") == "中"
        )

        if strong_dims >= 2:
            result["overall_evidence_level"] = "强"
        elif strong_dims >= 1 or medium_dims >= 2:
            result["overall_evidence_level"] = "中"
        else:
            result["overall_evidence_level"] = "弱"

        return result


# ============================================================
# 便捷函数
# ============================================================

_announcement_analyzer_instance = None


def get_announcement_analyzer() -> AnnouncementDeepAnalyzer:
    """获取公告分析器单例"""
    global _announcement_analyzer_instance
    if _announcement_analyzer_instance is None:
        _announcement_analyzer_instance = AnnouncementDeepAnalyzer()
    return _announcement_analyzer_instance


def analyze_announcements(stock_code: str, stock_name: str = "", days: int = 180) -> EvidenceVerificationResult:
    """便捷函数：分析公告"""
    return get_announcement_analyzer().analyze_announcements(stock_code, stock_name, days)


def multi_dimension_verify(stock_code: str, stock_name: str = "", stock_data=None) -> Dict:
    """便捷函数：多维度验证"""
    verifier = MultiDimensionalEvidenceVerifier()
    return verifier.verify(stock_code, stock_name, stock_data)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Serenity公告深度解读模块测试")
    print("=" * 60)
    print()

    test_codes = [
        ("688126", "沪硅产业"),
        ("603650", "彤程新材"),
    ]

    analyzer = AnnouncementDeepAnalyzer()

    for code, name in test_codes:
        print(f"正在分析 {name}({code}) 的公告...")
        result = analyzer.analyze_announcements(code, name, days=90)
        print(f"  公告总数: {result.total_announcements}")
        print(f"  强证据: {result.strong_evidence_count}条")
        print(f"  中证据: {result.medium_evidence_count}条")
        print(f"  证据等级: {result.evidence_level}")
        print(f"  综合评分: {result.overall_score}")
        print(f"  摘要: {result.verification_summary}")
        if result.key_announcements:
            print(f"  最重要公告:")
            for ann in result.key_announcements[:3]:
                print(f"    [{ann.evidence_strength.value}] {ann.title[:40]}...")
        print()

    print("测试完成！")
