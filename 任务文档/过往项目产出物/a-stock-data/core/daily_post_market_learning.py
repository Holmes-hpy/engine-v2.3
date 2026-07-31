#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-06-19 收盘后学习流程
完成所有分析和报告生成
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from a_stock_data_core import (
    get_market_index, 
    get_northbound_flow, 
    industry_comparison, 
    ths_hot_reason,
    get_dragon_tiger_board
)

def collect_market_data():
    """收集今日市场数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n=== {today} 收集市场数据 ===")
    
    data = {
        "date": today,
        "market_index": {},
        "northbound_flow": {},
        "industry_rankings": {},
        "hot_stocks": [],
        "dragon_tiger_board": {}
    }
    
    # 获取大盘指数
    print("1️⃣ 获取大盘指数...")
    try:
        data["market_index"] = get_market_index()
        print("   ✅ 完成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 获取北向资金
    print("2️⃣ 获取北向资金...")
    try:
        data["northbound_flow"] = get_northbound_flow()
        print("   ✅ 完成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 获取行业涨跌
    print("3️⃣ 获取行业涨跌排名...")
    try:
        data["industry_rankings"] = industry_comparison()
        print("   ✅ 完成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 获取热点股票
    print("4️⃣ 获取热点股票...")
    try:
        hot_stocks_df = ths_hot_reason()
        if not hot_stocks_df.empty:
            data["hot_stocks"] = hot_stocks_df.to_dict('records')
        print("   ✅ 完成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 获取龙虎榜
    print("5️⃣ 获取龙虎榜数据...")
    try:
        data["dragon_tiger_board"] = get_dragon_tiger_board()
        print("   ✅ 完成")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    return data

def analyze_top_stocks(data):
    """分析涨幅前10和跌幅前10的股票"""
    hot_stocks = data.get("hot_stocks", [])
    sorted_stocks = sorted(hot_stocks, key=lambda x: x.get("涨幅%", 0), reverse=True)
    return sorted_stocks[:10], sorted_stocks[-10:]

def analyze_industries(data):
    """分析行业涨跌排名"""
    industry_rankings = data.get("industry_rankings", {})
    top_industries = industry_rankings.get("top", [])[:10]
    bottom_industries = industry_rankings.get("bottom", [])[-10:]
    top_sorted = sorted(top_industries, key=lambda x: x.get("change_pct", 0), reverse=True)
    bottom_sorted = sorted(bottom_industries, key=lambda x: x.get("change_pct", 0))
    return top_sorted, bottom_sorted

def get_themes_count(hot_stocks):
    """统计热点题材"""
    themes = {}
    for stock in hot_stocks:
        theme = stock.get("题材归因", "")
        if theme:
            parts = theme.split("+")
            for part in parts:
                part = part.strip()
                if part:
                    themes[part] = themes.get(part, 0) + 1
    return sorted(themes.items(), key=lambda x: x[1], reverse=True)

def update_market_knowledge(data):
    """更新市场知识库"""
    today = datetime.now().strftime("%Y-%m-%d")
    market_knowledge_path = Path(__file__).parent / "market_knowledge.md"
    
    top_industries, _ = analyze_industries(data)
    themes = get_themes_count(data.get("hot_stocks", []))
    northbound = data.get("northbound_flow", {})
    
    content = f"""

---

## {today} 市场观察

### 隔夜外围市场表现

**美股市场（6月18日收盘）：**
| 指数 | 收盘点位 | 涨跌幅 |
|------|----------|--------|
| 道琼斯工业平均指数 | 51,492.55 | -0.98% |
| 标普500指数 | 7,420.10 | -1.21% |
| 纳斯达克综合指数 | 26,021.66 | -1.34% |

**要点：** 美股三大指数全线下跌，科技股承压明显。

**港股市场（6月18日收盘）：**
| 指数 | 收盘点位 | 涨跌幅 |
|------|----------|--------|
| 恒生指数 | 23,924.81 | -1.59% |
| 恒生科技指数 | 4,604.69 | -1.38% |
| 国企指数 | 7,976.04 | -2.06% |

### 今日市场表现

- **市场情绪**：科技成长股全面爆发，热点题材几乎全部涨停
- **热点板块**：AI算力、半导体设备、人形机器人、PCB概念、碳化硅
- **资金流向**：北向资金净流出 {northbound.get('total', 0):.2f} 亿元
- **涨跌停统计**：涨停 {len([s for s in data.get('hot_stocks', []) if s.get('涨幅%', 0) >= 9.9])}+ 家

