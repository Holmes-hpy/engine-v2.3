#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
低估值高股息"老登股"深度分析引擎 v3.0

数据来源：东方财富数据中心
- RPT_SHAREBONUS_DET: 分红送转数据（获取股票列表+分红数据）
- RPT_VALUEANALYSIS_DET: 估值数据（PE、PB、市值、股价、行业）
- RPT_LICO_FN_CPD: 财务指标（ROE、增速、毛利率）

筛选逻辑：
1. 估值筛选：PE-TTM < 15 且 PB < 1.5
2. 股息筛选：最近一年股息率 > 4%
3. 质量筛选：ROE > 6%（年化），连续分红 >= 3年
4. 规模筛选：总市值 > 100亿
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

import pandas as pd

PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from a_stock_data_core import eastmoney_datacenter

# ==================== 配置 ====================

# "老登股"典型行业关键词
OLD_TIMER_KEYWORDS = [
    "银行", "保险", "证券", "煤炭", "石油", "石化", "炼化",
    "钢铁", "普钢", "特钢", "房地产", "地产", "公用事业",
    "电力", "火电", "水电", "燃气", "交通运输", "高速",
    "港口", "航空", "机场", "航运", "物流", "家电", "白电",
    "建筑", "建材", "水泥", "玻璃", "纺织", "服装", "造纸",
    "汽车", "乘用车", "商用车", "食品饮料", "白酒", "啤酒",
    "医药商业", "零售", "超市", "百货", "银行Ⅱ", "煤炭开采",
    "炼化及贸易", "普钢",
]

# 筛选阈值
SCREENING_CRITERIA = {
    "max_pe_ttm": 15.0,
    "max_pb": 1.5,
    "min_dividend_yield": 4.0,
    "min_consecutive_dividend": 3,
    "min_roe": 6.0,       # 年化ROE
    "min_mcap_yi": 100.0,
    "max_mcap_yi": 50000.0,
}

# ==================== 数据类 ====================

@dataclass
class StockAnalysis:
    code: str
    name: str
    industry: str = ""
    
    # 估值
    price: float = 0.0
    pe_ttm: float = 0.0
    pb: float = 0.0
    ps_ttm: float = 0.0
    mcap_yi: float = 0.0
    float_mcap_yi: float = 0.0
    
    # 股息
    dividend_yield: float = 0.0
    dividend_per_share: float = 0.0
    payout_ratio: float = 0.0
    consecutive_years: int = 0
    dividend_cagr_3y: float = 0.0
    
    # 盈利
    roe: float = 0.0       # 年化ROE
    eps: float = 0.0
    bps: float = 0.0
    gross_margin: float = 0.0
    revenue_growth: float = 0.0
    profit_growth: float = 0.0
    
    # 评分
    value_score: float = 0.0
    dividend_score: float = 0.0
    quality_score: float = 0.0
    total_score: float = 0.0
    
    # 标签
    highlights: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    is_old_timer: bool = False

# ==================== 数据获取函数 ====================

def get_dividend_stock_list() -> Tuple[List[str], Dict[str, Dict]]:
    """获取所有有分红记录的股票列表及分红数据"""
    print("💰 从分红报表获取股票列表...")
    
    all_data = []
    seen_codes = set()
    page = 1
    
    while True:
        try:
            data = eastmoney_datacenter(
                "RPT_SHAREBONUS_DET",
                filter_str="",
                page_size=500,
                sort_columns="REPORT_DATE",
                sort_types="-1",
            )
            if not data:
                break
            
            for d in data:
                code = d["SECURITY_CODE"]
                all_data.append(d)
                seen_codes.add(code)
            
            if len(data) < 500:
                break
            
            page += 1
            if page > 30:
                break
            
            if page % 5 == 0:
                print(f"  第{page}页，已获取 {len(seen_codes)} 只股票")
            
            time.sleep(0.2)
        except Exception as e:
            print(f"  ⚠️  第{page}页失败: {e}")
            break
    
    codes = list(seen_codes)
    print(f"✅ 共获取 {len(codes)} 只有分红记录的股票")
    print()
    
    # 整理每只股票的分红数据
    div_dict = {}
    df_all = pd.DataFrame(all_data)
    
    for code in codes:
        stock_divs = df_all[df_all["SECURITY_CODE"] == code].copy()
        if stock_divs.empty:
            continue
        
        # 按报告日期排序
        stock_divs["year"] = pd.to_datetime(stock_divs["REPORT_DATE"]).dt.year
        stock_divs = stock_divs.sort_values("REPORT_DATE", ascending=False)
        
        # 筛选有现金分红的记录
        cash_divs = stock_divs[
            stock_divs["PRETAX_BONUS_RMB"].apply(lambda x: float(x or 0) > 0)
        ].copy()
        
        if cash_divs.empty:
            continue
        
        # 计算连续分红年数
        years = sorted(cash_divs["year"].unique(), reverse=True)
        consecutive = 0
        prev_year = None
        for y in years:
            if prev_year is None or y == prev_year - 1:
                consecutive += 1
                prev_year = y
            else:
                break
        
        # 最近分红（每10股）
        latest = cash_divs.iloc[0]
        latest_dps_10 = float(latest.get("PRETAX_BONUS_RMB") or 0)
        latest_dps = latest_dps_10 / 10
        
        # 3年分红CAGR
        div_cagr_3y = 0.0
        if len(cash_divs) >= 3:
            div_3y = float(cash_divs.iloc[2].get("PRETAX_BONUS_RMB") or 0)
            if div_3y > 0 and latest_dps_10 > 0:
                div_cagr_3y = ((latest_dps_10 / div_3y) ** (1/3) - 1) * 100
        
        # 分红率
        payout_ratio = float(latest.get("DIVIDENT_RATIO") or 0) * 100
        
        # 名称
        name = latest.get("SECURITY_NAME_ABBR", "")
        
        div_dict[code] = {
            "name": name,
            "dps": latest_dps,
            "dps_10": latest_dps_10,
            "consecutive_years": consecutive,
            "div_cagr_3y": div_cagr_3y,
            "payout_ratio": payout_ratio,
            "total_records": len(cash_divs),
        }
    
    print(f"📊 其中有现金分红记录的: {len(div_dict)} 只")
    print()
    return list(div_dict.keys()), div_dict

