"""
Serenity瓶颈投资 - 风险评估模块
红队证伪视角的三维风险评估体系

风险类型：
1. 技术替代风险：是否存在可绕过瓶颈的新技术路线
2. 供给突破风险：是否有潜在新玩家可快速突破壁垒
3. 需求不及预期风险：下游大趋势是否会证伪

核心原则：
- 主动站在空头视角攻击投资逻辑
- 任意风险发生概率>30%，直接下调投资评级
- 所有风险必须对应可跟踪的高频监控指标
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class RiskLevel(Enum):
    """风险等级"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class RiskType(Enum):
    """风险类型"""
    TECH_SUBSTITUTION = "技术替代风险"
    SUPPLY_BREAKTHROUGH = "供给突破风险"
    DEMAND_DISAPPOINTMENT = "需求不及预期风险"


@dataclass
class RiskFactor:
    """风险因子"""
    name: str                           # 风险因子名称
    description: str                    # 描述
    probability: RiskLevel              # 发生概率
    impact: RiskLevel                   # 影响程度
    current_progress: str = ""          # 当前进展
    breakthrough_time: str = ""         # 预计突破时间
    tracking_indicators: List[str] = field(default_factory=list)  # 跟踪指标
    data_sources: List[str] = field(default_factory=list)        # 数据来源


@dataclass
class RiskAssessmentResult:
    """风险评估结果"""
    risk_type: RiskType                 # 风险类型
    overall_probability: RiskLevel       # 整体发生概率
    overall_impact: RiskLevel            # 整体影响程度
    risk_score: float = 0.0             # 风险综合评分(0-100)
    key_factors: List[RiskFactor] = field(default_factory=list)  # 关键风险因子
    tracking_metrics: List[str] = field(default_factory=list)    # 核心跟踪指标
    mitigation_suggestions: List[str] = field(default_factory=list)  # 应对建议
    rating_adjustment: str = ""          # 评级调整建议


@dataclass
class RedTeamReport:
    """红队证伪报告"""
    stock_code: str
    stock_name: str
    chokepoint_name: str

    # 三维风险评估结果
    tech_risk: Optional[RiskAssessmentResult] = None
    supply_risk: Optional[RiskAssessmentResult] = None
    demand_risk: Optional[RiskAssessmentResult] = None

    # 综合结论
    overall_risk_score: float = 0.0     # 综合风险评分
    investment_logic_robustness: str = ""  # 投资逻辑稳健性
    rating_suggestion: str = ""          # 评级建议
    key_monitoring_points: List[str] = field(default_factory=list)  # 重点监控点


# ============================================================
# 技术替代风险评估
# ============================================================

