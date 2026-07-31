"""
每日选股综合报告生成脚本
整合Serenity框架筛选结果 + 缠论技术分析
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chan_strategy import ChanStrategy
from serenity_enhanced_analyzer import SerenityEnhancedAnalyzer
from a_stock_data_core import get_stock_quote


def generate_comprehensive_report():
    """生成每日选股综合报告"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 读取选股数据
    data_file = Path("serenity_stock_data/daily_reviews/selection_data_2026-07-01.json")
    if not data_file.exists():
        print(f"❌ 选股数据文件不存在: {data_file}")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        selection_data = json.load(f)
    
    candidates = selection_data.get("candidates", [])
    matched_selections = selection_data.get("matched_selections", [])
    
    # 去重获取股票代码
    unique_stocks = {}
    for sel in matched_selections:
        code = sel["stock_code"]
        if code not in unique_stocks:
            unique_stocks[code] = sel
    
    print("=" * 70)
    print("  Serenity每日选股综合报告生成")
    print(f"  日期: {today}")
    print("=" * 70)
    print()
    
    # === 第一部分：基本面分析汇总 ===
    lines = []
    lines.append("=" * 70)
    lines.append("  Serenity每日选股综合报告")
    lines.append(f"  日期: {today}")
    lines.append("=" * 70)
    lines.append("")
    
    lines.append("【一、Serenity基本面筛选结果】")
    lines.append("-" * 50)
    lines.append("")
    lines.append(f"产业链数据库覆盖赛道: 5个")
    lines.append(f"候选瓶颈环节总数: {len(candidates)}个")
    lines.append(f"匹配选股标的数: {len(unique_stocks)}只（去重后）")
    lines.append("")
    
    # === 第二部分：候选瓶颈评分排名 ===
    lines.append("【二、候选瓶颈环节评分排名】")
    lines.append("-" * 50)
    lines.append("")
    
    for i, cand in enumerate(candidates, 1):
        lines.append(f"候选{i}: {cand['chokepoint_name']}")
        lines.append(f"  所属赛道: {cand['track_name']}")
        lines.append(f"  产业链位置: 第{cand['layer_num']}层 - {cand['chain_position']}")
        lines.append(f"  综合评分: {cand['comprehensive_score']:.1f}分")
        lines.append(f"    - 物理四问: {cand['physical_score']}分")
        lines.append(f"    - 供给刚性: {cand['supply_score']}分")
        lines.append(f"    - 市场忽视: {cand['neglect_score']}分")
        lines.append(f"    - 国产化率: {cand['localization_rate']}%")
        lines.append(f"  代表标的: {', '.join([s['name'] for s in cand['representative_stocks']])}")
        lines.append("")
    
    # === 第三部分：实时行情与技术分析 ===
    lines.append("【三、实时行情与缠论技术分析】")
    lines.append("-" * 50)
    lines.append("")
    
    # 对每只股票进行缠论分析
    analysis_results = []
    
    for code, stock_info in unique_stocks.items():
        name = stock_info["stock_name"]
        chokepoint = stock_info["chokepoint_name"]
        comprehensive_score = stock_info["comprehensive_score"]
        
        lines.append(f"正在分析 {name}({code})...")
        
        # 获取实时行情
        try:
            quote = get_stock_quote(code)
            if quote:
                current_price = quote.get('close', 0)
                change_pct = quote.get('change_pct', 0)
                volume = quote.get('volume', 0)
                turnover = quote.get('amount', 0)
                
                lines.append(f"  ✅ 实时行情获取成功")
                lines.append(f"     当前价: {current_price:.2f}元")
                lines.append(f"     今日涨跌: {change_pct:+.2f}%")
                lines.append(f"     成交量: {volume/10000:.0f}万手")
            else:
                lines.append(f"  ⚠️  实时行情获取失败，使用理论价格")
                current_price = 0
                change_pct = 0
        except Exception as e:
            lines.append(f"  ⚠️  实时行情异常: {str(e)[:50]}")
            current_price = 0
            change_pct = 0
        
        # 缠论分析
        try:
            strategy = ChanStrategy(code, name)
            if strategy.prepare_data(days=120):
                strategy.detect_divergence()
                signals = strategy.find_buy_signals()
                
                if signals:
                    latest_signal = signals[-1]
                    chan_score = latest_signal['score']
                    chan_reasons = ', '.join(latest_signal['reasons'])
                    lines.append(f"  ✅ 缠论分析完成")
                    lines.append(f"     缠论评分: {chan_score}/100")
                    lines.append(f"     信号类型: {latest_signal['signal_type']}")
                    lines.append(f"     技术特征: {chan_reasons}")
                    
                    analysis_results.append({
                        "code": code,
                        "name": name,
                        "chokepoint": chokepoint,
                        "comprehensive_score": comprehensive_score,
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "chan_score": chan_score,
                        "chan_reasons": chan_reasons,
                        "signal_date": str(latest_signal['date'])[:10],
                        "combined_score": (comprehensive_score * 0.6 + chan_score * 0.4),
                    })
                else:
                    lines.append(f"  ⚠️  未发现缠论买点信号")
                    analysis_results.append({
                        "code": code,
                        "name": name,
                        "chokepoint": chokepoint,
                        "comprehensive_score": comprehensive_score,
                        "current_price": current_price,
                        "change_pct": change_pct,
                        "chan_score": 0,
                        "chan_reasons": "无明确买点",
                        "combined_score": comprehensive_score * 0.7,
                    })
            else:
                lines.append(f"  ⚠️  缠论数据准备失败")
                analysis_results.append({
                    "code": code,
                    "name": name,
                    "chokepoint": chokepoint,
                    "comprehensive_score": comprehensive_score,
                    "current_price": current_price,
                    "change_pct": change_pct,
                    "chan_score": 0,
                    "chan_reasons": "数据不足",
                    "combined_score": comprehensive_score * 0.7,
                })
        except Exception as e:
            lines.append(f"  ⚠️  缠论分析异常: {str(e)[:50]}")
            analysis_results.append({
                "code": code,
                "name": name,
                "chokepoint": chokepoint,
                "comprehensive_score": comprehensive_score,
                "current_price": current_price,
                "change_pct": change_pct,
                "chan_score": 0,
                "chan_reasons": "分析异常",
                "combined_score": comprehensive_score * 0.7,
            })
        
        lines.append("")
    
    # === 第四部分：综合评分排名 ===
    lines.append("【四、综合评分排名（基本面60% + 技术面40%）】")
    lines.append("-" * 50)
    lines.append("")
    
    # 按综合评分排序
    analysis_results.sort(key=lambda x: -x["combined_score"])
    
    for i, result in enumerate(analysis_results, 1):
        lines.append(f"排名{i}: {result['name']}({result['code']})")
        lines.append(f"  瓶颈环节: {result['chokepoint']}")
        lines.append(f"  当前价格: {result['current_price']:.2f}元 ({result['change_pct']:+.2f}%)")
        lines.append(f"  综合评分: {result['combined_score']:.1f}分")
        lines.append(f"    - 基本面评分: {result['comprehensive_score']:.1f}分")
        lines.append(f"    - 缠论评分: {result['chan_score']}/100")
        lines.append(f"    - 技术特征: {result['chan_reasons']}")
        lines.append("")
    
    # === 第五部分：策略匹配推荐 ===
    lines.append("【五、策略匹配推荐】")
    lines.append("-" * 50)
    lines.append("")
    
    # 按策略分组
    strategy_groups = {}
    for sel in matched_selections:
        sid = sel["strategy_id"]
        if sid not in strategy_groups:
            strategy_groups[sid] = {"name": sel["strategy_name"], "stocks": []}
        
        # 查找该股票的综合分析结果
        for r in analysis_results:
            if r["code"] == sel["stock_code"]:
                strategy_groups[sid]["stocks"].append(r)
                break
    
    for sid, sdata in strategy_groups.items():
        lines.append(f"策略 [{sid}] {sdata['name']}")
        
        # 排序该策略下的股票
        sdata["stocks"].sort(key=lambda x: -x["combined_score"])
        
        for j, stock in enumerate(sdata["stocks"][:3], 1):  # 每策略推荐3只
            lines.append(f"  推荐{j}: {stock['name']}({stock['code']})")
            lines.append(f"     综合评分: {stock['combined_score']:.1f}分")
            lines.append(f"     当前价: {stock['current_price']:.2f}元")
            lines.append(f"     技术状态: {stock['chan_reasons']}")
        
        lines.append("")
    
    # === 第六部分：决策建议 ===
    lines.append("【六、今日决策建议】")
    lines.append("-" * 50)
    lines.append("")
    
    if analysis_results:
        top3 = analysis_results[:3]
        lines.append("🌟 今日重点关注标的（TOP3）：")
        for i, stock in enumerate(top3, 1):
            lines.append(f"  {i}. {stock['name']}({stock['code']}) - 综合评分{stock['combined_score']:.1f}分")
            lines.append(f"     瓶颈环节: {stock['chokepoint']}")
            lines.append(f"     当前价格: {stock['current_price']:.2f}元")
            if stock['chan_score'] >= 70:
                lines.append(f"     ⭐ 缠论信号较强，技术面支持买入")
            elif stock['chan_score'] >= 50:
                lines.append(f"     ✅ 缠论信号中等，可分批建仓")
            else:
                lines.append(f"     ⚠️  暂无明确技术信号，建议观望")
        lines.append("")
    
    lines.append("💡 操作建议：")
    lines.append("  1. 优先关注综合评分≥80分的标的")
    lines.append("  2. 缠论评分≥70分可考虑建仓")
    lines.append("  3. 分批买入，单只仓位不超过10%")
    lines.append("  4. 设置止损线-10%，止盈线20%-25%")
    lines.append("  5. 关注产业链重大事件变化")
    lines.append("")
    
    lines.append("⚠️  风险提示：")
    lines.append("  1. 本报告为理论筛选结果，需结合实际市场环境")
    lines.append("  2. 缠论分析依赖历史数据，可能滞后于市场变化")
    lines.append("  3. 瓶颈投资策略需要耐心持有，不适合短线交易")
    lines.append("  4. 建议进一步核实公告、新闻等公开信息")
    lines.append("")
    
    lines.append("=" * 70)
    lines.append("  报告结束")
    lines.append("=" * 70)
    
    # 保存报告
    report_file = Path("serenity_stock_data/daily_reviews/daily_comprehensive_review_2026-07-01.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    
    print()
    print(f"✅ 综合报告已保存: {report_file}")
    print()
    
    # 同时保存JSON数据
    json_file = Path("serenity_stock_data/daily_reviews/comprehensive_analysis_2026-07-01.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "date": today,
            "candidates": candidates,
            "analysis_results": analysis_results,
            "strategy_groups": {k: {"name": v["name"], "top3": v["stocks"][:3]} for k, v in strategy_groups.items()},
        }, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析数据已保存: {json_file}")
    print()
    
    # 输出报告
    print("\n".join(lines))
    
    return analysis_results


if __name__ == "__main__":
    generate_comprehensive_report()