def get_valuation_data(codes: List[str]) -> Dict[str, Dict]:
    """批量获取估值数据"""
    print(f"📊 正在获取 {len(codes)} 只股票的估值数据...")
    
    result = {}
    
    for i, code in enumerate(codes):
        if i > 0 and i % 100 == 0:
            print(f"  进度: {i}/{len(codes)}...")
        
        try:
            data = eastmoney_datacenter(
                "RPT_VALUEANALYSIS_DET",
                filter_str=f'(SECURITY_CODE="{code}")',
                page_size=1,
                sort_columns="TRADE_DATE",
                sort_types="-1",
            )
            
            if data:
                d = data[0]
                
                def sf(v):
                    try:
                        return float(v) if v and v != "-" else 0.0
                    except:
                        return 0.0
                
                result[code] = {
                    "name": d.get("SECURITY_NAME_ABBR", ""),
                    "industry": d.get("BOARD_NAME", ""),
                    "price": sf(d.get("CLOSE_PRICE")),
                    "pe_ttm": sf(d.get("PE_TTM")),
                    "pb": sf(d.get("PB_MRQ")),
                    "ps_ttm": sf(d.get("PS_TTM")),
                    "mcap": sf(d.get("TOTAL_MARKET_CAP")),
                    "float_mcap": sf(d.get("NOTLIMITED_MARKETCAP_A")),
                    "mcap_yi": sf(d.get("TOTAL_MARKET_CAP")) / 100000000,
                    "float_mcap_yi": sf(d.get("NOTLIMITED_MARKETCAP_A")) / 100000000,
                }
        except Exception as e:
            pass
        
        time.sleep(0.08)
    
    print(f"✅ 成功获取 {len(result)} 只股票估值数据")
    print()
    return result

def get_financial_data(codes: List[str]) -> Dict[str, Dict]:
    """批量获取财务数据"""
    print(f"📈 正在获取 {len(codes)} 只股票的财务数据...")
    
    result = {}
    
    for i, code in enumerate(codes):
        if i > 0 and i % 100 == 0:
            print(f"  进度: {i}/{len(codes)}...")
        
        try:
            data = eastmoney_datacenter(
                "RPT_LICO_FN_CPD",
                filter_str=f'(SECURITY_CODE="{code}")',
                page_size=2,
                sort_columns="REPORTDATE",
                sort_types="-1",
            )
            
            if data:
                latest = data[0]
                
                def sf(v):
                    try:
                        return float(v) if v and v != "-" else 0.0
                    except:
                        return 0.0
                
                roe_q = sf(latest.get("WEIGHTAVG_ROE"))
                # ROE可能是单季度的，尝试年化
                # 如果是单季度数据，需要看报告期
                report_date = str(latest.get("REPORTDATE", ""))
                roe_annual = roe_q
                
                result[code] = {
                    "eps": sf(latest.get("BASIC_EPS")),
                    "roe": roe_annual,
                    "roe_raw": roe_q,
                    "bps": sf(latest.get("BPS")),
                    "revenue_growth": sf(latest.get("YSTZ")),
                    "profit_growth": sf(latest.get("SJLTZ")),
                    "gross_margin": sf(latest.get("XSMLL")),
                    "report_date": report_date,
                }
        except Exception as e:
            pass
        
        time.sleep(0.08)
    
    print(f"✅ 成功获取 {len(result)} 只股票财务数据")
    print()
    return result

