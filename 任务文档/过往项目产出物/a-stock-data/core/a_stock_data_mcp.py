from mcp.server.fastmcp import FastMCP
import json
import sys
import os

from a_stock_data_core import (
    get_stock_quote as core_get_stock_quote,
    get_historical_k_data as core_get_historical_k_data,
    get_stock_basic_info as core_get_stock_basic_info,
    get_quarterly_report as core_get_quarterly_report,
    get_northbound_flow as core_get_northbound_flow,
    get_dragon_tiger_board as core_get_dragon_tiger_board,
    get_stock_news as core_get_stock_news,
    get_research_reports as core_get_research_reports,
    get_industry_comparison as core_get_industry_comparison,
    get_lockup_expiry as core_get_lockup_expiry,
    get_market_index as core_get_market_index,
    ths_hot_reason,
    baidu_concept_blocks,
    eastmoney_fund_flow_minute,
    industry_comparison,
    margin_trading_detail,
    block_trade,
    shareholder_count,
    dividend_history,
    stock_fund_flow_120d,
    cls_flash_news,
    cninfo_announcements,
    sina_financial_statements,
)

mcp = FastMCP("A股数据服务")

@mcp.tool()
def get_stock_quote(stock_code: str) -> str:
    """
    获取股票实时行情数据
    参数:
        stock_code: 股票代码，如 600519 或 000001
    返回:
        包含最新价格、涨跌幅、成交量、PE、PB等信息的JSON字符串
    """
    try:
        result = core_get_stock_quote(stock_code)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取行情失败: {str(e)}"

@mcp.tool()
def get_historical_k_data(stock_code: str, period: str = "daily", days: int = 30) -> str:
    """
    获取股票历史K线数据
    参数:
        stock_code: 股票代码
        period: 周期，可选 daily(日线), weekly(周线), monthly(月线)
        days: 获取最近多少天的数据
    返回:
        包含日期、开盘价、收盘价、最高价、最低价、成交量的JSON字符串
    """
    try:
        result = core_get_historical_k_data(stock_code, period, days)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取K线失败: {str(e)}"

@mcp.tool()
def get_stock_basic_info(stock_code: str) -> str:
    """
    获取股票基本信息
    参数:
        stock_code: 股票代码
    返回:
        包含公司名称、行业、主营业务、上市日期等信息的JSON字符串
    """
    try:
        result = core_get_stock_basic_info(stock_code)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取基本信息失败: {str(e)}"

@mcp.tool()
def get_quarterly_report(stock_code: str, quarters: int = 4) -> str:
    """
    获取股票季度报告数据
    参数:
        stock_code: 股票代码
        quarters: 获取最近几个季度的报告
    返回:
        包含营收、净利润、ROE等财务指标的JSON字符串
    """
    try:
        result = core_get_quarterly_report(stock_code, quarters)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取财报失败: {str(e)}"

@mcp.tool()
def get_northbound_flow() -> str:
    """
    获取北向资金当日流入流出数据
    返回:
        包含沪股通、深股通、北向合计资金流向的JSON字符串
    """
    try:
        result = core_get_northbound_flow()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取北向资金失败: {str(e)}"

@mcp.tool()
def get_dragon_tiger_board(date: str = None) -> str:
    """
    获取龙虎榜数据
    参数:
        date: 日期，格式 YYYY-MM-DD，默认为今日
    返回:
        包含上榜股票、净买入金额、营业部信息的JSON字符串
    """
    try:
        result = core_get_dragon_tiger_board(date)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取龙虎榜失败: {str(e)}"

@mcp.tool()
def get_stock_news(stock_code: str, days: int = 30) -> str:
    """
    获取股票相关新闻
    参数:
        stock_code: 股票代码
        days: 获取最近多少天的新闻
    返回:
        包含新闻标题、发布时间、来源的JSON字符串
    """
    try:
        result = core_get_stock_news(stock_code, days)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取新闻失败: {str(e)}"

@mcp.tool()
def get_research_reports(stock_code: str, days: int = 90) -> str:
    """
    获取股票研报和一致预期
    参数:
        stock_code: 股票代码
        days: 获取最近多少天的研报
    返回:
        包含研报标题、机构、评级、目标价的JSON字符串
    """
    try:
        result = core_get_research_reports(stock_code, days)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取研报失败: {str(e)}"

@mcp.tool()
def get_industry_comparison(stock_codes: list) -> str:
    """
    对比多只股票的估值和财务指标
    参数:
        stock_codes: 股票代码列表，如 ["600519", "000858"]
    返回:
        包含PE、PB、ROE、营收增速等对比数据的JSON字符串
    """
    try:
        result = core_get_industry_comparison(stock_codes)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"行业对比失败: {str(e)}"

@mcp.tool()
def get_lockup_expiry(stock_code: str, months: int = 3) -> str:
    """
    获取股票限售解禁信息
    参数:
        stock_code: 股票代码
        months: 获取未来几个月的解禁信息
    返回:
        包含解禁日期、解禁数量、占总股本比例的JSON字符串
    """
    try:
        result = core_get_lockup_expiry(stock_code, months)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取解禁信息失败: {str(e)}"

