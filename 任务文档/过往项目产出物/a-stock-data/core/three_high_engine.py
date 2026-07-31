# -*- coding: utf-8 -*-
"""
三高环节筛选引擎 - Three-High Screening Engine
= 高增长(High Growth) + 高利润(High Profit) + 高壁垒(High Barrier)
+ 供需失衡分析 + 龙头识别

核心流程:
1. 从BOM产业链知识库获取所有节点
2. 对每个节点进行四维度评估:
   - 高壁垒: 技术壁垒 + 国产化率低(进口替代空间)
   - 高增长: 行业增速 + 企业营收/利润增速
   - 高利润: 毛利率/净利率高于行业平均
   - 供需失衡: 需求扩张 > 供给扩张
3. 在每个"三高"节点中筛选龙头股
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from bom_industry_chain import (
    ALL_CHAINS, ChainNode, ChainLevel, IndustryCategory,
    get_all_leading_stocks,
)


@dataclass
class StockEvaluation:
    """股票评估结果"""
    code: str
    name: str
    node_name: str
    category: str
    level: str
    barrier_score: float  # 壁垒得分 0-100
    growth_score: float   # 增长得分 0-100
    profit_score: float   # 利润得分 0-100
    supply_demand_score: float  # 供需失衡得分 0-100
    total_score: float    # 总分 0-100
    quote: Dict = field(default_factory=dict)
    reason: str = ""


class ThreeHighEngine:
    """三高环节筛选引擎"""

    def __init__(self):
        self.stocks_data = get_all_leading_stocks()
        self.quotes_cache = {}

    # ============= 实时行情获取 =============

    def fetch_real_time_quotes(self, stock_codes: List[str]) -> Dict[str, Dict]:
        """批量获取股票实时行情"""
        from a_stock_data_core import get_stock_quote

        quotes = {}
        for code in stock_codes:
            code_clean = re.sub(r'[^0-9]', '', code)
            if code_clean in self.quotes_cache:
                quotes[code_clean] = self.quotes_cache[code_clean]
                continue

            try:
                result = get_stock_quote(code_clean)
                if code_clean in result:
                    quotes[code_clean] = result[code_clean]
                    self.quotes_cache[code_clean] = result[code_clean]
            except Exception as e:
                print(f"  ⚠️ 获取行情失败 {code_clean}: {e}")

            time.sleep(0.1)  # 限速

        return quotes

    # ============= 单维度评估 =============

    def evaluate_barrier(self, stock: Dict) -> float:
        """评估高壁垒"""
        score = 0

        # 1. 公司自有壁垒分数 (来自知识库)
        barrier_score = stock.get("barrier_score", 0)
        score += barrier_score * 0.6

        # 2. 国产化率判断 (越低 = 替代空间越大)
        supply_demand = stock.get("supply_demand", "")
        barrier_text = stock.get("barrier", "")

        # 关键词打分
        high_barrier_keywords = [
            ("垄断", 20), ("唯一", 15), ("极高", 15), ("全球仅", 20),
            ("突破前夜", 10), ("最卡脖子", 15), ("专利壁垒", 10),
            ("国产率<5%", 15), ("国产率<10%", 10), ("国产化率低", 10),
            ("EUV", 10), ("核医学", 10), ("CT球管", 10),
            ("光刻胶", 8), ("培养基", 8), ("靶材", 5),
        ]
        for keyword, weight in high_barrier_keywords:
            if keyword in barrier_text or keyword in supply_demand:
                score += weight

        # 3. 上游环节 + 高技术壁垒加分
        if stock.get("level") == "上游":
            score += 5

        return min(score, 100)

    def evaluate_growth(self, stock: Dict, quote: Dict) -> float:
        """评估高增长"""
        score = 0

        # 1. 从行业增长率推断
        # 提取行业增长率数字
        growth_text = ""
        for k, v in stock.items():
            if isinstance(v, str) and ("增长" in v or "增速" in v):
                growth_text += v

        import re
        growth_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', growth_text)
        if growth_matches:
            max_growth = max(float(g) for g in growth_matches)
            if max_growth >= 50:
                score += 30
            elif max_growth >= 30:
                score += 25
            elif max_growth >= 20:
                score += 20
            elif max_growth >= 10:
                score += 10

        # 2. 行业增长率 (从节点推断)
        node_growth_keywords = {
            "爆发期": 35, "突破前夜": 30, "快速成长期": 25,
            "成长期": 20, "升级期": 15, "成熟期": 10,
            "周期底部→复苏期": 25,
        }
        node_text = json.dumps(stock, ensure_ascii=False)
        for keyword, weight in node_growth_keywords.items():
            if keyword in node_text:
                score += weight
                break

        # 3. 近期股票表现 (动量因子)
        if quote:
            change_pct = quote.get("change_pct", 0)
            if change_pct > 5:
                score += 10
            elif change_pct > 2:
                score += 5

        # 4. 行业景气度判断
        boom_keywords = ["爆发期", "快速成长期", "突破前夜", "复苏"]
        for kw in boom_keywords:
            if kw in node_text:
                score += 5
                break

        return min(score, 100)

    def evaluate_profit(self, stock: Dict, quote: Dict) -> float:
        """评估高利润"""
        score = 0

        # 1. 龙头地位 (市场份额)
        market_share = stock.get("market_share", "")
        if "全球第一" in market_share or "全球前列" in market_share:
            score += 30
        elif "国内第一" in market_share:
            score += 25
        elif "国内领先" in market_share:
            score += 20

        # 2. 行业规模 (大行业 + 高份额 = 利润空间)
        node_text = json.dumps(stock, ensure_ascii=False)
        scale_matches = re.findall(r'(\d+(?:\.\d+)?)\s*亿美元', node_text)
        if scale_matches:
            total_scale = sum(float(s) for s in scale_matches)
            if total_scale >= 100:
                score += 20
            elif total_scale >= 50:
                score += 15
            elif total_scale >= 20:
                score += 10

        # 3. PE估值合理性 (低PE + 高增长 = 利润弹性)
        if quote:
            pe = quote.get("pe_ttm", 0)
            if pe > 0:
                if pe <= 30:
                    score += 15
                elif pe <= 50:
                    score += 10
                elif pe <= 80:
                    score += 5
                else:
                    score -= 5  # 高PE可能透支利润预期

        # 4. 国产替代空间带来的利润增量
        supply_demand = stock.get("supply_demand", "")
        if "供需紧张" in supply_demand or "国产率极低" in supply_demand or "替代空间巨大" in supply_demand:
            score += 20
        elif "快速提升" in supply_demand or "国产替代" in supply_demand:
            score += 10

        return min(score, 100)

    def evaluate_supply_demand(self, stock: Dict) -> float:
        """评估供需失衡"""
        score = 0

        supply_demand = stock.get("supply_demand", "")
        node_text = json.dumps(stock, ensure_ascii=False)
        combined_text = supply_demand + node_text

        # 强供需失衡关键词
        strong_imbalance = [
            "供需紧张", "供应短缺", "长期依赖进口", "国产化率低",
            "国产率极低", "替代空间巨大", "产能紧张",
        ]
        for kw in strong_imbalance:
            if kw in combined_text:
                score += 25
                break

        # 中度供需失衡
        medium_imbalance = [
            "快速提升", "国产替代", "替代", "供需平衡",
            "供给跟不上", "供不应求",
        ]
        for kw in medium_imbalance:
            if kw in combined_text:
                score += 15
                break

        # 需求扩张关键词
        demand_expansion = [
            "爆发", "快速成长", "突破", "扩张", "升级",
            "市场规模", "全球", "需求", "十五五",
        ]
        for kw in demand_expansion:
            if kw in combined_text:
                score += 10

        # 上游环节天然具有定价权
        if stock.get("level") == "上游":
            score += 10

        return min(score, 100)

    # ============= 综合评估 =============

    def evaluate_stock(self, stock: Dict, quote: Dict) -> StockEvaluation:
        """综合评估单只股票"""
        barrier = self.evaluate_barrier(stock)
        growth = self.evaluate_growth(stock, quote)
        profit = self.evaluate_profit(stock, quote)
        supply_demand = self.evaluate_supply_demand(stock)

        # 加权总分 (四维度)
        total_score = (
            barrier * 0.30      # 高壁垒权重最高
            + growth * 0.25     # 高增长
            + profit * 0.25     # 高利润
            + supply_demand * 0.20  # 供需失衡
        )

        # 构建理由
        reason_parts = []
        if barrier >= 60:
            reason_parts.append(f"高壁垒({barrier:.0f})")
        if growth >= 60:
            reason_parts.append(f"高增长({growth:.0f})")
        if profit >= 60:
            reason_parts.append(f"高利润地位({profit:.0f})")
        if supply_demand >= 60:
            reason_parts.append(f"供需失衡机会({supply_demand:.0f})")

        reason = "、".join(reason_parts) if reason_parts else "综合评分"

        return StockEvaluation(
            code=re.sub(r'[^0-9]', '', stock.get("code", "")),
            name=stock.get("name", ""),
            node_name=stock.get("node_name", ""),
            category=stock.get("category", ""),
            level=stock.get("level", ""),
            barrier_score=barrier,
            growth_score=growth,
            profit_score=profit,
            supply_demand_score=supply_demand,
            total_score=total_score,
            quote=quote,
            reason=reason,
        )

    # ============= 主流程 =============

    def run_screening(self, top_n: int = 20) -> List[StockEvaluation]:
        """执行选股主流程"""
        print("="*80)
        print("🏭 BOM产业链拆解 + 三高环节筛选引擎")
        print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Step 1: 获取所有候选股票
        print("\n📋 Step 1: 加载BOM产业链知识库...")
        candidate_stocks = self.stocks_data
        unique_stocks = {}
        for s in candidate_stocks:
            code = re.sub(r'[^0-9]', '', s.get("code", ""))
            if code and code not in unique_stocks:
                unique_stocks[code] = s
            elif code:
                # 取最高分的记录
                existing_score = unique_stocks[code].get("barrier_score", 0)
                new_score = s.get("barrier_score", 0)
                if new_score > existing_score:
                    unique_stocks[code] = s

        print(f"   → 共 {len(unique_stocks)} 只候选股票")

        # Step 2: 获取实时行情
        print("\n📈 Step 2: 获取实时行情数据...")
        codes = list(unique_stocks.keys())
        quotes = self.fetch_real_time_quotes(codes)
        print(f"   → 成功获取 {len(quotes)} 只股票行情")

        # Step 3: 四维度评估
        print("\n🔍 Step 3: 四维度综合评估 (高壁垒×高增长×高利润×供需失衡)...")
        evaluations = []
        for code, stock in unique_stocks.items():
            quote = quotes.get(code, {})
            eval_result = self.evaluate_stock(stock, quote)
            evaluations.append(eval_result)

        # Step 4: 按总分排序
        evaluations.sort(key=lambda x: x.total_score, reverse=True)

        # Step 5: 输出结果
        self.print_results(evaluations[:top_n])

        return evaluations[:top_n]

    # ============= 输出 =============

    def print_results(self, results: List[StockEvaluation]):
        """打印选股结果"""
        print("\n" + "="*80)
        print(f"🏆 三高环节选股 TOP {len(results)}")
        print("="*80)

        header = f"{'排名':<6}{'股票':<12}{'代码':<10}{'环节':<14}{'行业':<10}{'层级':<8}{'壁垒':<6}{'增长':<6}{'利润':<6}{'供需':<6}{'总分':<6}{'现价':<8}{'涨跌幅':<10}"
        print(header)
        print("-" * 120)

        for i, r in enumerate(results, 1):
            price = r.quote.get('price', 0)
            change = r.quote.get('change_pct', 0)
            line = f"{i:<6}{r.name:<12}{r.code:<10}{r.node_name:<14}{r.category:<10}{r.level:<8}{r.barrier_score:<6.0f}{r.growth_score:<6.0f}{r.profit_score:<6.0f}{r.supply_demand_score:<6.0f}{r.total_score:<6.0f}{price:<8.2f}{change:>+.2f}%"
            print(line)

        print("-" * 120)

        # 详细分析TOP 5
        print("\n\n📊 详细分析 TOP 5:")
        print("-" * 80)
        for i, r in enumerate(results[:5], 1):
            print(f"\n{i}. {r.name}({r.code}) - {r.node_name}")
            print(f"   行业: {r.category} | 层级: {r.level}")
            print(f"   壁垒:{r.barrier_score:.0f} | 增长:{r.growth_score:.0f} | 利润:{r.profit_score:.0f} | 供需:{r.supply_demand_score:.0f} | 总分:{r.total_score:.0f}")
            print(f"   理由: {r.reason}")
            if r.quote:
                print(f"   现价:{r.quote.get('price',0):.2f} | PE(TTM):{r.quote.get('pe_ttm',0):.1f} | 市值:{r.quote.get('mcap_yi',0):.0f}亿")

        print("\n" + "="*80)


def main():
    engine = ThreeHighEngine()
    results = engine.run_screening(top_n=20)
    return results


if __name__ == "__main__":
    main()