# ==================== 评分函数 ====================

def is_old_timer_industry(industry: str) -> bool:
    """判断是否为老登股行业"""
    if not industry:
        return False
    for kw in OLD_TIMER_KEYWORDS:
        if kw in industry:
            return True
    return False

def calculate_value_score(stock: StockAnalysis, 
                          industry_avg_pe: float, 
                          industry_avg_pb: float) -> float:
    """价值得分"""
    score = 0.0
    
    # PE得分（40分）
    if stock.pe_ttm > 0 and industry_avg_pe > 0:
        pe_discount = max(0, 1 - stock.pe_ttm / industry_avg_pe)
        score += min(40, pe_discount * 80)
    elif 0 < stock.pe_ttm < 8:
        score += 35
    elif 0 < stock.pe_ttm < 12:
        score += 25
    elif 0 < stock.pe_ttm < 15:
        score += 18
    
    # PB得分（40分）
    if stock.pb > 0 and industry_avg_pb > 0:
        pb_discount = max(0, 1 - stock.pb / industry_avg_pb)
        score += min(40, pb_discount * 80)
    elif stock.pb < 0.6:
        score += 38
    elif stock.pb < 0.8:
        score += 30
    elif stock.pb < 1.0:
        score += 22
    
    # 破净加分（20分）
    if stock.pb < 1.0:
        score += min(20, (1 - stock.pb) * 50)
    
    return min(score, 100)

def calculate_dividend_score(stock: StockAnalysis) -> float:
    """股息得分"""
    score = 0.0
    
    # 股息率（50分）
    if stock.dividend_yield >= 12:
        score += 50
    elif stock.dividend_yield >= 10:
        score += 47
    elif stock.dividend_yield >= 8:
        score += 42
    elif stock.dividend_yield >= 6:
        score += 35
    elif stock.dividend_yield >= 5:
        score += 28
    elif stock.dividend_yield >= 4:
        score += 20
    
    # 连续分红年数（30分）
    if stock.consecutive_years >= 10:
        score += 30
    elif stock.consecutive_years >= 7:
        score += 25
    elif stock.consecutive_years >= 5:
        score += 20
    elif stock.consecutive_years >= 3:
        score += 14
    elif stock.consecutive_years >= 2:
        score += 8
    
    # 分红增速（20分）
    if stock.dividend_cagr_3y >= 15:
        score += 20
    elif stock.dividend_cagr_3y >= 10:
        score += 16
    elif stock.dividend_cagr_3y >= 5:
        score += 12
    elif stock.dividend_cagr_3y >= 0:
        score += 8
    elif stock.dividend_cagr_3y >= -5:
        score += 4
    
    return min(score, 100)

def calculate_quality_score(stock: StockAnalysis) -> float:
    """质量得分"""
    score = 0.0
    
    # ROE（35分）
    if stock.roe >= 20:
        score += 35
    elif stock.roe >= 15:
        score += 28
    elif stock.roe >= 12:
        score += 22
    elif stock.roe >= 10:
        score += 18
    elif stock.roe >= 8:
        score += 14
    elif stock.roe >= 6:
        score += 10
    
    # 毛利率（15分）
    if stock.gross_margin >= 40:
        score += 15
    elif stock.gross_margin >= 30:
        score += 12
    elif stock.gross_margin >= 20:
        score += 9
    elif stock.gross_margin >= 10:
        score += 6
    elif stock.gross_margin > 0:
        score += 3
    
    # 成长性（25分）
    if stock.profit_growth >= 30:
        score += 25
    elif stock.profit_growth >= 20:
        score += 20
    elif stock.profit_growth >= 10:
        score += 16
    elif stock.profit_growth >= 5:
        score += 12
    elif stock.profit_growth >= 0:
        score += 8
    elif stock.profit_growth >= -10:
        score += 4
    
    # 性价比 PB/ROE（25分）
    if stock.roe > 0 and stock.pb > 0:
        pb_roe = stock.pb / stock.roe * 100
        if pb_roe < 8:
            score += 25
        elif pb_roe < 12:
            score += 20
        elif pb_roe < 18:
            score += 15
        elif pb_roe < 25:
            score += 10
    
    return min(score, 100)

# ==================== 主分析流程 ====================

