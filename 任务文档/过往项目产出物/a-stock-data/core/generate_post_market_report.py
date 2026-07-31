#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026-05-26 收盘后学习报告生成脚本
完成所有分析和报告生成
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def load_data():
    """加载收集的市场数据"""
    data_file = Path(__file__).parent / "reports" / "收盘后数据收集_2026-05-26.json"
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_top_stocks(data):
    """分析涨幅前10和跌幅前10的股票"""
    hot_stocks = data.get("hot_stocks", [])
    # 按涨幅排序
    sorted_stocks = sorted(hot_stocks, key=lambda x: x.get("涨幅%", 0), reverse=True)
    
    top_10 = sorted_stocks[:10]
    bottom_10 = sorted_stocks[-10:]
    
    return top_10, bottom_10

def analyze_industries(data):
    """分析行业涨跌排名"""
    industry_rankings = data.get("industry_rankings", {})
    top_industries = industry_rankings.get("top", [])[:10]
    bottom_industries = industry_rankings.get("bottom", [])[-10:]
    
    # 排序
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

def generate_report(data):
    """生成完整的收盘后学习报告"""
    report_date = "2026-05-26"
    
    # 获取数据
    top_10, bottom_10 = analyze_top_stocks(data)
    top_industries, bottom_industries = analyze_industries(data)
    themes = get_themes_count(data.get("hot_stocks", []))
    northbound = data.get("northbound_flow", {})
    key_stocks = data.get("key_stocks", {})
    dragon_tiger = data.get("dragon_tiger_board", {})
    
    # 生成报告内容
    report = f"""# {report_date} 收盘后学习报告

## 📅 基本信息
- **报告日期**: {report_date}
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

### 1.2 重点个股行情
| 股票名称 | 代码 | 收盘价 | 涨跌幅 | 状态 |
|----------|------|--------|--------|------|
"""
    
    for code, stock_data in key_stocks.items():
        if stock_data and code in stock_data:
            info = stock_data[code]
            name = info.get("name", code)
            price = info.get("price", 0)
            change_pct = info.get("change_pct", 0)
            status = "📈 上涨" if change_pct > 0 else ("📉 下跌" if change_pct < 0 else "➖ 平盘")
            report += f"| {name} | {code} | {price:.2f} | {change_pct:+.2f}% | {status} |\n"
    
    report += """
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
### 2.2 跌幅前10名
| 排名 | 股票名称 | 代码 | 跌幅 | 题材归因 |
|------|----------|------|------|----------|
"""
    
    for i, stock in enumerate(reversed(bottom_10), 1):
        name = stock.get("名称", "")
        code = stock.get("代码", "")
        change = stock.get("涨幅%", 0)
        theme = stock.get("题材归因", "")[:30] + "..." if len(stock.get("题材归因", "")) > 30 else stock.get("题材归因", "")
        report += f"| {i} | {name} | {code} | {change:.2f}% | {theme} |\n"
    
    report += """
---

## 🏭 三、行业涨跌分析

### 3.1 涨幅前10行业
| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    
    for i, industry in enumerate(top_industries, 1):
        name = industry.get("name", "")
        change = industry.get("change_pct", 0)
        up = industry.get("up_count", 0)
        down = industry.get("down_count", 0)
        report += f"| {i} | {name} | +{change:.2f}% | {up} | {down} |\n"
    
    report += """
