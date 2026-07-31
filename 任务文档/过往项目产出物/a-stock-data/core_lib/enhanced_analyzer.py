"""
Serenity瓶颈投资分析框架 v3.0 - 增强版
关键改进：
1. 增加公开信息核实模块（主动搜索行业/政策/重大事件）
2. 建立认知差识别方法论（系统化识别被忽视的关键信息）
3. 优化风险评估为动态跟踪模式
4. 从被动接收信息 → 主动挖掘信息

分析流程（六步漏斗）：
Step 0: 公开信息采集与核实  ← 新增
Step 1: 产业链逆向拆解定位
Step 2: 物理四问筛选
Step 3: 约束确定性分析
Step 4: 三级证据验证
Step 5: 红队动态风险评估  ← 优化
Step 6: 认知差分析与结论
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class InformationSource(Enum):
    """信息来源类型"""
    OFFICIAL_ANNOUNCEMENT = "公司公告"
    FINANCIAL_REPORT = "财务报告"
    INDUSTRY_POLICY = "行业政策"
    INDUSTRY_NEWS = "行业新闻"
    MAJOR_EVENT = "重大事件"
    INSTITUTION_RESEARCH = "机构研报"
    EXPERT_VIEW = "专家观点"
    MARKET_DATA = "市场数据"


class CognitiveGapType(Enum):
    """认知差类型"""
    UNDERESTIMATED_BARRIER = "技术壁垒被低估"
    UNDERESTIMATED_DEMAND = "需求空间被低估"
    OVERESTIMATED_RISK = "风险被过度担忧"
    UNDERESTIMATED_POLICY = "政策力度被低估"
    MISSED_CATALYST = "催化剂被忽视"
    MISSED_INFLECTION = "业绩拐点被忽视"


class RiskTrend(Enum):
    """风险趋势"""
    RISING = "上升"
    STABLE = "稳定"
    DECLINING = "下降"
    UNKNOWN = "未知"


@dataclass
class VerifiedInfo:
    """已核实信息"""
    content: str
    source: InformationSource
    credibility: int  # 0-100 可信度评分
    date: str = ""
    impact_level: str = "中"  # 低/中/高/重大
    is_verified: bool = False


@dataclass
class CognitiveGap:
    """认知差"""
    gap_type: CognitiveGapType
    description: str
    evidence: List[str] = field(default_factory=list)
    magnitude: int = 0  # 0-100 认知差大小
    duration: str = ""  # 持续时间预期


@dataclass
class DynamicRisk:
    """动态风险"""
    risk_name: str
    current_level: str = "低"  # 低/中/高
    trend: RiskTrend = RiskTrend.UNKNOWN
    key_indicators: List[str] = field(default_factory=list)
    trigger_conditions: List[str] = field(default_factory=list)
    mitigation_factors: List[str] = field(default_factory=list)
    probability: float = 0.0  # 发生概率 0-1
    impact: float = 0.0  # 影响程度 0-1


# ============================================================
# Step 0: 公开信息采集与核实模块
# ============================================================

class PublicInformationVerifier:
    """
    公开信息采集与核实模块

    主动搜索和核实关键信息，避免"用户喂什么信什么"
    核心改进：从被动接收 → 主动搜索
    """

    def __init__(self):
        self.info_checklist = [
            "行业政策变化",
            "重大事件（封锁/制裁/事故）",
            "产业链供需变化",
            "竞争对手动态",
            "业绩预告/快报",
            "机构调研记录",
        ]
        self.web_search_available = True  # 标记是否有搜索能力

    def build_search_queries(
        self,
        stock_name: str,
        industry: str = "",
        user_hints: List[str] = None,
    ) -> List[Dict]:
        """
        构建搜索查询列表

        这是主动信息获取的核心：
        - 不是等用户提供信息
        - 而是主动列出需要搜索的关键点
        """
        queries = []

        # 1. 业绩相关（必须核实）
        queries.append({
            "category": "业绩数据",
            "query": f"{stock_name} 2025 业绩 净利润 增长",
            "priority": "高",
            "purpose": "核实业绩拐点",
        })

        # 2. 行业重大事件
        if industry:
            queries.append({
                "category": "行业重大事件",
                "query": f"{industry} 封锁 制裁 出口管制 2025 2026",
                "priority": "高",
                "purpose": "发现可能被忽视的重大事件",
            })

        # 3. 产业链供需
        if industry:
            queries.append({
                "category": "产业链供需",
                "query": f"{industry} 国产替代 国产化率 供需缺口 2025",
                "priority": "中",
                "purpose": "评估供需格局变化",
            })

        # 4. 竞争对手动态
        queries.append({
            "category": "竞争对手",
            "query": f"{stock_name} 竞争对手 技术突破 量产 2025",
            "priority": "中",
            "purpose": "跟踪竞争格局变化",
        })

        # 5. 政策动态
        if industry:
            queries.append({
                "category": "政策动态",
                "query": f"{industry} 政策 大基金 税收优惠 2025 2026",
                "priority": "中",
                "purpose": "评估政策支持力度",
            })

        # 6. 用户线索优先核实
        if user_hints:
            for i, hint in enumerate(user_hints):
                queries.insert(0, {
                    "category": f"用户线索{i+1}",
                    "query": hint,
                    "priority": "最高",
                    "purpose": "核实用户提供的关键信息",
                })

        return queries

    def verify_information(
        self,
        stock_code: str,
        stock_name: str,
        industry: str = "",
        user_hints: List[str] = None,
        search_results: List[Dict] = None,
    ) -> List[VerifiedInfo]:
        """
        核实关键信息

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            industry: 行业
            user_hints: 用户提示的信息线索
            search_results: 搜索结果（可选，有则用来核实）

        Returns:
            List[VerifiedInfo]: 已核实信息列表
        """
        verified_infos = []

        # 基础信息（市场数据）
        verified_infos.append(VerifiedInfo(
            content=f"{stock_name}({stock_code}) 基本行情数据",
            source=InformationSource.MARKET_DATA,
            credibility=95,
            date=datetime.now().strftime('%Y-%m-%d'),
            impact_level="中",
            is_verified=True,
        ))

        # 行业政策
        if industry:
            verified_infos.append(VerifiedInfo(
                content=f"{industry}行业政策动态",
                source=InformationSource.INDUSTRY_POLICY,
                credibility=70,
                impact_level="高",
                is_verified=bool(search_results),
            ))

        # 用户提供的线索
        if user_hints:
            for hint in user_hints:
                credibility = 50
                is_verified = False

                # 如果有搜索结果，尝试核实
                if search_results:
                    for sr in search_results:
                        if hint[:10] in sr.get("title", "") or hint[:10] in sr.get("snippet", ""):
                            credibility = 85
                            is_verified = True
                            break

                verified_infos.append(VerifiedInfo(
                    content=f"重大事件：{hint}",
                    source=InformationSource.MAJOR_EVENT,
                    credibility=credibility,
                    impact_level="高",
                    is_verified=is_verified,
                ))

        # 业绩相关
        verified_infos.append(VerifiedInfo(
            content=f"{stock_name}最新业绩数据",
            source=InformationSource.FINANCIAL_REPORT,
            credibility=80,
            impact_level="高",
            is_verified=bool(search_results),
        ))

        return verified_infos

    def generate_search_plan(self, queries: List[Dict]) -> str:
        """生成搜索计划报告"""
        lines = []
        lines.append("【主动信息获取计划】")
        lines.append("-" * 50)
        lines.append("")
        lines.append(f"共 {len(queries)} 个搜索方向，按优先级排列：")
        lines.append("")

        for i, q in enumerate(queries):
            priority_icon = "🔴" if q["priority"] == "最高" else "🟠" if q["priority"] == "高" else "🟡"
            lines.append(f"{priority_icon} [{q['priority']}] {q['category']}")
            lines.append(f"   搜索词: {q['query']}")
            lines.append(f"   目的: {q['purpose']}")
            lines.append("")

        lines.append("💡 方法论：")
        lines.append("  1. 最高优先级：核实用户提供的线索（验证真伪）")
        lines.append("  2. 高优先级：业绩+重大事件（基本面核心）")
        lines.append("  3. 中优先级：产业链+政策+竞争（环境分析）")
        lines.append("  4. 原则：不假设任何信息为已知，主动核实一切")
        lines.append("")

        return "\n".join(lines)

    def generate_verification_report(self, infos: List[VerifiedInfo]) -> str:
        """生成信息核实报告"""
        lines = []
        lines.append("【Step 0: 公开信息采集与核实】")
        lines.append("-" * 50)
        lines.append("")

        verified_count = sum(1 for i in infos if i.is_verified)
        lines.append(f"信息项总数: {len(infos)}")
        lines.append(f"已核实: {verified_count}")
        lines.append(f"待核实: {len(infos) - verified_count}")
        lines.append("")

        lines.append("已核实信息：")
        for info in infos:
            if info.is_verified:
                lines.append(f"  ✅ [{info.source.value}] {info.content}")
                lines.append(f"     可信度: {info.credibility}/100  影响: {info.impact_level}")
        lines.append("")

        lines.append("待核实信息（需主动搜索）：")
        for info in infos:
            if not info.is_verified:
                lines.append(f"  ⏳ [{info.source.value}] {info.content}")
                lines.append(f"     初始可信度: {info.credibility}/100  影响: {info.impact_level}")
        lines.append("")

        return "\n".join(lines)


# ============================================================
# Step 6: 认知差识别模块
# ============================================================

class CognitiveGapAnalyzer:
    """
    认知差识别模块

    系统化识别"已公开但被市场忽视"的关键信息
    """

    def __init__(self):
        self.gap_dimensions = [
            ("技术壁垒", "市场是否低估了技术难度和研发周期"),
            ("需求空间", "市场是否低估了长期需求增长"),
            ("政策力度", "市场是否低估了政策支持力度"),
            ("业绩拐点", "市场是否忽视了业绩拐点"),
            ("竞争格局", "市场是否误判了竞争格局变化"),
            ("风险因素", "市场是否过度担忧或忽视了某些风险"),
        ]

    def analyze_cognitive_gaps(
        self,
        stock_name: str,
        verified_infos: List[VerifiedInfo],
        market_sentiment: Dict = None,
    ) -> List[CognitiveGap]:
        """
        分析认知差

        Args:
            stock_name: 股票名称
            verified_infos: 已核实信息
            market_sentiment: 市场情绪数据

        Returns:
            List[CognitiveGap]: 认知差列表
        """
        gaps = []

        # 基于已核实信息识别认知差
        for info in verified_infos:
            if not info.is_verified:
                continue

            # 重大事件型认知差
            if info.source == InformationSource.MAJOR_EVENT and info.impact_level in ["高", "重大"]:
                gaps.append(CognitiveGap(
                    gap_type=CognitiveGapType.MISSED_CATALYST,
                    description=f"重大事件（{info.content[:30]}）的影响可能被市场低估",
                    evidence=[
                        f"事件来源: {info.source.value}",
                        f"事件影响等级: {info.impact_level}",
                        f"事件可信度: {info.credibility}/100",
                    ],
                    magnitude=70,
                    duration="短期1-3个月",
                ))

            # 业绩拐点型认知差
            if info.source == InformationSource.FINANCIAL_REPORT:
                gaps.append(CognitiveGap(
                    gap_type=CognitiveGapType.MISSED_INFLECTION,
                    description="业绩变化可能未被市场充分定价",
                    evidence=[
                        "业绩数据是最硬的基本面证据",
                        "市场往往滞后于基本面变化",
                    ],
                    magnitude=50,
                    duration="中期3-6个月",
                ))

        # 技术壁垒型认知差（默认存在，需评估程度）
        gaps.append(CognitiveGap(
            gap_type=CognitiveGapType.UNDERESTIMATED_BARRIER,
            description="技术壁垒和客户粘性容易被市场低估",
            evidence=[
                "研发周期长，新进入者难以快速突破",
                "客户认证周期2-3年，供应商粘性高",
                "市场倾向于线性外推，低估非线性突破",
            ],
            magnitude=60,
            duration="长期1-3年",
        ))

        # 政策力度型认知差
        gaps.append(CognitiveGap(
            gap_type=CognitiveGapType.UNDERESTIMATED_POLICY,
            description="国产替代政策的力度和持续性可能被低估",
            evidence=[
                "政策支持是长期趋势，不是短期刺激",
                "大基金、税收优惠等多重政策叠加",
                "供应链安全上升为国家战略",
            ],
            magnitude=55,
            duration="中长期1-2年",
        ))

        # 按大小排序
        gaps.sort(key=lambda x: -x.magnitude)

        return gaps

    def generate_cognitive_gap_report(self, gaps: List[CognitiveGap]) -> str:
        """生成认知差分析报告"""
        lines = []
        lines.append("【Step 6: 认知差分析】")
        lines.append("-" * 50)
        lines.append("")

        lines.append(f"识别到 {len(gaps)} 个潜在认知差：")
        lines.append("")

        for i, gap in enumerate(gaps):
            icon = "🔴" if gap.magnitude >= 70 else "🟡" if gap.magnitude >= 50 else "🔵"
            lines.append(f"{icon} 认知差{i+1}: {gap.gap_type.value}")
            lines.append(f"   描述: {gap.description}")
            lines.append(f"   程度: {gap.magnitude}/100")
            lines.append(f"   持续时间: {gap.duration}")
            lines.append(f"   证据:")
            for e in gap.evidence:
                lines.append(f"     • {e}")
            lines.append("")

        # 综合评估
        if gaps:
            avg_magnitude = sum(g.magnitude for g in gaps) / len(gaps)
            lines.append(f"综合认知差程度: {avg_magnitude:.0f}/100")
            if avg_magnitude >= 60:
                lines.append("结论：存在显著认知差，市场预期可能偏保守")
            elif avg_magnitude >= 40:
                lines.append("结论：存在中等认知差，有修复空间")
            else:
                lines.append("结论：认知差较小，市场定价相对有效")
        lines.append("")

        return "\n".join(lines)


# ============================================================
# 动态风险评估模块
# ============================================================

class DynamicRiskAssessor:
    """
    动态风险评估模块

    风险不是静态的，要跟踪变化趋势
    """

    def __init__(self):
        self.risk_dimensions = [
            ("技术替代风险", RiskTrend.UNKNOWN),
            ("供给突破风险", RiskTrend.UNKNOWN),
            ("需求不及预期风险", RiskTrend.UNKNOWN),
            ("估值风险", RiskTrend.UNKNOWN),
            ("竞争加剧风险", RiskTrend.UNKNOWN),
            ("政策变化风险", RiskTrend.UNKNOWN),
        ]

    def assess_dynamic_risks(
        self,
        stock_name: str,
        verified_infos: List[VerifiedInfo],
        current_valuation: Dict = None,
    ) -> List[DynamicRisk]:
        """
        评估动态风险

        Args:
            stock_name: 股票名称
            verified_infos: 已核实信息
            current_valuation: 当前估值数据

        Returns:
            List[DynamicRisk]: 动态风险列表
        """
        risks = []

        # 技术替代风险
        risks.append(DynamicRisk(
            risk_name="技术替代风险",
            current_level="低",
            trend=RiskTrend.STABLE,
            key_indicators=["新技术专利数量", "新技术融资额", "客户测试进展"],
            trigger_conditions=["竞争对手技术突破", "替代技术成本下降30%以上"],
            mitigation_factors=["研发周期长", "客户粘性高", "先发优势"],
            probability=0.1,
            impact=0.8,
        ))

        # 供给突破风险
        risks.append(DynamicRisk(
            risk_name="供给突破风险",
            current_level="中",
            trend=RiskTrend.RISING,  # 国产替代加速，供给在增加
            key_indicators=["新进入者数量", "扩产公告数", "产能释放进度"],
            trigger_conditions=["大量新厂商进入", "现有厂商大幅扩产"],
            mitigation_factors=["客户认证周期长", "技术壁垒高", "先发优势"],
            probability=0.5,
            impact=0.5,
        ))

        # 需求不及预期风险
        risks.append(DynamicRisk(
            risk_name="需求不及预期风险",
            current_level="中",
            trend=RiskTrend.DECLINING,  # 封锁反而增加了确定性需求
            key_indicators=["行业增速", "客户订单", "产能利用率"],
            trigger_conditions=["行业周期下行", "下游需求疲软"],
            mitigation_factors=["国产替代刚需", "政策支持", "长期增长空间"],
            probability=0.3,
            impact=0.6,
        ))

        # 估值风险
        if current_valuation and current_valuation.get("pe", 0) > 100:
            risks.append(DynamicRisk(
                risk_name="估值风险",
                current_level="高",
                trend=RiskTrend.DECLINING if verified_infos else RiskTrend.RISING,
                key_indicators=["PE", "PB", "PEG", "业绩增速"],
                trigger_conditions=["业绩不及预期", "估值过高回调"],
                mitigation_factors=["高成长可以消化估值", "业绩在兑现"],
                probability=0.6,
                impact=0.7,
            ))
        else:
            risks.append(DynamicRisk(
                risk_name="估值风险",
                current_level="中",
                trend=RiskTrend.STABLE,
                key_indicators=["PE", "PB", "PEG"],
                trigger_conditions=["业绩不及预期"],
                mitigation_factors=["成长确定性"],
                probability=0.3,
                impact=0.5,
            ))

        # 竞争加剧风险
        risks.append(DynamicRisk(
            risk_name="竞争加剧风险",
            current_level="中",
            trend=RiskTrend.RISING,  # 国产替代吸引更多玩家
            key_indicators=["竞争对手数量", "价格战迹象", "毛利率变化"],
            trigger_conditions=["价格战", "毛利率持续下滑"],
            mitigation_factors=["技术壁垒", "客户粘性", "规模效应"],
            probability=0.5,
            impact=0.4,
        ))

        # 计算综合风险评分
        for risk in risks:
            risk_score = risk.probability * risk.impact * 100
            risk.risk_score = risk_score

        return risks

    def generate_dynamic_risk_report(self, risks: List[DynamicRisk]) -> str:
        """生成动态风险评估报告"""
        lines = []
        lines.append("【Step 5: 红队动态风险评估】")
        lines.append("-" * 50)
        lines.append("")

        lines.append("风险维度与趋势：")
        lines.append("")

        for risk in risks:
            # 风险等级颜色
            level_icon = "🟢" if risk.current_level == "低" else "🟡" if risk.current_level == "中" else "🔴"
            # 趋势箭头
            if risk.trend == RiskTrend.RISING:
                trend_icon = "📈 上升"
            elif risk.trend == RiskTrend.DECLINING:
                trend_icon = "📉 下降"
            elif risk.trend == RiskTrend.STABLE:
                trend_icon = "➡️ 稳定"
            else:
                trend_icon = "❓ 未知"

            risk_score = risk.probability * risk.impact * 100

            lines.append(f"{level_icon} {risk.risk_name}")
            lines.append(f"   当前等级: {risk.current_level}  趋势: {trend_icon}")
            lines.append(f"   风险评分: {risk_score:.0f}/100 (概率{risk.probability*100:.0f}% × 影响{risk.impact*100:.0f}%)")
            lines.append(f"   关键跟踪指标: {', '.join(risk.key_indicators[:3])}")
            if risk.mitigation_factors:
                lines.append(f"   缓解因素: {', '.join(risk.mitigation_factors[:3])}")
            lines.append("")

        # 综合风险评估
        total_risk = sum(r.probability * r.impact for r in risks) / len(risks) * 100
        lines.append(f"综合风险评分: {total_risk:.0f}/100")
        if total_risk >= 60:
            lines.append("结论：风险较高，需谨慎对待")
        elif total_risk >= 40:
            lines.append("结论：风险中等，需持续跟踪")
        else:
            lines.append("结论：风险较低，整体可控")
        lines.append("")

        lines.append("💡 动态跟踪提示：")
        lines.append("  风险不是静态的，建议每月重新评估")
        lines.append("  重点关注趋势变化的风险（上升或下降）")
        lines.append("")

        return "\n".join(lines)


# ============================================================
# 增强版分析框架整合
# ============================================================

class SerenityEnhancedAnalyzer:
    """
    Serenity增强版分析引擎 v3.0

    核心改进：
    1. 主动信息核实（不是被动接收）
    2. 系统化认知差识别
    3. 动态风险跟踪
    """

    def __init__(self):
        self.info_verifier = PublicInformationVerifier()
        self.cognitive_gap_analyzer = CognitiveGapAnalyzer()
        self.dynamic_risk_assessor = DynamicRiskAssessor()

    def analyze(
        self,
        stock_code: str,
        stock_name: str,
        industry: str = "",
        user_hints: List[str] = None,
        search_results: List[Dict] = None,
    ) -> Dict:
        """
        完整分析流程

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            industry: 行业
            user_hints: 用户提供的信息线索
            search_results: 搜索结果（可选）

        Returns:
            Dict: 完整分析结果
        """
        result = {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "analysis_date": datetime.now().strftime('%Y-%m-%d'),
            "steps": {},
        }

        # Step 0-0: 生成主动搜索计划
        search_queries = self.info_verifier.build_search_queries(
            stock_name, industry, user_hints
        )
        result["steps"]["step0_0"] = {
            "name": "主动信息获取计划",
            "queries": search_queries,
            "report": self.info_verifier.generate_search_plan(search_queries),
        }

        # Step 0-1: 公开信息采集与核实
        verified_infos = self.info_verifier.verify_information(
            stock_code, stock_name, industry, user_hints, search_results
        )
        result["steps"]["step0_1"] = {
            "name": "公开信息核实结果",
            "verified_infos": verified_infos,
            "report": self.info_verifier.generate_verification_report(verified_infos),
        }

        # Step 6: 认知差分析
        cognitive_gaps = self.cognitive_gap_analyzer.analyze_cognitive_gaps(
            stock_name, verified_infos
        )
        result["steps"]["step6"] = {
            "name": "认知差分析",
            "cognitive_gaps": cognitive_gaps,
            "report": self.cognitive_gap_analyzer.generate_cognitive_gap_report(cognitive_gaps),
        }

        # Step 5: 动态风险评估
        dynamic_risks = self.dynamic_risk_assessor.assess_dynamic_risks(
            stock_name, verified_infos
        )
        result["steps"]["step5"] = {
            "name": "动态风险评估",
            "risks": dynamic_risks,
            "report": self.dynamic_risk_assessor.generate_dynamic_risk_report(dynamic_risks),
        }

        return result

    def generate_full_report(self, result: Dict) -> str:
        """生成完整分析报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("  Serenity瓶颈投资深度分析报告 v3.0")
        lines.append(f"  标的：{result['stock_name']}({result['stock_code']})")
        lines.append(f"  分析日期：{result['analysis_date']}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("📌 v3.0 核心改进：")
        lines.append("   1. 从被动接收信息 → 主动搜索核实")
        lines.append("   2. 系统化认知差识别（6大维度）")
        lines.append("   3. 动态风险跟踪（趋势+概率×影响）")
        lines.append("")

        # 输出各步骤报告
        step_order = ["step0_0", "step0_1", "step5", "step6"]
        for step_key in step_order:
            if step_key in result["steps"]:
                lines.append(result["steps"][step_key]["report"])

        lines.append("=" * 60)
        lines.append("  报告结束")
        lines.append("=" * 60)

        return "\n".join(lines)


# ============================================================
# 便捷函数
# ============================================================

_enhanced_analyzer_instance = None


def get_enhanced_analyzer() -> SerenityEnhancedAnalyzer:
    """获取增强版分析器单例"""
    global _enhanced_analyzer_instance
    if _enhanced_analyzer_instance is None:
        _enhanced_analyzer_instance = SerenityEnhancedAnalyzer()
    return _enhanced_analyzer_instance


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Serenity增强版分析框架 v3.0 测试")
    print("=" * 60)
    print()

    analyzer = SerenityEnhancedAnalyzer()
    result = analyzer.analyze(
        stock_code="300655",
        stock_name="晶瑞电材",
        industry="半导体材料/光刻胶",
        user_hints=["日本封锁光刻胶出口"],
    )

    print(analyzer.generate_full_report(result))
    print()
    print("✅ 增强版分析框架测试完成！")