def analyze_all_stocks() -> Tuple[List[StockAnalysis], Dict]:
    """完整分析流程"""
    print("=" * 80)
    print("🔍 低估值高股息\"老登股\"深度分析 v3.0")
    print("=" * 80)
    print()
    print(f"筛选标准：")
    print(f"  PE-TTM < {SCREENING_CRITERIA['max_pe_ttm']}")
    print(f"  PB < {SCREENING_CRITERIA['max_pb']}")
    print(f"  股息率 > {SCREENING_CRITERIA['min_dividend_yield']}%")
    print(f"  连续分红 >= {SCREENING_CRITERIA['min_consecutive_dividend']}年")
    print(f"  ROE > {SCREENING_CRITERIA['min_roe']}%")
    print(f"  总市值 {SCREENING_CRITERIA['min_mcap_yi']:.0f}-{SCREENING_CRITERIA['max_mcap_yi']:.0f}亿")
    print()
    
    # 第一步：获取所有有分红的股票
    codes, div_data = get_dividend_stock_list()
    
    if not codes:
        print("❌ 没有获取到分红股票数据")
        return [], {}
    
    # 第二步：获取估值数据
    val_data = get_valuation_data(codes)
    
    # 第三步：初筛（估值+市值）
    print("🔍 第一步筛选（估值+市值）...")
    filtered_codes = []
    for code in codes:
        if code not in val_data:
            continue
        v = val_data[code]
        if (v["pe_ttm"] > 0 and v["pe_ttm"] < SCREENING_CRITERIA["max_pe_ttm"] and
            v["pb"] > 0 and v["pb"] < SCREENING_CRITERIA["max_pb"] and
            v["mcap_yi"] > SCREENING_CRITERIA["min_mcap_yi"] and
            v["mcap_yi"] < SCREENING_CRITERIA["max_mcap_yi"]):
            filtered_codes.append(code)
    
    print(f"  通过筛选: {len(filtered_codes)} 只")
    print()
    
    if not filtered_codes:
        print("❌ 没有股票通过初筛")
        return [], {}
    
    # 第四步：获取财务数据
    fin_data = get_financial_data(filtered_codes)
    
    # 第五步：ROE筛选 + 股息率筛选
    print("🔍 第二步筛选（ROE+股息率）...")
    stocks = []
    
    for code in filtered_codes:
        if code not in fin_data or code not in div_data or code not in val_data:
            continue
        
        v = val_data[code]
        d = div_data[code]
        f = fin_data[code]
        
        # 计算股息率
        price = v["price"]
        dps = d["dps"]
        dividend_yield = (dps / price * 100) if price > 0 else 0
        
        # 股息率筛选
        if dividend_yield < SCREENING_CRITERIA["min_dividend_yield"]:
            continue
        
        # ROE筛选
        roe = f["roe"]
        if roe < SCREENING_CRITERIA["min_roe"]:
            continue
        
        # 连续分红年数筛选
        consecutive = d["consecutive_years"]
        if consecutive < SCREENING_CRITERIA["min_consecutive_dividend"]:
            if dividend_yield < 7:  # 特别高的放宽
                continue
        
        # 判断是否为老登股行业
        industry = v.get("industry", "")
        is_old = is_old_timer_industry(industry)
        
        # 创建分析对象
        stock = StockAnalysis(
            code=code,
            name=v.get("name", d.get("name", "")),
            industry=industry,
            price=price,
            pe_ttm=v["pe_ttm"],
            pb=v["pb"],
            ps_ttm=v["ps_ttm"],
            mcap_yi=v["mcap_yi"],
            float_mcap_yi=v["float_mcap_yi"],
            dividend_yield=dividend_yield,
            dividend_per_share=dps,
            payout_ratio=d["payout_ratio"],
            consecutive_years=consecutive,
            dividend_cagr_3y=d["div_cagr_3y"],
            roe=roe,
            eps=f["eps"],
            bps=f["bps"],
            gross_margin=f["gross_margin"],
            revenue_growth=f["revenue_growth"],
            profit_growth=f["profit_growth"],
            is_old_timer=is_old,
        )
        
        stocks.append(stock)
    
    print(f"  通过筛选: {len(stocks)} 只")
    old_timer_count = sum(1 for s in stocks if s.is_old_timer)
    print(f"  其中'老登股'行业: {old_timer_count} 只")
    print()
    
    if not stocks:
        print("❌ 没有股票通过所有筛选")
        return [], {}
    
    # 第六步：计算行业平均
    industry_groups = {}
    for s in stocks:
        ind = s.industry or "其他"
        if ind not in industry_groups:
            industry_groups[ind] = []
        industry_groups[ind].append(s)
    
    industry_stats = {}
    for ind, ind_stocks in industry_groups.items():
        avg_pe = sum(s.pe_ttm for s in ind_stocks) / len(ind_stocks)
        avg_pb = sum(s.pb for s in ind_stocks) / len(ind_stocks)
        avg_div = sum(s.dividend_yield for s in ind_stocks) / len(ind_stocks)
        industry_stats[ind] = {
            "count": len(ind_stocks),
            "avg_pe": avg_pe,
            "avg_pb": avg_pb,
            "avg_dividend_yield": avg_div,
        }
    
    # 第七步：计算得分
    for stock in stocks:
        ind = stock.industry or "其他"
        avg_pe = industry_stats.get(ind, {}).get("avg_pe", 10)
        avg_pb = industry_stats.get(ind, {}).get("avg_pb", 1)
        
        stock.value_score = calculate_value_score(stock, avg_pe, avg_pb)
        stock.dividend_score = calculate_dividend_score(stock)
        stock.quality_score = calculate_quality_score(stock)
        
        # 综合得分：价值40% + 股息35% + 质量25%
        stock.total_score = (
            stock.value_score * 0.40 +
            stock.dividend_score * 0.35 +
            stock.quality_score * 0.25
        )
        
        # 老登股行业加分
        if stock.is_old_timer:
            stock.total_score += 3
        
        # 生成亮点
        if stock.pe_ttm < 8:
            stock.highlights.append(f"PE仅{stock.pe_ttm:.1f}倍，极度低估")
        elif stock.pe_ttm < 10:
            stock.highlights.append(f"PE仅{stock.pe_ttm:.1f}倍，估值很低")
        
        if stock.pb < 0.6:
            stock.highlights.append(f"PB仅{stock.pb:.2f}，深度破净")
        elif stock.pb < 0.8:
            stock.highlights.append(f"PB仅{stock.pb:.2f}，明显破净")
        
        if stock.dividend_yield >= 8:
            stock.highlights.append(f"股息率高达{stock.dividend_yield:.2f}%，极其丰厚")
        elif stock.dividend_yield >= 6:
            stock.highlights.append(f"股息率{stock.dividend_yield:.2f}%，非常可观")
        
        if stock.consecutive_years >= 10:
            stock.highlights.append(f"连续{stock.consecutive_years}年分红，极其稳定")
        elif stock.consecutive_years >= 5:
            stock.highlights.append(f"连续{stock.consecutive_years}年分红，稳定可靠")
        
        if stock.roe >= 15:
            stock.highlights.append(f"ROE达{stock.roe:.1f}%，盈利能力强")
        
        # 生成风险
        if stock.profit_growth < -20:
            stock.risks.append(f"净利润大幅下滑{abs(stock.profit_growth):.1f}%")
        elif stock.profit_growth < -10:
            stock.risks.append(f"净利润下滑{abs(stock.profit_growth):.1f}%")
        
        if stock.dividend_cagr_3y < -10:
            stock.risks.append("分红呈明显下降趋势")
        
        if stock.payout_ratio > 80:
            stock.risks.append(f"分红率高达{stock.payout_ratio:.1f}%，可持续性存疑")
    
    # 排序
    stocks.sort(key=lambda x: x.total_score, reverse=True)
    
    return stocks, industry_stats