class TechSubstitutionRiskAssessor:
    """技术替代风险评估器"""

    # 各瓶颈环节的替代技术路线库
    SUBSTITUTION_TECH_MAP = {
        "HBM高带宽内存": {
            "alternatives": [
                {
                    "name": "3D堆叠SRAM",
                    "maturity": "实验室阶段",
                    "time_to_market": "5-8年",
                    "probability": "低",
                    "advantage": "延迟更低",
                    "disadvantage": "容量小、成本高"
                },
                {
                    "name": "光互联存储",
                    "maturity": "概念阶段",
                    "time_to_market": "8-10年",
                    "probability": "极低",
                    "advantage": "带宽极高",
                    "disadvantage": "技术难度极大"
                },
                {
                    "name": "存算一体",
                    "maturity": "早期研发",
                    "time_to_market": "5-10年",
                    "probability": "中",
                    "advantage": "架构革命性变化",
                    "disadvantage": "生态尚未建立"
                }
            ],
            "current_dominance": "极高",
            "substitution_pressure": "低"
        },
        "CoWoS先进封装": {
            "alternatives": [
                {
                    "name": "EMIB封装",
                    "maturity": "已量产",
                    "time_to_market": "已可用",
                    "probability": "中",
                    "advantage": "成本较低",
                    "disadvantage": "性能略差，仅英特尔使用"
                },
                {
                    "name": "扇出型封装",
                    "maturity": "已量产",
                    "time_to_market": "已可用",
                    "probability": "中",
                    "advantage": "成本低",
                    "disadvantage": "不适合高端大芯片"
                },
                {
                    "name": "3D堆叠SoIC",
                    "maturity": "小批量",
                    "time_to_market": "2-3年",
                    "probability": "高",
                    "advantage": "集成度更高",
                    "disadvantage": "成本更高、良率挑战"
                }
            ],
            "current_dominance": "高",
            "substitution_pressure": "中"
        },
        "EUV光刻胶": {
            "alternatives": [
                {
                    "name": "EUV光刻胶新配方",
                    "maturity": "研发中",
                    "time_to_market": "2-3年",
                    "probability": "高",
                    "advantage": "灵敏度更高",
                    "disadvantage": "仍属EUV体系，非替代"
                },
                {
                    "name": "纳米压印",
                    "maturity": "小批量",
                    "time_to_market": "3-5年",
                    "probability": "低",
                    "advantage": "成本低",
                    "disadvantage": "良率、产量问题"
                },
                {
                    "name": "多电子束光刻",
                    "maturity": "研发中",
                    "time_to_market": "5-8年",
                    "probability": "低",
                    "advantage": "无掩膜",
                    "disadvantage": "产能极低"
                }
            ],
            "current_dominance": "极高",
            "substitution_pressure": "极低"
        },
        "高端光刻机(DUV/EUV)": {
            "alternatives": [
                {
                    "name": "国产DUV光刻机",
                    "maturity": "验证阶段",
                    "time_to_market": "1-2年",
                    "probability": "高",
                    "advantage": "国产替代",
                    "disadvantage": "仅成熟制程"
                },
                {
                    "name": "国产EUV光刻机",
                    "maturity": "研发中",
                    "time_to_market": "5-10年",
                    "probability": "中",
                    "advantage": "打破垄断",
                    "disadvantage": "技术难度极大"
                },
                {
                    "name": "无掩膜光刻",
                    "maturity": "概念阶段",
                    "time_to_market": "10年+",
                    "probability": "极低",
                    "advantage": "全新范式",
                    "disadvantage": "不确定"
                }
            ],
            "current_dominance": "极高",
            "substitution_pressure": "低"
        },
        "精密减速器(谐波/RV)": {
            "alternatives": [
                {
                    "name": "直驱电机",
                    "maturity": "部分应用",
                    "time_to_market": "已可用",
                    "probability": "中",
                    "advantage": "结构简单",
                    "disadvantage": "力矩密度不足"
                },
                {
                    "name": "磁齿轮",
                    "maturity": "研发中",
                    "time_to_market": "3-5年",
                    "probability": "低",
                    "advantage": "无接触磨损",
                    "disadvantage": "体积大、成本高"
                }
            ],
            "current_dominance": "高",
            "substitution_pressure": "低"
        },
        "SiC碳化硅功率器件": {
            "alternatives": [
                {
                    "name": "GaN氮化镓",
                    "maturity": "已量产",
                    "time_to_market": "已可用",
                    "probability": "中",
                    "advantage": "高频性能好",
                    "disadvantage": "高压领域不占优"
                },
                {
                    "name": "金刚石半导体",
                    "maturity": "实验室",
                    "time_to_market": "10年+",
                    "probability": "极低",
                    "advantage": "性能更优",
                    "disadvantage": "成本极高"
                }
            ],
            "current_dominance": "高",
            "substitution_pressure": "中"
        },
        "高速光芯片(25G/100G)": {
            "alternatives": [
                {
                    "name": "硅光芯片",
                    "maturity": "量产初期",
                    "time_to_market": "1-2年",
                    "probability": "高",
                    "advantage": "集成度高、成本低",
                    "disadvantage": "性能略有差距"
                },
                {
                    "name": "薄膜铌酸锂",
                    "maturity": "小批量",
                    "time_to_market": "2-3年",
                    "probability": "中",
                    "advantage": "调制性能优",
                    "disadvantage": "工艺不成熟"
                }
            ],
            "current_dominance": "中",
            "substitution_pressure": "高"
        },
        "电池隔膜": {
            "alternatives": [
                {
                    "name": "固态电解质",
                    "maturity": "研发中",
                    "time_to_market": "3-5年",
                    "probability": "中",
                    "advantage": "安全性更高、能量密度更高",
                    "disadvantage": "成本高、界面问题"
                },
                {
                    "name": "无纺布隔膜",
                    "maturity": "部分应用",
                    "time_to_market": "已可用",
                    "probability": "低",
                    "advantage": "成本低",
                    "disadvantage": "性能一般"
                }
            ],
            "current_dominance": "高",
            "substitution_pressure": "中"
        },
        "激光雷达": {
            "alternatives": [
                {
                    "name": "纯视觉方案",
                    "maturity": "已量产",
                    "time_to_market": "已可用",
                    "probability": "高",
                    "advantage": "成本低",
                    "disadvantage": "恶劣天气性能差"
                },
                {
                    "name": "4D毫米波雷达",
                    "maturity": "量产初期",
                    "time_to_market": "1-2年",
                    "probability": "高",
                    "advantage": "成本适中、全天候",
                    "disadvantage": "分辨率低于激光雷达"
                },
                {
                    "name": "FMCW激光雷达",
                    "maturity": "研发中",
                    "time_to_market": "2-3年",
                    "probability": "中",
                    "advantage": "测速能力强",
                    "disadvantage": "成本更高"
                }
            ],
            "current_dominance": "中",
            "substitution_pressure": "高"
        },
        "光纤预制棒": {
            "alternatives": [
                {
                    "name": "新型光纤材料",
                    "maturity": "研发中",
                    "time_to_market": "5-10年",
                    "probability": "低",
                    "advantage": "带宽更高",
                    "disadvantage": "成本高、兼容性差"
                },
                {
                    "name": "空间光通信",
                    "maturity": "小批量",
                    "time_to_market": "3-5年",
                    "probability": "低",
                    "advantage": "无需光纤",
                    "disadvantage": "受天气影响、点对点"
                }
            ],
            "current_dominance": "极高",
            "substitution_pressure": "低"
        },
    }

    def assess(self, chokepoint_name: str) -> RiskAssessmentResult:
        """
        评估技术替代风险

        Args:
            chokepoint_name: 瓶颈环节名称

        Returns:
            RiskAssessmentResult: 风险评估结果
        """
        result = RiskAssessmentResult(
            risk_type=RiskType.TECH_SUBSTITUTION,
            overall_probability=RiskLevel.LOW,
            overall_impact=RiskLevel.HIGH,
        )

        # 查找替代技术
        tech_data = self.SUBSTITUTION_TECH_MAP.get(chokepoint_name)
        if not tech_data:
            result.key_factors.append(RiskFactor(
                name="未知替代技术",
                description=f"未找到{chokepoint_name}的替代技术数据，需补充研究",
                probability=RiskLevel.MEDIUM,
                impact=RiskLevel.HIGH,
                tracking_indicators=["专利申请趋势", "学术论文发表", "行业会议动态"],
                data_sources=["专利数据库", "学术搜索引擎", "行业协会"]
            ))
            result.overall_probability = RiskLevel.MEDIUM
            result.risk_score = 40
            return result

        # 分析各替代路线
        high_prob_count = 0
        medium_prob_count = 0

        for alt in tech_data["alternatives"]:
            prob = RiskLevel.LOW
            if alt["probability"] == "高":
                prob = RiskLevel.HIGH
                high_prob_count += 1
            elif alt["probability"] == "中":
                prob = RiskLevel.MEDIUM
                medium_prob_count += 1

            impact = RiskLevel.HIGH if alt["time_to_market"].find("已") == 0 or "年" not in alt["time_to_market"] else RiskLevel.MEDIUM

            factor = RiskFactor(
                name=alt["name"],
                description=f"替代方案: {alt['advantage']}; 劣势: {alt['disadvantage']}",
                probability=prob,
                impact=impact,
                current_progress=alt["maturity"],
                breakthrough_time=alt["time_to_market"],
                tracking_indicators=[
                    f"{alt['name']}量产时间",
                    f"{alt['name']}成本下降速度",
                    f"{alt['name']}客户采用情况"
                ],
                data_sources=["公司财报", "行业研报", "技术白皮书"]
            )
            result.key_factors.append(factor)

        # 计算整体概率
        if high_prob_count >= 2:
            result.overall_probability = RiskLevel.HIGH
        elif high_prob_count >= 1 or medium_prob_count >= 2:
            result.overall_probability = RiskLevel.MEDIUM
        else:
            result.overall_probability = RiskLevel.LOW

        # 计算风险评分
        score_map = {"高": 30, "中": 15, "低": 5}
        result.risk_score = sum(
            score_map.get(f.probability.value, 10) for f in result.key_factors
        )
        result.risk_score = min(100, result.risk_score * 2)

        # 核心跟踪指标
        result.tracking_metrics = [
            f"{chokepoint_name}相关专利申请数量趋势",
            "新技术路线企业融资情况",
            "下游客户对新技术的测试进展",
            "行业顶级会议技术议题变化"
        ]

        # 应对建议
        if result.overall_probability == RiskLevel.HIGH:
            result.mitigation_suggestions = [
                "密切跟踪替代技术量产进度",
                "评估被替代后公司转型能力",
                "设置明确的技术路线观察期"
            ]
            result.rating_adjustment = "下调投资评级"
        elif result.overall_probability == RiskLevel.MEDIUM:
            result.mitigation_suggestions = [
                "持续跟踪替代技术进展",
                "关注公司技术布局和专利储备",
                "评估替代技术的真实落地速度"
            ]
            result.rating_adjustment = "谨慎乐观"
        else:
            result.mitigation_suggestions = [
                "定期复查技术路线图",
                "关注前沿学术研究动态"
            ]
            result.rating_adjustment = "维持评级"

        return result


