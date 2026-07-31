"""
隔夜持股法策略回测
回测时间：近6个月历史数据
回测逻辑：14:50买入 → 次日涨3%卖/跌3%止损
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a_stock_data_core import get_stock_quote, get_historical_k_data


class NightHoldBacktest:
    """隔夜持股法回测引擎"""
    
    def __init__(self, initial_cash=20000.0, start_date=None, end_date=None):
        self.initial_cash = initial_cash
        self.start_date = start_date or (datetime.now() - timedelta(days=180)).strftime('%Y%m%d')
        self.end_date = end_date or datetime.now().strftime('%Y%m%d')
        
        self.cash = initial_cash
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        
        self.stats = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'total_profit': 0,
            'win_rate': 0,
            'avg_profit': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
        }
    
    def check_buy_conditions(self, hist_data, current_idx):
        """
        检查是否符合买入条件
        使用前一日的数据作为信号
        """
        if current_idx < 25:
            return False, 0, []
        
        prev_day = hist_data.iloc[current_idx - 1]
        prev_2day = hist_data.iloc[current_idx - 2]
        
        change_pct = prev_day['change_pct']
        vol_ratio = prev_day.get('vol_ratio', 1.0)
        turnover = prev_day.get('turnover_pct', 0)
        
        conditions = []
        passed = True
        score = 0
        
        if not (3.0 <= change_pct <= 8.0):
            passed = False
            conditions.append(f"涨幅{change_pct:.2f}%不在(3-8%)")
        else:
            if 3.0 <= change_pct <= 5.0:
                score += 30
                conditions.append("涨幅3-5%最佳")
            elif 5.0 < change_pct <= 8.0:
                score += 25
                conditions.append("涨幅5-8%良好")
        
        if vol_ratio < 1.5:
            passed = False
            conditions.append(f"量比{vol_ratio:.2f}<1.5")
        else:
            if vol_ratio >= 2.0:
                score += 20
                conditions.append(f"量比{vol_ratio:.2f}优秀")
            else:
                score += 15
                conditions.append(f"量比{vol_ratio:.2f}良好")
        
        if turnover < 2.0:
            passed = False
            conditions.append(f"换手率{turnover:.2f}%<2%")
        else:
            score += 10
            conditions.append(f"换手率{turnover:.2f}%良好")
        
        if current_idx < 20:
            passed = False
            conditions.append("历史数据不足")
        else:
            ma5 = hist_data['close'].rolling(5).mean().iloc[current_idx - 1]
            ma10 = hist_data['close'].rolling(10).mean().iloc[current_idx - 1]
            ma20 = hist_data['close'].rolling(20).mean().iloc[current_idx - 1]
            prev_close = prev_day['close']
            
            if not (ma5 > ma10 > ma20):
                passed = False
                conditions.append("均线未多头排列")
            else:
                score += 30
                conditions.append("均线完美多头")
            
            boll_mid = ma20
            boll_std = hist_data['close'].rolling(20).std().iloc[current_idx - 1]
            boll_upper = boll_mid + 2 * boll_std
            boll_lower = boll_mid - 2 * boll_std
            
            if prev_close < boll_lower:
                passed = False
                conditions.append("价格在布林下轨以下")
            elif prev_close > boll_upper:
                passed = False
                conditions.append("价格接近布林上轨")
            elif prev_close > boll_mid:
                score += 20
                conditions.append("价格在布林中轨上方")
        
        return passed, score, conditions
    
    def simulate_trade(self, code, name, buy_date, buy_price, sell_date, sell_price):
        """模拟单笔交易"""
        shares = 100  # 固定100股
        buy_cost = buy_price * shares
        sell_value = sell_price * shares
        
        commission_buy = buy_cost * 0.0003
        commission_sell = sell_value * 0.0013
        
        net_profit = sell_value - buy_cost - commission_buy - commission_sell
        profit_pct = net_profit / (buy_cost) * 100
        
        trade = {
            'code': code,
            'name': name,
            'buy_date': buy_date,
            'sell_date': sell_date,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'shares': shares,
            'profit': net_profit,
            'profit_pct': profit_pct,
            'commission': commission_buy + commission_sell,
        }
        
        self.trades.append(trade)
        return trade
    
    def run_backtest_stock(self, code, name):
        """对单只股票进行回测"""
        try:
            hist = get_historical_k_data(code, 'daily', 250)
            if hist is None or len(hist) < 30:
                return []
            
            hist['change_pct'] = hist['close'].pct_change() * 100
            hist['vol_ratio'] = hist['volume'] / hist['volume'].rolling(5).mean()
            hist['turnover_pct'] = hist.get('turnover', 0)
            
            stock_trades = []
            
            for i in range(25, len(hist) - 1):
                signal_date = hist.index[i]
                buy_price = hist.iloc[i]['close']
                
                passed, score, reasons = self.check_buy_conditions(hist, i)
                
                if passed and score >= 70:
                    sell_date = hist.index[i + 1]
                    sell_price = hist.iloc[i + 1]['close']
                    
                    sell_type = '次日收盘卖出'
                    profit_pct = (sell_price - buy_price) / buy_price * 100
                    
                    if sell_price >= buy_price * 1.03:
                        sell_type = '次日涨3%止盈'
                        sell_price = buy_price * 1.03
                    elif sell_price <= buy_price * 0.97:
                        sell_type = '次日跌3%止损'
                        sell_price = buy_price * 0.97
                    else:
                        sell_price = sell_price
                    
                    profit_pct = (sell_price - buy_price) / buy_price * 100
                    
                    trade = {
                        'code': code,
                        'name': name,
                        'signal_date': signal_date,
                        'buy_date': buy_date,
                        'sell_date': sell_date,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct,
                        'sell_type': sell_type,
                        'score': score,
                        'reasons': ', '.join(reasons[:3]),
                    }
                    stock_trades.append(trade)
            
            return stock_trades
            
        except Exception as e:
            print(f"回测 {name}({code}) 时出错: {e}")
            return []
    
    def run_backtest(self, stock_pool):
        """对股票池进行回测"""
        print("="*70)
        print("隔夜持股法策略回测")
        print("="*70)
        print(f"回测时间：{self.start_date} 至 {self.end_date}")
        print(f"初始资金：{self.initial_cash:.2f}元")
        print(f"测试股票：{len(stock_pool)}只")
        print("="*70)
        
        all_trades = []
        
        for i, (code, name) in enumerate(stock_pool, 1):
            print(f"\n回测中 {name}({code})... [{i}/{len(stock_pool)}]")
            trades = self.run_backtest_stock(code, name)
            all_trades.extend(trades)
            if trades:
                print(f"  找到 {len(trades)} 个交易信号")
        
        self.trades = all_trades
        
        self.calculate_statistics()
        
        return all_trades
    
    def calculate_statistics(self):
        """计算统计指标"""
        if not self.trades:
            print("\n没有找到任何符合条件的交易！")
            return
        
        df = pd.DataFrame(self.trades)
        
        total_trades = len(df)
        wins = df[df['profit_pct'] > 0]
        losses = df[df['profit_pct'] <= 0]
        
        win_rate = len(wins) / total_trades * 100
        total_profit = df['profit_pct'].sum()
        avg_profit = wins['profit_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['profit_pct'].mean() if len(losses) > 0 else 0
        
        total_profit_ratio = df[df['profit_pct'] > 0]['profit_pct'].sum()
        total_loss_ratio = abs(df[df['profit_pct'] < 0]['profit_pct'].sum())
        profit_factor = total_profit_ratio / total_loss_ratio if total_loss_ratio > 0 else float('inf')
        
        self.stats = {
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'total_profit': total_profit,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
        }
        
        self.print_results(df)
    
    def print_results(self, df):
        """打印回测结果"""
        print("\n" + "="*70)
        print("回测结果统计")
        print("="*70)
        
        print(f"\n📊 基础统计：")
        print(f"  总交易次数：{self.stats['total_trades']} 次")
        print(f"  盈利次数：{self.stats['wins']} 次")
        print(f"  亏损次数：{self.stats['losses']} 次")
        print(f"  胜率：{self.stats['win_rate']:.2f}%")
        
        print(f"\n💰 收益统计：")
        print(f"  总收益率：{self.stats['total_profit']:.2f}%")
        print(f"  平均盈利：{self.stats['avg_profit']:.2f}%")
        print(f"  平均亏损：{self.stats['avg_loss']:.2f}%")
        print(f"  盈亏比：{abs(self.stats['avg_profit']/self.stats['avg_loss']) if self.stats['avg_loss'] != 0 else '∞':.2f}")
        
        if self.stats['profit_factor'] != float('inf'):
            print(f"  利润因子：{self.stats['profit_factor']:.2f}")
        else:
            print(f"  利润因子：∞（无亏损）")
        
        print(f"\n📈 卖出原因分析：")
        sell_types = df['sell_type'].value_counts()
        for sell_type, count in sell_types.items():
            pct = count / len(df) * 100
            print(f"  {sell_type}：{count}次 ({pct:.1f}%)")
        
        print(f"\n🏆 最成功的交易（Top 5）：")
        top5 = df.nlargest(5, 'profit_pct')
        for i, row in top5.iterrows():
            print(f"  {row['name']}({row['code']})：{row['profit_pct']:+.2f}% | {row['signal_date']}")
        
        print(f"\n💔 最失败的交易（Top 5）：")
        bottom5 = df.nsmallest(5, 'profit_pct')
        for i, row in bottom5.iterrows():
            print(f"  {row['name']}({row['code']})：{row['profit_pct']:+.2f}% | {row['signal_date']}")
        
        print("\n" + "="*70)
        
        print("\n📋 详细交易记录（前20条）：")
        print("-"*70)
        for i, row in df.head(20).iterrows():
            print(f"{row['signal_date']} | {row['name']:8s} | 买:{row['buy_price']:8.2f} | "
                  f"卖:{row['sell_price']:8.2f} | {row['profit_pct']:+6.2f}% | {row['sell_type']}")
        
        print("\n" + "="*70)
    
    def generate_report(self, output_file='backtest_report.md'):
        """生成Markdown格式的回测报告"""
        df = pd.DataFrame(self.trades)
        
        report = f"""# 隔夜持股法策略回测报告