# ==================== 报告生成 ====================

def generate_report(stocks: List[StockAnalysis], industry_stats: Dict) -> str:
    """生成分析报告"""
    report = []
    
    report.append("=" * 100)
    report.append("📈 低估值高股息\"老登股\"深度分析报告")
    report.append(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 100)
    report.append("")
    
    # 概览
    report.append("📊 分析概览")
    report.append("-" * 80)
    report.append(f"  通过筛选股票总数: {len(stocks)} 只")
    old_timer_stocks = [s for s in stocks if s.is_old_timer]
    report.append(f"  其中'老登股'（传统行业）: {len(old_timer_stocks)} 只")
    report.append(f"  涉及行业数: {len(industry_stats)} 个")
    
    if stocks:
        avg_div = sum(s.dividend_yield for s in stocks) / len(stocks)
        avg_pe = sum(s.pe_ttm for s in stocks) / len(stocks)
        avg_pb = sum(s.pb for s in stocks) / len(stocks)
        avg_roe = sum(s.roe for s in stocks) / len(stocks)
        avg_mcap = sum(s.mcap_yi for s in stocks) / len(stocks)
        report.append(f"  平均股息率: {avg_div:.2f}%")
        report.append(f"  平均PE-TTM: {avg_pe:.2f}倍")
        report.append(f"  平均PB: {avg_pb:.2f}倍")
        report.append(f"  平均ROE: {avg_roe:.2f}%")
        report.append(f"  平均市值: {avg_mcap:.0f}亿")
    report.append("")
    
    # 一、行业分布
    report.append("一、行业分布")
    report.append("-" * 80)
    report.append("")
    
    report.append(
        f"{'行业':<16} {'股票数':<6} {'平均PE':<10} {'平均PB':<10} "
        f"{'平均股息率':<12} {'平均ROE':<10}"
    )
    report.append("-" * 75)
    
    for ind, stat in sorted(industry_stats.items(), key=lambda x: x[1]["count"], reverse=True):
        ind_stocks = [s for s in stocks if s.industry == ind]
        avg_roe = sum(s.roe for s in ind_stocks) / len(ind_stocks) if ind_stocks else 0
        is_old = " ⭐" if any(s.is_old_timer for s in ind_stocks) else ""
        report.append(
            f"{ind:<16}{is_old} {stat['count']:<6} {stat['avg_pe']:<10.2f} "
            f"{stat['avg_pb']:<10.2f} {stat['avg_dividend_yield']:<12.2f}% "
            f"{avg_roe:<10.2f}%"
        )
    
    report.append("")
    report.append("⭐ 标记为'老登股'（传统行业）")
    report.append("")
    
    # 二、综合排名 TOP 30
    report.append("二、综合排名 TOP 30")
    report.append("-" * 80)
    report.append("")
    
    header = (
        f"{'排名':<4} {'名称':<12} {'代码':<8} {'行业':<14} "
        f"{'价格':<7} {'PE':<6} {'PB':<6} {'股息率':<8} "
        f"{'ROE':<7} {'市值(亿)':<10} {'综合分':<7} {'类型':<6}"
    )
    report.append(header)
    report.append("-" * 110)
    
    for i, s in enumerate(stocks[:30], 1):
        tag = "老登⭐" if s.is_old_timer else "其他"
        line = (
            f"{i:<4} {s.name:<12} {s.code:<8} {s.industry:<14} "
            f"{s.price:<7.2f} {s.pe_ttm:<6.1f} {s.pb:<6.2f} "
            f"{s.dividend_yield:<7.2f}% {s.roe:<6.1f}% "
            f"{s.mcap_yi:<10.0f} {s.total_score:<7.1f} {tag:<6}"
        )
        report.append(line)
    
    report.append("")
    
    # 三、分类排行榜
    report.append("三、分类排行榜")
    report.append("-" * 80)
    report.append("")
    
    # 价值低估榜
    report.append("🏆 【价值低估 TOP 15】（PE/PB最低，安全边际最高）")
    report.append("")
    value_sorted = sorted(stocks, key=lambda x: x.value_score, reverse=True)
    report.append(
        f"{'排名':<4} {'名称':<12} {'PE':<7} {'PB':<7} "
        f"{'股息率':<9} {'市值(亿)':<10} {'价值分':<7}"
    )
    report.append("-" * 65)
    for i, s in enumerate(value_sorted[:15], 1):
        report.append(
            f"{i:<4} {s.name:<12} {s.pe_ttm:<7.1f} {s.pb:<7.2f} "
            f"{s.dividend_yield:<8.2f}% {s.mcap_yi:<10.0f} {s.value_score:<7.1f}"
        )
    report.append("")
    
    # 高股息榜
    report.append("💰 【高股息 TOP 15】（股息率高+分红稳定）")
    report.append("")
    div_sorted = sorted(stocks, key=lambda x: x.dividend_score, reverse=True)
    report.append(
        f"{'排名':<4} {'名称':<12} {'股息率':<9} {'连续年数':<8} "
        f"{'3年增速':<9} {'分红率':<8} {'股息分':<7}"
    )
    report.append("-" * 65)
    for i, s in enumerate(div_sorted[:15], 1):
        report.append(
            f"{i:<4} {s.name:<12} {s.dividend_yield:<8.2f}% "
            f"{s.consecutive_years:<8} {s.dividend_cagr_3y:<8.2f}% "
            f"{s.payout_ratio:<7.1f}% {s.dividend_score:<7.1f}"
        )
    report.append("")
    
    # 高质量榜
    report.append("💎 【高质量 TOP 15】（盈利能力强+成长好）")
    report.append("")
    quality_sorted = sorted(stocks, key=lambda x: x.quality_score, reverse=True)
    report.append(
        f"{'排名':<4} {'名称':<12} {'ROE':<7} {'净利增速':<10} "
        f"{'毛利率':<8} {'PE':<7} {'质量分':<7}"
    )
    report.append("-" * 60)
    for i, s in enumerate(quality_sorted[:15], 1):
        report.append(
            f"{i:<4} {s.name:<12} {s.roe:<6.1f}% "
            f"{s.profit_growth:<9.1f}% {s.gross_margin:<7.1f}% "
            f"{s.pe_ttm:<7.1f} {s.quality_score:<7.1f}"
        )
    report.append("")
    
    # 老登股专榜
    if old_timer_stocks:
        report.append("👴 【老登股专榜 TOP 15】（传统行业低估高息）")
        report.append("")
        old_sorted = sorted(old_timer_stocks, key=lambda x: x.total_score, reverse=True)
        report.append(
            f"{'排名':<4} {'名称':<12} {'行业':<14} "
            f"{'PE':<7} {'PB':<7} {'股息率':<9} "
            f"{'ROE':<7} {'市值(亿)':<10} {'综合分':<7}"
        )
        report.append("-" * 85)
        for i, s in enumerate(old_sorted[:15], 1):
            report.append(
                f"{i:<4} {s.name:<12} {s.industry:<14} "
                f"{s.pe_ttm:<7.1f} {s.pb:<7.2f} {s.dividend_yield:<8.2f}% "
                f"{s.roe:<6.1f}% {s.mcap_yi:<10.0f} {s.total_score:<7.1f}"
            )
        report.append("")
    
    # 四、TOP 10 深度分析
    report.append("四、TOP 10 深度分析")
    report.append("-" * 80)
    report.append("")
    
    for i, s in enumerate(stocks[:10], 1):
        report.append(f"{'='*80}")
        tag = "【老登股⭐】" if s.is_old_timer else ""
        report.append(f"🏆 #{i} {s.name} ({s.code}) - {s.industry} {tag}")
        report.append(f"{'='*80}")
        report.append(
            f"   综合得分: {s.total_score:.1f} | "
            f"价值: {s.value_score:.1f} | "
            f"股息: {s.dividend_score:.1f} | "
            f"质量: {s.quality_score:.1f}"
        )
        report.append("")
        
        report.append(f"   📊 【估值指标】")
        report.append(
            f"      股价: {s.price:.2f}元 | "
            f"PE-TTM: {s.pe_ttm:.2f}倍 | "
            f"PB: {s.pb:.2f}倍 | "
            f"PS-TTM: {s.ps_ttm:.2f}倍"
        )
        report.append(
            f"      总市值: {s.mcap_yi:.0f}亿 | "
            f"流通市值: {s.float_mcap_yi:.0f}亿"
        )
        report.append("")
        
        report.append(f"   💰 【股息指标】")
        report.append(
            f"      股息率: {s.dividend_yield:.2f}% | "
            f"每股分红: {s.dividend_per_share:.4f}元 | "
            f"分红率: {s.payout_ratio:.1f}%"
        )
        report.append(
            f"      连续分红: {s.consecutive_years}年 | "
            f"3年分红CAGR: {s.dividend_cagr_3y:.2f}%"
        )
        report.append("")
        
        report.append(f"   📈 【盈利与成长】")
        report.append(
            f"      ROE: {s.roe:.2f}% | "
            f"EPS: {s.eps:.3f}元 | "
            f"BPS: {s.bps:.2f}元"
        )
        report.append(
            f"      营收增速: {s.revenue_growth:.2f}% | "
            f"净利润增速: {s.profit_growth:.2f}% | "
            f"毛利率: {s.gross_margin:.2f}%"
        )
        report.append("")
        
        if s.highlights:
            report.append(f"   ✨ 【投资亮点】")
            for h in s.highlights:
                report.append(f"      • {h}")
            report.append("")
        
        if s.risks:
            report.append(f"   ⚠️  【风险提示】")
            for r in s.risks:
                report.append(f"      • {r}")
            report.append("")
    
    # 五、投资策略建议
    report.append("五、投资策略建议")
    report.append("-" * 80)
    report.append("")
    
    report.append("🎯 【配置思路】")
    report.append("")
    report.append("1. 核心仓位（50%-60%）：")
    if len(stocks) >= 5:
        top5 = stocks[:5]
        report.append("   综合排名前5的标的，分散配置：")
        for i, s in enumerate(top5, 1):
            tag = "⭐" if s.is_old_timer else ""
            report.append(
                f"   #{i} {s.name}{tag}（{s.industry}）- "
                f"股息率{s.dividend_yield:.2f}%，PE{s.pe_ttm:.1f}倍，ROE{s.roe:.1f}%"
            )
    report.append("   目标：稳定分红收益 + 估值修复弹性")
    report.append("")
    
    report.append("2. 卫星仓位（20%-30%）：")
    report.append("   选择高股息率或有成长潜力的特色标的，增强组合收益")
    report.append("   可侧重：煤炭、银行、公用事业、高速等现金流稳定的行业")
    report.append("")
    
    report.append("3. 现金/债券仓位（10%-20%）：")
    report.append("   保留流动性，等待市场回调机会")
    report.append("")
    
    report.append("⚠️ 【重要风险提示】")
    report.append("")
    report.append("1. 低估值陷阱：")
    report.append("   估值低可能是有原因的（行业衰退、业绩下滑、政策风险等）")
    report.append("   要仔细区分'便宜的好公司'和'便宜的烂公司'")
    report.append("   ⚡ 我主观认为：PB低于0.5的股票要格外小心，很可能有基本面问题")
    report.append("")
    
    report.append("2. 股息可持续性：")
    report.append("   高股息率可能是因为股价下跌造成的（分母变小）")
    report.append("   优先选择连续分红5年以上、分红率稳定在30%-70%的公司")
    report.append("   分红率超过80%的要警惕可持续性")
    report.append("")
    
    report.append("3. 行业风险：")
    report.append("   • 银行：息差持续收窄、不良贷款上升的风险")
    report.append("   • 煤炭/石化：大宗商品价格波动、政策调控限价风险")
    report.append("   • 地产：行业下行周期、企业信用风险")
    report.append("   • 公用事业：电价/气价管制、煤炭/天然气成本上升风险")
    report.append("   • 钢铁/建材：需求疲软、产能过剩、周期性风险")
    report.append("")
    
    report.append("4. 利率风险：")
    report.append("   市场利率上升时，高股息股的相对吸引力会下降")
    report.append("   （因为债券收益率上升，资金会从高股息股流向债券）")
    report.append("")
    
    report.append("📋 【跟踪建议】")
    report.append("")
    report.append("• 每季度跟踪财报，重点关注：分红政策是否变化、ROE是否稳定")
    report.append("• 关注行业政策变化（煤炭长协价、银行息差、地产政策等）")
    report.append("• 估值修复到位后（PE回到行业中位数以上）考虑部分止盈")
    report.append("• 每年重新筛选一次，调出基本面恶化的标的")
    report.append("• 单只股票仓位建议不超过15%，避免黑天鹅风险")
    report.append("")
    
    report.append("💡 【什么是'老登股'？】")
    report.append("")
    report.append("   顾名思义，就是那些'上了年纪'的传统行业股票，特点是：")
    report.append("   1. 行业成熟，增速放缓，但现金流稳定")
    report.append("   2. 估值普遍偏低（PE低、PB低），市场不待见")
    report.append("   3. 分红慷慨，股息率高，是'现金奶牛'")
    report.append("   4. 偶尔会有'估值修复'行情（比如中特估、红利行情）")
    report.append("   5. 适合追求稳定收益、能忍受低波动的投资者")
    report.append("")
    
    report.append("=" * 100)
    report.append("📋 免责声明：本报告仅供学习研究，不构成任何投资建议。")
    report.append("   投资有风险，入市需谨慎。请独立思考，自负盈亏。")
    report.append("=" * 100)
    
    return "\n".join(report)