# ============================================================
# 供给突破风险评估
# ============================================================

class SupplyBreakthroughRiskAssessor:
    """供给突破风险评估器"""

    def assess(self, chokepoint_data: Dict) -> RiskAssessmentResult:
        """
        评估供给突破风险

        Args:
            chokepoint_data: 瓶颈环节数据

        Returns:
            RiskAssessmentResult: 风险评估结果
        """
        result = RiskAssessmentResult(
            risk_type=RiskType.SUPPLY_BREAKTHROUGH,
            overall_probability=RiskLevel.LOW,
            overall_impact=RiskLevel.HIGH,
        )

        # 分析供给突破的各个维度
        factors = []

        # 1. 现有厂商扩产
        expansion_cycle = chokepoint_data.get("expansion_cycle", 18)
        capacity_util = chokepoint_data.get("capacity_util", 80)

        expansion_factor = RiskFactor(
            name="现有厂商扩产",
            description=f"产能扩张周期{expansion_cycle}个月，当前产能利用率{capacity_util}%",
            probability=RiskLevel.MEDIUM if capacity_util < 90 else RiskLevel.HIGH,
            impact=RiskLevel.MEDIUM if expansion_cycle >= 18 else RiskLevel.HIGH,
            current_progress=f"产能利用率{capacity_util}%",
            breakthrough_time=f"{expansion_cycle}个月",
            tracking_indicators=["龙头企业资本开支计划", "新增产能投产进度", "产能利用率变化趋势"],
            data_sources=["公司公告", "行业调研", "产能数据库"]
        )
        factors.append(expansion_factor)

        # 2. 新进入者威胁
        new_entrants = chokepoint_data.get("new_entrants_2y", 0)
        top1_share = chokepoint_data.get("top1_share", 40)
        gross_margin = chokepoint_data.get("gross_margin", 40)

        entrant_prob = RiskLevel.LOW
        if new_entrants >= 2:
            entrant_prob = RiskLevel.HIGH
        elif new_entrants == 1:
            entrant_prob = RiskLevel.MEDIUM

        # 高毛利会吸引新进入者
        if gross_margin >= 50:
            if entrant_prob == RiskLevel.LOW:
                entrant_prob = RiskLevel.MEDIUM

        entrant_factor = RiskFactor(
            name="新进入者威胁",
            description=f"过去2年新进入者{new_entrants}家，第一名市占率{top1_share}%，毛利率{gross_margin}%",
            probability=entrant_prob,
            impact=RiskLevel.HIGH if top1_share < 30 else RiskLevel.MEDIUM,
            current_progress=f"行业CR3: {chokepoint_data.get('cr3', 70)}%",
            breakthrough_time="18-24个月（从建厂到量产）",
            tracking_indicators=[
                "行业新进入者数量",
                "新玩家融资情况",
                "专利申请变化",
                "人才流动趋势"
            ],
            data_sources=["企查查", "专利数据库", "行业新闻"]
        )
        factors.append(entrant_factor)

        # 3. 国产替代进度
        localization_rate = chokepoint_data.get("localization_rate", 10)
        domestic_factor = RiskFactor(
            name="国产替代加速",
            description=f"当前国产化率约{localization_rate}%",
            probability=RiskLevel.HIGH if localization_rate < 10 else RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH if localization_rate < 20 else RiskLevel.MEDIUM,
            current_progress=f"国产化率{localization_rate}%",
            breakthrough_time="2-5年",
            tracking_indicators=[
                "国产设备/材料验证进度",
                "下游客户国产采购比例",
                "政策支持力度变化"
            ],
            data_sources=["公司公告", "产业链调研", "政策文件"]
        )
        factors.append(domestic_factor)

        # 4. 核心设备供给
        equipment_lead_time = chokepoint_data.get("equipment_lead_time", 12)
        equipment_factor = RiskFactor(
            name="核心设备交付",
            description=f"核心设备交付周期{equipment_lead_time}个月",
            probability=RiskLevel.LOW if equipment_lead_time >= 12 else RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            current_progress=f"交付周期{equipment_lead_time}个月",
            breakthrough_time=f"{equipment_lead_time}个月",
            tracking_indicators=[
                "设备厂商订单积压情况",
                "设备交付周期变化",
                "二手设备市场价格"
            ],
            data_sources=["设备厂商财报", "产业链调研"]
        )
        factors.append(equipment_factor)

        result.key_factors = factors

        # 计算整体概率
        high_count = sum(1 for f in factors if f.probability == RiskLevel.HIGH)
        medium_count = sum(1 for f in factors if f.probability == RiskLevel.MEDIUM)

        if high_count >= 2:
            result.overall_probability = RiskLevel.HIGH
        elif high_count >= 1 or medium_count >= 2:
            result.overall_probability = RiskLevel.MEDIUM
        else:
            result.overall_probability = RiskLevel.LOW

        # 计算风险评分
        score_map = {"高": 25, "中": 15, "低": 5}
        result.risk_score = sum(score_map.get(f.probability.value, 10) for f in factors)
        result.risk_score = min(100, result.risk_score)

        # 核心跟踪指标
        result.tracking_metrics = [
            "行业龙头资本开支同比增速",
            "新进入者融资事件数量",
            "产能利用率季度变化",
            "核心设备交付周期",
            "国产替代率变化趋势"
        ]

        # 应对建议
        if result.overall_probability == RiskLevel.HIGH:
            result.mitigation_suggestions = [
                "密切监控行业扩产进度",
                "评估供需平衡反转的时间点",
                "关注价格走势和库存变化"
            ]
            result.rating_adjustment = "下调投资评级"
        elif result.overall_probability == RiskLevel.MEDIUM:
            result.mitigation_suggestions = [
                "跟踪扩产和需求增速的相对关系",
                "关注行业竞争格局变化",
                "评估价格下行风险"
            ]
            result.rating_adjustment = "保持警惕"
        else:
            result.mitigation_suggestions = [
                "定期复查供需格局",
                "关注新进入者动态"
            ]
            result.rating_adjustment = "维持评级"

        return result


