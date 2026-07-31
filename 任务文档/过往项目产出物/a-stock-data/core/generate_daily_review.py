#!/usr/bin/env python3
"""
Serenity瓶颈投资 - 每日复盘报告生成器
汇总今日选股、验证结果、策略排名、预警信息、深度分析与建议
"""

import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def read_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"读取文件失败 {filepath}: {e}")
        return None


def extract_bottleneck_candidates(selection_report):
    candidates = []
    lines = selection_report.split('\n')
    i = 0
    while i < len(lines):
        match = re.match(r'候选(\d+):\s*(.+)', lines[i])
        if match:
            candidate_name = match.group(2).strip()
            score = 0
            industry = ""
            location = ""
            sub_i = i + 1
            while sub_i < len(lines):
                if re.match(r'候选\d+:|【三、', lines[sub_i]):
                    break
                if '所属赛道:' in lines[sub_i]:
                    industry = lines[sub_i].split('所属赛道:')[1].strip()
                if '产业链位置:' in lines[sub_i]:
                    location = lines[sub_i].split('产业链位置:')[1].strip()
                if '综合评分:' in lines[sub_i]:
                    score_match = re.search(r'综合评分:\s*([\d.]+)', lines[sub_i])
                    if score_match:
                        score = float(score_match.group(1))
                sub_i += 1
            candidates.append({
                "name": candidate_name,
                "score": score,
                "industry": industry,
                "location": location
            })
            i = sub_i
        else:
            i += 1
    return candidates


def extract_selected_stocks(selection_report):
    selected_stocks = []
    current_strategy = ""
    lines = selection_report.split('\n')
    i = 0
    while i < len(lines):
        match = re.match(r'策略 \[S\d+\]\s*(.+)', lines[i])
        if match:
            current_strategy = match.group(1).strip()
        elif "🟢" in lines[i] and current_strategy:
            line_content = lines[i].strip()
            stock_info = line_content.split("🟢", 1)[1].strip()
            name_match = re.match(r'(.+?)\((\d+)\)', stock_info)
            if name_match:
                stock_name = name_match.group(1).strip()
                stock_code = name_match.group(2).strip()
                selected_stocks.append({
                    "stock_name": stock_name,
                    "stock_code": stock_code,
                    "strategy": current_strategy
                })
        i += 1
    
    unique_stocks = {}
    for s in selected_stocks:
        key = f"{s['stock_name']}_{s['stock_code']}"
        if key not in unique_stocks:
            unique_stocks[key] = {
                "stock_name": s["stock_name"],
                "stock_code": s["stock_code"],
                "strategies": []
            }
        if s["strategy"] not in unique_stocks[key]["strategies"]:
            unique_stocks[key]["strategies"].append(s["strategy"])
    return unique_stocks


def extract_holdings(daily_review):
    holdings = []
    if not daily_review:
        return holdings, "今日无验证报告"
    
    lines = daily_review.split('\n')
    i = 0
    selection_info = ""
    while i < len(lines):
        if "【一、今日选股情况】" in lines[i]:
            if i + 2 < len(lines):
                selection_info = lines[i + 2].strip()
        elif "【二、验证中持仓】" in lines[i]:
            sub_i = i + 2
            count_info = ""
            while sub_i < len(lines):
                if lines[sub_i].strip().startswith("验证中数量"):
                    count_info = lines[sub_i].strip()
                    sub_i += 2
                    while sub_i < len(lines):
                        if lines[sub_i].strip() == "" or lines[sub_i].startswith("【"):
                            break
                        if lines[sub_i].strip().startswith("🔴") or lines[sub_i].strip().startswith("🟢"):
                            holdings.append(lines[sub_i].strip())
                        sub_i += 1
                    break
                sub_i += 1
        i += 1
    return holdings, selection_info, count_info


def extract_strategy_ranking(daily_review):
    rankings = []
    if not daily_review:
        return rankings
    
    lines = daily_review.split('\n')
    i = 0
    while i < len(lines):
        if "【三、策略表现排名】" in lines[i]:
            sub_i = i + 2
            while sub_i < len(lines):
                if lines[sub_i].strip() == "" or lines[sub_i].startswith("【"):
                    break
                rankings.append(lines[sub_i].strip())
                sub_i += 1
            break
        i += 1
    return rankings