**回测日期**：{datetime.now().strftime('%Y-%m-%d %H:%M')}  
**回测周期**：{self.start_date} 至 {self.end_date}  
**初始资金**：{self.initial_cash:.2f}元

---

## 一、回测参数

### 交易规则
- **买入时间**：T日收盘（模拟14:50买入）
- **卖出条件**：
  - T+1日涨3% → 止盈卖出
  - T+1日跌3% → 止损卖出
  - 其他情况 → T+1日收盘卖出

### 选股条件
- 当日涨幅：3% - 8%
- 量比：≥ 1.5
- 换手率：≥ 2%
- 均线多头排列：MA5 > MA10 > MA20
- 价格在布林带中轨上方

---

## 二、回测结果

### 2.1 整体表现

| 指标 | 数值 |
|------|------|
| 总交易次数 | {self.stats['total_trades']} |
| 盈利次数 | {self.stats['wins']} |
| 亏损次数 | {self.stats['losses']} |
| **胜率** | **{self.stats['win_rate']:.2f}%** |
| 总收益率 | {self.stats['total_profit']:.2f}% |
| 平均盈利 | {self.stats['avg_profit']:.2f}% |
| 平均亏损 | {self.stats['avg_loss']:.2f}% |
| 盈亏比 | {abs(self.stats['avg_profit']/self.stats['avg_loss']) if self.stats['avg_loss'] != 0 else '∞':.2f} |

