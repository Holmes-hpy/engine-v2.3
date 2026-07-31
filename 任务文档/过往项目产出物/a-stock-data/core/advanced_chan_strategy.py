"""
优质缠论量化策略系统 v2.0
整合三类买卖点、多级别联立、背驰精确判断、优化框架
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a_stock_data_core import get_stock_quote, get_historical_k_data


class AdvancedChanStrategy:
    """高级缠论策略 - 整合三类买卖点"""
    
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
        
        # 振幅
        self.data['amplitude'] = (self.data['high'] - self.data['low']) / self.data['open'] * 100
        
        return True
    
    def detect_precise_divergence(self):
        """精确背驰检测 - 多维度判断"""
        if self.data is None:
            return
        
        df = self.data.copy()
        df['divergence'] = 0  # 0:无, 1:顶背驰, -1:底背驰
        df['divergence_score'] = 0  # 背驰强度评分
        
        for i in range(30, len(df)):
            recent_window = df.iloc[i-20:i]
            earlier_window = df.iloc[i-40:i-20]
            
            if len(recent_window) < 15 or len(earlier_window) < 15:
                continue
            
            recent_high = recent_window['high'].max()
            earlier_high = earlier_window['high'].max()
            recent_low = recent_window['low'].min()
            earlier_low = earlier_window['low'].min()
            
            recent_macd_area = recent_window['MACD_HIST'].abs().sum()
            earlier_macd_area = earlier_window['MACD_HIST'].abs().sum()
            recent_macd_max = recent_window['MACD_HIST'].max()
            earlier_macd_max = earlier_window['MACD_HIST'].max()
            
            # 顶背驰判断
            top_div_score = 0
            if recent_high > earlier_high:
                if recent_macd_area < earlier_macd_area * 0.7:
                    top_div_score += 40
                if recent_macd_max < earlier_macd_max * 0.8:
                    top_div_score += 30
                if df['MACD'].iloc[i] < df['MACD'].iloc[i-20]:
                    top_div_score += 30
            
            # 底背驰判断
            bottom_div_score = 0
            if recent_low < earlier_low:
                if recent_macd_area < earlier_macd_area * 0.7:
                    bottom_div_score += 40
                if recent_macd_max > earlier_macd_max * 0.8:
                    bottom_div_score += 30
                if df['MACD'].iloc[i] > df['MACD'].iloc[i-20]:
                    bottom_div_score += 30
            
            if top_div_score >= 70:
                df.loc[df.index[i], 'divergence'] = 1
                df.loc[df.index[i], 'divergence_score'] = top_div_score
            
            if bottom_div_score >= 70:
                df.loc[df.index[i], 'divergence'] = -1
                df.loc[df.index[i], 'divergence_score'] = bottom_div_score
        
        self.data = df
    
    def detect_type1_buy(self):
        """第一类买点检测 - 趋势背驰后抄底"""
        signals = []
        df = self.data
        
        for i in range(40, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            if curr['divergence'] != -1 or curr['divergence_score'] < 70:
                continue
            
            # 趋势下跌确认
            if curr['MA20'] <= curr['MA60']:
                continue
            
            # MACD金叉确认
            if prev['MACD'] <= prev['MACD_SIGNAL'] and curr['MACD'] > curr['MACD_SIGNAL']:
                score = 0
                reasons = []
                
                score += curr['divergence_score']
                reasons.append("底背驰")
                
                if curr['MA20'] > curr['MA60']:
                    score += 15
                    reasons.append("MA20>MA60")
                
                if curr['RSI'] < 50 and curr['RSI'] > 30:
                    score += 15
                    reasons.append("RSI超卖后回升")
                
                if score >= 85:
                    signals.append({
                        'date': df.index[i],
                        'type': '第一类买点',
                        'price': curr['close'],
                        'score': score,
                        'reasons': reasons,
                    })
        
        return signals
    
    def detect_type2_buy(self):
        """第二类买点检测 - 回调不创新低（最稳健）"""
        signals = []
        df = self.data
        
        for i in range(30, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            
            # 均线多头确认
            if curr['MA5'] <= curr['MA10'] or curr['MA10'] <= curr['MA20']:
                continue
            
            # RSI健康确认
            if curr['RSI'] < 50 or curr['RSI'] > 80:
                continue
            
            # MACD金叉确认
            if prev['MACD'] <= prev['MACD_SIGNAL'] and curr['MACD'] > curr['MACD_SIGNAL']:
                # 回调确认
                recent_low = df.iloc[i-10:i]['low'].min()
                if curr['low'] > recent_low * 0.98:
                    score = 0
                    reasons = []
                    
                    if curr['MA5'] > curr['MA10'] > curr['MA20']:
                        score += 35
                        reasons.append("均线完美多头")
                    
                    if curr['MACD'] > curr['MACD_SIGNAL']:
                        score += 30
                        reasons.append("MACD金叉")
                    
                    if curr['close'] > curr['BOLL_MID']:
                        score += 20
                        reasons.append("布林带中轨上方")
                    
                    if curr['vol_ratio'] > 1.2:
                        score += 15
                        reasons.append("量比放量")
                    
                    if score >= 80:
                        signals.append({
                            'date': df.index[i],
                            'type': '第二类买点',
                            'price': curr['close'],
                            'score': score,
                            'reasons': reasons,
                        })
        
        return signals
    
    def detect_type3_buy(self):
        """第三类买点检测 - 突破回抽确认"""
        signals = []
        df = self.data
        
        for i in range(30, len(df)):
            curr = df.iloc[i]
            
            # 价格位置确认
            if curr['close'] <= curr['BOLL_MID']:
                continue
            
            # 突破前高确认
            recent_high = df.iloc[i-10:i]['high'].max()
            if curr['close'] < recent_high * 1.02:
                continue
            
            # 量比放量确认
            if curr['vol_ratio'] < 1.3:
                continue
            
            score = 0
            reasons = []
            
            if curr['MA5'] > curr['MA10'] > curr['MA20']:
                score += 30
                reasons.append("均线多头")
            
            if curr['vol_ratio'] > 1.5:
                score += 30
                reasons.append("量比强势")
            
            if curr['close'] > curr['BOLL_MID'] * 1.01:
                score += 25
                reasons.append("突破中轨")
            
            if curr['RSI'] > 55 and curr['RSI'] < 75:
                score += 15
                reasons.append("RSI健康")
            
            if score >= 80:
                signals.append({
                    'date': df.index[i],
                    'type': '第三类买点',
                    'price': curr['close'],
                    'score': score,
                    'reasons': reasons,
                })
        
        return signals
    
    def find_all_signals(self):
        """寻找所有三类买卖点信号"""
        signals = []
        
        signals.extend(self.detect_type1_buy())
        signals.extend(self.detect_type2_buy())
        signals.extend(self.detect_type3_buy())
        
        signals.sort(key=lambda x: x['score'], reverse=True)
        self.signals = signals
        
        return signals
    
    def run_complete_analysis(self):
        """完整分析流程"""
        if not self.prepare_data():
            print(f"❌ {self.name}({self.code}) 获取数据失败")
            return []
        
        self.detect_precise_divergence()
        signals = self.find_all_signals()
        
        return signals


class StrategyOptimizer:
    """策略优化器 - 回测和优化框架"""
    
    def __init__(self, initial_cash=20000):
        self.initial_cash = initial_cash
        self.trades = []
    
    def run_backtest(self, stock_pool, params=None):
        """策略回测"""
        print("="*80)
        print("优质缠论策略回测 v2.0")
        print("="*80)
        
        all_trades = []
        
        for code, name in stock_pool:
            print(f"\n分析 {name}({code})...")
            strategy = AdvancedChanStrategy(code, name)
            signals = strategy.run_complete_analysis()
            
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
        return self.calculate_and_print_results()
    
    def calculate_and_print_results(self):
        """计算并打印结果"""
        if not self.trades:
            print("\n没有找到任何信号！")
            return
        
        df = pd.DataFrame(self.trades)
        
        total_trades = len(df)
        wins = df[df['profit_pct'] > 0]
        losses = df[df['profit_pct'] <= 0]
        
        win_rate = len(wins) / total_trades * 100
        total_profit = df['profit_pct'].sum()
        avg_profit = wins['profit_pct'].mean() if len(wins) > 0 else 0
        avg_loss = losses['profit_pct'].mean() if len(losses) > 0 else 0
        
        # 按买卖点类型统计
        type_stats = df.groupby('type')['profit_pct'].agg(['count', 'mean', 'sum'])
        
        print("\n" + "="*80)
        print("【回测结果统计】")
        print("="*80)
        
        print(f"\n📊 总体表现：")
        print(f"  总交易次数：{total_trades}")
        print(f"  盈利次数：{len(wins)}")
        print(f"  亏损次数：{len(losses)}")
        print(f"  胜率：{win_rate:.2f}%")
        print(f"  总收益率：{total_profit:.2f}%")
        print(f"  平均盈利：{avg_profit:.2f}%")
        print(f"  平均亏损：{avg_loss:.2f}%")
        
        if avg_loss != 0:
            print(f"  盈亏比：{abs(avg_profit/avg_loss):.2f}")
        
        print(f"\n📈 买卖点类型分析：")
        for idx, row in type_stats.iterrows():
            win_type = len(df[(df['type'] == idx) & (df['profit_pct'] > 0)])
            total_type = int(row['count'])
            type_win_rate = win_type / total_type * 100 if total_type > 0 else 0
            print(f"  {idx}: {total_type}次, 胜率{type_win_rate:.1f}%, 平均收益{row['mean']:.2f}%")
        
        print(f"\n📋 详细交易记录：")
        for i, row in df.head(15).iterrows():
            print(f"{row['date']} | {row['name']} | {row['type']} | 买:{row['buy_price']:.2f} | 卖:{row['sell_price']:.2f} | {row['profit_pct']:+.2f}%")
        
        results = {
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_trades': total_trades,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'type_stats': type_stats,
            'trades': self.trades,
        }
        
        return results


def run_quality_strategy(stock_pool):
    """运行优质缠论策略"""
    print("="*80)
    print("🏆 优质缠论量化策略 v2.0 - 选股筛选")
    print("="*80)
    
    results = []
    
    for code, name in stock_pool:
        print(f"\n分析 {name}({code})...")
        strategy = AdvancedChanStrategy(code, name)
        signals = strategy.run_complete_analysis()
        
        if signals:
            latest_signal = signals[0]
            print(f"  ✅ 找到信号！类型：{latest_signal['type']}，评分：{latest_signal['score']}")
            print(f"  理由：{'，'.join(latest_signal['reasons'])}")
            
            results.append({
                'code': code,
                'name': name,
                'type': latest_signal['type'],
                'price': latest_signal['price'],
                'score': latest_signal['score'],
                'reasons': latest_signal['reasons'],
                'signal_date': str(latest_signal['date'])[:10],
            })
        else:
            print(f"  ❌ 未找到信号")
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "="*80)
    print("【今日选股结果】")
    print("="*80)
    
    if not results:
        print("暂无符合条件的股票")
        return results
    
    for i, r in enumerate(results[:5], 1):
        print(f"\n{i}. {r['name']}({r['code']})")
        print(f"   类型：{r['type']}")
        print(f"   现价：{r['price']:.2f}元")
        print(f"   评分：{r['score']}/100")
        print(f"   信号日期：{r['signal_date']}")
        print(f"   理由：{'，'.join(r['reasons'])}")
    
    return results


if __name__ == "__main__":
    print("优质缠论量化策略系统 v2.0")
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
    
    print("\n【第一阶段】选股筛选")
    selected = run_quality_strategy(stock_pool)
    
    print("\n" + "="*80)
    print("【第二阶段】策略回测")
    optimizer = StrategyOptimizer()
    results = optimizer.run_backtest(stock_pool)
    
    print("\n" + "="*80)
    print("【第三阶段】最终推荐")
    print("="*80)
    
    if selected:
        print("\n🎯 优先推荐股票：")
        for i, s in enumerate(selected[:3], 1):
            print(f"{i}. {s['name']}({s['code']}) - {s['type']}")
            print(f"   现价：{s['price']:.2f}元，评分：{s['score']}")
    else:
        print("\n暂无符合条件的股票，建议等待更好的机会")
    
    print("\n✅ 优质缠论策略分析完成！")