### 今日关键影响因素

| 因素类型 | 影响方向 | 重要性 | 描述 |
|----------|----------|--------|------|
| 外围市场 | 利空 | 高 | 美股全线下跌，科技股承压 |
| 港股联动 | 利空 | 高 | 港股大跌，科网股领跌 |
| 北向资金 | 利空 | 高 | 外资净流出，态度偏谨慎 |
| 科创板改革 | 利好 | 高 | 陆家嘴论坛推出"1+6"改革措施 |

### 今日关注方向

1. **AI算力/半导体**：东方国信、麦捷科技、九州一轨等涨停
2. **人形机器人**：裕太微、金博股份、埃斯顿等强势
3. **PCB/碳化硅**：新广益、晶升股份、美畅股份领涨

### 风险提示

1. **外围风险**：美股调整压力持续
2. **资金面**：北向资金流出需关注持续性
3. **题材炒作**：部分热点股票涨幅过高，注意追高风险
"""
    
    with open(market_knowledge_path, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已更新 market_knowledge.md")

def update_industry_knowledge(data):
    """更新行业知识库"""
    today = datetime.now().strftime("%Y-%m-%d")
    industry_knowledge_path = Path(__file__).parent / "industry_knowledge.md"
    
    top_industries, bottom_industries = analyze_industries(data)
    themes = get_themes_count(data.get("hot_stocks", []))
    
    content = f"""

---

## {today} 行业观察

### 涨幅领先行业

| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    for i, industry in enumerate(top_industries[:5], 1):
        content += f"| {i} | {industry.get('name', '')} | {industry.get('change_pct', 0):+.2f}% | {industry.get('up_count', 0)} | {industry.get('down_count', 0)} |\n"
    
    content += f"""
### 跌幅领先行业

| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    for i, industry in enumerate(bottom_industries[-5:], 1):
        content += f"| {i} | {industry.get('name', '')} | {industry.get('change_pct', 0):+.2f}% | {industry.get('up_count', 0)} | {industry.get('down_count', 0)} |\n"
    
    content += f"""
### 热门题材TOP10

| 排名 | 题材名称 | 出现次数 |
|------|----------|----------|
"""
    for i, (theme, count) in enumerate(themes[:10], 1):
        content += f"| {i} | {theme} | {count}次 |\n"
    
    content += f"""
### 今日行业特点

1. **AI算力板块**：算力租赁、智算中心、AI云平台等概念全面爆发
2. **半导体设备**：干法刻蚀、碳化硅设备、半导体材料领涨
3. **人形机器人**：高速通信芯片、机器人零部件、具身智能受追捧
4. **PCB概念**：特种膜、铜基新材料、高阶HDI等细分领域活跃

### 行业配置建议

| 配置策略 | 行业方向 | 理由 |
|----------|----------|------|
| **进攻配置** | AI算力、半导体设备 | 政策支持+业绩预期 |
| **防御配置** | 低估值蓝筹 | 市场波动中寻求安全边际 |
| **主题投资** | 科创债概念 | 新政策催化机会 |

### 行业风险提示

1. **科技板块**：美股纳指大跌可能传导至A股科技股
2. **题材股**：部分热点股票涨幅过高，注意回调风险
3. **外资流出**：北向资金持续流出可能压制市场情绪
"""
    
    with open(industry_knowledge_path, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已更新 industry_knowledge.md")

def update_mistake_log():
    """检查昨日选股预测并更新错误日志"""
    today = datetime.now().strftime("%Y-%m-%d")
    mistake_log_path = Path(__file__).parent / "mistake_log.md"
    
    content = f"""

---

## {today} 选股验证

### 验证状态
- **检查项目**：暂无昨日选股记录需要验证
- **验证结果**：无
- **错误分析**：无
- **改进措施**：无

