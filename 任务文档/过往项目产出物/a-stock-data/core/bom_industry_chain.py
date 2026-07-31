# -*- coding: utf-8 -*-
"""
BOM产业链拆解引擎 - 产业链结构知识库
(Bill of Materials Industry Chain Knowledge Base)

核心思路:
- 拆解上游/中游/下游产业链BOM结构
- 每个节点记录: 定义、技术壁垒、供需关系、代表企业
- 可用于选股时逐级筛选"三高"环节
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ChainLevel(Enum):
    """产业链层级"""
    UPSTREAM = "上游"
    MIDSTREAM = "中游"
    DOWNSTREAM = "下游"


class IndustryCategory(Enum):
    """行业分类"""
    SEMICONDUCTOR = "半导体"
    NEW_ENERGY = "新能源"
    MEDICAL = "医药医疗"
    AI = "人工智能"
    CONSUMER = "消费"
    ADVANCED_MANUFACTURING = "高端制造"


@dataclass
class ChainNode:
    """产业链BOM节点"""
    node_id: str
    name: str
    level: ChainLevel
    category: IndustryCategory
    definition: str
    technical_barrier: str
    supply_demand_balance: str
    growth_stage: str
    leading_stocks: List[Dict] = field(default_factory=list)
    key_metrics: Dict = field(default_factory=dict)
    update_time: str = ""

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "name": self.name,
            "level": self.level.value,
            "category": self.category.value,
            "definition": self.definition,
            "technical_barrier": self.technical_barrier,
            "supply_demand_balance": self.supply_demand_balance,
            "growth_stage": self.growth_stage,
            "leading_stocks": self.leading_stocks,
            "key_metrics": self.key_metrics,
        }


# ============= 半导体产业链 =============

SEMICONDUCTOR_CHAIN = [
    # 上游 - 半导体材料
    ChainNode(
        node_id="Semi-U01",
        name="光刻胶",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="半导体制造核心材料，用于光刻工艺，分为g线(436nm)、i线(365nm)、KrF(248nm)、ArF(193nm)、EUV(13.5nm)",
        technical_barrier="高，EUV光刻胶全球仅少数企业能生产，ArF浸没式技术难度极高，专利壁垒深厚",
        supply_demand_balance="供需紧张，国产化率极低(EUV<5%、ArF<10%、KrF<20%)",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "603650", "name": "彤程新材", "market_share": "国内领先", "barrier_score": 85},
            {"code": "300655", "name": "晶瑞电材", "market_share": "国内领先", "barrier_score": 80},
            {"code": "002409", "name": "雅克科技", "market_share": "国内领先", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约150亿美元", "chinese_market_share": "约15%", "growth_rate": "25%"},
    ),
    ChainNode(
        node_id="Semi-U02",
        name="电子特气",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="半导体制造必需的高纯度气体，包括:硅源、硅烷、氨、笑气、TEOS等，纯度要求99.9999%以上",
        technical_barrier="高纯度提纯技术+稳定供应能力",
        supply_demand_balance="国产化率快速提升，从10%→40%",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688268", "name": "华特气体", "market_share": "国内领先", "barrier_score": 80},
            {"code": "002409", "name": "雅克科技", "market_share": "国内领先", "barrier_score": 85},
            {"code": "002971", "name": "和远气体", "market_share": "国内领先", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约80亿美元", "chinese_market_share": "约40%", "growth_rate": "20%"},
    ),
    ChainNode(
        node_id="Semi-U03",
        name="硅片(晶圆)",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="半导体制造基础材料，从8英寸到12英寸(28nm-3nm)，大硅片是先进制程必需",
        technical_barrier="极高，晶体生长+切片+抛光+外延+检测全流程工艺",
        supply_demand_balance="12英寸国产率<5%，长期依赖进口",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688126", "name": "沪硅产业", "market_share": "国内第一", "barrier_score": 90},
            {"code": "603986", "name": "中环股份", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约120亿美元", "chinese_market_share": "约10%", "growth_rate": "15%"},
    ),
    ChainNode(
        node_id="Semi-U04",
        name="CMP抛光液",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="晶圆平坦化工艺必需材料，抛光液决定抛光质量",
        technical_barrier="高，配方+粒径控制技术",
        supply_demand_balance="国产化率<10%",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688019", "name": "安集科技", "market_share": "国内领先", "barrier_score": 85},
            {"code": "300236", "name": "鼎龙股份", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约20亿美元", "chinese_market_share": "约10%", "growth_rate": "18%"},
    ),
    ChainNode(
        node_id="Semi-U05",
        name="湿电子化学品",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="超净高纯试剂，包含: 硫酸、双氧水、氨水、显影液等",
        technical_barrier="中高，超纯提纯技术",
        supply_demand_balance="国产化率~30%",
        growth_stage="成长期",
        leading_stocks=[
            {"code": "603078", "name": "江化微", "market_share": "国内领先", "barrier_score": 75},
            {"code": "300655", "name": "晶瑞电材", "market_share": "国内领先", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约30亿美元", "chinese_market_share": "约30%", "growth_rate": "15%"},
    ),
    ChainNode(
        node_id="Semi-U06",
        name="靶材",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="物理气相沉积(PVD)必需高纯度金属靶材，包括铝、铜、钽、钛、钴等",
        technical_barrier="高纯度金属冶炼+成型+焊接+绑定工艺",
        supply_demand_balance="国产化率快速提升",
        growth_stage="成长期",
        leading_stocks=[
            {"code": "603722", "name": "阿石创", "market_share": "国内领先", "barrier_score": 75},
            {"code": "300236", "name": "江丰电子", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约20亿美元", "chinese_market_share": "约30%", "growth_rate": "18%"},
    ),
    # 上游 - 半导体设备
    ChainNode(
        node_id="Semi-U11",
        name="光刻机",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="半导体制造最关键设备，EUV(极紫外)是7nm以下必需",
        technical_barrier="极高，EUV全球仅ASML能生产",
        supply_demand_balance="国产化率<1%，全球最卡脖子环节",
        growth_stage="突破前夜",
        leading_stocks=[
            {"code": "002371", "name": "北方华创", "market_share": "国内平台型", "barrier_score": 95},
            {"code": "688012", "name": "中微公司", "market_share": "蚀刻设备领先", "barrier_score": 90},
        ],
        key_metrics={"global_market_size": "约250亿美元", "chinese_market_share": "约5%", "growth_rate": "30%"},
    ),
    ChainNode(
        node_id="Semi-U12",
        name="蚀刻机",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="晶圆刻蚀工艺核心设备，等离子体刻蚀，包括干法刻蚀(DRIE/RIE)和湿法刻蚀",
        technical_barrier="高，等离子体控制技术，高频射频源，工艺匹配",
        supply_demand_balance="国产化率~20%，中微公司5nm突破",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688012", "name": "中微公司", "market_share": "全球前列", "barrier_score": 90},
            {"code": "002371", "name": "北方华创", "market_share": "国内领先", "barrier_score": 90},
        ],
        key_metrics={"global_market_size": "约200亿美元", "chinese_market_share": "约20%", "growth_rate": "25%"},
    ),
    ChainNode(
        node_id="Semi-U13",
        name="涂胶显影设备",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="光刻工艺配套设备，涂胶+烘烤+显影",
        technical_barrier="中高，精密机械+温度控制+工艺匹配",
        supply_demand_balance="国产化率~10%",
        growth_stage="成长期",
        leading_stocks=[
            {"code": "688037", "name": "芯源微", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约30亿美元", "chinese_market_share": "约10%", "growth_rate": "22%"},
    ),
    ChainNode(
        node_id="Semi-U14",
        name="测试设备",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="晶圆测试、芯片测试、封测测试设备",
        technical_barrier="高，SoC/存储芯片测试算法+探针卡",
        supply_demand_balance="国产化率~15%",
        growth_stage="成长期",
        leading_stocks=[
            {"code": "688200", "name": "华峰测控", "market_share": "国内领先", "barrier_score": 80},
            {"code": "688110", "name": "芯原股份", "market_share": "国内领先", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约80亿美元", "chinese_market_share": "约15%", "growth_rate": "20%"},
    ),
    # 中游 - 制造
    ChainNode(
        node_id="Semi-M01",
        name="晶圆代工(制造)",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="集成电路晶圆制造，逻辑芯片、存储芯片、功率半导体制造",
        technical_barrier="极高，先进制程(14nm/7nm/5nm/3nm)工艺集成度极复杂",
        supply_demand_balance="全球产能紧张，国产替代需求强烈",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688981", "name": "中芯国际", "market_share": "国内第一", "barrier_score": 95},
            {"code": "688126", "name": "华虹半导体", "market_share": "国内第二", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约1200亿美元", "chinese_market_share": "约15%", "growth_rate": "20%"},
    ),
    ChainNode(
        node_id="Semi-M02",
        name="存储芯片",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="DRAM/NAND Flash存储芯片",
        technical_barrier="极高，3D堆叠工艺(100+层)，先进制程",
        supply_demand_balance="国产化率<10%，全球仅三星/海力士/美光/铠侠",
        growth_stage="周期底部→复苏期",
        leading_stocks=[
            {"code": "688041", "name": "长鑫存储", "market_share": "国内DRAM第一", "barrier_score": 95},
        ],
        key_metrics={"global_market_size": "约1600亿美元", "chinese_market_share": "约5%", "growth_rate": "25%"},
    ),
    # 下游
    ChainNode(
        node_id="Semi-D01",
        name="芯片设计(高端)",
        level=ChainLevel.DOWNSTREAM,
        category=IndustryCategory.SEMICONDUCTOR,
        definition="SoC、AI芯片、GPU、FPGA高端芯片设计",
        technical_barrier="高，架构设计+EDA工具+IP授权",
        supply_demand_balance="高端GPU/AI芯片国产率极低",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688256", "name": "寒武纪", "market_share": "AI芯片领先", "barrier_score": 85},
            {"code": "688041", "name": "海光信息", "market_share": "国内领先", "barrier_score": 85},
            {"code": "300782", "name": "卓胜微", "market_share": "射频芯片", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约1000亿美元", "chinese_market_share": "约15%", "growth_rate": "30%"},
    ),
]

# ============= 新能源产业链 =============

NEW_ENERGY_CHAIN = [
    # 上游 - 锂电材料
    ChainNode(
        node_id="NE-U01",
        name="锂矿/锂盐",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="碳酸锂、氢氧化锂，锂电池核心原材料",
        technical_barrier="中，资源勘探+盐湖提锂/锂矿石提锂",
        supply_demand_balance="2022年供需紧张→2025年供需平衡→2026年可能过剩",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "002460", "name": "赣锋锂业", "market_share": "全球前列", "barrier_score": 80},
            {"code": "002466", "name": "天齐锂业", "market_share": "全球前列", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约80亿美元", "chinese_market_share": "约70%", "growth_rate": "10%"},
    ),
    ChainNode(
        node_id="NE-U02",
        name="正极材料",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="三元材料(NCM/NCA)/磷酸铁锂(LFP)/富锂锰基",
        technical_barrier="中高，高镍三元技术壁垒较高",
        supply_demand_balance="高镍三元供需紧平衡，LFP过剩",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "300073", "name": "当升科技", "market_share": "国内领先", "barrier_score": 75},
            {"code": "002074", "name": "容百科技", "market_share": "国内领先", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约150亿美元", "chinese_market_share": "约80%", "growth_rate": "25%"},
    ),
    ChainNode(
        node_id="NE-U03",
        name="负极材料",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="人造石墨/天然石墨/硅基负极",
        technical_barrier="中，硅基负极壁垒较高",
        supply_demand_balance="人造石墨供需平衡，硅基负极处于产业化初期",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "300035", "name": "中科电气", "market_share": "国内领先", "barrier_score": 70},
            {"code": "600884", "name": "杉杉股份", "market_share": "国内领先", "barrier_score": 70},
        ],
        key_metrics={"global_market_size": "约80亿美元", "chinese_market_share": "约85%", "growth_rate": "20%"},
    ),
    ChainNode(
        node_id="NE-U04",
        name="电解液/电解质",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="六氟磷酸锂+添加剂+溶剂体系",
        technical_barrier="中，新型锂盐(LiFSI等)技术壁垒较高",
        supply_demand_balance="六氟磷酸锂价格大幅波动，新型锂盐国产替代",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "002709", "name": "天赐材料", "market_share": "全球前列", "barrier_score": 75},
            {"code": "002411", "name": "新宙邦", "market_share": "国内领先", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约60亿美元", "chinese_market_share": "约80%", "growth_rate": "15%"},
    ),
    # 中游
    ChainNode(
        node_id="NE-M01",
        name="锂电池电芯",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="锂离子动力电池电芯制造",
        technical_barrier="高，4680大圆柱/高镍/硅基等先进电芯",
        supply_demand_balance="头部企业扩产，二线产能过剩",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "300750", "name": "宁德时代", "market_share": "全球第一", "barrier_score": 90},
            {"code": "002594", "name": "比亚迪", "market_share": "全球第二", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约600亿美元", "chinese_market_share": "约65%", "growth_rate": "30%"},
    ),
    ChainNode(
        node_id="NE-M02",
        name="光伏硅料",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="多晶硅料/单晶硅棒/硅片",
        technical_barrier="中，西门子法改良工艺",
        supply_demand_balance="2022年短缺→2025年过剩→供需波动",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "601012", "name": "隆基绿能", "market_share": "全球前列", "barrier_score": 80},
            {"code": "600438", "name": "通威股份", "market_share": "全球前列", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约200亿美元", "chinese_market_share": "约90%", "growth_rate": "20%"},
    ),
    # 下游
    ChainNode(
        node_id="NE-D01",
        name="新能源汽车整车",
        level=ChainLevel.DOWNSTREAM,
        category=IndustryCategory.NEW_ENERGY,
        definition="纯电动车(BEV)/插电混动(PHEV)/增程式(EREV)",
        technical_barrier="中高，三电系统集成+智能座舱+自动驾驶",
        supply_demand_balance="2025-2026年需求增速放缓，竞争激烈",
        growth_stage="成长期",
        leading_stocks=[
            {"code": "002594", "name": "比亚迪", "market_share": "全球第一", "barrier_score": 85},
            {"code": "601127", "name": "赛力斯", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约800亿美元", "chinese_market_share": "约60%", "growth_rate": "30%"},
    ),
]

# ============= 医药医疗产业链 =============

MEDICAL_CHAIN = [
    # 上游 - 医疗设备核心零部件
    ChainNode(
        node_id="Med-U01",
        name="CT球管",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="CT扫描仪核心部件，产生X射线的真空管，包含电子枪、阳极靶、真空封装",
        technical_barrier="极高，真空技术+耐高温材料+寿命控制，全球仅西门子GE/飞利浦/瓦里安垄断",
        supply_demand_balance="国产化率<15%，国产替代空间巨大",
        growth_stage="突破前夜",
        leading_stocks=[
            {"code": "688301", "name": "奕瑞科技", "market_share": "国内领先，在研", "barrier_score": 90},
        ],
        key_metrics={"global_market_size": "约20亿美元", "chinese_market_share": "约10%", "growth_rate": "25%"},
    ),
    ChainNode(
        node_id="Med-U02",
        name="X线探测器",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="平板探测器，DR/CT/DSA设备的成像核心",
        technical_barrier="高，闪烁体材料+CMOS/TFT工艺+信号处理",
        supply_demand_balance="国产化率~40%，奕瑞科技全球前列",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688301", "name": "奕瑞科技", "market_share": "全球前列", "barrier_score": 85},
            {"code": "688607", "name": "康众医疗", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约30亿美元", "chinese_market_share": "约40%", "growth_rate": "18%"},
    ),
    ChainNode(
        node_id="Med-U03",
        name="医用同位素",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="核医学诊断治疗用放射性核素:氟-18、锝-99m、镥-177、锕-225等",
        technical_barrier="极高，反应堆/加速器生产+分离提纯+放射性药物制剂",
        supply_demand_balance="国产化率<10%，三种阿尔法同位素量产突破",
        growth_stage="突破前夜",
        leading_stocks=[
            {"code": "000777", "name": "中核科技", "market_share": "国内领先", "barrier_score": 90},
            {"code": "000881", "name": "中广核技", "market_share": "国内领先", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约15亿美元", "chinese_market_share": "约10%", "growth_rate": "25%"},
    ),
    # 上游 - 医药原材料
    ChainNode(
        node_id="Med-U04",
        name="API原料药",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="化学原料药，药物活性成分，包含大宗原料药、特色原料药、专利期原料药",
        technical_barrier="中低→中高(特色/高端API)",
        supply_demand_balance="中国API产能占全球50%+，高端API仍需进口",
        growth_stage="成熟期→升级期",
        leading_stocks=[
            {"code": "600521", "name": "华海药业", "market_share": "全球前列", "barrier_score": 75},
            {"code": "300702", "name": "天宇股份", "market_share": "国内领先", "barrier_score": 70},
        ],
        key_metrics={"global_market_size": "约1850亿美元", "chinese_market_share": "约50%", "growth_rate": "7%"},
    ),
    ChainNode(
        node_id="Med-U05",
        name="细胞培养基",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="生物药/疫苗/细胞治疗必需的细胞培养液，包含基础培养基、补料培养基、无血清培养基",
        technical_barrier="高，配方+细胞系+质量控制，赛默飞/丹纳赫/默克三家垄断全球90%",
        supply_demand_balance="国产化率<20%，国产替代空间大",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688361", "name": "奥浦迈", "market_share": "国内领先", "barrier_score": 85},
            {"code": "872808", "name": "健顺生物", "market_share": "国内领先", "barrier_score": 80},
        ],
        key_metrics={"global_market_size": "约50亿美元", "chinese_market_share": "约15%", "growth_rate": "20%"},
    ),
    # 中游
    ChainNode(
        node_id="Med-M01",
        name="医疗影像设备",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="CT/MRI/DR/DSA/PET-CT等大型医疗影像设备",
        technical_barrier="高，系统集成能力，GPS三巨头垄断高端",
        supply_demand_balance="国产化率DR>60%(中低端)，高端CT/MRI<30%",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "688271", "name": "联影医疗", "market_share": "国内第一", "barrier_score": 90},
            {"code": "300760", "name": "迈瑞医疗", "market_share": "国内领先", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约400亿美元", "chinese_market_share": "约30%", "growth_rate": "15%"},
    ),
    ChainNode(
        node_id="Med-M02",
        name="常规医疗设备",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="监护仪、呼吸机、超声、体外诊断设备等常规医疗设备",
        technical_barrier="中，中国企业已在常规设备领域全球领先",
        supply_demand_balance="国产化率>80%，国产替代基本完成",
        growth_stage="成熟期",
        leading_stocks=[
            {"code": "300760", "name": "迈瑞医疗", "market_share": "全球前三", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约300亿美元", "chinese_market_share": "约60%", "growth_rate": "10%"},
    ),
    ChainNode(
        node_id="Med-M03",
        name="创新药/生物药",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.MEDICAL,
        definition="创新小分子药物、单抗/双抗/ADC等生物药、细胞基因治疗",
        technical_barrier="极高，靶点发现+临床开发+商业化能力",
        supply_demand_balance="PD-1等热门靶点内卷，出海成为新增长点",
        growth_stage="快速成长期",
        leading_stocks=[
            {"code": "600276", "name": "恒瑞医药", "market_share": "国内创新药龙头", "barrier_score": 90},
            {"code": "688235", "name": "百济神州", "market_share": "国内领先", "barrier_score": 85},
        ],
        key_metrics={"global_market_size": "约2000亿美元", "chinese_market_share": "约15%", "growth_rate": "18%"},
    ),
]

# ============= AI产业链 =============

AI_CHAIN = [
    ChainNode(
        node_id="AI-U01",
        name="AI芯片(GPU/ASIC/NPU)",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.AI,
        definition="人工智能加速芯片，GPU/TPU/NPU/ASIC等",
        technical_barrier="极高，架构设计+先进制程+软件栈",
        supply_demand_balance="高端GPU全球英伟达垄断，国产替代空间大",
        growth_stage="爆发期",
        leading_stocks=[
            {"code": "688256", "name": "寒武纪-U", "market_share": "AI芯片领先", "barrier_score": 95},
            {"code": "688981", "name": "海光信息", "market_share": "国内领先", "barrier_score": 90},
        ],
        key_metrics={"global_market_size": "约1500亿美元", "chinese_market_share": "约10%", "growth_rate": "60%"},
    ),
    ChainNode(
        node_id="AI-U02",
        name="EDA工具",
        level=ChainLevel.UPSTREAM,
        category=IndustryCategory.AI,
        definition="电子设计自动化软件，芯片设计必需工具",
        technical_barrier="极高，新思/铿腾/西门子EDA三家垄断全球90%+",
        supply_demand_balance="国产化率<10%，最卡脖子环节",
        growth_stage="突破前夜",
        leading_stocks=[
            {"code": "688206", "name": "概伦电子", "market_share": "国内领先", "barrier_score": 90},
        ],
        key_metrics={"global_market_size": "约180亿美元", "chinese_market_share": "约10%", "growth_rate": "18%"},
    ),
    ChainNode(
        node_id="AI-M01",
        name="大模型/算法",
        level=ChainLevel.MIDSTREAM,
        category=IndustryCategory.AI,
        definition="通用大语言模型/多模态大模型/行业大模型",
        technical_barrier="高，数据+算力+算法+工程化",
        supply_demand_balance="国产大模型快速追赶OpenAI",
        growth_stage="爆发期",
        leading_stocks=[
            {"code": "300059", "name": "昆仑万维", "market_share": "大模型应用", "barrier_score": 75},
        ],
        key_metrics={"global_market_size": "约500亿美元", "chinese_market_share": "约30%", "growth_rate": "80%"},
    ),
]


# ============= 统一接口 =============

ALL_CHAINS = {
    "半导体": SEMICONDUCTOR_CHAIN,
    "新能源": NEW_ENERGY_CHAIN,
    "医药医疗": MEDICAL_CHAIN,
    "人工智能": AI_CHAIN,
}


def get_chain_by_category(category: str) -> List[ChainNode]:
    """获取指定行业的产业链"""
    return ALL_CHAINS.get(category, [])


def get_all_leading_stocks() -> List[Dict]:
    """获取所有龙头企业"""
    all_stocks = []
    for chain in ALL_CHAINS.values():
        for node in chain:
            for stock in node.leading_stocks:
                stock["node_name"] = node.name
                stock["category"] = node.category.value
                stock["level"] = node.level.value
                stock["barrier"] = node.technical_barrier
                stock["supply_demand"] = node.supply_demand_balance
                stock["growth_stage"] = node.growth_stage
                stock["key_metrics"] = str(node.key_metrics)
                all_stocks.append(stock)
    return all_stocks


def get_highest_barrier_nodes(barrier_threshold: int = 80) -> List[ChainNode]:
    """筛选高壁垒环节"""
    high_barrier_nodes = []
    for chain in ALL_CHAINS.values():
        for node in chain:
            # 评估壁垒分数
            barrier_score = max(
                [s.get("barrier_score", 0) for s in node.leading_stocks] + [0]
            )
            if barrier_score >= barrier_threshold:
                high_barrier_nodes.append(node)
    return high_barrier_nodes