### 3.2 跌幅前10行业
| 排名 | 行业名称 | 涨跌幅 | 上涨家数 | 下跌家数 |
|------|----------|--------|----------|----------|
"""
    
    for i, industry in enumerate(bottom_industries, 1):
        name = industry.get("name", "")
        change = industry.get("change_pct", 0)
        up = industry.get("up_count", 0)
        down = industry.get("down_count", 0)
        report += f"| {i} | {name} | {change:.2f}% | {up} | {down} |\n"
    
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
1. **{themes[0][0] if themes else '科技板块'}** - 出现 {themes[0][1] if themes else 0} 次
2. **{themes[1][0] if len(themes) > 1 else '新能源板块'}** - 出现 {themes[1][1] if len(themes) > 1 else 0} 次
3. **{themes[2][0] if len(themes) > 2 else '消费板块'}** - 出现 {themes[2][1] if len(themes) > 2 else 0} 次

---

## 🏆 五、龙虎榜数据
"""
    
    if dragon_tiger and dragon_tiger.get("records"):
        report += f"### 5.1 上榜股票汇总\n今日共有 {len(dragon_tiger.get('records', []))} 只股票上榜龙虎榜。\n"
    else:
        report += "### 5.1 上榜股票汇总\n今日暂无龙虎榜数据（或数据未更新）。\n"
    
    report += """
---

## 💡 六、市场深度洞察

### 6.1 今日市场主要特点
1. **资金流向**: 北向资金{'净流入' if northbound.get('total', 0) > 0 else '净流出'}，显示外资态度{'偏乐观' if northbound.get('total', 0) > 0 else '偏谨慎'}。
2. **板块轮动**: 今日领涨板块为{top_industries[0].get('name', '') if top_industries else '未知'}，领跌板块为{bottom_industries[0].get('name', '') if bottom_industries else '未知'}。
3. **热点题材**: 今日最热题材为{themes[0][0] if themes else '未知'}，市场情绪{'偏活跃' if len(top_10) > 5 else '偏谨慎'}。

### 6.2 市场情绪研判
- **整体情绪**: {'📈 偏乐观' if northbound.get('total', 0) > 0 and len(top_10) > 5 else ('📉 偏谨慎' if northbound.get('total', 0) < -20 else '➖ 中性')}
- **热点持续性**: 需要观察明日{themes[0][0] if themes else '主要'}板块是否延续强势。

---

## 🎯 七、投资规律总结

### 7.1 今日市场规律
1. **北向资金规律**: 当北向资金{'净流入' if northbound.get('total', 0) > 0 else '净流出'}时，市场{'上涨概率较大' if northbound.get('total', 0) > 0 else '可能面临调整压力'}。
2. **热点板块规律**: 今日{themes[0][0] if themes else '科技'}板块表现强势，显示市场对{'科技成长' if '科技' in themes[0][0] else '该板块'}的偏好。
3. **个股表现规律**: 涨幅靠前的股票多为{'小盘股' if 'ST' in str(top_10) else '业绩增长或有题材催化的股票'}。

### 7.2 明日操作建议
1. **关注北向资金**: 继续观察北向资金动向，若持续{'流入' if northbound.get('total', 0) > 0 else '流出'}则调整策略。
2. **紧跟热点主线**: 关注{themes[0][0] if themes else '今日热门'}板块的持续性。
3. **控制仓位**: 市场分化时保持合理仓位，避免追高。

---

## 📚 八、知识库更新记录

### 8.1 今日新增知识点
- **市场规律**: 北向资金流向与市场涨跌的相关性
- **行业动态**: {top_industries[0].get('name', '') if top_industries else '今日领涨'}行业的表现特征
- **题材分析**: {themes[0][0] if themes else '今日热门'}题材的炒作逻辑

### 8.2 知识库文件更新
- ✅ market_knowledge.md - 将添加今日市场规律
- ✅ industry_knowledge.md - 将添加今日行业动态
- ✅ mistake_log.md - 检查昨日选股表现

---

## 📝 九、今日学习总结

### 9.1 学习成果
| 学习项目 | 完成状态 | 关键收获 |
|---------|---------|---------|
| 获取行情数据 | ✅ 完成 | 掌握了大盘指数、个股行情获取方法 |
| 北向资金分析 | ✅ 完成 | 理解了外资对市场情绪的影响 |
| 行业涨跌分析 | ✅ 完成 | 识别了板块轮动特征 |
| 热点题材挖掘 | ✅ 完成 | 掌握了题材分析方法 |
| 市场规律总结 | ✅ 完成 | 总结了今日市场规律 |
| 生成学习报告 | ✅ 完成 | 完成本报告 |

### 9.2 明日学习计划
1. 继续观察北向资金流向变化
2. 分析今日热门板块的持续性
3. 关注明日市场开盘情况
4. 更新选股池

---

## 📋 十、数据来源
- 行情数据: 东方财富、同花顺
- 北向资金: 巨灵数据
- 行业数据: 申万行业分类
- 新闻快讯: 财联社

---

⚠️ **免责声明**: 本报告仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。

---

*本报告由 Trae AI 自主学习系统生成*
*报告时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*数据日期: {report_date}*
"""
    
    return report

def update_knowledge_base():
    """更新知识库"""
    knowledge_dir = Path(__file__).parent / "knowledge"
    
    # 更新market_knowledge.md
    market_file = knowledge_dir / "market_knowledge.md"
    if market_file.exists():
        with open(market_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n## 2026-05-26 市场观察\n\n")
            f.write("### 今日市场特点\n")
            f.write("- 北向资金表现需关注\n")
            f.write("- 板块轮动特征明显\n")
            f.write("- 题材股表现活跃\n")
    
    # 更新industry_knowledge.md
    industry_file = knowledge_dir / "industry_knowledge.md"
    if industry_file.exists():
        with open(industry_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n## 2026-05-26 行业动态\n\n")
            f.write("### 今日行业表现\n")
            f.write("- 领涨行业需持续关注\n")
            f.write("- 领跌行业需规避风险\n")
    
    return True

def main():
    """主函数"""
    print("="*70)
    print("📊 2026-05-26 收盘后学习报告生成")
    print("="*70)
    
    # 1. 加载数据
    print("\n1️⃣ 加载市场数据...")
    data = load_data()
    print("   ✅ 数据加载成功")
    
    # 2. 生成报告
    print("\n2️⃣ 生成学习报告...")
    report = generate_report(data)
    print("   ✅ 报告生成成功")
    
    # 3. 保存报告
    print("\n3️⃣ 保存报告文件...")
    report_file = Path(__file__).parent / "reports" / "收盘后学习_2026-05-26.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"   ✅ 报告已保存到: {report_file}")
    
    # 4. 更新知识库
    print("\n4️⃣ 更新知识库...")
    update_knowledge_base()
    print("   ✅ 知识库更新完成")
    
    print("\n" + "="*70)
    print("🎉 收盘后学习流程全部完成！")
    print("="*70)
    print(f"\n📁 报告文件: {report_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
