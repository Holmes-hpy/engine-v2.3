"""
Serenity瓶颈投资 - 真实数据接入模块
整合A股数据核心模块，为瓶颈分析提供真实市场数据

数据类型：
1. 行情数据（实时行情、历史K线）
2. 基本面数据（财报、估值、财务指标）
3. 资金面数据（北向资金、龙虎榜、融资融券）
4. 研报与新闻数据
5. 行业板块数据
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pandas as pd

# 导入核心数据模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.stock_data import (
        get_stock_quote,
        get_historical_k_data,
        get_stock_basic_info,
        get_quarterly_report,
        get_research_reports,
        get_stock_news,
        baidu_concept_blocks,
        get_dragon_tiger_board,
        get_northbound_flow,
        margin_trading_detail,
        block_trade,
        shareholder_count,
        dividend_history,
        industry_comparison,
        cninfo_announcements,
    )
    CORE_MODULE_AVAILABLE = True
except ImportError:
    CORE_MODULE_AVAILABLE = False
    print("[Serenity Data] 警告: 核心数据模块不可用，将使用模拟数据")


# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class StockQuoteData:
    """股票行情数据"""
    code: str
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    change_amt: float = 0.0
    volume: float = 0.0
    turnover_pct: float = 0.0
    pe_ttm: float = 0.0
    pb: float = 0.0
    mcap_yi: float = 0.0           # 总市值(亿)
    float_mcap_yi: float = 0.0      # 流通市值(亿)
    high: float = 0.0
    low: float = 0.0
    open_price: float = 0.0
    last_close: float = 0.0
    vol_ratio: float = 0.0
    limit_up: float = 0.0
    limit_down: float = 0.0

@dataclass
class StockFinancialData:
    """股票财务数据"""
    code: str
    revenue: float = 0.0            # 营业收入
    net_profit: float = 0.0          # 净利润
    gross_margin: float = 0.0        # 毛利率
    net_margin: float = 0.0          # 净利率
    roe: float = 0.0                 # ROE
    revenue_growth: float = 0.0      # 营收增速
    profit_growth: float = 0.0       # 净利润增速
    pe_ttm: float = 0.0
    pb: float = 0.0
    eps: float = 0.0

@dataclass
class StockFundFlowData:
    """资金流向数据"""
    code: str
    northbound_holding_pct: float = 0.0   # 北向持仓占比
    fund_holding_pct: float = 0.0         # 公募持仓占比
    total_institutional_pct: float = 0.0  # 机构合计持仓
    margin_balance: float = 0.0           # 融资余额
    recent_inflow: float = 0.0            # 近期资金流入

@dataclass
class ResearchReportData:
    """研报数据"""
    code: str
    report_count_3m: int = 0         # 近3月研报数量
    covered_brokers: int = 0          # 覆盖券商数量
    avg_rating: str = ""              # 平均评级
    target_price_avg: float = 0.0     # 平均目标价
    recent_reports: List = field(default_factory=list)

@dataclass
class ChokepointStockData:
    """瓶颈标的完整数据"""
    code: str
    name: str = ""
    quote: Optional[StockQuoteData] = None
    financial: Optional[StockFinancialData] = None
    fund_flow: Optional[StockFundFlowData] = None
    research: Optional[ResearchReportData] = None
    news: List = field(default_factory=list)
    announcements: List = field(default_factory=list)

    # 分析指标
    evidence_level: str = "待评估"     # 证据等级：强/中/弱
    market_neglect_score: float = 0.0  # 市场忽视度评分(0-100)
    supply_rigidity_score: float = 0.0 # 供给刚性评分(0-100)
    overall_score: float = 0.0         # 综合评分


# ============================================================
# 数据获取器
# ============================================================

class SerenityDataFetcher:
    """
    Serenity瓶颈投资数据获取器

    整合多种数据源，为瓶颈分析提供完整的标的数据
    """

    def __init__(self):
        self.cache = {}
        self.cache_expiry = 300  # 缓存有效期5分钟

    def get_stock_full_data(self, stock_code: str) -> ChokepointStockData:
        """
        获取标的完整数据

        Args:
            stock_code: 股票代码

        Returns:
            ChokepointStockData: 完整的标的数据
        """
        result = ChokepointStockData(code=stock_code)

        if not CORE_MODULE_AVAILABLE:
            self._fill_mock_data(result)
            return result

        try:
            # 1. 行情数据
            result.quote = self._get_quote_data(stock_code)
            if result.quote:
                result.name = result.quote.name

            # 2. 财务数据
            result.financial = self._get_financial_data(stock_code)

            # 3. 资金流向
            result.fund_flow = self._get_fund_flow_data(stock_code)

            # 4. 研报数据
            result.research = self._get_research_data(stock_code)

            # 5. 新闻数据
            result.news = self._get_news_data(stock_code)

            # 6. 公告数据
            result.announcements = self._get_announcements(stock_code)

        except Exception as e:
            print(f"[Serenity Data] 获取 {stock_code} 数据时出错: {e}")

        # 计算分析指标
        self._calculate_analysis_scores(result)

        return result

    def _get_quote_data(self, code: str) -> Optional[StockQuoteData]:
        """获取行情数据"""
        try:
            quote_dict = get_stock_quote(code)
            if not quote_dict or code not in quote_dict:
                return None
            q = quote_dict[code]
            return StockQuoteData(
                code=code,
                name=q.get("name", ""),
                price=q.get("price", 0),
                change_pct=q.get("change_pct", 0),
                change_amt=q.get("change_amt", 0),
                turnover_pct=q.get("turnover_pct", 0),
                pe_ttm=q.get("pe_ttm", 0),
                pb=q.get("pb", 0),
                mcap_yi=q.get("mcap_yi", 0),
                float_mcap_yi=q.get("float_mcap_yi", 0),
                high=q.get("high", 0),
                low=q.get("low", 0),
                open_price=q.get("open", 0),
                last_close=q.get("last_close", 0),
                vol_ratio=q.get("vol_ratio", 0),
                limit_up=q.get("limit_up", 0),
                limit_down=q.get("limit_down", 0),
            )
        except Exception as e:
            print(f"[Serenity Data] 行情数据获取失败: {e}")
            return None

    def _get_financial_data(self, code: str) -> Optional[StockFinancialData]:
        """获取财务数据"""
        try:
            basic_info = get_stock_basic_info(code)
            if not basic_info:
                return None

            result = StockFinancialData(code=code)
            result.pe_ttm = basic_info.get("pe_ttm", 0)
            result.pb = basic_info.get("pb", 0)

            # 获取季度报告
            try:
                q_reports = get_quarterly_report(code, quarters=4)
                if q_reports is not None and not q_reports.empty:
                    latest = q_reports.iloc[0]
                    result.revenue = float(latest.get("营业收入", 0) or 0) / 100000000
                    result.net_profit = float(latest.get("净利润", 0) or 0) / 100000000
                    result.gross_margin = float(latest.get("毛利率", 0) or 0)
                    result.net_margin = float(latest.get("净利率", 0) or 0)
                    result.revenue_growth = float(latest.get("营业收入同比", 0) or 0)
                    result.profit_growth = float(latest.get("净利润同比", 0) or 0)
            except:
                pass

            return result
        except Exception as e:
            print(f"[Serenity Data] 财务数据获取失败: {e}")
            return None

    def _get_fund_flow_data(self, code: str) -> Optional[StockFundFlowData]:
        """获取资金流向数据"""
        try:
            result = StockFundFlowData(code=code)

            # 股东户数变化
            try:
                sh_data = get_shareholder_count(code)
                if sh_data is not None and not sh_data.empty:
                    pass
            except:
                pass

            # 融资融券
            try:
                from datetime import date
                today = date.today().strftime("%Y-%m-%d")
                margin_data = margin_trading_detail(code, today, days=30)
                if margin_data is not None and not margin_data.empty:
                    pass
            except:
                pass

            return result
        except Exception as e:
            print(f"[Serenity Data] 资金流向数据获取失败: {e}")
            return None

    def _get_research_data(self, code: str) -> Optional[ResearchReportData]:
        """获取研报数据"""
        try:
            reports = get_research_reports(code, days=90)
            if not reports:
                return ResearchReportData(code=code)

            # 统计覆盖券商
            brokers = set()
            for r in reports[:20]:
                broker_name = r.get("research_org_name", "") or r.get("orgName", "")
                if broker_name:
                    brokers.add(broker_name)

            result = ResearchReportData(
                code=code,
                report_count_3m=len(reports),
                covered_brokers=len(brokers),
                recent_reports=reports[:10]
            )

            return result
        except Exception as e:
            print(f"[Serenity Data] 研报数据获取失败: {e}")
            return ResearchReportData(code=code)

    def _get_news_data(self, code: str) -> List:
        """获取新闻数据"""
        try:
            news = get_stock_news(code, days=30)
            return news[:20]
        except Exception as e:
            print(f"[Serenity Data] 新闻数据获取失败: {e}")
            return []

    def _get_announcements(self, code: str) -> List:
        """获取公告数据"""
        try:
            anns = cninfo_announcements(code, days=90)
            return anns[:20]
        except Exception as e:
            print(f"[Serenity Data] 公告数据获取失败: {e}")
            return []

    def _calculate_analysis_scores(self, data: ChokepointStockData):
        """计算分析指标"""
        # 市场忽视度评分
        neglect_score = 50  # 基准分

        if data.quote:
            mcap = data.quote.mcap_yi
            # 市值越小越被忽视
            if mcap < 50:
                neglect_score += 20
            elif mcap < 100:
                neglect_score += 10
            elif mcap > 300:
                neglect_score -= 20

        if data.research:
            # 研报越少越被忽视
            if data.research.report_count_3m <= 5:
                neglect_score += 20
            elif data.research.report_count_3m <= 10:
                neglect_score += 10
            elif data.research.report_count_3m > 20:
                neglect_score -= 15

        data.market_neglect_score = min(100, max(0, neglect_score))

        # 证据等级判断
        data.evidence_level = self._assess_evidence_level(data)

    def _assess_evidence_level(self, data: ChokepointStockData) -> str:
        """评估商业化证据等级"""
        strong_evidence_count = 0
        medium_evidence_count = 0

        # 检查公告中的订单/合作信息
        order_keywords = ["订单", "合同", "合作", "定点", "中标", "签约", "量产"]
        if data.announcements:
            for ann in data.announcements:
                title = str(ann.get("ann_title", "") + ann.get("title", ""))
                if any(kw in title for kw in order_keywords):
                    strong_evidence_count += 1
                    break

        # 检查业绩增长
        if data.financial and data.financial.profit_growth > 30:
            medium_evidence_count += 1
        if data.financial and data.financial.revenue_growth > 20:
            medium_evidence_count += 1

        # 综合判断
        if strong_evidence_count >= 1:
            return "强"
        elif medium_evidence_count >= 2:
            return "中"
        else:
            return "弱"

    def _fill_mock_data(self, data: ChokepointStockData):
        """填充模拟数据（当核心模块不可用时）"""
        data.quote = StockQuoteData(
            code=data.code,
            name="示例标的",
            price=50.0,
            change_pct=2.5,
            mcap_yi=100.0,
            pe_ttm=40.0,
            pb=3.0,
        )
        data.financial = StockFinancialData(
            code=data.code,
            revenue=20.0,
            net_profit=3.0,
            gross_margin=45.0,
            revenue_growth=35.0,
            profit_growth=50.0,
        )
        data.research = ResearchReportData(
            code=data.code,
            report_count_3m=6,
            covered_brokers=4,
        )
        data.evidence_level = "中"
        data.market_neglect_score = 70

    # ============================================================
    # 批量数据获取
    # ============================================================

    def get_stocks_data(self, stock_codes: List[str]) -> Dict[str, ChokepointStockData]:
        """
        批量获取多只股票数据

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict: 股票代码到数据的映射
        """
        result = {}
        for code in stock_codes:
            try:
                result[code] = self.get_stock_full_data(code)
            except Exception as e:
                print(f"[Serenity Data] 获取 {code} 数据失败: {e}")
        return result

    def get_stock_price_change(self, code: str, days: int = 120) -> Dict:
        """
        获取股票历史涨跌幅

        Args:
            code: 股票代码
            days: 天数

        Returns:
            Dict: 各周期涨跌幅
        """
        if not CORE_MODULE_AVAILABLE:
            return {"1m": 10.0, "3m": 25.0, "6m": 40.0, "1y": 60.0}

        try:
            k_data = get_historical_k_data(code, period="daily", days=days)
            if k_data is None or k_data.empty:
                return {}

            closes = k_data["close"].values
            result = {}

            if len(closes) >= 20:
                result["1m"] = (closes[-1] / closes[-20] - 1) * 100
            if len(closes) >= 60:
                result["3m"] = (closes[-1] / closes[-60] - 1) * 100
            if len(closes) >= 120:
                result["6m"] = (closes[-1] / closes[-120] - 1) * 100
            if len(closes) >= 250:
                result["1y"] = (closes[-1] / closes[-250] - 1) * 100

            return result
        except Exception as e:
            print(f"[Serenity Data] 历史涨跌幅计算失败: {e}")
            return {}

    def get_industry_data(self, industry_name: str = "半导体") -> Dict:
        """
        获取行业数据

        Args:
            industry_name: 行业名称

        Returns:
            Dict: 行业数据
        """
        if not CORE_MODULE_AVAILABLE:
            return {"industry": industry_name, "change_pct": 1.5, "top_gainers": []}

        try:
            comp = industry_comparison(top_n=30)
            return comp
        except Exception as e:
            print(f"[Serenity Data] 行业数据获取失败: {e}")
            return {}


# ============================================================
# 便捷函数
# ============================================================

_data_fetcher_instance = None


def get_data_fetcher() -> SerenityDataFetcher:
    """获取数据获取器单例"""
    global _data_fetcher_instance
    if _data_fetcher_instance is None:
        _data_fetcher_instance = SerenityDataFetcher()
    return _data_fetcher_instance


def fetch_stock_data(stock_code: str) -> ChokepointStockData:
    """便捷函数：获取单只股票完整数据"""
    return get_data_fetcher().get_stock_full_data(stock_code)


def fetch_stocks_data(stock_codes: List[str]) -> Dict[str, ChokepointStockData]:
    """便捷函数：批量获取股票数据"""
    return get_data_fetcher().get_stocks_data(stock_codes)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Serenity数据接入模块测试")
    print("=" * 60)
    print()

    fetcher = get_data_fetcher()

    # 测试单只股票
    test_codes = ["688126", "002371"]  # 沪硅产业、北方华创

    for code in test_codes:
        print(f"\n正在获取 {code} 数据...")
        data = fetcher.get_stock_full_data(code)

        print(f"  标的名称: {data.name or '未知'}")
        if data.quote:
            print(f"  当前价格: {data.quote.price}")
            print(f"  总市值: {data.quote.mcap_yi:.2f}亿")
            print(f"  PE(TTM): {data.quote.pe_ttm:.2f}")
        if data.financial:
            print(f"  毛利率: {data.financial.gross_margin:.2f}%")
            print(f"  营收增速: {data.financial.revenue_growth:.2f}%")
        if data.research:
            print(f"  近3月研报数: {data.research.report_count_3m}")
            print(f"  覆盖券商数: {data.research.covered_brokers}")
        print(f"  证据等级: {data.evidence_level}")
        print(f"  市场忽视度: {data.market_neglect_score:.1f}")

    print("\n测试完成！")
