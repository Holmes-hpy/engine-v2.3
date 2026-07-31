"""
半导体行业Serenity瓶颈分析执行脚本
基于产业链专家初步分析的深度瓶颈剖析
"""

from serenity_chokepoint_agent import SerenityChokepointAnalyzer, EvidenceLevel, ChokepointEvidence, InvestmentDecision, InvestmentRating

# ==================== 半导体行业完整分析数据 ====================
semiconductor_trend_data = {
    "trend_name": "半导体国产替代 + AI算力需求爆发",
    "has_capex_plan": True,
    "has_real_data": True,
    "is_irreversible": True,
    "is_tech_driven": True,
    "terminal_drivers": ["AI大模型训练", "数据中心扩建", "智能手机升级", "新能源车智能化"],
    "capex_entities": ["中芯国际", "长江存储", "长鑫存储", "台积电", "三星", "英特尔"],
    "growth_rate": "年复合增速15-20%",
    "trend_cycle": "3-5年",
    "chain_breakdown": [
        {
            "layer_num": 1,
            "layer_name": "终端需求",
            "core_products": ["AI芯片", "智能手机SoC", "汽车MCU", "存储芯片"],
            "key_suppliers": ["英伟达", "高通", "苹果", "AMD"],
            "bottleneck_question": "缺了高端芯片，AI应用和智能终端就无法落地"
        },
        {
            "layer_num": 2,
            "layer_name": "芯片设计",
            "core_products": ["SoC设计", "IP授权", "EDA工具"],
            "key_suppliers": ["新思科技", "铿腾", "西门子EDA"],
            "bottleneck_question": "缺了高端EDA工具，先进芯片就无法设计"
        },
        {
            "layer_num": 3,
            "layer_name": "晶圆代工",
            "core_products": ["14nm/7nm/5nm芯片制造", "先进封装"],
            "key_suppliers": ["台积电", "三星", "中芯国际"],
            "bottleneck_question": "缺了先进制程产能，高端芯片就无法量产"
        },
        {
            "layer_num": 4,
            "layer_name": "半导体设备",
            "core_products": ["光刻机", "刻蚀机", "沉积设备", "清洗设备"],
            "key_suppliers": ["ASML", "应用材料", "拉姆研究", "东京电子"],
            "bottleneck_question": "缺了EUV光刻机，7nm以下先进制程就无法生产"
        },
        {
            "layer_num": 5,
            "layer_name": "核心材料",
            "core_products": ["光刻胶", "硅片", "电子特气", "靶材", "抛光液"],
            "key_suppliers": ["信越化学", "JSR", "东京应化", "住友化学"],
            "bottleneck_question": "缺了高纯度光刻胶，晶圆良率就大幅下降"
        },
        {
            "layer_num": 6,
            "layer_name": "零部件与耗材",
            "core_products": ["精密轴承", "激光器", "光栅", "掩模版"],
            "key_suppliers": ["蔡司", "通快", "HOYA"],
            "bottleneck_question": "缺了高精度光学部件，光刻机就无法工作"
        },
        {
            "layer_num": 7,
            "layer_name": "检测与计量",
            "core_products": ["电子显微镜", "量测设备", "缺陷检测"],
            "key_suppliers": ["日立高新", "Applied Materials", "KLA"],
            "bottleneck_question": "缺了高精度检测设备，芯片良率就无法保障"
        },
        {
            "layer_num": 8,
            "layer_name": "物理基础设施",
            "core_products": ["超纯水", "特气输送", "洁净室", "电力供应"],
            "key_suppliers": ["各大设备商", "能源公司"],
            "bottleneck_question": "缺了超洁净环境，芯片制造就无法进行"
        }
    ],
    "candidates": [
        {
            "name": "EUV光刻胶",
            "layer_num": 5,
            "chain_position": "核心材料/光刻胶",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 0.8,
            "global_suppliers": 3,
            "cr3": 95,
            "capacity_util": 92,
            "expansion_cycle": 36,
            "top1_share": 45,
            "top2_sum": 85,
            "new_entrants_2y": 0,
            "gross_margin": 65,
            "mktcap_min": 30,
            "mktcap_max": 150,
            "covered_brokers": 8,
            "fund_holding": 3,
            "recent_gain_6m": 35
        },
        {
            "name": "12英寸大硅片",
            "layer_num": 5,
            "chain_position": "核心材料/硅片",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 3.5,
            "global_suppliers": 4,
            "cr3": 85,
            "capacity_util": 88,
            "expansion_cycle": 24,
            "top1_share": 35,
            "top2_sum": 70,
            "new_entrants_2y": 1,
            "gross_margin": 45,
            "mktcap_min": 80,
            "mktcap_max": 300,
            "covered_brokers": 15,
            "fund_holding": 5,
            "recent_gain_6m": 45
        },
        {
            "name": "高端电子特气",
            "layer_num": 5,
            "chain_position": "核心材料/电子特气",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 2.0,
            "global_suppliers": 5,
            "cr3": 75,
            "capacity_util": 85,
            "expansion_cycle": 18,
            "top1_share": 30,
            "top2_sum": 60,
            "new_entrants_2y": 2,
            "gross_margin": 40,
            "mktcap_min": 25,
            "mktcap_max": 120,
            "covered_brokers": 10,
            "fund_holding": 4,
            "recent_gain_6m": 50
        },
        {
            "name": "EUV光刻机",
            "layer_num": 4,
            "chain_position": "核心设备/光刻机",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 15,
            "global_suppliers": 1,
            "cr3": 100,
            "capacity_util": 98,
            "expansion_cycle": 48,
            "top1_share": 100,
            "top2_sum": 100,
            "new_entrants_2y": 0,
            "gross_margin": 70,
            "mktcap_min": 500,
            "mktcap_max": 3000,
            "covered_brokers": 30,
            "fund_holding": 10,
            "recent_gain_6m": 60
        },
        {
            "name": "刻蚀机",
            "layer_num": 4,
            "chain_position": "核心设备/刻蚀机",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 8,
            "global_suppliers": 3,
            "cr3": 80,
            "capacity_util": 90,
            "expansion_cycle": 24,
            "top1_share": 40,
            "top2_sum": 70,
            "new_entrants_2y": 1,
            "gross_margin": 45,
            "mktcap_min": 50,
            "mktcap_max": 200,
            "covered_brokers": 18,
            "fund_holding": 6,
            "recent_gain_6m": 40
        },
        {
            "name": "涂胶显影设备",
            "layer_num": 4,
            "chain_position": "核心设备/涂胶显影",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 5,
            "global_suppliers": 2,
            "cr3": 95,
            "capacity_util": 88,
            "expansion_cycle": 20,
            "top1_share": 70,
            "top2_sum": 95,
            "new_entrants_2y": 0,
            "gross_margin": 50,
            "mktcap_min": 40,
            "mktcap_max": 150,
            "covered_brokers": 12,
            "fund_holding": 4,
            "recent_gain_6m": 30
        },
        {
            "name": "CMP抛光液",
            "layer_num": 5,
            "chain_position": "核心材料/抛光液",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 1.2,
            "global_suppliers": 4,
            "cr3": 70,
            "capacity_util": 82,
            "expansion_cycle": 18,
            "top1_share": 35,
            "top2_sum": 65,
            "new_entrants_2y": 1,
            "gross_margin": 38,
            "mktcap_min": 30,
            "mktcap_max": 100,
            "covered_brokers": 8,
            "fund_holding": 3,
            "recent_gain_6m": 25
        },
        {
            "name": "溅射靶材",
            "layer_num": 5,
            "chain_position": "核心材料/靶材",
            "required_per_unit": True,
            "no_substitute_3y": True,
            "cost_ratio": 1.5,
            "global_suppliers": 5,
            "cr3": 65,
            "capacity_util": 80,
            "expansion_cycle": 15,
            "top1_share": 25,
            "top2_sum": 55,
            "new_entrants_2y": 2,
            "gross_margin": 35,
            "mktcap_min": 20,
            "mktcap_max": 80,
            "covered_brokers": 6,
            "fund_holding": 2,
            "recent_gain_6m": 20
        }
    ]
}

