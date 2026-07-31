"""
缠论量化策略系统
结合分型、笔、线段、中枢、背驰等缠论核心概念
整合MACD、MA、布林带等技术指标
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from a_stock_data_core import get_stock_quote, get_historical_k_data


class ChanPatternRecognizer:
    """缠论形态识别器"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.processed = False
    
    def handle_containing(self):
        """处理包含关系（K线合并）"""
        df = self.data.copy()
        df['high_merged'] = df['high']
        df['low_merged'] = df['low']
        
        trend = 0  # 0: 未知, 1: 上升, -1: 下降
        
        for i in range(1, len(df)):
            prev_high = df['high_merged'].iloc[i-1]
            prev_low = df['low_merged'].iloc[i-1]
            curr_high = df['high'].iloc[i]
            curr_low = df['low'].iloc[i]
            
            if curr_high <= prev_high and curr_low >= prev_low:
                if trend == 1:
                    df.loc[df.index[i], 'high_merged'] = prev_high
                    df.loc[df.index[i], 'low_merged'] = max(prev_low, curr_low)
                elif trend == -1:
                    df.loc[df.index[i], 'high_merged'] = min(prev_high, curr_high)
                    df.loc[df.index[i], 'low_merged'] = prev_low
                else:
                    df.loc[df.index[i], 'high_merged'] = prev_high
                    df.loc[df.index[i], 'low_merged'] = prev_low
            else:
                if curr_high > prev_high:
                    trend = 1
                else:
                    trend = -1
            
        self.data['high_merged'] = df['high_merged']
        self.data['low_merged'] = df['low_merged']
        self.processed = True
    
    def find_fx(self):
        """识别顶底分型"""
        if not self.processed:
            self.handle_containing()
        
        df = self.data.copy()
        df['fx_type'] = 0  # 0: 无, 1: 顶分型, -1: 底分型
        df['fx_high'] = np.nan
        df['fx_low'] = np.nan
        
        for i in range(1, len(df) - 1):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            next_ = df.iloc[i+1]
            
            # 顶分型
            if curr['high_merged'] >= prev['high_merged'] and \
               curr['high_merged'] >= next_['high_merged']:
                df.loc[df.index[i], 'fx_type'] = 1
                df.loc[df.index[i], 'fx_high'] = curr['high_merged']
            
            # 底分型
            elif curr['low_merged'] <= prev['low_merged'] and \
                 curr['low_merged'] <= next_['low_merged']:
                df.loc[df.index[i], 'fx_type'] = -1
                df.loc[df.index[i], 'fx_low'] = curr['low_merged']
        
        self.data = df
        return df
    
    def find_bi(self):
        """识别笔"""
        if 'fx_type' not in self.data.columns:
            self.find_fx()
        
        df = self.data.copy()
        df['bi_type'] = 0  # 0: 无, 1: 上升笔, -1: 下降笔
        df['bi_start'] = np.nan
        df['bi_end'] = np.nan
        
        fxs = df[df['fx_type'] != 0]
        
        if len(fxs) < 2:
            return df
        
        bi_start = None
        bi_type = 0
        
        for i in range(1, len(fxs)):
            prev_fx = fxs.iloc[i-1]
            curr_fx = fxs.iloc[i]
            
            if prev_fx['fx_type'] != curr_fx['fx_type']:
                if prev_fx['fx_type'] == -1 and curr_fx['fx_type'] == 1:
                    bi_type = 1
                    start_idx = df.index.get_loc(prev_fx.name)
                    end_idx = df.index.get_loc(curr_fx.name)
                    df.loc[df.index[end_idx], 'bi_type'] = 1
                    df.loc[df.index[end_idx], 'bi_start'] = prev_fx['fx_low']
                    df.loc[df.index[end_idx], 'bi_end'] = curr_fx['fx_high']
                elif prev_fx['fx_type'] == 1 and curr_fx['fx_type'] == -1:
                    bi_type = -1
                    start_idx = df.index.get_loc(prev_fx.name)
                    end_idx = df.index.get_loc(curr_fx.name)
                    df.loc[df.index[end_idx], 'bi_type'] = -1
                    df.loc[df.index[end_idx], 'bi_start'] = prev_fx['fx_high']
                    df.loc[df.index[end_idx], 'bi_end'] = curr_fx['fx_low']
        
        self.data = df
        return df
    
    def find_zsw(self):
        """识别中枢"""
        if 'bi_type' not in self.data.columns:
            self.find_bi()
        
        df = self.data.copy()
        df['zsw_start'] = np.nan
        df['zsw_end'] = np.nan
        df['zsw_high'] = np.nan
        df['zsw_low'] = np.nan
        
        bis = df[df['bi_type'] != 0]
        
        if len(bis) < 3:
            return df
        
        for i in range(2, len(bis)):
            bi1 = bis.iloc[i-2]
            bi2 = bis.iloc[i-1]
            bi3 = bis.iloc[i]
            
            if bi1['bi_type'] != bi2['bi_type'] and bi2['bi_type'] != bi3['bi_type']:
                highs = [bi1['bi_end'], bi2['bi_end'], bi3['bi_end']]
                lows = [bi1['bi_start'], bi2['bi_start'], bi3['bi_start']]
                
                zsw_high = min([h for h in highs if h is not None])
                zsw_low = max([l for l in lows if l is not None])
                
                if zsw_high > zsw_low:
                    end_idx = df.index.get_loc(bi3.name)
                    df.loc[df.index[end_idx], 'zsw_high'] = zsw_high
                    df.loc[df.index[end_idx], 'zsw_low'] = zsw_low
        
        self.data = df
        return df