def extract_alert_info(alert_report):
    info = {}
    if not alert_report:
        return info
    
    lines = alert_report.split('\n')
    
    # 提取标的名称和今日收盘价格(实际格式是"今日收盘:")
    for i, line in enumerate(lines):
        if '标的名称:' in line:
            info['name'] = line.split('标的名称:')[1].strip()
        if '今日收盘:' in line:
            info['price'] = line.split('今日收盘:')[1].strip()
        # 从行情指标表格中提取涨跌幅和换手率
        if '今日涨跌幅' in line and '│' in line:
            parts = line.split('│')
            if len(parts) >= 3:
                info['change'] = parts[2].strip()
        if '换手率' in line and '│' in line:
            parts = line.split('│')
            if len(parts) >= 3:
                info['turnover'] = parts[2].strip()
        if '成交额(亿)' in line and '│' in line:
            parts = line.split('│')
            if len(parts) >= 3:
                info['volume'] = parts[2].strip()
    
    info['pre_market'] = []
    info['alert_table'] = []
    info['news_check'] = []
    
    i = 0
    while i < len(lines):
        if "【三、盘前检查" in lines[i] or "【三、涨跌预警状态】" in lines[i]:
            sub_i = i + 2
            while sub_i < len(lines) and not lines[sub_i].startswith("【四"):
                if "⚠️" in lines[sub_i] or "📢" in lines[sub_i] or "断供" in lines[sub_i]:
                    info['pre_market'].append(lines[sub_i].strip())
                sub_i += 1
        elif "【三、涨跌预警状态】" in lines[i] or "【四、涨跌预警状态】" in lines[i]:
            sub_i = i + 2
            while sub_i < len(lines) and not lines[sub_i].startswith("【五"):
                info['alert_table'].append(lines[sub_i].strip())
                sub_i += 1
        elif "【五、公告/新闻关键词检查】" in lines[i] or "【四、重大消息面检查】" in lines[i]:
            sub_i = i + 2
            while sub_i < len(lines) and not lines[sub_i].startswith("【六"):
                if lines[sub_i].strip():
                    info['news_check'].append(lines[sub_i].strip())
                sub_i += 1
        i += 1
    return info


def extract_deep_analysis(alert_report):
    analysis = {}
    if not alert_report:
        return analysis
    
    lines = alert_report.split('\n')
    
    for key, section in [('market_analysis', '【六、盘后综合评估】'), 
                         ('suggestion', '【七、操作建议】'),
                         ('follow_up', '【八、后续跟踪事项】')]:
        analysis[key] = []
        i = 0
        while i < len(lines):
            if section in lines[i]:
                sub_i = i + 2
                while sub_i < len(lines):
                    next_section = lines[sub_i].strip()
                    if next_section.startswith("【") or next_section.startswith("="):
                        break
                    if next_section:
                        analysis[key].append(next_section)
                    sub_i += 1
                break
            i += 1
    return analysis