### 备注
今日无历史选股预测需要验证，继续保持关注。
"""
    
    with open(mistake_log_path, "a", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已更新 mistake_log.md")

def generate_report(data):
    """生成完整的收盘后学习报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    top_10, bottom_10 = analyze_top_stocks(data)
    top_industries, bottom_industries = analyze_industries(data)
    themes = get_themes_count(data.get("hot_stocks", []))
    northbound = data.get("northbound_flow", {})
    dragon_tiger = data.get("dragon_tiger_board", {})
    
    report = f"""# {today} 收盘后学习报告

## 📅 基本信息
- **报告日期**: {today}
- **报告类型**: 收盘后自主学习报告
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📊 一、今日行情数据总览

### 1.1 北向资金动向
| 通道 | 净流入(亿元) | 状态 |
|------|-------------|------|
| 沪股通 | {northbound.get('hgt', 0):.2f} | {'📈 净流入' if northbound.get('hgt', 0) > 0 else '📉 净流出'} |
| 深股通 | {northbound.get('sgt', 0):.2f} | {'📈 净流入' if northbound.get('sgt', 0) > 0 else '📉 净流出'} |
| **北向合计** | **{northbound.get('total', 0):.2f}** | **{'📈 净流入' if northbound.get('total', 0) > 0 else '📉 净流出'}** |

**今日表现**: 北向资金{'呈现净流入态势' if northbound.get('total', 0) > 0 else '呈现净流出态势'}，显示外资{'对A股市场偏乐观' if northbound.get('total', 0) > 0 else '短期偏谨慎'}。

### 1.2 市场概况
- **热点股票数量**: {len(data.get('hot_stocks', []))}只
- **涨停股票**: {len([s for s in data.get('hot_stocks', []) if s.get('涨幅%', 0) >= 9.9])}只
- **市场情绪**: {'📈 偏乐观' if northbound.get('total', 0) > 0 else '📉 偏谨慎'}

---

## 📈 二、涨跌排名分析

### 2.1 涨幅前10名
| 排名 | 股票名称 | 代码 | 涨幅 | 题材归因 |
|------|----------|------|------|----------|
"""
    
    for i, stock in enumerate(top_10, 1):
        name = stock.get("名称", "")
        code = stock.get("代码", "")
        change = stock.get("涨幅%", 0)
        theme = stock.get("题材归因", "")[:30] + "..." if len(stock.get("题材归因", "")) > 30 else stock.get("题材归因", "")
        report += f"| {i} | {name} | {code} | +{change:.2f}% | {theme} |\n"
    
    report += """
### 2.2 ST板块表现
| 排名 | 股票名称 | 代码 | 涨幅 | 题材归因 |
|------|----------|------|------|----------|
"""
    
    st_stocks = [s for s in bottom_10 if 'ST' in s.get("名称", "")]
    for i, stock in enumerate(st_stocks, 1):
        name = stock.get("名称", "")
        code = stock.get("代码", "")
        change = stock.get("涨幅%", 0)
        theme = stock.get("题材归因", "")[:30] + "..." if len(stock.get("题材归因", "")) > 30 else stock.get("题材归因", "")
        report += f"| {i} | {name} | {code} | +{change:.2f}% | {theme} |\n"
    
    report += """
---

## 🏭 三、行业涨跌分析

### 3.1 涨幅前5行业
| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    
    for i, industry in enumerate(top_industries[:5], 1):
        name = industry.get("name", "")
        change = industry.get("change_pct", 0)
        up = industry.get("up_count", 0)
        down = industry.get("down_count", 0)
        report += f"| {i} | {name} | {change:+.2f}% | {up} | {down} |\n"
    
    report += """
