#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
今日大盘分析 + 近3个月板块对比 + 估值偏低股票筛选
"""
import sys
sys.path.insert(0, '.')

import pandas as pd
from a_stock_data_core import get_historical_k_data, get_index_list

def get_market_overview():
    """获取大盘概况"""
    index_list = [
        ("000001", "上证指数"),
        ("399001", "深证成指"),
        ("399006", "创业板指"),
        ("000016", "上证50"),
        ("000905", "中证500"),
    ]
    
    results = {}
    
    for code, name in index_list:
        try:
            df = get_historical_k_data(code, period="daily", days=90)  # 近3个月
            if df is not None and not df.empty:
                latest_close = df['close'].iloc[-1]
                change_3m = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                change_1m = (df['close'].iloc[-1] / df['close'].iloc[-22] - 1) * 100 if len(df) >= 22 else 0
                
                results[name] = {
                    'code': code,
                    'latest_close': latest_close,
                    'change_3m': change_3m,
                    'change_1m': change_1m,
                }
        except Exception as e:
            print(f"获取 {name} 数据失败: {e}")
    
    return results

def get_sector_data():
    """获取板块数据（半导体相关ETF作为板块代表）"""
    sector_codes = [
        ("512480", "半导体ETF", "半导体"),
        ("512760", "芯片ETF", "芯片"),
        ("159813", "芯片产业ETF", "芯片产业"),
        ("515220", "新能源汽车ETF", "新能源汽车"),
        ("159806", "光伏ETF", "光伏"),
        ("512880", "证券ETF", "证券"),
        ("510050", "50ETF", "蓝筹"),
        ("159915", "创业板ETF", "创业板"),
    ]
    
    results = {}
    
    for code, name, sector in sector_codes:
        try:
            df = get_historical_k_data(code, period="daily", days=90)
            if df is not None and not df.empty:
                latest_close = df['close'].iloc[-1]
                change_3m = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
                change_1m = (df['close'].iloc[-1] / df['close'].iloc[-22] - 1) * 100 if len(df) >= 22 else 0
                
                results[sector] = {
                    'code': code,
                    'name': name,
                    'latest_close': latest_close,
                    'change_3m': change_3m,
                    'change_1m': change_1m,
                }
        except Exception as e:
            print(f"获取 {name} 数据失败: {e}")
    
    return results

def analyze_market():
    """分析市场"""
    print("=" * 100)
    print("今日大盘分析 + 近3个月板块对比")
    print("=" * 100)
    print()
    
    # 获取大盘数据
    market_data = get_market_overview()
    
    print("【大盘指数近3个月表现】")
    print("-" * 80)
    print(f"{'指数':<12} {'最新收盘':<12} {'3个月涨跌':<12} {'1个月涨跌':<12}")
    print("-" * 80)
    
    for name, data in market_data.items():
        print(f"{name:<12} {data['latest_close']:<12.2f} {data['change_3m']:<12.2f}% {data['change_1m']:<12.2f}%")
    
    print()
    
    # 获取板块数据
    sector_data = get_sector_data()
    
    print("【主要板块近3个月表现】")
    print("-" * 80)
    print(f"{'板块':<12} {'ETF名称':<15} {'最新收盘':<12} {'3个月涨跌':<12} {'1个月涨跌':<12}")
    print("-" * 80)
    
    sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1]['change_3m'], reverse=True)
    
    for sector, data in sorted_sectors:
        print(f"{sector:<12} {data['name']:<15} {data['latest_close']:<12.3f} {data['change_3m']:<12.2f}% {data['change_1m']:<12.2f}%")
    
    print()
    
    # 主流板块判断
    print("【主流板块判断】")
    print("-" * 80)
    
    # 定义主流板块：3个月涨幅超过10%，且1个月涨幅超过5%
    mainstream_sectors = [s for s in sorted_sectors if s[1]['change_3m'] > 10 and s[1]['change_1m'] > 3]
    
    if mainstream_sectors:
        print("当前主流板块：")
        for sector, data in mainstream_sectors:
            print(f"  ✅ {sector}：3个月+{data['change_3m']:.1f}%，1个月+{data['change_1m']:.1f}%")
    else:
        print("当前无明显主流板块")
    
    print()
    
    return market_data, sector_data

if __name__ == "__main__":
    try:
        market_data, sector_data = analyze_market()
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