class ChanStrategy:
    """缠论量化策略"""
    
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.data = None
        self.signals = []
    
    def prepare_data(self, days=120):
        """准备数据"""
        hist = get_historical_k_data(self.code, 'daily', days)
        if hist is None or len(hist) < 60:
            return False
        
        self.data = hist.copy()
        self.data['change_pct'] = self.data['close'].pct_change() * 100
        
        # 计算技术指标
        self.data['MA5'] = self.data['close'].rolling(5).mean()
        self.data['MA10'] = self.data['close'].rolling(10).mean()
        self.data['MA20'] = self.data['close'].rolling(20).mean()
        
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
        rs = avg_gain / avg_loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        return True
    
    def detect_divergence(self):
        """检测背驰"""
        if self.data is None:
            return
        
        df = self.data.copy()
        df['divergence'] = 0  # 0: 无, 1: 顶背驰, -1: 底背驰
        
        for i in range(20, len(df)):
            recent = df.iloc[i-5:i]
            earlier = df.iloc[i-15:i-5]
            
            if len(recent) < 5 or len(earlier) < 5:
                continue
            
            recent_high = recent['high'].max()
            earlier_high = earlier['high'].max()
            recent_low = recent['low'].min()
            earlier_low = earlier['low'].min()
            
            recent_macd = recent['MACD_HIST'].sum()
            earlier_macd = earlier['MACD_HIST'].sum()
            
            if recent_high > earlier_high and recent_macd < earlier_macd * 0.7:
                df.loc[df.index[i], 'divergence'] = 1
            
            if recent_low < earlier_low and recent_macd > earlier_macd * 0.7:
                df.loc[df.index[i], 'divergence'] = -1
        
        self.data = df
    
    def find_buy_signals(self):
        """寻找买入信号"""
        if self.data is None:
            return
        
        df = self.data.copy()
        signals = []
        
        # 缠论第二类买点条件
        for i in range(20, len(df)):
            curr = df.iloc[i]
            prev = df.iloc[i-1]
            prev5 = df.iloc[i-5:i]
            
            # 条件1: 底背驰
            if curr['divergence'] != -1:
                continue
            
            # 条件2: 均线多头
            if curr['MA5'] <= curr['MA10'] or curr['MA10'] <= curr['MA20']:
                continue
            
            # 条件3: RSI低于50后回升
            if prev5['RSI'].min() >= 50:
                continue
            
            # 条件4: MACD金叉
            if prev['MACD'] <= prev['MACD_SIGNAL'] and curr['MACD'] > curr['MACD_SIGNAL']:
                continue
            
            # 条件5: 价格在布林带中轨上方
            if curr['close'] <= curr['BOLL_MID']:
                continue
            
            score = 0
            reasons = []
            
            if curr['divergence'] == -1:
                score += 30
                reasons.append("底背驰")
            
            if curr['MA5'] > curr['MA10'] > curr['MA20']:
                score += 25
                reasons.append("均线多头")
            
            if curr['MACD'] > curr['MACD_SIGNAL']:
                score += 20
                reasons.append("MACD金叉")
            
            if curr['close'] > curr['BOLL_MID']:
                score += 15
                reasons.append("布林带中轨上方")
            
            if curr['RSI'] > 50:
                score += 10
                reasons.append("RSI健康")
            
            if score >= 70:
                signals.append({
                    'date': df.index[i],
                    'code': self.code,
                    'name': self.name,
                    'price': curr['close'],
                    'score': score,
                    'reasons': reasons,
                    'signal_type': '第二类买点',
                })
        
        self.signals = signals
        return signals
    
    def run_strategy(self):
        """运行策略"""
        if not self.prepare_data():
            print(f"❌ {self.name}({self.code}) 获取数据失败")
            return []
        
        self.detect_divergence()
        signals = self.find_buy_signals()
        
        return signals