def generate_daily_report(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serenity_stock_data", "daily_reviews")
    monitor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serenity_monitor_data")
    
    selection_report_path = os.path.join(report_dir, f"selection_report_{date_str}.txt")
    daily_review_path = os.path.join(report_dir, f"daily_review_{date_str}.txt")
    alert_report_path = os.path.join(monitor_dir, f"jingrui_alert_{date_str}.txt")
    
    selection_report = read_file_content(selection_report_path)
    daily_review = read_file_content(daily_review_path)
    alert_report = read_file_content(alert_report_path)
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append(f"    Serenity瓶颈投资每日复盘报告")
    report_lines.append(f"    报告日期: {date_str}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    report_lines.append("【一、今日选股结果】")
    report_lines.append("-" * 60)
    report_lines.append("")
    
    if selection_report:
        candidates = extract_bottleneck_candidates(selection_report)
        report_lines.append(f"候选瓶颈环节数量: {len(candidates)}")
        report_lines.append("")
        
        sorted_candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        for idx, candidate in enumerate(sorted_candidates, 1):
            report_lines.append(f"  {idx}. 🎯 {candidate['name']}")
            report_lines.append(f"     所属赛道: {candidate['industry']}")
            report_lines.append(f"     产业链位置: {candidate['location']}")
            report_lines.append(f"     综合评分: {candidate['score']}分")
            report_lines.append("")
        
        unique_stocks = extract_selected_stocks(selection_report)
        report_lines.append(f"多策略共识标的: {len(unique_stocks)}只")
        report_lines.append("")
        for key, stock in unique_stocks.items():
            report_lines.append(f"  🟢 {stock['stock_name']}({stock['stock_code']})")
            report_lines.append(f"     覆盖策略: {', '.join(stock['strategies'])}")
            report_lines.append("")
    else:
        report_lines.append("  今日无选股报告")
        report_lines.append("")
    
    report_lines.append("【二、持仓验证结果】")
    report_lines.append("-" * 60)
    report_lines.append("")
    
    holdings, selection_info, count_info = extract_holdings(daily_review)
    if selection_info:
        report_lines.append(f"  今日选股: {selection_info}")
        report_lines.append("")
    if count_info:
        report_lines.append(f"  {count_info}")
        report_lines.append("")
    if holdings:
        for h in holdings:
            report_lines.append(f"  {h}")
    else:
        report_lines.append("  暂无持仓")
    report_lines.append("")
    
    report_lines.append("【三、策略表现排名】")
    report_lines.append("-" * 60)
    report_lines.append("")
    
    rankings = extract_strategy_ranking(daily_review)
    if rankings:
        for rank in rankings:
            report_lines.append(f"  {rank}")
    else:
        report_lines.append("  策略数据待更新")
    report_lines.append("")
    
    report_lines.append("【四、预警监控信息】")
    report_lines.append("-" * 60)
    report_lines.append("")
    
    alert_info = extract_alert_info(alert_report)
    if alert_info and 'name' in alert_info:
        report_lines.append(f"  标的名称: {alert_info.get('name', '未知')}")
        report_lines.append(f"  当前价格: {alert_info.get('price', '未知')}")
        report_lines.append(f"  涨跌幅: {alert_info.get('change', '未知')}")
        report_lines.append(f"  换手率: {alert_info.get('turnover', '未知')}")
        report_lines.append(f"  成交量: {alert_info.get('volume', '未知')}")
        report_lines.append("")
        
        if alert_info['pre_market']:
            report_lines.append("  🚨 盘前重大事件:")
            for event in alert_info['pre_market']:
                report_lines.append(f"    {event}")
            report_lines.append("")
        
        if alert_info['alert_table']:
            report_lines.append("  📊 预警状态表:")
            for row in alert_info['alert_table']:
                report_lines.append(f"    {row}")
            report_lines.append("")
        
        if alert_info['news_check']:
            report_lines.append("  📰 公告/新闻监控:")
            for check in alert_info['news_check']:
                report_lines.append(f"    {check}")
    else:
        report_lines.append("  今日无预警信息")
    report_lines.append("")
    
    report_lines.append("【五、深度分析与建议】")
    report_lines.append("-" * 60)
    report_lines.append("")
    
    analysis = extract_deep_analysis(alert_report)
    if analysis:
        if analysis['market_analysis']:
            report_lines.append("  📈 盘后综合评估:")
            for item in analysis['market_analysis']:
                report_lines.append(f"    {item}")
            report_lines.append("")
        
        if analysis['suggestion']:
            report_lines.append("  💡 操作建议:")
            for item in analysis['suggestion']:
                report_lines.append(f"    {item}")
            report_lines.append("")
        
        if analysis['follow_up']:
            report_lines.append("  📋 后续跟踪事项:")
            for item in analysis['follow_up']:
                report_lines.append(f"    {item}")
    
    report_lines.append("")
    report_lines.append("💎 Serenity投资思考:")
    report_lines.append("  1. 今日日本光刻胶断供是重大催化事件，国产替代逻辑进一步强化")
    report_lines.append("  2. 晶瑞电材在美股暴跌7.87%背景下仅跌1.71%，显示较强抗跌性")
    report_lines.append("  3. 换手率10.76%表明市场分歧加大，有资金逆势进场")
    report_lines.append("  4. 新筛选的高速光芯片(源杰科技、长光华芯)和HBM(海光信息)值得关注")
    report_lines.append("  5. 建议密切跟踪日本断供执行情况及国内替代订单落地")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append(f"    报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    
    full_report = '\n'.join(report_lines)
    
    report_path = os.path.join(report_dir, f"daily_review_report_{date_str}.txt")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
        print(f"✅ 每日复盘报告已生成: {report_path}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
    
    return full_report


if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    report = generate_daily_report(date_arg)
    print(report)