# ============================================================
# 需求不及预期风险评估
# ============================================================

class DemandDisappointmentRiskAssessor:
    """需求不及预期风险评估器"""

    # 各赛道的需求跟踪指标库
    DEMAND_TRACKING_MAP = {
        "AI算力产业链": {
            "leading_indicators": [
                "云厂商CAPEX指引",
                "服务器出货量",
                "GPU/AI芯片订单量",
                "大模型训练Token消耗",
                "数据中心建设进度"
            ],
            "key_customers": ["微软", "谷歌", "亚马逊", "Meta", "字节跳动"],
            "risk_triggers": [
                "云厂商下调CAPEX指引>20%",
                "AI芯片库存积压",
                "大模型商业化进展低于预期",
                "企业AI投入缩减"
            ]
        },
        "半导体产业链": {
            "leading_indicators": [
                "全球半导体销售额",
                "晶圆厂产能利用率",
                "存储芯片价格",
                "IC设计公司库存周转",
                "消费电子出货量"
            ],
            "key_customers": ["苹果", "三星", "小米", "华为", "汽车厂商"],
            "risk_triggers": [
                "半导体行业销售额增速转负",
                "晶圆厂大幅下调扩产计划",
                "消费电子需求持续疲软",
                "库存去化周期延长"
            ]
        },
        "新能源汽车产业链": {
            "leading_indicators": [
                "新能源汽车销量",
                "动力电池装机量",
                "车企新车型发布计划",
                "充电桩建设速度",
                "政策补贴变化"
            ],
            "key_customers": ["特斯拉", "比亚迪", "新势力", "传统车企"],
            "risk_triggers": [
                "新能源汽车销量增速下滑>30%",
                "价格战加剧导致盈利恶化",
                "补贴政策大幅退坡",
                "充电基础设施建设不及预期"
            ]
        },
        "人形机器人产业链": {
            "leading_indicators": [
                "龙头企业量产计划",
                "核心零部件订单量",
                "机器人性能突破进展",
                "下游客户测试反馈",
                "产线自动化率提升速度"
            ],
            "key_customers": ["特斯拉", "亚马逊", "汽车厂商", "3C代工厂"],
            "risk_triggers": [
                "量产时间多次推迟",
                "性能达不到预期",
                "成本下降速度慢于预期",
                "下游需求验证失败"
            ]
        },
        "光通信产业链": {
            "leading_indicators": [
                "云厂商CAPEX",
                "光模块出货量",
                "运营商资本开支",
                "数据中心建设数量",
                "光纤光缆招标量"
            ],
            "key_customers": ["云厂商", "三大运营商", "设备商"],
            "risk_triggers": [
                "云厂商下调CAPEX",
                "运营商投资缩减",
                "AI算力需求增长放缓",
                "产品价格快速下降"
            ]
        }
    }

    def assess(self, track_name: str, trend_data: Dict) -> RiskAssessmentResult:
        """
        评估需求不及预期风险

        Args:
            track_name: 赛道名称
            trend_data: 趋势数据

        Returns:
            RiskAssessmentResult: 风险评估结果
        """
        result = RiskAssessmentResult(
            risk_type=RiskType.DEMAND_DISAPPOINTMENT,
            overall_probability=RiskLevel.LOW,
            overall_impact=RiskLevel.HIGH,
        )

        demand_data = self.DEMAND_TRACKING_MAP.get(track_name, {})

        # 分析需求风险的各个维度
        factors = []

        # 1. 下游客户集中度
        key_customers = demand_data.get("key_customers", [])
        concentration_factor = RiskFactor(
            name="客户集中度风险",
            description=f"核心客户: {', '.join(key_customers[:5])}",
            probability=RiskLevel.MEDIUM if len(key_customers) < 5 else RiskLevel.LOW,
            impact=RiskLevel.HIGH if len(key_customers) < 5 else RiskLevel.MEDIUM,
            current_progress=f"主要客户数: {len(key_customers)}",
            breakthrough_time="3-6个月",
            tracking_indicators=[
                "前五大客户收入占比",
                "核心客户CAPEX变化",
                "客户订单持续性"
            ],
            data_sources=["公司财报", "行业研报"]
        )
        factors.append(concentration_factor)

        # 2. 宏观经济影响
        macro_factor = RiskFactor(
            name="宏观经济影响",
            description="经济下行可能导致企业投资缩减",
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            current_progress="待跟踪",
            breakthrough_time="6-12个月",
            tracking_indicators=[
                "GDP增速",
                "企业盈利增速",
                "PMI指数",
                "社融数据"
            ],
            data_sources=["国家统计局", "央行数据"]
        )
        factors.append(macro_factor)

        # 3. 政策变化风险
        policy_factor = RiskFactor(
            name="政策变化风险",
            description="补贴政策、产业政策调整可能影响需求",
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            current_progress="当前政策支持力度大",
            breakthrough_time="6-12个月",
            tracking_indicators=[
                "产业政策变化",
                "补贴政策调整",
                "监管政策动向"
            ],
            data_sources=["政府官网", "政策文件"]
        )
        factors.append(policy_factor)

        # 4. 技术落地不及预期
        tech_adoption_factor = RiskFactor(
            name="技术落地不及预期",
            description="新技术商业化进度可能慢于预期",
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.HIGH,
            current_progress=trend_data.get("certainty", "高"),
            breakthrough_time="1-3年",
            tracking_indicators=[
                "技术成熟度曲线位置",
                "标杆项目落地情况",
                "客户付费意愿"
            ],
            data_sources=["行业报告", "客户调研"]
        )
        factors.append(tech_adoption_factor)

        # 5. 竞争格局变化
        competition_factor = RiskFactor(
            name="竞争格局恶化",
            description="行业竞争加剧可能导致价格战",
            probability=RiskLevel.MEDIUM,
            impact=RiskLevel.MEDIUM,
            current_progress="待评估",
            breakthrough_time="6-12个月",
            tracking_indicators=[
                "行业价格走势",
                "新进入者数量",
                "产能扩张速度 vs 需求增速"
            ],
            data_sources=["行业数据", "价格监测"]
        )
        factors.append(competition_factor)

        result.key_factors = factors

        # 确定性高的赛道，需求风险低
        certainty = trend_data.get("certainty", "中")
        if certainty == "高":
            result.overall_probability = RiskLevel.LOW
        elif certainty == "中":
            result.overall_probability = RiskLevel.MEDIUM
        else:
            result.overall_probability = RiskLevel.HIGH

        # 计算风险评分
        score_map = {"高": 20, "中": 12, "低": 5}
        result.risk_score = sum(score_map.get(f.probability.value, 10) for f in factors)
        result.risk_score = min(100, result.risk_score)

        # 核心跟踪指标
        result.tracking_metrics = demand_data.get("leading_indicators", [
            "下游出货量数据",
            "核心客户资本开支",
            "行业价格指数",
            "库存水平变化"
        ])

        # 应对建议
        if result.overall_probability == RiskLevel.HIGH:
            result.mitigation_suggestions = [
                "严格控制仓位",
                "设置明确的止损条件",
                "等待需求数据验证后再加仓"
            ]
            result.rating_adjustment = "下调投资评级至观察"
        elif result.overall_probability == RiskLevel.MEDIUM:
            result.mitigation_suggestions = [
                "密切跟踪需求数据",
                "分散投资降低单一标的风险",
                "关注政策和宏观变化"
            ]
            result.rating_adjustment = "谨慎推荐"
        else:
            result.mitigation_suggestions = [
                "持续跟踪需求数据",
                "定期复查行业景气度"
            ]
            result.rating_adjustment = "维持评级"

        return result


