"""
Serenity瓶颈投资 - 产业链数据库
包含多个核心赛道的八层逆向拆解数据

赛道列表：
1. AI算力产业链
2. 半导体/芯片产业链
3. 新能源汽车产业链
4. 人形机器人产业链
5. 光通信产业链
6. 存储芯片产业链
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ChainLayerData:
    """产业链层级数据"""
    layer_num: int                      # 层级编号(1-8)
    layer_name: str                     # 层级名称
    core_products: List[str]            # 核心产品
    key_suppliers_global: List[str]     # 全球关键供应商
    key_suppliers_china: List[str]      # 国内关键供应商（A股）
    bottleneck_question: str            # "缺了什么就停摆"
    notes: str = ""                     # 备注


@dataclass
class ChokepointData:
    """瓶颈环节数据（用于物理四问筛选）"""
    name: str                           # 环节名称
    layer_num: int                      # 所属层级
    chain_position: str                 # 产业链位置描述

    # 物理必需性
    required_per_unit: bool = True      # 每单位终端产品必需
    no_substitute_3y: bool = True       # 3年内无成熟替代
    cost_ratio: float = 2.0             # 成本占比(%)
    failure_impact: str = "产线停摆"     # 失效影响

    # 供给刚性
    global_suppliers: int = 5           # 全球合格供应商数
    industry_cr3: float = 80.0          # 行业CR3(%)
    capacity_util: float = 85.0         # 产能利用率(%)
    expansion_cycle: int = 18           # 产能扩张周期(月)
    equipment_lead_time: int = 12       # 核心设备交付周期(月)

    # 格局垄断
    top1_share: float = 40.0            # 第一名市占率(%)
    top2_sum: float = 70.0              # 前两名合计(%)
    new_entrants_2y: int = 0            # 过去2年新进入者
    gross_margin: float = 45.0          # 毛利率(%)
    patent_barrier: str = "高"          # 专利壁垒

    # 市场忽视度
    mktcap_min: float = 30.0            # 最小市值(亿)
    mktcap_max: float = 200.0           # 最大市值(亿)
    covered_brokers: int = 8            # 近3月覆盖券商数
    fund_holding: float = 3.0           # 公募+北向持仓占比(%)
    recent_gain_6m: float = 30.0        # 近6月累计涨幅(%)

    # 代表标的
    representative_stocks: List[Dict] = field(default_factory=list)

    # 国产化率
    localization_rate: float = 10.0     # 国产化率(%)


@dataclass
class TrackDatabase:
    """赛道数据库"""
    track_name: str                     # 赛道名称
    trend_type: str                     # 驱动类型
    certainty: str                      # 确定性等级
    terminal_drivers: List[str]         # 终端驱动
    capex_entities: List[str]           # CAPEX主体
    growth_rate: str                    # 需求增速
    trend_cycle: str = "3-5年"          # 趋势周期

    # 八层拆解
    chain_layers: List[ChainLayerData] = field(default_factory=list)

    # 候选瓶颈环节
    chokepoint_candidates: List[ChokepointData] = field(default_factory=list)

    # 风险跟踪指标
    risk_indicators: Dict = field(default_factory=dict)


# ============================================================
# 赛道1：AI算力产业链
# ============================================================

AI_COMPUTE_TRACK = TrackDatabase(
    track_name="AI算力产业链",
    trend_type="技术驱动",
    certainty="高",
    terminal_drivers=[
        "大模型训练需求爆发",
        "AI推理应用规模化落地",
        "数据中心算力扩张",
        "云厂商AI服务收入增长"
    ],
    capex_entities=[
        "微软", "谷歌", "亚马逊", "Meta",
        "阿里云", "腾讯云", "百度智能云",
        "字节跳动"
    ],
    growth_rate="年复合增速50%+",
    trend_cycle="3-5年",
    risk_indicators={
        "技术替代": ["新架构GPU", "专用AI芯片", "光子计算"],
        "供给突破": ["新厂商产能", "设备交付周期", "良率提升"],
        "需求不及预期": ["云厂商CAPEX调整", "大模型落地进度", "企业AI投入"]
    }
)

# AI算力 - 八层拆解
AI_COMPUTE_TRACK.chain_layers = [
    ChainLayerData(
        layer_num=1,
        layer_name="终端需求与应用",
        core_products=["大模型训练", "AI推理服务", "AIGC应用", "智能驾驶算力"],
        key_suppliers_global=["OpenAI", "Google", "Anthropic", "Microsoft"],
        key_suppliers_china=["百度", "阿里", "腾讯", "字节跳动", "科大讯飞"],
        bottleneck_question="缺了算力，AI大模型就训练不出来、应用跑不起来"
    ),
    ChainLayerData(
        layer_num=2,
        layer_name="系统集成与服务器",
        core_products=["AI训练服务器", "AI推理服务器", "GPU服务器", "液冷服务器"],
        key_suppliers_global=["戴尔", "HPE", "超微", "联想"],
        key_suppliers_china=["浪潮信息", "中科曙光", "紫光股份", "华为"],
        bottleneck_question="缺了AI服务器，数据中心就无法提供算力"
    ),
    ChainLayerData(
        layer_num=3,
        layer_name="核心计算模块",
        core_products=["GPU模组", "CPU", "DPU", "NPU", "高速互联"],
        key_suppliers_global=["英伟达", "AMD", "英特尔", "博通"],
        key_suppliers_china=["寒武纪", "海光信息", "华为昇腾", "壁仞科技"],
        bottleneck_question="缺了GPU/NPU，服务器就没有AI计算能力"
    ),
    ChainLayerData(
        layer_num=4,
        layer_name="核心芯片与元器件",
        core_products=["GPU芯片", "HBM显存", "SerDes", "高速接口芯片", "电源管理芯片"],
        key_suppliers_global=["英伟达", "三星", "SK海力士", "美光"],
        key_suppliers_china=["长鑫存储", "兆易创新", "韦尔股份"],
        bottleneck_question="缺了HBM显存，GPU性能大幅下降50%以上"
    ),
    ChainLayerData(
        layer_num=5,
        layer_name="封装与组装",
        core_products=["CoWoS先进封装", "2.5D/3D封装", "FCBGA", "EMIB"],
        key_suppliers_global=["台积电", "英特尔", "三星", "日月光"],
        key_suppliers_china=["长电科技", "通富微电", "华天科技", "中芯国际"],
        bottleneck_question="缺了CoWoS，HBM就无法与GPU集成，高端AI芯片造不出来"
    ),
    ChainLayerData(
        layer_num=6,
        layer_name="生产设备与计量仪器",
        core_products=["光刻机", "刻蚀机", "薄膜沉积", "测试设备", "光罩设备"],
        key_suppliers_global=["ASML", "应用材料", "东京电子", "科磊"],
        key_suppliers_china=["北方华创", "中微公司", "芯源微", "长川科技"],
        bottleneck_question="缺了EUV光刻机，7nm以下先进制程就无法生产"
    ),
    ChainLayerData(
        layer_num=7,
        layer_name="核心材料与耗材",
        core_products=["光刻胶", "电子特气", "CMP抛光液", "靶材", "硅片", "光罩"],
        key_suppliers_global=["信越化学", "JSR", "东京应化", "林德", "空气化工"],
        key_suppliers_china=["彤程新材", "晶瑞电材", "华特气体", "江丰电子", "安集科技"],
        bottleneck_question="缺了特定规格光刻胶，晶圆良率大幅下降甚至报废"
    ),
    ChainLayerData(
        layer_num=8,
        layer_name="物理基础设施",
        core_products=["工业电力", "液冷散热", "光纤光缆", "数据中心机柜", "UPS电源"],
        key_suppliers_global=["施耐德", "伊顿", "Vertiv"],
        key_suppliers_china=["宁德时代", "阳光电源", "英维克", "佳力图", "烽火通信"],
        bottleneck_question="缺了足够电力和散热，超算中心无法满载运行"
    )
]

# AI算力 - 候选瓶颈环节
AI_COMPUTE_TRACK.chokepoint_candidates = [
    ChokepointData(
        name="HBM高带宽内存",
        layer_num=4,
        chain_position="存储芯片/核心元器件",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=2.5,
        failure_impact="GPU性能下降50%以上，无法用于AI训练",
        global_suppliers=3,
        industry_cr3=98,
        capacity_util=95,
        expansion_cycle=24,
        equipment_lead_time=18,
        top1_share=45,
        top2_sum=88,
        new_entrants_2y=0,
        gross_margin=55,
        patent_barrier="极高",
        mktcap_min=50,
        mktcap_max=200,
        covered_brokers=6,
        fund_holding=2.5,
        recent_gain_6m=25,
        localization_rate=5,
        representative_stocks=[
            {"code": "688041", "name": "海光信息", "note": "CPU+DCU相关"},
            {"code": "688126", "name": "沪硅产业", "note": "硅片基础材料"},
        ]
    ),
    ChokepointData(
        name="CoWoS先进封装",
        layer_num=5,
        chain_position="先进封装/2.5D封装",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=3.0,
        failure_impact="高端AI芯片无法集成HBM，整颗芯片报废",
        global_suppliers=3,
        industry_cr3=90,
        capacity_util=90,
        expansion_cycle=20,
        equipment_lead_time=15,
        top1_share=60,
        top2_sum=85,
        new_entrants_2y=0,
        gross_margin=48,
        patent_barrier="高",
        mktcap_min=30,
        mktcap_max=150,
        covered_brokers=8,
        fund_holding=3.5,
        recent_gain_6m=40,
        localization_rate=15,
        representative_stocks=[
            {"code": "600584", "name": "长电科技", "note": "国内封测龙头"},
            {"code": "002156", "name": "通富微电", "note": "AMD合作封装"},
        ]
    ),
    ChokepointData(
        name="EUV光刻胶",
        layer_num=7,
        chain_position="半导体材料/光刻材料",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=0.8,
        failure_impact="7nm以下制程晶圆全部报废",
        global_suppliers=3,
        industry_cr3=95,
        capacity_util=90,
        expansion_cycle=36,
        equipment_lead_time=24,
        top1_share=50,
        top2_sum=90,
        new_entrants_2y=0,
        gross_margin=60,
        patent_barrier="极高",
        mktcap_min=30,
        mktcap_max=100,
        covered_brokers=5,
        fund_holding=1.5,
        recent_gain_6m=15,
        localization_rate=2,
        representative_stocks=[
            {"code": "603650", "name": "彤程新材", "note": "光刻胶龙头"},
            {"code": "300655", "name": "晶瑞电材", "note": "光刻胶国产替代"},
        ]
    ),
    ChokepointData(
        name="高速光模块(800G/1.6T)",
        layer_num=3,
        chain_position="光通信/高速互联",
        required_per_unit=True,
        no_substitute_3y=False,
        cost_ratio=4.0,
        failure_impact="数据中心互联带宽不足，算力集群效率下降",
        global_suppliers=8,
        industry_cr3=70,
        capacity_util=80,
        expansion_cycle=12,
        equipment_lead_time=9,
        top1_share=30,
        top2_sum=55,
        new_entrants_2y=2,
        gross_margin=35,
        patent_barrier="中",
        mktcap_min=100,
        mktcap_max=500,
        covered_brokers=25,
        fund_holding=10,
        recent_gain_6m=80,
        localization_rate=50,
        representative_stocks=[
            {"code": "300308", "name": "中际旭创", "note": "光模块龙头"},
            {"code": "002281", "name": "光迅科技", "note": "光器件龙头"},
        ]
    ),
    ChokepointData(
        name="液冷散热方案",
        layer_num=8,
        chain_position="数据中心基础设施/散热",
        required_per_unit=False,
        no_substitute_3y=False,
        cost_ratio=5.0,
        failure_impact="高密度算力集群过热降频，算力利用率下降30%",
        global_suppliers=10,
        industry_cr3=50,
        capacity_util=60,
        expansion_cycle=9,
        equipment_lead_time=6,
        top1_share=20,
        top2_sum=40,
        new_entrants_2y=3,
        gross_margin=30,
        patent_barrier="低",
        mktcap_min=20,
        mktcap_max=80,
        covered_brokers=10,
        fund_holding=2,
        recent_gain_6m=20,
        localization_rate=70,
        representative_stocks=[
            {"code": "002837", "name": "英维克", "note": "液冷龙头"},
            {"code": "603912", "name": "佳力图", "note": "精密空调"},
        ]
    ),
]


# ============================================================
# 赛道2：半导体/芯片产业链
# ============================================================

SEMICONDUCTOR_TRACK = TrackDatabase(
    track_name="半导体/芯片产业链",
    trend_type="政策驱动+国产替代",
    certainty="高",
    terminal_drivers=[
        "国产替代加速",
        "新能源汽车电子需求",
        "AIoT终端爆发",
        "工业自动化升级"
    ],
    capex_entities=[
        "中芯国际", "华虹半导体", "长江存储", "长鑫存储",
        "国家大基金"
    ],
    growth_rate="年复合增速20%+",
    trend_cycle="5-10年",
    risk_indicators={
        "技术替代": ["新制程突破", "新材料应用", "新架构芯片"],
        "供给突破": ["国产设备验证进度", "新晶圆厂投产", "海外厂商扩产"],
        "需求不及预期": ["消费电子需求", "汽车销量", "工业自动化投资"]
    }
)

SEMICONDUCTOR_TRACK.chain_layers = [
    ChainLayerData(
        layer_num=1,
        layer_name="终端应用",
        core_products=["智能手机", "汽车电子", "工业控制", "消费电子", "通信设备"],
        key_suppliers_global=["苹果", "三星", "特斯拉", "华为"],
        key_suppliers_china=["小米", "比亚迪", "华为", "中兴通讯"],
        bottleneck_question="缺了芯片，所有电子产品都无法运转"
    ),
    ChainLayerData(
        layer_num=2,
        layer_name="芯片设计",
        core_products=["SoC", "MCU", "模拟芯片", "功率器件", "传感器"],
        key_suppliers_global=["高通", "联发科", "英伟达", "英特尔", "德州仪器"],
        key_suppliers_china=["韦尔股份", "兆易创新", "紫光国微", "卓胜微"],
        bottleneck_question="缺了芯片设计，就没有可用的芯片产品"
    ),
    ChainLayerData(
        layer_num=3,
        layer_name="晶圆制造代工",
        core_products=["逻辑晶圆代工", "存储晶圆制造", "功率器件制造", "模拟芯片制造"],
        key_suppliers_global=["台积电", "三星", "英特尔", "格芯"],
        key_suppliers_china=["中芯国际", "华虹半导体", "晶合集成"],
        bottleneck_question="缺了晶圆制造，设计好的芯片无法生产"
    ),
    ChainLayerData(
        layer_num=4,
        layer_name="封装测试",
        core_products=["传统封装", "先进封装", "晶圆测试", "成品测试"],
        key_suppliers_global=["日月光", "安靠", "台积电", "三星"],
        key_suppliers_china=["长电科技", "通富微电", "华天科技", "长川科技"],
        bottleneck_question="缺了封装测试，晶圆无法变成可用芯片"
    ),
    ChainLayerData(
        layer_num=5,
        layer_name="半导体设备",
        core_products=["光刻机", "刻蚀机", "薄膜沉积", "离子注入", "CMP抛光", "测试设备"],
        key_suppliers_global=["ASML", "应用材料", "东京电子", "科磊", "泛林"],
        key_suppliers_china=["北方华创", "中微公司", "芯源微", "长川科技", "华峰测控"],
        bottleneck_question="缺了半导体设备，晶圆厂无法建设和运转"
    ),
    ChainLayerData(
        layer_num=6,
        layer_name="半导体材料",
        core_products=["硅片", "光刻胶", "电子特气", "CMP抛光液", "靶材", "湿电子化学品"],
        key_suppliers_global=["信越化学", "SUMCO", "JSR", "林德", "陶氏"],
        key_suppliers_china=["沪硅产业", "彤程新材", "华特气体", "安集科技", "江丰电子"],
        bottleneck_question="缺了半导体材料，晶圆制造无法进行"
    ),
    ChainLayerData(
        layer_num=7,
        layer_name="设备零部件",
        core_products=["真空系统", "射频电源", "精密阀门", "精密电机", "光刻机光学系统"],
        key_suppliers_global=["爱德华", "MKS", "VAT", "蔡司"],
        key_suppliers_china=["富创精密", "新莱应材", "万业企业"],
        bottleneck_question="缺了关键零部件，半导体设备无法制造和维护"
    ),
    ChainLayerData(
        layer_num=8,
        layer_name="基础原材料与能源",
        core_products=["多晶硅", "高纯金属", "工业电力", "工业气体", "超纯水"],
        key_suppliers_global=["瓦克", "REC", "林德集团"],
        key_suppliers_china=["通威股份", "隆基绿能", "宝钢股份", "华测检测"],
        bottleneck_question="缺了基础原材料和能源，整个产业无法运转"
    )
]

SEMICONDUCTOR_TRACK.chokepoint_candidates = [
    ChokepointData(
        name="高端光刻机(DUV/EUV)",
        layer_num=5,
        chain_position="半导体设备/光刻设备",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=1.0,
        failure_impact="先进制程芯片完全无法生产",
        global_suppliers=1,
        industry_cr3=100,
        capacity_util=100,
        expansion_cycle=36,
        equipment_lead_time=24,
        top1_share=100,
        top2_sum=100,
        new_entrants_2y=0,
        gross_margin=70,
        patent_barrier="极高",
        mktcap_min=500,
        mktcap_max=2000,
        covered_brokers=30,
        fund_holding=8,
        recent_gain_6m=50,
        localization_rate=1,
        representative_stocks=[
            {"code": "002371", "name": "北方华创", "note": "设备平台型龙头"},
        ]
    ),
    ChokepointData(
        name="12英寸大硅片",
        layer_num=6,
        chain_position="半导体材料/晶圆材料",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=3.0,
        failure_impact="晶圆厂原材料断供，生产停滞",
        global_suppliers=5,
        industry_cr3=85,
        capacity_util=90,
        expansion_cycle=24,
        equipment_lead_time=18,
        top1_share=35,
        top2_sum=65,
        new_entrants_2y=1,
        gross_margin=40,
        patent_barrier="高",
        mktcap_min=50,
        mktcap_max=300,
        covered_brokers=12,
        fund_holding=4,
        recent_gain_6m=20,
        localization_rate=8,
        representative_stocks=[
            {"code": "688126", "name": "沪硅产业", "note": "12寸硅片龙头"},
        ]
    ),
    ChokepointData(
        name="ArF光刻胶",
        layer_num=6,
        chain_position="半导体材料/光刻材料",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=0.5,
        failure_impact="90nm-14nm制程晶圆良率大幅下降",
        global_suppliers=4,
        industry_cr3=90,
        capacity_util=88,
        expansion_cycle=30,
        equipment_lead_time=20,
        top1_share=40,
        top2_sum=75,
        new_entrants_2y=0,
        gross_margin=55,
        patent_barrier="极高",
        mktcap_min=30,
        mktcap_max=100,
        covered_brokers=6,
        fund_holding=2,
        recent_gain_6m=15,
        localization_rate=5,
        representative_stocks=[
            {"code": "603650", "name": "彤程新材", "note": "ArF光刻胶突破"},
            {"code": "300655", "name": "晶瑞电材", "note": "光刻胶全品类"},
        ]
    ),
    ChokepointData(
        name="刻蚀设备",
        layer_num=5,
        chain_position="半导体设备/蚀刻设备",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=1.5,
        failure_impact="晶圆刻蚀工艺无法完成，芯片报废",
        global_suppliers=3,
        industry_cr3=90,
        capacity_util=85,
        expansion_cycle=24,
        equipment_lead_time=15,
        top1_share=45,
        top2_sum=80,
        new_entrants_2y=1,
        gross_margin=45,
        patent_barrier="高",
        mktcap_min=50,
        mktcap_max=200,
        covered_brokers=15,
        fund_holding=5,
        recent_gain_6m=35,
        localization_rate=20,
        representative_stocks=[
            {"code": "688012", "name": "中微公司", "note": "刻蚀设备龙头"},
            {"code": "002371", "name": "北方华创", "note": "多品类设备"},
        ]
    ),
]


# ============================================================
# 赛道3：新能源汽车产业链
# ============================================================

NEV_TRACK = TrackDatabase(
    track_name="新能源汽车产业链",
    trend_type="政策驱动+需求驱动",
    certainty="高",
    terminal_drivers=[
        "全球电动化率提升",
        "智能化升级",
        "充电基础设施完善",
        "成本下降推动普及"
    ],
    capex_entities=[
        "特斯拉", "比亚迪", "宁德时代", "大众", "丰田",
        "国内新势力"
    ],
    growth_rate="年复合增速30%+",
    trend_cycle="5-10年",
    risk_indicators={
        "技术替代": ["固态电池", "氢燃料电池", "新驱动技术"],
        "供给突破": ["新电池厂投产", "锂矿供给释放", "新玩家进入"],
        "需求不及预期": ["汽车销量", "补贴政策变化", "宏观经济"]
    }
)

NEV_TRACK.chain_layers = [
    ChainLayerData(
        layer_num=1,
        layer_name="整车制造与品牌",
        core_products=["纯电动车", "插电混动", "增程式", "智能驾驶"],
        key_suppliers_global=["特斯拉", "大众", "丰田", "现代"],
        key_suppliers_china=["比亚迪", "理想汽车", "蔚来", "小鹏", "吉利"],
        bottleneck_question="缺了整车厂，新能源汽车无法交付给消费者"
    ),
    ChainLayerData(
        layer_num=2,
        layer_name="核心三电系统",
        core_products=["动力电池", "驱动电机", "电控系统", "BMS电池管理"],
        key_suppliers_global=["松下", "LG新能源", "SK On", "博世", "电装"],
        key_suppliers_china=["宁德时代", "比亚迪电池", "国轩高科", "汇川技术"],
        bottleneck_question="缺了三电系统，新能源汽车就没有动力来源"
    ),
    ChainLayerData(
        layer_num=3,
        layer_name="电池电芯与材料",
        core_products=["正极材料", "负极材料", "隔膜", "电解液", "电芯"],
        key_suppliers_global=["松下", "LG化学", "三星SDI", "住友化学"],
        key_suppliers_china=["宁德时代", "赣锋锂业", "恩捷股份", "天赐材料"],
        bottleneck_question="缺了电池材料，动力电池无法生产"
    ),
    ChainLayerData(
        layer_num=4,
        layer_name="上游矿产资源",
        core_products=["锂矿", "钴矿", "镍矿", "石墨", "稀土", "铜箔"],
        key_suppliers_global=["SQM", "雅宝", "嘉能可", "力拓", "淡水河谷"],
        key_suppliers_china=["天齐锂业", "赣锋锂业", "华友钴业", "北方稀土"],
        bottleneck_question="缺了关键矿产资源，电池产能扩张受制约"
    ),
    ChainLayerData(
        layer_num=5,
        layer_name="智能驾驶系统",
        core_products=["激光雷达", "毫米波雷达", "摄像头", "自动驾驶芯片", "域控制器"],
        key_suppliers_global=["Mobileye", "英伟达", "博世", "大陆", "法雷奥"],
        key_suppliers_china=["华为", "地平线", "速腾聚创", "禾赛科技"],
        bottleneck_question="缺了智能驾驶硬件，高阶智能驾驶功能无法实现"
    ),
    ChainLayerData(
        layer_num=6,
        layer_name="功率半导体",
        core_products=["IGBT", "SiC碳化硅", "MOSFET", "电源管理芯片"],
        key_suppliers_global=["英飞凌", "安森美", "意法半导体", "德州仪器"],
        key_suppliers_china=["斯达半导", "时代电气", "士兰微", "新洁能"],
        bottleneck_question="缺了功率半导体，电机驱动和充电都无法实现"
    ),
    ChainLayerData(
        layer_num=7,
        layer_name="生产设备",
        core_products=["电池生产设备", "整车焊接设备", "激光设备", "检测设备"],
        key_suppliers_global=["德国Manz", "韩国Wonik", "日本制钢所"],
        key_suppliers_china=["先导智能", "利元亨", "赢合科技", "大族激光"],
        bottleneck_question="缺了生产设备，电池厂和整车厂无法建设投产"
    ),
    ChainLayerData(
        layer_num=8,
        layer_name="基础材料与基础设施",
        core_products=["充电设施", "铜铝加工", "钢材", "塑料粒子", "工业电力"],
        key_suppliers_global=["ABB", "西门子", "施耐德"],
        key_suppliers_china=["特锐德", "星星充电", "宝钢股份", "南山铝业"],
        bottleneck_question="缺了充电设施，新能源汽车使用便利性大幅下降"
    )
]

NEV_TRACK.chokepoint_candidates = [
    ChokepointData(
        name="SiC碳化硅功率器件",
        layer_num=6,
        chain_position="功率半导体/SiC器件",
        required_per_unit=False,
        no_substitute_3y=False,
        cost_ratio=2.5,
        failure_impact="高端车型续航和充电速度无法达到设计目标",
        global_suppliers=4,
        industry_cr3=85,
        capacity_util=90,
        expansion_cycle=24,
        equipment_lead_time=18,
        top1_share=40,
        top2_sum=75,
        new_entrants_2y=1,
        gross_margin=50,
        patent_barrier="高",
        mktcap_min=50,
        mktcap_max=300,
        covered_brokers=10,
        fund_holding=4,
        recent_gain_6m=25,
        localization_rate=10,
        representative_stocks=[
            {"code": "600460", "name": "士兰微", "note": "SiC IDM布局"},
            {"code": "300376", "name": "易事特", "note": "SiC应用"},
        ]
    ),
    ChokepointData(
        name="激光雷达",
        layer_num=5,
        chain_position="智能驾驶/感知传感器",
        required_per_unit=False,
        no_substitute_3y=False,
        cost_ratio=3.0,
        failure_impact="高阶自动驾驶功能降级或不可用",
        global_suppliers=8,
        industry_cr3=60,
        capacity_util=50,
        expansion_cycle=12,
        equipment_lead_time=9,
        top1_share=25,
        top2_sum=45,
        new_entrants_2y=3,
        gross_margin=35,
        patent_barrier="中",
        mktcap_min=50,
        mktcap_max=200,
        covered_brokers=15,
        fund_holding=5,
        recent_gain_6m=40,
        localization_rate=40,
        representative_stocks=[
            {"code": "688169", "name": "石头科技", "note": "激光雷达技术"},
            {"code": "688686", "name": "澳华内镜", "note": "光学技术"},
        ]
    ),
    ChokepointData(
        name="电池隔膜",
        layer_num=3,
        chain_position="电池材料/隔膜",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=4.0,
        failure_impact="电池安全性无法保障，存在起火爆炸风险",
        global_suppliers=5,
        industry_cr3=80,
        capacity_util=85,
        expansion_cycle=18,
        equipment_lead_time=12,
        top1_share=35,
        top2_sum=65,
        new_entrants_2y=1,
        gross_margin=40,
        patent_barrier="高",
        mktcap_min=100,
        mktcap_max=500,
        covered_brokers=20,
        fund_holding=8,
        recent_gain_6m=10,
        localization_rate=80,
        representative_stocks=[
            {"code": "002812", "name": "恩捷股份", "note": "隔膜全球龙头"},
        ]
    ),
]


# ============================================================
# 赛道4：人形机器人产业链
# ============================================================

HUMANOID_ROBOT_TRACK = TrackDatabase(
    track_name="人形机器人产业链",
    trend_type="技术驱动",
    certainty="中",
    terminal_drivers=[
        "劳动力成本上升",
        "工业制造自动化",
        "养老陪护需求",
        "AI大模型赋能具身智能"
    ],
    capex_entities=[
        "特斯拉", "波士顿动力", "小米", "优必选",
        "国内科研机构"
    ],
    growth_rate="年复合增速100%+",
    trend_cycle="5-10年",
    risk_indicators={
        "技术替代": ["新驱动技术", "新材料应用", "新AI架构"],
        "供给突破": ["核心零部件量产", "新玩家进入", "成本下降速度"],
        "需求不及预期": ["商业化落地进度", "产品价格", "客户接受度"]
    }
)

HUMANOID_ROBOT_TRACK.chain_layers = [
    ChainLayerData(
        layer_num=1,
        layer_name="整机与应用",
        core_products=["工业人形机器人", "服务型人形机器人", "特种机器人"],
        key_suppliers_global=["特斯拉", "波士顿动力", "Agility Robotics"],
        key_suppliers_china=["优必选", "小米", "傅利叶智能", "智元机器人"],
        bottleneck_question="缺了整机集成，人形机器人产品无法交付"
    ),
    ChainLayerData(
        layer_num=2,
        layer_name="核心执行系统",
        core_products=["伺服电机", "减速器", "编码器", "关节模组", "直线执行器"],
        key_suppliers_global=["哈默纳科", "纳博特斯克", "安川", "松下"],
        key_suppliers_china=["绿的谐波", "双环传动", "汇川技术", "禾川科技"],
        bottleneck_question="缺了减速器和伺服电机，机器人关节无法精确运动"
    ),
    ChainLayerData(
        layer_num=3,
        layer_name="感知与传感系统",
        core_products=["视觉传感器", "力触觉传感器", "IMU", "激光雷达", "声音传感器"],
        key_suppliers_global=["索尼", "基恩士", "CSI", "ATI"],
        key_suppliers_china=["奥比中光", "歌尔股份", "韦尔股份", "汉威科技"],
        bottleneck_question="缺了感知传感器，机器人无法感知环境和操作物体"
    ),
    ChainLayerData(
        layer_num=4,
        layer_name="控制与计算单元",
        core_products=["主控制器", "运动控制芯片", "AI处理器", "实时操作系统"],
        key_suppliers_global=["英伟达", "英特尔", "高通", "德州仪器"],
        key_suppliers_china=["华为昇腾", "全志科技", "瑞芯微", "地平线"],
        bottleneck_question="缺了控制器，机器人无法协调全身运动"
    ),
    ChainLayerData(
        layer_num=5,
        layer_name="动力系统",
        core_products=["电池系统", "电源管理", "无线充电", "驱动电路"],
        key_suppliers_global=["松下", "LG化学", "TI", "ADI"],
        key_suppliers_china=["宁德时代", "比亚迪电池", "亿纬锂能", "圣邦股份"],
        bottleneck_question="缺了动力系统，人形机器人续航时间不足"
    ),
    ChainLayerData(
        layer_num=6,
        layer_name="核心零部件材料",
        core_products=["精密齿轮", "特种合金", "碳纤维材料", "柔性材料", "磁钢"],
        key_suppliers_global=["日本精机", "美国铝业", "东丽"],
        key_suppliers_china=["中钢国际", "光威复材", "中科三环", "宁波韵升"],
        bottleneck_question="缺了高性能材料，机器人重量和性能无法平衡"
    ),
    ChainLayerData(
        layer_num=7,
        layer_name="生产设备与测试",
        core_products=["精密加工设备", "3D打印设备", "测试设备", "校准设备"],
        key_suppliers_global=["DMG MORI", "马扎克", "蔡司", "海克斯康"],
        key_suppliers_china=["大族激光", "迈为股份", "创世纪", "华测检测"],
        bottleneck_question="缺了精密加工设备，高精度零部件无法生产"
    ),
    ChainLayerData(
        layer_num=8,
        layer_name="软件与AI能力",
        core_products=["大模型接口", "运动控制算法", "SLAM导航", "机器视觉算法"],
        key_suppliers_global=["OpenAI", "Google DeepMind", "Boston Dynamics"],
        key_suppliers_china=["百度文心", "阿里通义", "商汤科技", "旷视科技"],
        bottleneck_question="缺了AI算法，人形机器人只是一堆金属不会动"
    )
]

HUMANOID_ROBOT_TRACK.chokepoint_candidates = [
    ChokepointData(
        name="精密减速器(谐波/RV)",
        layer_num=2,
        chain_position="核心零部件/减速器",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=8.0,
        failure_impact="机器人关节精度下降，无法完成精细操作",
        global_suppliers=4,
        industry_cr3=90,
        capacity_util=85,
        expansion_cycle=18,
        equipment_lead_time=12,
        top1_share=40,
        top2_sum=75,
        new_entrants_2y=1,
        gross_margin=45,
        patent_barrier="高",
        mktcap_min=30,
        mktcap_max=150,
        covered_brokers=12,
        fund_holding=4,
        recent_gain_6m=50,
        localization_rate=25,
        representative_stocks=[
            {"code": "688017", "name": "绿的谐波", "note": "谐波减速器龙头"},
            {"code": "002472", "name": "双环传动", "note": "RV减速器突破"},
        ]
    ),
    ChokepointData(
        name="伺服电机与驱动器",
        layer_num=2,
        chain_position="核心零部件/伺服系统",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=6.0,
        failure_impact="关节动力不足，机器人运动性能大幅下降",
        global_suppliers=8,
        industry_cr3=65,
        capacity_util=75,
        expansion_cycle=12,
        equipment_lead_time=9,
        top1_share=30,
        top2_sum=55,
        new_entrants_2y=2,
        gross_margin=35,
        patent_barrier="中",
        mktcap_min=30,
        mktcap_max=200,
        covered_brokers=10,
        fund_holding=3,
        recent_gain_6m=35,
        localization_rate=40,
        representative_stocks=[
            {"code": "300124", "name": "汇川技术", "note": "伺服系统龙头"},
            {"code": "688320", "name": "禾川科技", "note": "伺服与驱动"},
        ]
    ),
    ChokepointData(
        name="力矩传感器",
        layer_num=3,
        chain_position="传感系统/力觉传感",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=1.5,
        failure_impact="机器人无法实现柔顺控制，易损坏工件或自伤",
        global_suppliers=5,
        industry_cr3=85,
        capacity_util=70,
        expansion_cycle=24,
        equipment_lead_time=18,
        top1_share=40,
        top2_sum=70,
        new_entrants_2y=0,
        gross_margin=55,
        patent_barrier="极高",
        mktcap_min=20,
        mktcap_max=80,
        covered_brokers=3,
        fund_holding=1,
        recent_gain_6m=20,
        localization_rate=5,
        representative_stocks=[
            {"code": "300007", "name": "汉威科技", "note": "传感器布局"},
            {"code": "688285", "name": "航天软件", "note": "工业软件"},
        ]
    ),
]


# ============================================================
# 赛道5：光通信产业链
# ============================================================

OPTICAL_COMM_TRACK = TrackDatabase(
    track_name="光通信产业链",
    trend_type="技术驱动+需求驱动",
    certainty="高",
    terminal_drivers=[
        "AI算力带动数据中心互联需求",
        "5G/6G网络建设",
        "光纤到户升级",
        "云服务带宽需求增长"
    ],
    capex_entities=[
        "三大运营商", "云计算厂商", "互联网巨头",
        "海外云厂商"
    ],
    growth_rate="年复合增速25%+",
    trend_cycle="3-5年",
    risk_indicators={
        "技术替代": ["硅光集成", "空间光通信", "新调制技术"],
        "供给突破": ["新产能释放", "新玩家进入", "芯片国产化进度"],
        "需求不及预期": ["云厂商CAPEX", "运营商投资", "AI发展进度"]
    }
)

OPTICAL_COMM_TRACK.chain_layers = [
    ChainLayerData(
        layer_num=1,
        layer_name="终端应用",
        core_products=["数据中心互联", "5G基站", "FTTH光纤到户", "企业网", "城域网"],
        key_suppliers_global=["谷歌", "微软", "亚马逊", "Meta"],
        key_suppliers_china=["三大运营商", "阿里云", "腾讯云", "华为"],
        bottleneck_question="缺了光通信，数据和信号无法高速传输"
    ),
    ChainLayerData(
        layer_num=2,
        layer_name="系统设备",
        core_products=["光传输设备", "光交换机", "路由器", "波分设备"],
        key_suppliers_global=["思科", "瞻博", "诺基亚", "爱立信"],
        key_suppliers_china=["华为", "中兴通讯", "烽火通信", "紫光股份"],
        bottleneck_question="缺了系统设备，光网络无法组网运行"
    ),
    ChainLayerData(
        layer_num=3,
        layer_name="光模块与光器件",
        core_products=["高速光模块", "光收发器", "光分路器", "光连接器"],
        key_suppliers_global=["Coherent", "Lumentum", "新飞通", "Intel"],
        key_suppliers_china=["中际旭创", "新易盛", "光迅科技", "华工科技"],
        bottleneck_question="缺了光模块，光纤中的光信号无法收发"
    ),
    ChainLayerData(
        layer_num=4,
        layer_name="核心光芯片",
        core_products=["激光器芯片", "探测器芯片", "调制器芯片", "硅光芯片"],
        key_suppliers_global=["博通", "Macom", "三菱", "住友", "Infinera"],
        key_suppliers_china=["光迅科技", "源杰科技", "长光华芯", "仕佳光子"],
        bottleneck_question="缺了光芯片，光模块无法实现光电转换"
    ),
    ChainLayerData(
        layer_num=5,
        layer_name="光纤光缆",
        core_products=["单模光纤", "多模光纤", "特种光纤", "海底光缆"],
        key_suppliers_global=["康宁", "古河电工", "住友电工", "普利司通"],
        key_suppliers_china=["长飞光纤", "亨通光电", "中天科技", "烽火通信"],
        bottleneck_question="缺了光纤，光信号就没有传输介质"
    ),
    ChainLayerData(
        layer_num=6,
        layer_name="核心材料",
        core_products=["光纤预制棒", "光芯片材料", "陶瓷插芯", "光纤涂料"],
        key_suppliers_global=["康宁", "信越化学", "藤仓"],
        key_suppliers_china=["长飞光纤", "亨通光电", "天孚通信"],
        bottleneck_question="缺了光纤预制棒，光纤无法生产"
    ),
    ChainLayerData(
        layer_num=7,
        layer_name="生产设备",
        core_products=["光纤拉丝设备", "光芯片制造设备", "光模块测试设备", "熔接设备"],
        key_suppliers_global=["康宁设备", "AIXTRON", "Veeco"],
        key_suppliers_china=["大族激光", "华工科技", "长飞光纤设备"],
        bottleneck_question="缺了生产设备，光通信产品无法制造"
    ),
    ChainLayerData(
        layer_num=8,
        layer_name="基础原材料",
        core_products=["高纯硅", "稀有金属", "塑料粒子", "石英材料"],
        key_suppliers_global=["瓦克", "贺利氏", "康宁"],
        key_suppliers_china=["通威股份", "石英股份", "菲利华"],
        bottleneck_question="缺了高纯石英材料，高端光器件无法生产"
    )
]

OPTICAL_COMM_TRACK.chokepoint_candidates = [
    ChokepointData(
        name="高速光芯片(25G/100G)",
        layer_num=4,
        chain_position="核心光芯片/激光器+探测器",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=3.0,
        failure_impact="高速光模块无法实现核心光电转换功能",
        global_suppliers=5,
        industry_cr3=85,
        capacity_util=85,
        expansion_cycle=24,
        equipment_lead_time=18,
        top1_share=35,
        top2_sum=65,
        new_entrants_2y=1,
        gross_margin=50,
        patent_barrier="高",
        mktcap_min=30,
        mktcap_max=150,
        covered_brokers=8,
        fund_holding=3,
        recent_gain_6m=30,
        localization_rate=15,
        representative_stocks=[
            {"code": "688498", "name": "源杰科技", "note": "光芯片龙头"},
            {"code": "688048", "name": "长光华芯", "note": "激光芯片"},
        ]
    ),
    ChokepointData(
        name="光纤预制棒",
        layer_num=6,
        chain_position="光纤材料/预制棒",
        required_per_unit=True,
        no_substitute_3y=True,
        cost_ratio=5.0,
        failure_impact="光纤产能受限，网络建设进度延迟",
        global_suppliers=6,
        industry_cr3=75,
        capacity_util=85,
        expansion_cycle=18,
        equipment_lead_time=12,
        top1_share=30,
        top2_sum=55,
        new_entrants_2y=1,
        gross_margin=40,
        patent_barrier="高",
        mktcap_min=50,
        mktcap_max=200,
        covered_brokers=8,
        fund_holding=3,
        recent_gain_6m=10,
        localization_rate=60,
        representative_stocks=[
            {"code": "601869", "name": "长飞光纤", "note": "预制棒+光纤龙头"},
        ]
    ),
]


# ============================================================
# 数据库管理类
# ============================================================

class SerenityChainDatabase:
    """Serenity产业链数据库管理"""

    def __init__(self):
        self.tracks: Dict[str, TrackDatabase] = {
            "AI算力产业链": AI_COMPUTE_TRACK,
            "半导体产业链": SEMICONDUCTOR_TRACK,
            "新能源汽车产业链": NEV_TRACK,
            "人形机器人产业链": HUMANOID_ROBOT_TRACK,
            "光通信产业链": OPTICAL_COMM_TRACK,
        }

    def get_all_tracks(self) -> List[str]:
        """获取所有赛道名称"""
        return list(self.tracks.keys())

    def get_track(self, track_name: str) -> Optional[TrackDatabase]:
        """获取指定赛道数据"""
        return self.tracks.get(track_name)

    def search_chokepoint(self, keyword: str) -> List[ChokepointData]:
        """搜索瓶颈环节"""
        results = []
        for track in self.tracks.values():
            for cp in track.chokepoint_candidates:
                if keyword.lower() in cp.name.lower() or keyword.lower() in cp.chain_position.lower():
                    results.append(cp)
        return results

    def get_candidates_for_analysis(self, track_name: str) -> List[Dict]:
        """获取指定赛道的候选环节数据（用于分析）"""
        track = self.get_track(track_name)
        if not track:
            return []

        candidates = []
        for cp in track.chokepoint_candidates:
            candidates.append({
                "name": cp.name,
                "layer_num": cp.layer_num,
                "chain_position": cp.chain_position,
                "required_per_unit": cp.required_per_unit,
                "no_substitute_3y": cp.no_substitute_3y,
                "cost_ratio": cp.cost_ratio,
                "global_suppliers": cp.global_suppliers,
                "cr3": cp.industry_cr3,
                "capacity_util": cp.capacity_util,
                "expansion_cycle": cp.expansion_cycle,
                "equipment_lead_time": cp.equipment_lead_time,
                "top1_share": cp.top1_share,
                "top2_sum": cp.top2_sum,
                "new_entrants_2y": cp.new_entrants_2y,
                "gross_margin": cp.gross_margin,
                "mktcap_min": cp.mktcap_min,
                "mktcap_max": cp.mktcap_max,
                "covered_brokers": cp.covered_brokers,
                "fund_holding": cp.fund_holding,
                "recent_gain_6m": cp.recent_gain_6m,
                "representative_stocks": cp.representative_stocks,
                "localization_rate": cp.localization_rate,
                "failure_impact": cp.failure_impact,
            })
        return candidates

    def get_chain_layers_for_analysis(self, track_name: str) -> List[Dict]:
        """获取指定赛道的八层拆解数据（用于分析）"""
        track = self.get_track(track_name)
        if not track:
            return []

        layers = []
        for layer in track.chain_layers:
            layers.append({
                "layer_num": layer.layer_num,
                "layer_name": layer.layer_name,
                "core_products": layer.core_products,
                "key_suppliers": layer.key_suppliers_global + layer.key_suppliers_china,
                "bottleneck_question": layer.bottleneck_question,
            })
        return layers

    def get_trend_data(self, track_name: str) -> Dict:
        """获取趋势数据（用于第一步分析）"""
        track = self.get_track(track_name)
        if not track:
            return {}

        return {
            "trend_name": track.track_name,
            "trend_type": track.trend_type,
            "certainty": track.certainty,
            "terminal_drivers": track.terminal_drivers,
            "capex_entities": track.capex_entities,
            "growth_rate": track.growth_rate,
            "trend_cycle": track.trend_cycle,
            "risk_indicators": track.risk_indicators,
            "has_capex_plan": True,
            "has_real_data": True,
            "is_irreversible": True,
            "is_tech_driven": "技术驱动" in track.trend_type,
        }


# 全局数据库实例
_chain_db_instance = None


def get_chain_database() -> SerenityChainDatabase:
    """获取产业链数据库单例"""
    global _chain_db_instance
    if _chain_db_instance is None:
        _chain_db_instance = SerenityChainDatabase()
    return _chain_db_instance


# 便捷函数

def list_all_tracks() -> List[str]:
    """列出所有可用赛道"""
    return get_chain_database().get_all_tracks()


def get_track_data(track_name: str) -> Optional[TrackDatabase]:
    """获取赛道数据"""
    return get_chain_database().get_track(track_name)


if __name__ == "__main__":
    db = get_chain_database()
    print("=" * 60)
    print("Serenity产业链数据库")
    print("=" * 60)
    print()
    print(f"可用赛道数量：{len(db.get_all_tracks())}")
    print()
    for track_name in db.get_all_tracks():
        track = db.get_track(track_name)
        print(f"【{track_name}】")
        print(f"  - 确定性等级：{track.certainty}")
        print(f"  - 驱动类型：{track.trend_type}")
        print(f"  - 产业链层数：{len(track.chain_layers)}")
        print(f"  - 候选瓶颈数：{len(track.chokepoint_candidates)}")
        print()
