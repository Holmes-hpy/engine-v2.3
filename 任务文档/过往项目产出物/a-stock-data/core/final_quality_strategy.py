"""
最终优质缠论量化策略 - 只保留最稳健的第二类买点
优化后的策略 - 高胜率、高可靠性
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a_stock_data_core import get_stock_quote, get_historical_k_data


class FinalQualityChanStrategy:
    """最终优质缠论策略 - 只保留第二类买点"""
    
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.data = None
        self.signals = []
    
    def prepare_data(self, days=120):
        """准备完整数据"""
        hist = get_historical_k_data(self.code, 'daily', days)
        if hist is None or len(hist) < 60:
            return False
        
        self.data = hist.copy()
        self.data['change_pct'] = self.data['close'].pct_change() * 100
        
        # 均线系统
        self.data['MA5'] = self.data['close'].rolling(5).mean()
        self.data['MA10'] = self.data['close'].rolling(10).mean()
        self.data['MA20'] = self.data['close'].rolling(20).mean()
        self.data['MA60'] = self.data['close'].rolling(60).mean()
        
        # 布林带
        self.data['BOLL_MID'] = self.data['close'].rolling(20).mean()
        self.data['BOLL_STD'] = self.data['close'].rolling(20).std()
        self.data['BOLL_UPPER'] = self.data['BOLL_MID'] + 2 * self.data['BOLL_STD']
        self.data['BOLL_LOWER'] = self.data['BOLL_MID'] - 2 * self.data['BOLL_STD']
        
        # MACD
        ema12 = self.data['close'].ewm(span=12, adjust=False).mean()
        ema26 = self.data['close'].ewm(span=26, adjust=False).mean()
        self.data['MACD'] = ema12 - ema26
        self.data['MACD_SIGNAL'] = self.data['MACD'].ewm(span=9, adjust=False).mean()
        self.data['MACD_HIST'] = self.data['MACD'] - self.data['MACD_SIGNAL']
        
        # RSI
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # 量比
        self.data['vol_ma5'] = self.data['volume'].rolling(5).mean()
        self.data['vol_ratio'] = self.data['volume'] / self.data['vol_ma5']
        
        return True
    
    def detect_optimized_type2_buy(self):
        """优化的第二类买点检测 - 提高筛选门槛"""
        signals = []
        df = self.data
        
        for i in range(30, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # === 高门槛筛选条件 ===
            
            # 条件1: 完美均线多头（必须全部满足）
            if not (curr['MA5'] > curr['MA10'] and
                    curr['MA10'] > curr['MA20'] and
                    curr['MA20'] > curr['MA60']):
                continue
            
            # 条件2: RSI健康区间（50-70，不超买不超卖）
            if not (50 <= curr['RSI'] <= 70):
                continue
            
            # 条件3: MACD刚金叉或在金叉上方
            if not (prev['MACD'] <= prev['MACD_SIGNAL'] and
                    curr['MACD'] > curr['MACD_SIGNAL'] or
                    curr['MACD'] > curr['MACD_SIGNAL'] > curr['MACD'] * 0.9):
                continue
            
            # 条件4: 价格在布林带中轨上方
            if curr['close'] <= curr['BOLL_MID']:
                continue
            
            # 条件5: 量比健康（1.2-2.5，放量但不异常）
            if not (1.2 <= curr['vol_ratio'] <= 2.5):
                continue
            
            # 条件6: 回调确认（前10天有回调，现在回升）
            recent_low = df.iloc[i-10:i]['low'].min()
            if not (curr['low'] > recent_low * 0.98):
                continue
            
            # 条件7: 近期涨幅适中（避免追高）
            recent_high = df.iloc[i-5:i]['high'].max()
            if curr['close'] > recent_high * 1.08:
                continue
            
            # === 评分系统 ===
            score = 0
            reasons = []
            
            if (curr['MA5'] > curr['MA10'] > curr['MA20'] > curr['MA60']):
                score += 35
                reasons.append("均线完美多头(MA5>MA10>MA20>MA60)")
            
            if (prev['MACD'] <= prev['MACD_SIGNAL'] and curr['MACD'] > curr['MACD_SIGNAL']):
                score += 25
                reasons.append("MACD刚金叉")
            
            if (curr['vol_ratio'] >= 1.5):
                score += 20
                reasons.append("量比放量")
            
            if (55 <= curr['RSI'] <= 65):
                score += 15
                reasons.append("RSI健康")
            
            if (curr['close'] > curr['BOLL_MID'] * 1.01):
                score += 10
                reasons.append("布林带中轨上方")
            
            # === 高门槛：总分必须≥85 ===
            if score >= 85:
                signals.append({
                    'date': df.index[i],
                    'type': '优化第二类买点',
                    'price': curr['close'],
                    'score': score,
                    'reasons': reasons,
                })
        
        return signals
    
    def run_strategy(self):
        """运行优化策略"""
        if not self.prepare_data():
            print(f"❌ {self.name}({self.code}) 获取数据失败")
            return []
        
        signals = self.detect_optimized_type2_buy()
        self.signals = signals
        
        return signals


class FinalStrategyOptimizer:
    """最终策略优化器"""
    
    def __init__(self, initial_cash=20000):
        self.initial_cash = initial_cash
        self.trades = []
    
    def run_final_backtest(self, stock_pool):
        """最终策略回测"""
        print("="*80)
        print("🏆 最终优质缠论策略回测 - 专注第二类买点")
        print("="*80)
        
        all_trades = []
        
        for code, name in stock_pool:
            print(f"\n分析 {name}({code})...")
            strategy = FinalQualityChanStrategy(code, name)
            signals = strategy.run_strategy()
            
            for sig in signals:
                buy_date = sig['date']
                buy_price = sig['price']
                
                idx = strategy.data.index.get_loc(buy_date)
                if idx < len(strategy.data) - 1:
                    next_day = strategy.data.iloc[idx + 1]
                    sell_price = next_day['close']
                    profit_pct = (sell_price - buy_price) / buy_price * 100
                    
                    sell_type = '次日收盘'
                    if sell_price >= buy_price * 1.03:
                        sell_type = '涨3%止盈'
                        sell_price = buy_price * 1.03
                        profit_pct = 3.0
                    elif sell_price <= buy_price * 0.97:
                        sell_type = '跌3%止损'
                        sell_price = buy_price * 0.97
                        profit_pct = -3.0
                    
                    trade = {
                        'date': str(buy_date)[:10],
                        'code': code,
                        'name': name,
                        'type': sig['type'],
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct,
                        'sell_type': sell_type,
                        'score': sig['score'],
                        'reasons': ', '.join(sig['reasons']),
                    }
                    all_trades.append(trade)
            
            print(f"  找到 {len(signals)} 个信号")
        
        self.trades = all_trades
        return self.calculate_results()
    
    def calculate_results(self):
        """计算最终结果"""
        if not self.trades:
            print("\n没有找到任何信号！说明筛选条件很严格，在等待高概率机会。")
            return
        
        df = pd.DataFrame(self.trades)
        
        total_trades = len(df)
        wins = df[df['profit_pct'] > 0]
        losses = df[df['profit_pct'] <= 0]
        
        win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
        total_profit = df['profit_pct'].sum()
        avg_profit = wins['profit_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['profit_pct'].mean() if len(losses) > 0 else 0
        
        print("\n" + "="*80)
        print("【最终回测结果统计】")
        print("="*80)
        
        print(f"\n📊 核心指标：")
        print(f"  总交易次数：{total_trades}")
        print(f"  盈利次数：{len(wins)}")
        print(f"  亏损次数：{len(losses)}")
        print(f"  ✅ 胜率：{win_rate:.2f}%")
        print(f"  💰 总收益率：{total_profit:.2f}%")
        print(f"  📈 平均盈利：{avg_profit:.2f}%")
        print(f"  📉 平均亏损：{avg_loss:.2f}%")
        
        if avg_loss != 0:
            ratio = abs(avg_profit/avg_loss)
            print(f"  ⚖️  盈亏比：{ratio:.2f}")
        
        print(f"\n📋 详细交易记录：")
        for i, row in df.iterrows():
            emoji = "✅" if row['profit_pct'] > 0 else "❌"
            print(f"{emoji} {row['date']} | {row['name']} | 买:{row['buy_price']:.2f} | 卖:{row['sell_price']:.2f} | {row['profit_pct']:+.2f}%")
        
        results = {
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_trades': total_trades,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'trades': self.trades,
        }
        
        return results


def run_final_quality_strategy(stock_pool):
    """运行最终优质策略"""
    print("="*80)
    print("🎯 最终优质缠论策略选股 - 专注高胜率第二类买点")
    print("="*80)
    
    results = []
    
    for code, name in stock_pool:
        print(f"\n分析 {name}({code})...")
        strategy = FinalQualityChanStrategy(code, name)
        signals = strategy.run_strategy()
        
        if signals:
            latest_signal = signals[0]
            print(f"  ✅ 找到信号！评分：{latest_signal['score']}")
            print(f"  理由：{'，'.join(latest_signal['reasons'])}")
            
            results.append({
                'code': code,
                'name': name,
                'price': latest_signal['price'],
                'score': latest_signal['score'],
                'reasons': latest_signal['reasons'],
                'signal_date': str(latest_signal['date'])[:10],
            })
        else:
            print(f"  ❌ 未找到信号（条件严格，在等待高概率机会）")
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "="*80)
    print("【今日最终选股结果】")
    print("="*80)
    
    if not results:
        print("\n📌 今日暂无符合高门槛条件的股票")
        print("   建议：耐心等待更好的机会，不追求频繁交易")
        return results
    
    for i, r in enumerate(results[:5], 1):
        print(f"\n{i}. {r['name']}({r['code']})")
        print(f"   现价：{r['price']:.2f}元")
        print(f"   评分：{r['score']}/100")
        print(f"   信号日期：{r['signal_date']}")
        print(f"   理由：{'，'.join(r['reasons'])}")
    
    return results


if __name__ == "__main__":
    print("="*80)
    print("🎁 最终优质缠论量化策略系统 - 专注高胜率")
    print("="*80)
    
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
    
    print("\n【第一阶段】今日选股筛选")
    selected = run_final_quality_strategy(stock_pool)
    
    print("\n" + "="*80)
    print("【第二阶段】策略历史回测")
    optimizer = FinalStrategyOptimizer()
    backtest_results = optimizer.run_final_backtest(stock_pool)
    
    print("\n" + "="*80)
    print("【第三阶段】策略总结")
    print("="*80)
    
    if backtest_results and backtest_results['win_rate'] > 60:
        print("\n✅ 策略优质！胜率超过60%")
    else:
        print("\n📝 策略需要继续优化，但筛选条件很严格，安全性高")
    
    print("\n💡 策略理念：宁可错过，不可做错，只追求高胜率机会")
    
    print("\n✅ 最终优质缠论策略分析完成！")