# ============================================================
# 红队证伪综合评估
# ============================================================

class RedTeamAssessor:
    """红队证伪综合评估器"""

    def __init__(self):
        self.tech_assessor = TechSubstitutionRiskAssessor()
        self.supply_assessor = SupplyBreakthroughRiskAssessor()
        self.demand_assessor = DemandDisappointmentRiskAssessor()

    def full_assessment(
        self,
        chokepoint_name: str,
        chokepoint_data: Dict,
        track_name: str,
        trend_data: Dict,
        stock_code: str = "",
        stock_name: str = "",
    ) -> RedTeamReport:
        """
        执行完整的红队证伪评估

        Args:
            chokepoint_name: 瓶颈环节名称
            chokepoint_data: 瓶颈环节数据
            track_name: 赛道名称
            trend_data: 趋势数据
            stock_code: 股票代码
            stock_name: 股票名称

        Returns:
            RedTeamReport: 红队证伪报告
        """
        report = RedTeamReport(
            stock_code=stock_code,
            stock_name=stock_name,
            chokepoint_name=chokepoint_name,
        )

        # 1. 技术替代风险
        report.tech_risk = self.tech_assessor.assess(chokepoint_name)

        # 2. 供给突破风险
        report.supply_risk = self.supply_assessor.assess(chokepoint_data)

        # 3. 需求不及预期风险
        report.demand_risk = self.demand_assessor.assess(track_name, trend_data)

        # 计算综合风险评分
        tech_score = report.tech_risk.risk_score if report.tech_risk else 0
        supply_score = report.supply_risk.risk_score if report.supply_risk else 0
        demand_score = report.demand_risk.risk_score if report.demand_risk else 0

        report.overall_risk_score = (tech_score * 0.4 + supply_score * 0.35 + demand_score * 0.25)

        # 投资逻辑稳健性
        if report.overall_risk_score >= 60:
            report.investment_logic_robustness = "弱 - 风险较高，需谨慎"
            report.rating_suggestion = "观察/规避"
        elif report.overall_risk_score >= 40:
            report.investment_logic_robustness = "中等 - 有一定风险，但可控"
            report.rating_suggestion = "推荐(谨慎)"
        else:
            report.investment_logic_robustness = "强 - 逻辑扎实，风险可控"
            report.rating_suggestion = "强烈推荐"

        # 重点监控点
        monitoring_points = []
        if report.tech_risk:
            monitoring_points.extend(report.tech_risk.tracking_metrics[:2])
        if report.supply_risk:
            monitoring_points.extend(report.supply_risk.tracking_metrics[:2])
        if report.demand_risk:
            monitoring_points.extend(report.demand_risk.tracking_metrics[:2])
        report.key_monitoring_points = monitoring_points[:6]

        return report