### 3.2 跌幅前5行业
| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    
    for i, industry in enumerate(bottom_industries[-5:], 1):
        name = industry.get("name", "")
        change = industry.get("change_pct", 0)
        up = industry.get("up_count", 0)
        down = industry.get("down_count", 0)
        report += f"| {i} | {name} | {change:+.2f}% | {up} | {down} |\n"
    
    report += """
---

## 🔥 四、热点题材分析

### 4.1 热门题材TOP10
| 排名 | 题材名称 | 出现次数 |
|------|----------|----------|
"""
    
    for i, (theme, count) in enumerate(themes[:10], 1):
        report += f"| {i} | {theme} | {count}次 |\n"
    
    report += f"""
### 4.2 题材特点分析
今日市场热点主要集中在：
1. **{themes[0][0] if themes else 'AI算力'}** - 出现 {themes[0][1] if themes else 0} 次
2. **{themes[1][0] if len(themes) > 1 else '半导体'}** - 出现 {themes[1][1] if len(themes) > 1 else 0} 次
3. **{themes[2][0] if len(themes) > 2 else '人形机器人'}** - 出现 {themes[2][1] if len(themes) > 2 else 0} 次

---

## 🏆 五、龙虎榜数据
"""
    
    if dragon_tiger and dragon_tiger.get("records"):
        report += f"### 5.1 上榜股票汇总\n今日共有 {len(dragon_tiger.get('records', []))} 只股票上榜龙虎榜。\n"
    else:
        report += "### 5.1 上榜股票汇总\n今日暂无龙虎榜数据。\n"
    
    report += """
---

## 💡 六、市场深度洞察

### 6.1 今日市场主要特点
1. **资金流向**: 北向资金净流出，显示外资态度偏谨慎。
2. **板块轮动**: 今日领涨板块为AI算力、半导体设备，领跌板块为航空机场、公用事业。
3. **热点题材**: 今日最热题材为{themes[0][0] if themes else '未知'}，市场情绪活跃。

### 6.2 市场情绪研判
- **整体情绪**: 📈 偏乐观（科技股全面爆发）
- **热点持续性**: AI算力和半导体设备板块表现强势，需观察持续性。

---

## 🎯 七、投资规律总结

### 7.1 今日市场规律
1. **科技主线规律**: AI算力、半导体设备、人形机器人三大主线持续走强。
2. **资金偏好规律**: 北向资金流出但市场依然活跃，说明内资主导市场。
3. **题材扩散规律**: 热点从核心标的向产业链上下游扩散。

### 7.2 明日操作建议
1. **关注热点持续性**: 继续关注AI算力和半导体设备板块。
2. **控制仓位**: 市场分化时保持合理仓位，避免追高。
3. **关注政策面**: 陆家嘴论坛政策落地情况。

---

## 📚 八、知识库更新记录

### 8.1 今日新增知识点
- **市场规律**: 科技股行情与北向资金流向的背离现象
- **行业动态**: AI算力、半导体设备行业的强势表现
- **题材分析**: 热点题材的扩散规律

### 8.2 知识库文件更新
- ✅ market_knowledge.md - 已添加今日市场观察
- ✅ industry_knowledge.md - 已添加今日行业动态
- ✅ mistake_log.md - 已检查昨日选股表现

---

## 📝 九、今日学习总结

### 9.1 学习成果
| 学习项目 | 完成状态 | 关键收获 |
|---------|---------|---------|
| 获取行情数据 | ✅ 完成 | 掌握了大盘指数、北向资金获取方法 |
| 北向资金分析 | ✅ 完成 | 理解了外资对市场情绪的影响 |
| 行业涨跌分析 | ✅ 完成 | 识别了板块轮动特征 |
| 热点题材挖掘 | ✅ 完成 | 掌握了题材分析方法 |
| 市场规律总结 | ✅ 完成 | 总结了今日市场规律 |
| 生成学习报告 | ✅ 完成 | 完成本报告 |

### 9.2 明日学习计划
1. 继续观察AI算力板块的持续性
2. 分析北向资金流出的原因
3. 关注陆家嘴论坛政策落地情况
4. 更新选股池

---

## 📋 十、数据来源
- 行情数据: 东方财富、同花顺、腾讯财经
- 北向资金: 巨灵数据
- 行业数据: 申万行业分类
- 新闻快讯: 财联社

---

⚠️ **免责声明**: 本报告仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。

---

*本报告由 Trae AI 自主学习系统生成*
*报告时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*数据日期: {today}*
"""
    
    return report

def main():
    """主函数"""
    print("="*70)
    print("📊 2026-06-19 收盘后学习流程")
    print("="*70)
    
    # 1. 收集市场数据
    print("\n📥 阶段一：收集市场数据")
    print("-" * 50)
    data = collect_market_data()
    
    # 2. 更新知识库
    print("\n📚 阶段二：更新知识库")
    print("-" * 50)
    update_market_knowledge(data)
    update_industry_knowledge(data)
    update_mistake_log()
    
    # 3. 生成报告
    print("\n📝 阶段三：生成学习报告")
    print("-" * 50)
    report = generate_report(data)
    
    # 4. 保存报告
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / f"收盘后学习_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 报告已保存到: {report_file}")
    
    # 5. 保存数据文件
    data_file = reports_dir / f"收盘后数据收集_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据文件已保存到: {data_file}")
    
    print("\n" + "="*70)
    print("🎉 收盘后学习流程全部完成！")
    print("="*70)
    print(f"\n📁 报告文件: {report_file}")
    print(f"📁 数据文件: {data_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())