"""
Serenity瓶颈投资 - 回测系统
验证瓶颈投资策略的历史收益率表现

策略类型：
1. 瓶颈选股策略 - 物理四问筛选后的标的等权持有
2. 事件驱动策略 - 基于催化剂事件（订单/认证/产能扩张）
3. 认知差修复策略 - 低关注+高壁垒标的的均值回归

回测维度：
- 年化收益率
- 最大回撤
- 夏普比率
- 胜率
- 盈亏比
"""

import sys
import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.stock_data import get_historical_k_data
    HIST_DATA_AVAILABLE = True
except ImportError:
    HIST_DATA_AVAILABLE = False
    print("[Serenity Backtest] 警告: 历史数据接口不可用")


class BacktestStrategy(Enum):
    """回测策略类型"""
    CHOKEPOINT_EQUAL_WEIGHT = "瓶颈选股等权策略"
    EVENT_DRIVEN = "事件驱动策略"
    COGNITIVE_GAP = "认知差修复策略"


@dataclass
class TradeRecord:
    """交易记录"""
    date: str
    code: str
    name: str
    action: str  # buy/sell
    price: float
    shares: int
    amount: float
    reason: str = ""


@dataclass
class BacktestResult:
    """回测结果"""
    strategy: str
    start_date: str
    end_date: str
    initial_cash: float
    final_cash: float
    total_return: float = 0.0       # 总收益率%
    annual_return: float = 0.0       # 年化收益率%
    max_drawdown: float = 0.0        # 最大回撤%
    sharpe_ratio: float = 0.0        # 夏普比率
    win_rate: float = 0.0            # 胜率%
    profit_loss_ratio: float = 0.0   # 盈亏比
    total_trades: int = 0
    win_trades: int = 0
    loss_trades: int = 0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    equity_curve: List[Dict] = field(default_factory=list)
    trades: List[TradeRecord] = field(default_factory=list)
    benchmark_return: float = 0.0    # 基准收益率%
    excess_return: float = 0.0       # 超额收益%


# ============================================================
# 数据加载器
# ============================================================

class BacktestDataLoader:
    """回测数据加载器"""

    def __init__(self):
        self.cache = {}  # 缓存股票历史数据

    def get_stock_history(self, stock_code: str, days: int = 365) -> pd.DataFrame:
        """
        获取股票历史K线数据

        Args:
            stock_code: 股票代码
            days: 天数

        Returns:
            DataFrame: 历史K线数据
        """
        cache_key = f"{stock_code}_{days}"
        if cache_key in self.cache:
            return self.cache[cache_key].copy()

        if not HIST_DATA_AVAILABLE:
            # 使用模拟数据
            df = self._generate_mock_data(days)
            self.cache[cache_key] = df
            return df

        try:
            df = get_historical_k_data(stock_code, period="daily", days=days)
            if df is None or df.empty:
                df = self._generate_mock_data(days)
            else:
                df = df.copy()
                # 提取日期列（从索引中提取）
                if 'date' not in df.columns:
                    df['date'] = df.index.strftime('%Y-%m-%d')
                df = df.reset_index(drop=True)
                # 统一成交量列名
                if 'volume' not in df.columns and 'vol' in df.columns:
                    df['volume'] = df['vol']

            self.cache[cache_key] = df
            return df
        except Exception as e:
            print(f"[Backtest Data] 获取 {stock_code} 数据失败: {e}")
            df = self._generate_mock_data(days)
            self.cache[cache_key] = df
            return df

    def _generate_mock_data(self, days: int) -> pd.DataFrame:
        """生成模拟数据（用于测试）"""
        np.random.seed(42)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
        base_price = 50 + np.random.rand() * 50

        # 模拟随机漫步+趋势
        returns = np.random.normal(0.001, 0.02, days)
        prices = base_price * (1 + returns).cumprod()

        df = pd.DataFrame({
            'date': dates.strftime('%Y-%m-%d'),
            'open': prices * (1 + np.random.normal(0, 0.01, days)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.015, days))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.015, days))),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days),
            'amount': prices * np.random.randint(1000000, 10000000, days),
        })
        return df

    def get_benchmark(self, days: int = 365) -> pd.DataFrame:
        """获取基准指数数据（沪深300等）"""
        # 简化：使用第一只股票的弱化版本模拟大盘
        return self.get_stock_history("000300", days)