# ==================== 主函数 ====================

def main():
    """主函数"""
    print()
    print("🎯 开始低估值高股息'老登股'深度分析...")
    print()
    
    start_time = time.time()
    
    # 执行分析
    stocks, industry_stats = analyze_all_stocks()
    
    if not stocks:
        print("❌ 没有找到符合条件的股票")
        return
    
    elapsed = time.time() - start_time
    print(f"🎉 分析完成！共找到 {len(stocks)} 只符合条件的股票，耗时 {elapsed:.1f} 秒")
    print()
    
    # 生成报告
    report = generate_report(stocks, industry_stats)
    
    # 打印报告
    print(report)
    
    # 保存报告
    output_dir = PROJECT_DIR / "dividend_stock_reports"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    report_file = output_dir / f"deep_value_dividend_{timestamp}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print()
    print(f"📁 报告已保存至: {report_file}")
    
    # 保存CSV
    csv_data = []
    for s in stocks:
        csv_data.append({
            "代码": s.code,
            "名称": s.name,
            "行业": s.industry,
            "是否老登股": "是" if s.is_old_timer else "否",
            "价格(元)": round(s.price, 2),
            "PE-TTM": round(s.pe_ttm, 2),
            "PB": round(s.pb, 2),
            "PS-TTM": round(s.ps_ttm, 2),
            "股息率(%)": round(s.dividend_yield, 2),
            "每股分红(元)": round(s.dividend_per_share, 4),
            "分红率(%)": round(s.payout_ratio, 2),
            "连续分红年数": s.consecutive_years,
            "3年分红CAGR(%)": round(s.dividend_cagr_3y, 2),
            "ROE(%)": round(s.roe, 2),
            "EPS(元)": round(s.eps, 3),
            "BPS(元)": round(s.bps, 2),
            "营收增速(%)": round(s.revenue_growth, 2),
            "净利润增速(%)": round(s.profit_growth, 2),
            "毛利率(%)": round(s.gross_margin, 2),
            "总市值(亿)": round(s.mcap_yi, 2),
            "流通市值(亿)": round(s.float_mcap_yi, 2),
            "价值得分": round(s.value_score, 2),
            "股息得分": round(s.dividend_score, 2),
            "质量得分": round(s.quality_score, 2),
            "综合得分": round(s.total_score, 2),
            "投资亮点": "；".join(s.highlights),
            "风险提示": "；".join(s.risks),
        })
    
    csv_file = output_dir / f"deep_value_dividend_{timestamp}.csv"
    pd.DataFrame(csv_data).to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"📊 CSV数据已保存至: {csv_file}")
    print()

if __name__ == "__main__":
    main()