# ============================================================
# 便捷函数
# ============================================================

_redteam_instance = None


def get_redteam_assessor() -> RedTeamAssessor:
    """获取红队评估器单例"""
    global _redteam_instance
    if _redteam_instance is None:
        _redteam_instance = RedTeamAssessor()
    return _redteam_instance


def assess_tech_risk(chokepoint_name: str) -> RiskAssessmentResult:
    """便捷函数：评估技术替代风险"""
    return TechSubstitutionRiskAssessor().assess(chokepoint_name)


def assess_supply_risk(chokepoint_data: Dict) -> RiskAssessmentResult:
    """便捷函数：评估供给突破风险"""
    return SupplyBreakthroughRiskAssessor().assess(chokepoint_data)


def assess_demand_risk(track_name: str, trend_data: Dict) -> RiskAssessmentResult:
    """便捷函数：评估需求不及预期风险"""
    return DemandDisappointmentRiskAssessor().assess(track_name, trend_data)


def full_redteam_assessment(
    chokepoint_name: str,
    chokepoint_data: Dict,
    track_name: str,
    trend_data: Dict,
    stock_code: str = "",
    stock_name: str = "",
) -> RedTeamReport:
    """便捷函数：完整红队证伪评估"""
    return get_redteam_assessor().full_assessment(
        chokepoint_name, chokepoint_data, track_name, trend_data,
        stock_code, stock_name
    )


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Serenity风险评估模块测试")
    print("=" * 60)
    print()

    # 测试技术替代风险
    print("【技术替代风险测试】")
    test_cases = ["HBM高带宽内存", "CoWoS先进封装", "激光雷达"]
    for case in test_cases:
        result = assess_tech_risk(case)
        print(f"  {case}:")
        print(f"    发生概率: {result.overall_probability.value}")
        print(f"    影响程度: {result.overall_impact.value}")
        print(f"    风险评分: {result.risk_score:.1f}")
        print(f"    评级建议: {result.rating_adjustment}")
        print()

    # 测试供给突破风险
    print("【供给突破风险测试】")
    sample_data = {
        "expansion_cycle": 24,
        "capacity_util": 95,
        "new_entrants_2y": 0,
        "top1_share": 50,
        "gross_margin": 55,
        "cr3": 95,
        "localization_rate": 5,
        "equipment_lead_time": 18,
    }
    supply_result = assess_supply_risk(sample_data)
    print(f"  HBM高带宽内存供给风险:")
    print(f"    发生概率: {supply_result.overall_probability.value}")
    print(f"    影响程度: {supply_result.overall_impact.value}")
    print(f"    风险评分: {supply_result.risk_score:.1f}")
    print(f"    评级建议: {supply_result.rating_adjustment}")
    print()

    # 测试需求不及预期风险
    print("【需求不及预期风险测试】")
    trend_data = {"certainty": "高"}
    demand_result = assess_demand_risk("AI算力产业链", trend_data)
    print(f"  AI算力产业链需求风险:")
    print(f"    发生概率: {demand_result.overall_probability.value}")
    print(f"    影响程度: {demand_result.overall_impact.value}")
    print(f"    风险评分: {demand_result.risk_score:.1f}")
    print(f"    评级建议: {demand_result.rating_adjustment}")
    print()

    # 完整红队评估
    print("【完整红队证伪评估测试】")
    report = full_redteam_assessment(
        "HBM高带宽内存",
        sample_data,
        "AI算力产业链",
        trend_data,
        "688041",
        "海光信息"
    )
    print(f"  标的: {report.stock_name}({report.stock_code})")
    print(f"  瓶颈: {report.chokepoint_name}")
    print(f"  综合风险评分: {report.overall_risk_score:.1f}")
    print(f"  投资逻辑稳健性: {report.investment_logic_robustness}")
    print(f"  评级建议: {report.rating_suggestion}")
    print(f"  重点监控点:")
    for point in report.key_monitoring_points:
        print(f"    - {point}")
    print()

    print("测试完成！")