# ============================================================
# 回测引擎
# ============================================================

class SerenityBacktestEngine:
    """
    Serenity瓶颈投资回测引擎

    支持多种瓶颈投资策略的历史回测
    """

    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.data_loader = BacktestDataLoader()

    def run_chokepoint_backtest(
        self,
        stock_pool: List[Dict],
        start_date: str = "",
        end_date: str = "",
        rebalance_freq: str = "monthly",
        position_size: float = 0.1,  # 单只股票仓位10%
    ) -> BacktestResult:
        """
        瓶颈选股等权策略回测

        Args:
            stock_pool: 股票池 [{"code":..., "name":...}]
            start_date: 开始日期
            end_date: 结束日期
            rebalance_freq: 调仓频率
            position_size: 单票仓位

        Returns:
            BacktestResult: 回测结果
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        result = BacktestResult(
            strategy="瓶颈选股等权策略",
            start_date=start_date,
            end_date=end_date,
            initial_cash=self.initial_cash,
            final_cash=self.initial_cash,
        )

        # 加载所有股票数据
        stock_data = {}
        for stock in stock_pool:
            code = stock.get("code", "")
            if not code:
                continue
            try:
                df = self.data_loader.get_stock_history(code, days=180)
                stock_data[code] = {
                    "name": stock.get("name", code),
                    "data": df,
                }
            except Exception as e:
                print(f"[Backtest] 加载 {code} 数据失败: {e}")

        if not stock_data:
            return result

        # 构建权益曲线（等权持有）
        cash = self.initial_cash
        positions = {}  # {code: shares}
        equity_curve = []

        # 获取共同的交易日
        first_stock = list(stock_data.values())[0]
        dates = first_stock["data"]['date'].tolist()

        # 初始建仓
        num_stocks = len(stock_data)
        per_stock_value = cash * position_size if position_size < 1 else cash / num_stocks

        for code, info in stock_data.items():
            df = info["data"]
            if len(df) == 0:
                continue
            first_close = df['close'].iloc[0]
            if first_close > 0:
                shares = int(per_stock_value / first_close / 100) * 100  # 整手
                if shares > 0:
                    positions[code] = shares
                    cost = shares * first_close
                    cash -= cost
                    result.trades.append(TradeRecord(
                        date=dates[0],
                        code=code,
                        name=info["name"],
                        action="buy",
                        price=first_close,
                        shares=shares,
                        amount=cost,
                        reason="初始建仓"
                    ))

        # 每日净值计算
        for i, date in enumerate(dates):
            total_value = cash
            for code, shares in positions.items():
                if code in stock_data:
                    df = stock_data[code]["data"]
                    if i < len(df):
                        price = df['close'].iloc[i]
                        total_value += shares * price

            equity_curve.append({
                "date": date,
                "equity": total_value,
                "return": total_value / self.initial_cash - 1
            })

        result.equity_curve = equity_curve
        result.final_cash = total_value
        result.total_trades = len(result.trades)

        # 计算绩效指标
        self._calculate_metrics(result, equity_curve)

        return result

    def run_event_driven_backtest(
        self,
        stock_pool: List[Dict],
        event_dates: Dict[str, List[str]] = None,
        hold_days: int = 30,
    ) -> BacktestResult:
        """
        事件驱动策略回测

        Args:
            stock_pool: 股票池
            event_dates: 事件日期 {code: [date1, date2]}
            hold_days: 持有天数

        Returns:
            BacktestResult: 回测结果
        """
        result = BacktestResult(
            strategy="事件驱动策略",
            start_date="",
            end_date="",
            initial_cash=self.initial_cash,
            final_cash=self.initial_cash,
        )

        if event_dates is None:
            event_dates = {}

        cash = self.initial_cash
        positions = {}  # {code: {"shares":..., "buy_date":..., "buy_price":...}}
        trades = []
        all_dates = set()

        # 加载数据并模拟事件
        for stock in stock_pool:
            code = stock.get("code", "")
            name = stock.get("name", "")
            if not code:
                continue

            try:
                df = self.data_loader.get_stock_history(code, days=180)
                if df.empty:
                    continue

                dates = df['date'].tolist()
                closes = df['close'].tolist()
                all_dates.update(dates)

                # 如果没有指定事件日期，用"突破20日均线"模拟事件
                stock_events = event_dates.get(code, [])
                if not stock_events:
                    # 计算20日均线
                    df['ma20'] = df['close'].rolling(20).mean()
                    # 找突破点
                    for i in range(20, len(df)):
                        if df['close'].iloc[i] > df['ma20'].iloc[i] and \
                           df['close'].iloc[i-1] <= df['ma20'].iloc[i-1]:
                            stock_events.append(dates[i])

                # 模拟交易
                for event_date in stock_events:
                    # 找事件发生后的交易日
                    if event_date not in dates:
                        continue
                    buy_idx = dates.index(event_date)
                    if buy_idx >= len(dates) - 1:
                        continue

                    buy_price = closes[buy_idx + 1]  # 次日开盘价简化为收盘价
                    sell_idx = min(buy_idx + hold_days, len(dates) - 1)
                    sell_price = closes[sell_idx]

                    # 计算仓位（每只股票10%资金）
                    position_value = cash * 0.1
                    shares = int(position_value / buy_price / 100) * 100
                    if shares <= 0:
                        continue

                    buy_amount = shares * buy_price
                    sell_amount = shares * sell_price
                    profit = sell_amount - buy_amount

                    cash += profit  # 简化：只算盈亏

                    trades.append(TradeRecord(
                        date=dates[buy_idx],
                        code=code,
                        name=name,
                        action="buy",
                        price=buy_price,
                        shares=shares,
                        amount=buy_amount,
                        reason=f"事件驱动买入"
                    ))
                    trades.append(TradeRecord(
                        date=dates[sell_idx],
                        code=code,
                        name=name,
                        action="sell",
                        price=sell_price,
                        shares=shares,
                        amount=sell_amount,
                        reason=f"持有{hold_days}天卖出"
                    ))

                    # 更新统计
                    result.total_trades += 1
                    profit_pct = (sell_price / buy_price - 1) * 100
                    if profit_pct > 0:
                        result.win_trades += 1
                    else:
                        result.loss_trades += 1

            except Exception as e:
                print(f"[Backtest] 事件策略回测 {code} 失败: {e}")

        result.trades = trades
        result.final_cash = cash
        result.win_rate = (result.win_trades / result.total_trades * 100) if result.total_trades > 0 else 0
        result.total_return = (cash / self.initial_cash - 1) * 100

        return result

    def _calculate_metrics(self, result: BacktestResult, equity_curve: List[Dict]):
        """计算绩效指标"""
        if not equity_curve:
            return

        equities = [e["equity"] for e in equity_curve]
        returns = [e["return"] for e in equity_curve]

        # 总收益率
        result.total_return = (equities[-1] / self.initial_cash - 1) * 100

        # 年化收益率（按250个交易日计算）
        num_days = len(equities)
        if num_days > 0:
            annual_factor = 250 / num_days
            result.annual_return = ((1 + result.total_return / 100) ** annual_factor - 1) * 100

        # 最大回撤
        peak = equities[0]
        max_dd = 0
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd
        result.max_drawdown = max_dd

        # 夏普比率（简化：无风险利率按3%算）
        if len(returns) > 1:
            daily_returns = pd.Series(equities).pct_change().dropna()
            if len(daily_returns) > 0 and daily_returns.std() > 0:
                risk_free_daily = 0.03 / 250
                excess = daily_returns - risk_free_daily
                result.sharpe_ratio = (excess.mean() / daily_returns.std()) * np.sqrt(250)

    def compare_strategies(
        self,
        stock_pool: List[Dict],
    ) -> Dict[str, BacktestResult]:
        """
        对比多种策略

        Args:
            stock_pool: 股票池

        Returns:
            Dict: {策略名: 回测结果}
        """
        results = {}

        # 策略1：等权持有
        r1 = self.run_chokepoint_backtest(stock_pool)
        results["瓶颈选股等权策略"] = r1

        # 策略2：事件驱动
        r2 = self.run_event_driven_backtest(stock_pool)
        results["事件驱动策略"] = r2

        return results

    def generate_report(self, result: BacktestResult) -> str:
        """生成回测报告"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"Serenity瓶颈投资回测报告")
        lines.append("=" * 60)
        lines.append(f"策略名称: {result.strategy}")
        lines.append(f"回测区间: {result.start_date} ~ {result.end_date}")
        lines.append(f"初始资金: {result.initial_cash:,.2f}")
        lines.append(f"最终资金: {result.final_cash:,.2f}")
        lines.append("")
        lines.append("【收益指标】")
        lines.append(f"  总收益率: {result.total_return:.2f}%")
        lines.append(f"  年化收益: {result.annual_return:.2f}%")
        lines.append(f"  超额收益: {result.excess_return:.2f}%")
        lines.append("")
        lines.append("【风险指标】")
        lines.append(f"  最大回撤: {result.max_drawdown:.2f}%")
        lines.append(f"  夏普比率: {result.sharpe_ratio:.2f}")
        lines.append("")
        lines.append("【交易指标】")
        lines.append(f"  总交易次数: {result.total_trades}")
        lines.append(f"  胜率: {result.win_rate:.2f}%")
        lines.append(f"  盈利交易: {result.win_trades}")
        lines.append(f"  亏损交易: {result.loss_trades}")
        if result.profit_loss_ratio > 0:
            lines.append(f"  盈亏比: {result.profit_loss_ratio:.2f}")
        lines.append("")
        return "\n".join(lines)


