#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
半导体行业大盘走势分析
截止日期：2026年6月3日
"""
import sys
sys.path.insert(0, '.')

import requests
import pandas as pd
from datetime import datetime, timedelta
from a_stock_data_core import get_historical_k_data

def get_semiconductor_data():
    """获取半导体相关指数和ETF历史数据"""
    
    # 半导体相关指数和ETF代码
    semiconductor_codes = [
        ("512480", "半导体ETF"),
        ("512760", "芯片ETF"),
        ("159813", "芯片产业ETF"),
        ("515980", "集成电路ETF"),
        ("588200", "科创板芯片ETF"),
    ]
    
    print("=" * 80)
    print("半导体行业大盘走势分析")
    print("截止日期：2026年6月3日")
    print("=" * 80)
    print()
    
    results = {}
    
    for code, name in semiconductor_codes:
        try:
            print(f"正在获取 {name} ({code}) 数据...")
            # 获取最近60个交易日的数据
            df = get_historical_k_data(code, period="daily", days=60)
            if df is not None and not df.empty:
                # 筛选到2026年6月3日的数据
                df = df[df['date'] <= '2026-06-03']
                results[name] = {
                    'code': code,
                    'data': df,
                    'latest_close': df['close'].iloc[-1],
                    'latest_date': df['date'].iloc[-1],
                    'change_pct_5d': (df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100 if len(df) >= 6 else 0,
                    'change_pct_20d': (df['close'].iloc[-1] / df['close'].iloc[-21] - 1) * 100 if len(df) >= 21 else 0,
                    'change_pct_60d': (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100 if len(df) >= 60 else 0,
                }
                print(f"  ✅ 获取成功！最新收盘: {df['close'].iloc[-1]:.2f}")
            else:
                print(f"  ❌ 数据为空")
        except Exception as e:
            print(f"  ❌ 获取失败: {e}")
        print()
    
    return results

def analyze_results(results):
    """分析结果"""
    
    if not results:
        print("没有获取到有效数据！")
        return
    
    print()
    print("=" * 80)
    print("半导体行业走势分析结果")
    print("=" * 80)
    print()
    
    # 按5日涨跌幅排序
    sorted_results = sorted(results.items(), key=lambda x: x[1]['change_pct_5d'], reverse=True)
    
    print("【各ETF近期涨跌幅】")
    print("-" * 80)
    print(f"{'名称':<15} {'最新收盘':<12} {'5日涨跌':<10} {'20日涨跌':<10} {'60日涨跌':<10}")
    print("-" * 80)
    
    for name, data in sorted_results:
        latest_date = data['latest_date']
        close = data['latest_close']
        pct_5d = data['change_pct_5d']
        pct_20d = data['change_pct_20d']
        pct_60d = data['change_pct_60d']
        
        pct_5d_str = f"{pct_5d:+.2f}%"
        pct_20d_str = f"{pct_20d:+.2f}%"
        pct_60d_str = f"{pct_60d:+.2f}%"
        
        print(f"{name:<15} {close:<12.2f} {pct_5d_str:<10} {pct_20d_str:<10} {pct_60d_str:<10}")
    
    print()
    
    # 计算平均涨跌幅
    avg_5d = sum(r['change_pct_5d'] for r in results.values()) / len(results)
    avg_20d = sum(r['change_pct_20d'] for r in results.values()) / len(results)
    avg_60d = sum(r['change_pct_60d'] for r in results.values()) / len(results)
    
    print("【行业平均涨跌幅】")
    print("-" * 80)
    print(f"5日平均涨跌: {avg_5d:+.2f}%")
    print(f"20日平均涨跌: {avg_20d:+.2f}%")
    print(f"60日平均涨跌: {avg_60d:+.2f}%")
    print()
    
    # 显示最近5天的数据（以第一个ETF为例）
    if sorted_results:
        first_name, first_data = sorted_results[0]
        recent_df = first_data['data'].tail(5)
        
        print(f"【{first_name} 最近5个交易日数据】")
        print("-" * 80)
        print(f"{'日期':<12} {'开盘':<10} {'收盘':<10} {'涨跌幅':<10} {'成交量':<15}")
        print("-" * 80)
        
        for _, row in recent_df.iterrows():
            date = row['date']
            open_p = row['open']
            close_p = row['close']
            change_pct = row.get('pct_chg', 0)
            vol = row['volume']
            print(f"{date:<12} {open_p:<10.2f} {close_p:<10.2f} {change_pct:+.2f}%{'':<6} {vol:,.0f}")
        
        print()
    
    # 趋势判断
    print("【趋势判断】")
    print("-" * 80)
    if avg_60d > 10:
        trend_60d = "强势上涨"
    elif avg_60d > 0:
        trend_60d = "震荡上行"
    elif avg_60d > -10:
        trend_60d = "震荡下行"
    else:
        trend_60d = "明显下跌"
    
    if avg_5d > avg_20d:
        momentum = "近期动能增强"
    else:
        momentum = "近期动能减弱"
    
    print(f"60日趋势: {trend_60d}")
    print(f"5日相对20日: {momentum}")
    print(f"5日平均涨跌: {avg_5d:+.2f}%")
    print()

if __name__ == "__main__":
    try:
        results = get_semiconductor_data()
        analyze_results(results)
    except Exception as e:
        print(f"分析过程出错: {e}")
        import traceback
        traceback.print_exc()