### 2.2 卖出原因分析

"""
        
        if len(df) > 0:
            sell_types = df['sell_type'].value_counts()
            for sell_type, count in sell_types.items():
                pct = count / len(df) * 100
                report += f"- **{sell_type}**：{count}次 ({pct:.1f}%)\n"
        
        report += f"""

### 2.3 最佳交易（Top 10）

| 日期 | 股票 | 买入价 | 卖出价 | 收益率 | 卖出原因 |
|------|------|--------|--------|--------|----------|
"""
        
        if len(df) > 0:
            top10 = df.nlargest(10, 'profit_pct')
            for i, row in top10.iterrows():
                report += f"| {row['signal_date']} | {row['name']}({row['code']}) | {row['buy_price']:.2f} | {row['sell_price']:.2f} | {row['profit_pct']:+.2f}% | {row['sell_type']} |\n"
        
        report += f"""

### 2.4 最差交易（Top 10）

| 日期 | 股票 | 买入价 | 卖出价 | 收益率 | 卖出原因 |
|------|------|--------|--------|--------|----------|
"""
        
        if len(df) > 0:
            bottom10 = df.nsmallest(10, 'profit_pct')
            for i, row in bottom10.iterrows():
                report += f"| {row['signal_date']} | {row['name']}({row['code']}) | {row['buy_price']:.2f} | {row['sell_price']:.2f} | {row['profit_pct']:+.2f}% | {row['sell_type']} |\n"
        
        report += f"""

---

## 三、策略评估

### 3.1 胜率分析

当前胜率：{self.stats['win_rate']:.2f}%

"""
        
        if self.stats['win_rate'] >= 55:
            report += "✅ **评估**：胜率达标（≥55%），策略具备盈利基础。\n\n"
        elif self.stats['win_rate'] >= 50:
            report += "⚠️ **评估**：胜率一般（50-55%），需要优化选股条件。\n\n"
        else:
            report += "❌ **评估**：胜率不足（<50%），策略需要重大改进。\n\n"
        
        report += f"""### 3.2 盈亏比分析

- 平均盈利：{self.stats['avg_profit']:.2f}%
- 平均亏损：{self.stats['avg_loss']:.2f}%
- 盈亏比：{abs(self.stats['avg_profit']/self.stats['avg_loss']) if self.stats['avg_loss'] != 0 else '∞':.2f}