# ============================================================
# 便捷函数
# ============================================================

_backtest_engine_instance = None


def get_backtest_engine(initial_cash: float = 1000000) -> SerenityBacktestEngine:
    """获取回测引擎单例"""
    global _backtest_engine_instance
    if _backtest_engine_instance is None:
        _backtest_engine_instance = SerenityBacktestEngine(initial_cash)
    return _backtest_engine_instance


def run_backtest(stock_pool: List[Dict], strategy: str = "equal_weight") -> BacktestResult:
    """便捷函数：运行回测"""
    engine = get_backtest_engine()
    if strategy == "equal_weight":
        return engine.run_chokepoint_backtest(stock_pool)
    elif strategy == "event_driven":
        return engine.run_event_driven_backtest(stock_pool)
    else:
        return engine.run_chokepoint_backtest(stock_pool)


# ============================================================
# 测试
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Serenity回测系统测试")
    print("=" * 60)
    print()

    # 测试股票池
    test_pool = [
        {"code": "688126", "name": "沪硅产业"},
        {"code": "603650", "name": "彤程新材"},
        {"code": "600584", "name": "长电科技"},
    ]

    engine = SerenityBacktestEngine(initial_cash=1000000)

    # 测试等权策略
    print("【策略1：瓶颈选股等权策略】")
    r1 = engine.run_chokepoint_backtest(test_pool)
    print(engine.generate_report(r1))

    # 测试事件驱动策略
    print("【策略2：事件驱动策略】")
    r2 = engine.run_event_driven_backtest(test_pool)
    print(engine.generate_report(r2))

    print("回测测试完成！")