# ==================== 执行Serenity分析 ====================
def run_semiconductor_analysis():
    print("=" * 70)
    print("Serenity瓶颈点投资分析系统 - 半导体行业专项分析")
    print("=" * 70)
    
    # 初始化分析器
    analyzer = SerenityChokepointAnalyzer()
    
    # 执行分析
    report = analyzer.analyze("半导体产业链", semiconductor_trend_data)
    
    # 添加真实证据验证
    evidence_list = [
        ChokepointEvidence(
            stock_code="688012",
            stock_name="中微公司",
            evidence_level=EvidenceLevel.STRONG,
            core_verification_points=["5nm刻蚀机量产交付", "长江存储核心供应商", "毛利率持续提升"],
            performance_elasticity="业绩弹性2-3倍",
            market_cap=1500,
            current_price=350,
            target_price=525,
            upside_ratio=50
        ),
        ChokepointEvidence(
            stock_code="603650",
            stock_name="彤程新材",
            evidence_level=EvidenceLevel.STRONG,
            core_verification_points=["KrF光刻胶量产", "ArF光刻胶研发突破", "客户认证加速"],
            performance_elasticity="业绩弹性3-5倍",
            market_cap=120,
            current_price=65,
            target_price=130,
            upside_ratio=100
        ),
        ChokepointEvidence(
            stock_code="688126",
            stock_name="沪硅产业",
            evidence_level=EvidenceLevel.MEDIUM,
            core_verification_points=["12英寸硅片量产", "客户拓展加速", "产能利用率提升"],
            performance_elasticity="业绩弹性1.5-2倍",
            market_cap=280,
            current_price=25,
            target_price=40,
            upside_ratio=60
        ),
        ChokepointEvidence(
            stock_code="688268",
            stock_name="华特气体",
            evidence_level=EvidenceLevel.MEDIUM,
            core_verification_points=["通过台积电认证", "特种气体国产替代", "毛利率改善"],
            performance_elasticity="业绩弹性1-1.5倍",
            market_cap=80,
            current_price=35,
            target_price=50,
            upside_ratio=43
        ),
        ChokepointEvidence(
            stock_code="688019",
            stock_name="安集科技",
            evidence_level=EvidenceLevel.MEDIUM,
            core_verification_points=["CMP抛光液市占率提升", "技术壁垒巩固", "客户拓展"],
            performance_elasticity="业绩弹性1-1.5倍",
            market_cap=60,
            current_price=80,
            target_price=110,
            upside_ratio=38
        ),
        ChokepointEvidence(
            stock_code="688037",
            stock_name="芯源微",
            evidence_level=EvidenceLevel.MEDIUM,
            core_verification_points=["涂胶显影设备国产替代", "技术突破", "订单增长"],
            performance_elasticity="业绩弹性2-3倍",
            market_cap=90,
            current_price=95,
            target_price=140,
            upside_ratio=47
        )
    ]
    
    report.chokepoint_evidences = evidence_list
    
    # 添加投资决策
    decisions = [
        InvestmentDecision(
            stock_code="688012",
            stock_name="中微公司",
            priority=1,
            rating=InvestmentRating.STRONG_BUY,
            expected_return="50%+",
            suggested_position="重仓",
            buy_conditions=["回调至300元以下", "成交量显著放大", "中芯国际扩产公告"],
            sell_conditions=["达到目标价525元", "刻蚀技术路线被替代", "行业景气度下滑"]
        ),
        InvestmentDecision(
            stock_code="603650",
            stock_name="彤程新材",
            priority=2,
            rating=InvestmentRating.STRONG_BUY,
            expected_return="100%+",
            suggested_position="重仓",
            buy_conditions=["回调至55元以下", "ArF光刻胶认证进展", "机构持续加仓"],
            sell_conditions=["达到目标价130元", "光刻胶技术路线变化", "日本厂商降价"]
        ),
        InvestmentDecision(
            stock_code="688126",
            stock_name="沪硅产业",
            priority=3,
            rating=InvestmentRating.BUY,
            expected_return="60%",
            suggested_position="底仓",
            buy_conditions=["回调至20元以下", "产能利用率提升", "大硅片认证进展"],
            sell_conditions=["达到目标价40元", "硅片价格大幅下跌", "新进入者冲击"]
        ),
        InvestmentDecision(
            stock_code="688268",
            stock_name="华特气体",
            priority=4,
            rating=InvestmentRating.BUY,
            expected_return="43%",
            suggested_position="底仓",
            buy_conditions=["回调至30元以下", "特种气体订单落地", "国产替代加速"],
            sell_conditions=["达到目标价50元", "特气价格战", "供应过剩"]
        ),
        InvestmentDecision(
            stock_code="688037",
            stock_name="芯源微",
            priority=5,
            rating=InvestmentRating.BUY,
            expected_return="47%",
            suggested_position="底仓",
            buy_conditions=["回调至80元以下", "涂胶显影设备订单", "国产替代加速"],
            sell_conditions=["达到目标价140元", "东京电子降价", "技术壁垒被突破"]
        )
    ]
    
    report.investment_decisions = decisions
    
    # 生成并保存报告
    output_path = "/Users/houpengyuan/Documents/trae_projects/a-stock-data/semiconductor_chokepoint_report.md"
    analyzer.save_report(output_path)
    
    # 输出摘要
    summary = analyzer.get_summary()
    print("\n" + "=" * 70)
    print("分析摘要")
    print("=" * 70)
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    return analyzer

if __name__ == "__main__":
    run_semiconductor_analysis()