class ChanBacktest:
    """缠论策略回测"""
    
    def __init__(self, initial_cash=20000):
        self.initial_cash = initial_cash
        self.trades = []
    
    def run_backtest(self, stock_pool):
        """回测股票池"""
        print("="*70)
        print("缠论策略回测")
        print("="*70)
        
        all_signals = []
        
        for code, name in stock_pool:
            print(f"\n分析 {name}({code})...")
            strategy = ChanStrategy(code, name)
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
                    
                    self.trades.append({
                        'date': str(buy_date)[:10],
                        'code': code,
                        'name': name,
                        'buy_price': buy_price,
                        'sell_price': sell_price,
                        'profit_pct': profit_pct,
                        'sell_type': sell_type,
                        'score': sig['score'],
                        'reasons': ', '.join(sig['reasons']),
                    })
            
            print(f"  找到 {len(signals)} 个信号")
            all_signals.extend(signals)
        
        self.print_results()
        return self.trades
    
    def print_results(self):
        """打印回测结果"""
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
        
        print("\n" + "="*70)
        print("回测结果")
        print("="*70)
        print(f"总交易次数：{total_trades}")
        print(f"盈利次数：{len(wins)}")
        print(f"亏损次数：{len(losses)}")
        print(f"胜率：{win_rate:.2f}%")
        print(f"总收益率：{total_profit:.2f}%")
        print(f"平均盈利：{avg_profit:.2f}%")
        print(f"平均亏损：{avg_loss:.2f}%")
        
        print(f"\n📋 交易记录：")
        for i, row in df.head(10).iterrows():
            print(f"{row['date']} | {row['name']} | 买:{row['buy_price']:.2f} | 卖:{row['sell_price']:.2f} | {row['profit_pct']:+.2f}% | {row['sell_type']}")


def screen_stocks(stock_pool):
    """筛选符合缠论策略的股票"""
    print("="*70)
    print("缠论策略选股")
    print("="*70)
    
    results = []
    
    for code, name in stock_pool:
        print(f"\n分析 {name}({code})...")
        strategy = ChanStrategy(code, name)
        signals = strategy.run_strategy()
        
        if signals:
            latest_signal = signals[-1]
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
            print(f"  ❌ 未找到信号")
    
    results.sort(key=lambda x: x['score'], reverse=True)
    
    print("\n" + "="*70)
    print("选股结果")
    print("="*70)
    
    if not results:
        print("暂无符合条件的股票")
        return
    
    for i, r in enumerate(results[:5], 1):
        print(f"\n{i}. {r['name']}({r['code']})")
        print(f"   现价：{r['price']:.2f}元")
        print(f"   评分：{r['score']}/100")
        print(f"   信号日期：{r['signal_date']}")
        print(f"   理由：{'，'.join(r['reasons'])}")
    
    return results


if __name__ == "__main__":
    print("缠论量化策略系统")
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
    
    print("\n【模式1】选股筛选")
    results = screen_stocks(stock_pool)
    
    print("\n" + "="*70)
    print("【模式2】策略回测")
    backtest = ChanBacktest()
    backtest.run_backtest(stock_pool)
    
    print("\n完成！")
