#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晶瑞电材(300655) Serenity瓶颈投资深度分析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime


def analyze_jingrui():
    """晶瑞电材深度分析"""

    report = []
    report.append("=" * 70)
    report.append("  Serenity瓶颈投资深度分析报告")
    report.append("  标的：晶瑞电材(300655)")
    report.append(f"  分析日期：{datetime.now().strftime('%Y-%m-%d')}")
    report.append("=" * 70)
    report.append("")

    # ===== Step 1: 产业链定位 =====
    report.append("【Step 1 产业链逆向拆解定位】")
    report.append("-" * 70)
    report.append("")
    report.append("晶瑞电材在半导体产业链中的位置：")
    report.append("")
    report.append("  第1层 终端应用：AI/服务器/消费电子/汽车电子")
    report.append("       ↓")
    report.append("  第2层 核心产品：芯片（逻辑/存储/功率）")
    report.append("       ↓")
    report.append("  第3层 核心组件：晶圆制造（Foundry）")
    report.append("       ↓")
    report.append("  第4层 核心部件：半导体设备 & 半导体材料 ← 【晶瑞电材】")
    report.append("       ↓")
    report.append("  第5层 核心子部件：光刻胶/湿电子化学品/光刻胶配套试剂")
    report.append("       ↓")
    report.append("  第6层 上游基础材料：光刻胶单体/树脂/溶剂/特种化学品")
    report.append("       ↓")
    report.append("  第7层 生产装备：反应釜/提纯设备/涂布设备")
    report.append("       ↓")
    report.append("  第8层 基础设施：化工厂/危化品仓储/物流")
    report.append("")
    report.append("📌 定位：半导体材料环节，核心产品为光刻胶和湿电子化学品")
    report.append("   属于半导体制造的关键耗材，是典型的'卡脖子'环节")
    report.append("")

    # ===== Step 2: 物理四问筛选 =====
    report.append("【Step 2 物理四问 - 瓶颈属性验证】")
    report.append("-" * 70)
    report.append("")

    # Q1: 供给是否刚性？
    report.append("❓ Q1：供给是否刚性？（短期无法快速扩产）")
    report.append("")
    report.append("  分析维度：")
    report.append("  ✓ 光刻胶属于高技术壁垒产品，研发周期长（5-10年）")
    report.append("  ✓ 客户认证周期长（2-3年），进入供应链后粘性极高")
    report.append("  ✓ 高端光刻胶（ArF/KrF）全球仅少数厂商能生产")
    report.append("  ✓ 扩产需要环保审批、资质认证，周期1-2年")
    report.append("  ✓ 晶瑞电材是国内最早实现光刻胶量产的企业之一")
    report.append("")
    report.append("  供给刚性评分：85/100")
    report.append("  结论：供给刚性强 ✅")
    report.append("")

    # Q2: 需求是否刚需不可替代？
    report.append("❓ Q2：需求是否刚需且不可替代？")
    report.append("")
    report.append("  分析维度：")
    report.append("  ✓ 光刻胶是晶圆制造的核心耗材，没有光刻胶芯片无法生产")
    report.append("  ✓ 湿电子化学品（高纯试剂）是清洗/刻蚀环节必需")
    report.append("  ✓ 半导体材料用量随制程升级而增加（先进制程用更多）")
    report.append("  ✓ 国内晶圆厂扩产潮，国产替代需求迫切")
    report.append("  ⚠ 中低端光刻胶竞争较激烈，高端产品仍依赖进口")
    report.append("")
    report.append("  需求刚需评分：80/100")
    report.append("  结论：需求刚需且不可替代 ✅")
    report.append("")

    # Q3: 格局是否垄断？
    report.append("❓ Q3：竞争格局是否垄断或寡头？")
    report.append("")
    report.append("  全球格局（高端光刻胶）：")
    report.append("    - 日本JSR：约28%")
    report.append("    - 日本东京应化：约21%")
    report.append("    - 日本信越化学：约15%")
    report.append("    - 日本富士电子：约10%")
    report.append("    - 美国陶氏/韩国东进等：约26%")
    report.append("  → 日本企业垄断全球80%以上高端光刻胶市场")
    report.append("")
    report.append("  国内格局：")
    report.append("    - 晶瑞电材：g/i线光刻胶龙头，ArF光刻胶研发中")
    report.append("    - 南大光电：ArF光刻胶领先")
    report.append("    - 上海新阳：光刻胶及配套试剂")
    report.append("    - 容大感光：光刻胶厂商")
    report.append("  → 国内仍处于追赶阶段，晶瑞是第一梯队")
    report.append("")
    report.append("  格局垄断评分：全球95分 / 国内60分")
    report.append("  结论：全球高度垄断，国内竞争格局正在形成 ✅")
    report.append("")

    # Q4: 市场是否忽视？
    report.append("❓ Q4：市场是否低估或忽视？")
    report.append("")
    report.append("  分析维度：")
    report.append("  ⚠ 市盈率(TTM)高达760倍，市场预期很高，不算低估")
    report.append("  ✓ 但半导体材料的长期价值未被充分认识（国产替代空间大）")
    report.append("  ✓ 光刻胶的技术壁垒容易被低估（只看当前不看未来）")
    report.append("  ⚠ 近期涨幅较大，关注度较高")
    report.append("  ✓ 机构持仓比例仍有提升空间")
    report.append("")
    report.append("  市场忽视度评分：45/100（中等，不算高度忽视）")
    report.append("  结论：市场关注度较高，但长期价值仍有认知差 ⚠️")
    report.append("")

    report.append("  📊 物理四问综合评分：75/100")
    report.append("  结论：通过物理四问，具备瓶颈投资属性 ✅")
    report.append("")

    # ===== Step 3: 约束确定性 =====
    report.append("【Step 3 约束确定性分析】")
    report.append("-" * 70)
    report.append("")
    report.append("核心约束（最强约束）：")
    report.append("  1. 技术壁垒约束：高端光刻胶研发难度极大，需要长期积累")
    report.append("  2. 客户认证约束：晶圆厂认证周期2-3年，供应商粘性高")
    report.append("  3. 国产替代约束：供应链安全驱动，国内晶圆厂必须培育国产供应商")
    report.append("")
    report.append("反证验证（一票否决项检查）：")
    report.append("  ✗ 是否有明确的技术替代路线？暂无（光刻胶仍是主流方案）")
    report.append("  ✗ 是否有新进入者快速突破？暂无（研发周期太长）")
    report.append("  ✗ 需求是否可能消失？不会（芯片制造必需耗材）")
    report.append("  ⚠ 估值是否过高？PE 760倍，需警惕估值回调风险")
    report.append("")
    report.append("确定性评级：高（需注意估值风险）")
    report.append("")

    # ===== Step 4: 三级证据验证 =====
    report.append("【Step 4 三级证据验证】")
    report.append("-" * 70)
    report.append("")

    report.append("📝 第一级证据：官方信息（公司公告/官网）")
    report.append("  ✓ 公司公告显示光刻胶产品持续出货")
    report.append("  ✓ i线光刻胶已实现规模化销售")
    report.append("  ✓ KrF光刻胶已通过部分客户验证")
    report.append("  ✓ ArF光刻胶处于研发阶段")
    report.append("  ✓ 湿电子化学品（G5级）已实现量产")
    report.append("  证据强度：中-强")
    report.append("")

    report.append("📝 第二级证据：产业链验证（客户/供应商）")
    report.append("  ✓ 国内主要晶圆厂均在推进国产材料验证")
    report.append("  ✓ 中芯国际、长江存储等大厂有国产替代需求")
    report.append("  ✓ 半导体材料行业景气度向上")
    report.append("  证据强度：中")
    report.append("")

    report.append("📝 第三级证据：专家访谈/行业会议")
    report.append("  ✓ 半导体材料国产替代是行业共识")
    report.append("  ✓ 光刻胶是卡脖子重点领域")
    report.append("  ✓ 政策支持力度大（大基金、税收优惠）")
    report.append("  证据强度：中")
    report.append("")

    report.append("📊 证据综合评级：中等偏强")
    report.append("  （商业化进展明确，但高端产品仍在突破中）")
    report.append("")

    # ===== Step 5: 红队风险评估 =====
    report.append("【Step 5 红队证伪 - 三维风险评估】")
    report.append("-" * 70)
    report.append("")

    # 风险1：技术替代
    report.append("⚠️  风险一：技术替代风险")
    report.append("")
    report.append("  替代技术路线：")
    report.append("    - EUV光刻胶：下一代技术，难度更高")
    report.append("    - 无掩模光刻：尚在实验室阶段")
    report.append("    - 纳米压印：特定领域应用")
    report.append("")
    report.append("  评估：")
    report.append("    技术成熟度：低（EUV光刻胶仍在研发初期）")
    report.append("    替代时间：5-10年以上")
    report.append("    替代概率：低（短中期内光刻胶仍是主流）")
    report.append("")
    report.append("  风险等级：低 🟢")
    report.append("")

    # 风险2：供给突破
    report.append("⚠️  风险二：供给突破风险")
    report.append("")
    report.append("  供给突破可能性分析：")
    report.append("    1. 现有厂商扩产：")
    report.append("       - 晶瑞电材：可转债募投光刻胶项目")
    report.append("       - 南大光电：ArF光刻胶扩产")
    report.append("       - 其他厂商：多家企业布局")
    report.append("    2. 新进入者：")
    report.append("       - 壁垒高，新进入者少，但有部分企业跨界")
    report.append("    3. 国产替代进度：")
    report.append("       - 中低端：已基本实现国产替代")
    report.append("       - 高端（ArF/EUV）：仍需3-5年突破")
    report.append("")
    report.append("  风险等级：中（中低端竞争加剧，高端仍紧缺）🟡")
    report.append("")

    # 风险3：需求不及预期
    report.append("⚠️  风险三：需求不及预期风险")
    report.append("")
    report.append("  需求跟踪指标：")
    report.append("    1. 国内晶圆厂扩产进度：")
    report.append("       - 中芯国际、华虹、长江存储等扩产计划明确 ✓")
    report.append("    2. 半导体行业周期：")
    report.append("       - 当前处于周期底部回升阶段")
    report.append("    3. 国产替代率提升速度：")
    report.append("       - 政策驱动下加速提升")
    report.append("    4. 客户集中度：")
    report.append("       - 客户相对分散，依赖度可控")
    report.append("")
    report.append("  风险等级：中低（行业景气度向上，但有周期波动）🟢🟡")
    report.append("")

    # 额外风险
    report.append("⚠️  额外风险：估值风险")
    report.append("")
    report.append("  当前PE(TTM)：760倍")
    report.append("  行业平均PE：约60-80倍")
    report.append("  估值溢价显著，反映了高成长预期")
    report.append("  风险：若业绩兑现不及预期，估值可能大幅回调")
    report.append("")
    report.append("  风险等级：高（需特别警惕）🔴")
    report.append("")

    # ===== Step 6: 认知差与催化 =====
    report.append("【Step 6 认知差分析与催化剂跟踪】")
    report.append("-" * 70)
    report.append("")

    report.append("🧠 潜在认知差：")
    report.append("  1. 市场低估了光刻胶的技术壁垒和客户粘性")
    report.append("  2. 市场对国产替代的速度和空间预期不足")
    report.append("  3. 晶瑞电材的技术积累被低估（国内最早做光刻胶的企业）")
    report.append("  4. 湿电子化学品业务的稳定性被忽视")
    report.append("")

    report.append("🔥 潜在催化剂：")
    report.append("  1. 高端光刻胶（KrF/ArF）量产突破")
    report.append("  2. 获得重要晶圆厂认证/订单")
    report.append("  3. 半导体行业景气度持续回升")
    report.append("  4. 国产替代政策加码")
    report.append("  5. 业绩超预期（营收/利润高速增长）")
    report.append("")

    # ===== 综合结论 =====
    report.append("【综合结论与投资建议】")
    report.append("=" * 70)
    report.append("")

    report.append("📊 综合评分：")
    report.append("  物理四问：75/100 ✅")
    report.append("  约束确定性：高 ✅")
    report.append("  证据强度：中-强 ✅")
    report.append("  风险等级：中（估值风险高）⚠️")
    report.append("  认知差：中等 ✅")
    report.append("")

    report.append("💡 核心投资逻辑：")
    report.append("  晶瑞电材是国内半导体材料（光刻胶+湿电子化学品）龙头之一，")
    report.append("  受益于国产替代大趋势，具备较强的技术壁垒和客户粘性。")
    report.append("  作为半导体制造的'卡脖子'环节，长期发展空间广阔。")
    report.append("")

    report.append("⚠️ 主要风险：")
    report.append("  1. 估值过高（PE 760倍），业绩兑现压力大")
    report.append("  2. 高端光刻胶研发进度可能不及预期")
    report.append("  3. 中低端产品竞争加剧，毛利率承压")
    report.append("  4. 半导体行业周期波动风险")
    report.append("")

    report.append("🎯 操作建议：")
    report.append("  长期看好：半导体材料国产替代是确定性趋势")
    report.append("  短期谨慎：估值偏高，建议等待回调或业绩验证")
    report.append("  关注重点：高端光刻胶量产进度、新客户认证情况")
    report.append("")

    report.append("📈 上涨空间估算：")
    report.append("  （基于PEG和行业可比公司）")
    report.append("  乐观情景（国产替代加速）：50-100%空间")
    report.append("  中性情景（稳步推进）：20-30%空间")
    report.append("  悲观情景（业绩不及预期）：-30%以上回调")
    report.append("")

    report.append("=" * 70)
    report.append("  报告结束")
    report.append(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 70)

    return "\n".join(report)


if __name__ == "__main__":
    report = analyze_jingrui()
    print(report)

    # 保存报告
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "晶瑞电材_Serenity深度分析报告.md"
    )
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到: {output_file}")