"""
        
        if self.stats['avg_profit'] > abs(self.stats['avg_loss']):
            report += "✅ **评估**：盈亏比优秀，赚钱时赚得多，亏钱时亏得少。\n\n"
        else:
            report += "⚠️ **评估**：盈亏比不佳，需要优化止盈止损位。\n\n"
        
        report += f"""### 3.3 综合评分

根据回测结果，对策略进行综合评分：

| 维度 | 评分 | 说明 |
|------|------|------|
| 胜率 | {'⭐⭐⭐⭐⭐' if self.stats['win_rate'] >= 60 else '⭐⭐⭐⭐' if self.stats['win_rate'] >= 50 else '⭐⭐⭐'} | {'优秀' if self.stats['win_rate'] >= 60 else '良好' if self.stats['win_rate'] >= 50 else '一般'} |
| 盈亏比 | {'⭐⭐⭐⭐⭐' if self.stats['avg_profit'] > abs(self.stats['avg_loss']) * 1.2 else '⭐⭐⭐⭐' if self.stats['avg_profit'] > abs(self.stats['avg_loss']) else '⭐⭐⭐'} | {'优秀' if self.stats['avg_profit'] > abs(self.stats['avg_loss']) * 1.2 else '良好' if self.stats['avg_profit'] > abs(self.stats['avg_loss']) else '一般'} |
| 总收益 | {'⭐⭐⭐⭐⭐' if self.stats['total_profit'] > 30 else '⭐⭐⭐⭐' if self.stats['total_profit'] > 15 else '⭐⭐⭐'} | {'优秀' if self.stats['total_profit'] > 30 else '良好' if self.stats['total_profit'] > 15 else '一般'} |
| 风险控制 | ⭐⭐⭐⭐⭐ | 固定3%止损，纪律性强 |

---

## 四、投资建议

### 4.1 当前策略表现

"""
        
        if self.stats['win_rate'] >= 55 and self.stats['total_profit'] > 0:
            report += "✅ **可以执行**：策略回测表现良好，具备实盘价值。\n\n"
        elif self.stats['win_rate'] >= 50 and self.stats['total_profit'] > 0:
            report += "⚠️ **谨慎执行**：策略有一定效果，但需要进一步优化。\n\n"
        else:
            report += "❌ **不建议执行**：回测结果不理想，建议优化策略后再考虑。\n\n"
        
        report += f"""### 4.2 优化建议

1. **提高选股门槛**：增加基本面筛选（市盈率、业绩增长等）
2. **结合大盘环境**：在大盘上涨趋势时执行，胜率更高
3. **精选板块**：聚焦当前热门主线，避免追冷门股
4. **动态止盈**：可以根据市场热度调整止盈位（3-5%）
5. **仓位管理**：单次仓位不超过20%，分散风险

### 4.3 风险提示

- 回测结果不代表未来收益
- 实际交易中需考虑滑点、流动性等因素
- 建议先用模拟盘验证1-2个月
- 严格执行止损纪律

---

## 五、详细交易记录

"""
        
        report += "| 日期 | 股票代码 | 股票名称 | 买入价 | 卖出价 | 收益率 | 卖出原因 | 评分 |\n"
        report += "|------|----------|----------|--------|--------|--------|----------|------|\n"
        
        for i, row in df.iterrows():
            report += f"| {row['signal_date']} | {row['code']} | {row['name']} | {row['buy_price']:.2f} | {row['sell_price']:.2f} | {row['profit_pct']:+.2f}% | {row['sell_type']} | {row.get('score', 'N/A')} |\n"
        
        report += f"""

---

**免责声明**：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。

"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 回测报告已生成：{output_file}")
        
        return report


if __name__ == "__main__":
    print("隔夜持股法策略回测系统")
    print("="*70)
    
    stock_pool = [
        ('600584', '长电科技'),
        ('002371', '北方华创'),
        ('688012', '中微公司'),
        ('300750', '宁德时代'),
        ('002594', '比亚迪'),
        ('000858', '五粮液'),
        ('600519', '贵州茅台'),
        ('600036', '招商银行'),
        ('000001', '平安银行'),
        ('300041', '回天新材'),
        ('002415', '海康威视'),
    ]
    
    backtest = NightHoldBacktest(
        initial_cash=20000.0,
        start_date='2025-05-01',
        end_date='2026-05-26'
    )
    
    trades = backtest.run_backtest(stock_pool)
    
    if trades:
        report_file = f"reports/隔夜持股法回测报告_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        backtest.generate_report(report_file)
    
    print("\n回测完成！")