@mcp.tool()
def get_market_index() -> str:
    """
    获取大盘指数实时数据
    返回:
        包含上证指数、深证成指、创业板指、科创50的JSON字符串
    """
    try:
        result = core_get_market_index()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取大盘指数失败: {str(e)}"

@mcp.tool()
def get_ths_hot_stocks(date: str = None) -> str:
    """
    获取同花顺热点股票（当日强势股+题材归因）
    参数:
        date: 日期，格式 YYYY-MM-DD，默认为今日
    返回:
        包含股票代码、名称、涨幅、题材归因的JSON字符串
    """
    try:
        import pandas as pd
        result = ths_hot_reason(date)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取热点股票失败: {str(e)}"

@mcp.tool()
def get_stock_concept_blocks(stock_code: str) -> str:
    """
    获取股票概念板块归属
    参数:
        stock_code: 股票代码
    返回:
        包含行业、概念、地域分类的JSON字符串
    """
    try:
        result = baidu_concept_blocks(stock_code)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取概念板块失败: {str(e)}"

@mcp.tool()
def get_stock_fund_flow(stock_code: str) -> str:
    """
    获取个股资金流向（分钟级）
    参数:
        stock_code: 股票代码
    返回:
        包含主力、大单、中单、小单净流入的JSON字符串
    """
    try:
        result = eastmoney_fund_flow_minute(stock_code)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取资金流向失败: {str(e)}"

@mcp.tool()
def get_industry_rankings() -> str:
    """
    获取行业涨跌幅排名
    返回:
        包含涨跌幅排名靠前和靠后的行业JSON字符串
    """
    try:
        result = industry_comparison()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取行业排名失败: {str(e)}"

@mcp.tool()
def get_margin_trading(stock_code: str, days: int = 30) -> str:
    """
    获取融资融券数据
    参数:
        stock_code: 股票代码
        days: 获取最近多少天
    返回:
        包含融资余额、融券余额的JSON字符串
    """
    try:
        import pandas as pd
        from datetime import datetime
        code = ''.join(filter(str.isdigit, stock_code))
        trade_date = datetime.now().strftime("%Y-%m-%d")
        result = margin_trading_detail(code, trade_date, days)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取融资融券失败: {str(e)}"

@mcp.tool()
def get_block_trades(stock_code: str, days: int = 90) -> str:
    """
    获取大宗交易数据
    参数:
        stock_code: 股票代码
        days: 获取最近多少天
    返回:
        包含大宗交易详情的JSON字符串
    """
    try:
        import pandas as pd
        from datetime import datetime
        code = ''.join(filter(str.isdigit, stock_code))
        trade_date = datetime.now().strftime("%Y-%m-%d")
        result = block_trade(code, trade_date, days)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取大宗交易失败: {str(e)}"

@mcp.tool()
def get_shareholder_count(stock_code: str) -> str:
    """
    获取股东户数变化
    参数:
        stock_code: 股票代码
    返回:
        包含股东户数、户均持股变化的JSON字符串
    """
    try:
        import pandas as pd
        code = ''.join(filter(str.isdigit, stock_code))
        result = shareholder_count(code)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取股东户数失败: {str(e)}"

@mcp.tool()
def get_dividend_history(stock_code: str) -> str:
    """
    获取分红送转历史
    参数:
        stock_code: 股票代码
    返回:
        包含历史分红送转详情的JSON字符串
    """
    try:
        import pandas as pd
        code = ''.join(filter(str.isdigit, stock_code))
        result = dividend_history(code)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取分红历史失败: {str(e)}"

@mcp.tool()
def get_fund_flow_120d(stock_code: str) -> str:
    """
    获取个股120日资金流向
    参数:
        stock_code: 股票代码
    返回:
        包含120日主力资金流向的JSON字符串
    """
    try:
        import pandas as pd
        code = ''.join(filter(str.isdigit, stock_code))
        result = stock_fund_flow_120d(code)
        if hasattr(result, 'to_dict'):
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取资金流向失败: {str(e)}"

@mcp.tool()
def get_cls_flash_news() -> str:
    """
    获取财联社快讯
    返回:
        包含最新财经快讯的JSON字符串
    """
    try:
        result = cls_flash_news()
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取快讯失败: {str(e)}"

@mcp.tool()
def get_announcements(stock_code: str, days: int = 30) -> str:
    """
    获取股票公告
    参数:
        stock_code: 股票代码
        days: 获取最近多少天
    返回:
        包含公告列表的JSON字符串
    """
    try:
        code = ''.join(filter(str.isdigit, stock_code))
        result = cninfo_announcements(code, days=days)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"获取公告失败: {str(e)}"

if __name__ == "__main__":
    print("A股数据MCP服务启动中...")
    mcp.run(transport="stdio")
