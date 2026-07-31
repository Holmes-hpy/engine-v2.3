#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026年6月4日 A股大盘深度分析
"""
import sys
sys.path.insert(0, '.')

import requests
import pandas as pd
from datetime import datetime
import json

from a_stock_data_core import (
    get_stock_quote,
    get_historical_k_data,
    get_market_index as get_single_quote
)

def get_index_data(code):
    """获取指数或股票数据"""
    return get_stock_quote(code)

def print_sector_data():
    """获取主要指数数据"""
    print("=" * 80)
    print("2026年6月4日 A股大盘深度分析")
    print("=" * 80)
    print()
    
    # 主要指数（纯数字代码）
    indices = [
        ("000001", "上证指数"),
        ("399001", "深证成指"),
        ("399006", "创业板指"),
        ("000300", "沪深300"),
    ]
    
    print("【1. 主要指数今日行情】")
    print("-" * 80)
    for code, name in indices:
        try:
            data = get_stock_quote(code)
            if data:
                price = data.get('price', 0)
                pct = data.get('change_pct', 0)
                if price > 0:
                    print(f"{name}: {price} 涨跌: {pct}%")
                else:
                    print(f"{name}: 数据不可用")
            else:
                print(f"{name}: 数据获取失败")
        except Exception as e:
            print(f"{name}: 失败: {e}")
    print()
    
    # 部分热门股票
    print("【2. 热门股票今日表现】")
    print("-" * 80)
    hot_stocks = [
        ("600519", "贵州茅台"),
        ("000001", "平安银行"),
        ("300750", "宁德时代"),
        ("002594", "比亚迪"),
        ("000858", "五粮液"),
        ("600584", "北方华创"),
    ]
    for code, name in hot_stocks:
        try:
            data = get_stock_quote(code)
            if data:
                price = data.get('price', 0)
                pct = data.get('change_pct', 0)
                print(f"{name}({code}): {price} 涨跌: {pct}%")
        except Exception as e:
            print(f"{name}({code}): 失败")
    print()
    
    print("【3. 市场概况】")
    print("-" * 80)
    print("注：完整行业板块数据需更详细分析见下方")
    print()

if __name__ == "__main__":
    print_sector_data()
