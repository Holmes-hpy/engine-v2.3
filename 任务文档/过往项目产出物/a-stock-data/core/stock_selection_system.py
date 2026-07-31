#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主选股分析系统
每天自动选股、预测、验证、反思、进化
"""

import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from a_stock_data_core import (
    get_stock_quote,
    get_historical_k_data,
    get_stock_basic_info,
    get_market_index,
    get_northbound_flow
)


class StockSelectionSystem:
    """自主选股分析系统"""
    
    def __init__(self):
        self.base_dir = PROJECT_DIR
        self.db_dir = self.base_dir / "stock_selection_db"
        self.reports_dir = self.base_dir / "reports"
        
        # 创建目录
        for directory in [self.db_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
        
        # 数据库文件
        self.selection_history_file = self.db_dir / "selection_history.json"
        self.analysis_file = self.db_dir / "analysis_records.json"
        self.accuracy_file = self.db_dir / "accuracy_stats.json"
        
        # 初始化数据库
        self._initialize_databases()
        
        # 选股策略配置
        self.strategies = {
            'value': {
                'name': '价值选股策略',
                'weight': 0.3,
                'enabled': True
            },
            'momentum': {
                'name': '动量选股策略',
                'weight': 0.3,
                'enabled': True
            },
            'technical': {
                'name': '技术形态选股策略',
                'weight': 0.4,
                'enabled': True
            }
        }
    
    def _initialize_databases(self):
        """初始化数据库文件"""
        if not self.selection_history_file.exists():
            self.selection_history_file.write_text(json.dumps({
                'selections': [],
                'total_count': 0
            }, ensure_ascii=False, indent=2))
        else:
            # 兼容旧版本数据：确保必要字段存在
            data = json.loads(self.selection_history_file.read_text())
            if 'total_count' not in data:
                data['total_count'] = len(data.get('selections', []))
                self.selection_history_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        
        if not self.analysis_file.exists():
            self.analysis_file.write_text(json.dumps({
                'analyses': [],
                'success_cases': [],
                'failure_cases': []
            }, ensure_ascii=False, indent=2))
        
        if not self.accuracy_file.exists():
            self._update_accuracy_stats()
    
    def _load_history(self) -> Dict:
        """加载选股历史"""
        return json.loads(self.selection_history_file.read_text())
    
    def _save_history(self, data: Dict):
        """保存选股历史"""
        self.selection_history_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load_analyses(self) -> Dict:
        """加载分析记录"""
        return json.loads(self.analysis_file.read_text())
    
    def _save_analyses(self, data: Dict):
        """保存分析记录"""
        self.analysis_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load_accuracy_stats(self) -> Dict:
        """加载准确度统计"""
        return json.loads(self.accuracy_file.read_text())
    
    def _update_accuracy_stats(self):
        """更新准确度统计"""
        history = self._load_history()
        analyses = self._load_analyses()
        
        total = len([s for s in history['selections'] if s.get('result')])
        correct = len([s for s in history['selections'] if s.get('result') == 'correct'])
        incorrect = len([s for s in history['selections'] if s.get('result') == 'incorrect'])
        
        # 计算各策略准确度
        strategy_accuracy = {}
        for strategy_name in ['value', 'momentum', 'technical']:
            strategy_selections = [s for s in history['selections'] 
                                  if s.get('strategy') == strategy_name and s.get('result')]
            if strategy_selections:
                strategy_correct = len([s for s in strategy_selections if s.get('result') == 'correct'])
                strategy_accuracy[strategy_name] = {
                    'total': len(strategy_selections),
                    'correct': strategy_correct,
                    'accuracy': strategy_correct / len(strategy_selections) * 100
                }
        
        stats = {
            'total_predictions': total,
            'correct_predictions': correct,
            'incorrect_predictions': incorrect,
            'accuracy_rate': correct / total * 100 if total > 0 else 0,
            'strategy_accuracy': strategy_accuracy,
            'last_updated': datetime.now().isoformat()
        }
        
        self.accuracy_file.write_text(json.dumps(stats, ensure_ascii=False, indent=2))
        return stats
    
    def select_stock(self) -> Dict[str, Any]:
        """选股：从A股市场选择一只股票"""
        print("🔍 开始选股流程...")
        
        # 获取大盘状态
        market_status = self._get_market_status()
        
        # 根据市场状态调整策略权重
        self._adjust_strategy_weights(market_status)
        
        # 候选股票池（符合1万元以下可买的条件：股价<100元）
        candidate_pool = self._build_candidate_pool()
        
        if not candidate_pool:
            print("⚠️ 候选股票池为空，使用默认股票")
            candidate_pool = ['600584', '000001', '600519']
        
        # 使用策略评分选择股票
        selected_stock = self._score_and_select(candidate_pool, market_status)
        
        # 生成选股报告
        selection_report = {
            'stock_code': selected_stock['code'],
            'stock_name': selected_stock['name'],
            'price': selected_stock['price'],
            'selection_date': datetime.now().strftime('%Y-%m-%d'),
            'market_status': market_status,
            'strategy': selected_stock['main_strategy'],
            'strategy_scores': selected_stock['scores'],
            'timestamp': datetime.now().isoformat()
        }
        
        # 保存选股记录
        history = self._load_history()
        history['selections'].append(selection_report)
        history['total_count'] += 1
        self._save_history(history)
        
        print(f"✅ 选股完成: {selected_stock['name']}({selected_stock['code']}) @ {selected_stock['price']}元")
        
        return selection_report
    
    def _get_market_status(self) -> Dict:
        """获取市场状态"""
        try:
            index_data = get_market_index()
            northbound = get_northbound_flow()
            
            # 判断市场趋势
            total_change = 0
            for code, info in index_data.items():
                total_change += info.get('change_pct', 0)
            
            avg_change = total_change / len(index_data) if index_data else 0
            
            # 判断北向资金
            nb_total = northbound.get('total', 0) if northbound else 0
            
            # 综合判断
            if avg_change > 0.5 and nb_total > 0:
                trend = 'bullish'
                description = '市场上涨，北向资金流入'
            elif avg_change < -0.5 and nb_total < 0:
                trend = 'bearish'
                description = '市场下跌，北向资金流出'
            elif abs(avg_change) <= 0.5:
                trend = 'neutral'
                description = '市场震荡'
            else:
                trend = 'mixed'
                description = '市场分歧'
            
            return {
                'trend': trend,
                'description': description,
                'avg_change': avg_change,
                'northbound': nb_total,
                'indices': index_data
            }
            
        except Exception as e:
            print(f"⚠️ 获取市场状态失败: {e}")
            return {
                'trend': 'neutral',
                'description': '市场状态未知',
                'avg_change': 0,
                'northbound': 0
            }
    
    def _adjust_strategy_weights(self, market_status: Dict):
        """根据市场状态调整策略权重"""
        if market_status['trend'] == 'bullish':
            # 牛市：增加动量和技术策略权重
            self.strategies['momentum']['weight'] = 0.4
            self.strategies['technical']['weight'] = 0.4
            self.strategies['value']['weight'] = 0.2
        elif market_status['trend'] == 'bearish':
            # 熊市：增加价值策略权重
            self.strategies['value']['weight'] = 0.5
            self.strategies['momentum']['weight'] = 0.2
            self.strategies['technical']['weight'] = 0.3
        else:
            # 震荡市：均衡配置
            self.strategies['value']['weight'] = 0.3
            self.strategies['momentum']['weight'] = 0.3
            self.strategies['technical']['weight'] = 0.4
    
    def _build_candidate_pool(self) -> List[str]:
        """构建候选股票池"""
        # 候选股票池（可根据需要扩展）
        candidates = [
            '600584',  # 长电科技
            '600519',  # 贵州茅台
            '000001',  # 平安银行
            '300750',  # 宁德时代
            '600036',  # 招商银行
            '000858',  # 五粮液
            '601318',  # 中国平安
            '002594',  # 比亚迪
            '600276',  # 恒瑞医药
            '000333',  # 美的集团
        ]
        
        # 过滤掉近期已经选过的股票
        history = self._load_history()
        recent_selections = [s['stock_code'] for s in history['selections'][-5:]]
        
        filtered_candidates = [c for c in candidates if c not in recent_selections]
        
        return filtered_candidates if filtered_candidates else candidates
    
    def _score_and_select(self, candidates: List[str], market_status: Dict) -> Dict:
        """评分选股"""
        scores = {}
        
        for code in candidates:
            try:
                # 获取股票数据
                quotes_result = get_stock_quote(code)
                # get_stock_quote 返回的是字典，键是股票代码，值是行情数据
                quote = quotes_result.get(code, {}) if code in quotes_result else {}
                basic_info = get_stock_basic_info(code)
                k_data = get_historical_k_data(code, period='daily', days=60)
                
                if k_data.empty:
                    continue
                
                # 计算各策略得分
                value_score = self._evaluate_value_strategy(quote, basic_info)
                momentum_score = self._evaluate_momentum_strategy(k_data, market_status)
                technical_score = self._evaluate_technical_strategy(k_data)
                
                # 加权总分
                total_score = (
                    value_score * self.strategies['value']['weight'] +
                    momentum_score * self.strategies['momentum']['weight'] +
                    technical_score * self.strategies['technical']['weight']
                )
                
                scores[code] = {
                    'name': quote.get('name', code),
                    'price': quote.get('price', 0),
                    'total_score': total_score,
                    'scores': {
                        'value': value_score,
                        'momentum': momentum_score,
                        'technical': technical_score
                    },
                    'main_strategy': self._get_main_strategy_name(total_score, 
                                                                value_score, 
                                                                momentum_score, 
                                                                technical_score)
                }
                
            except Exception as e:
                print(f"⚠️ 评估股票{code}失败: {e}")
                continue
        
        if not scores:
            # 默认返回长电科技
            return {
                'code': '600584',
                'name': '长电科技',
                'price': 65.88,
                'scores': {'value': 50, 'momentum': 50, 'technical': 50},
                'main_strategy': 'default'
            }
        
        # 选择得分最高的股票
        best_code = max(scores.keys(), key=lambda k: scores[k]['total_score'])
        best_stock = scores[best_code]
        best_stock['code'] = best_code
        
        return best_stock
    
    def _evaluate_value_strategy(self, quote: Dict, basic_info: Dict) -> float:
        """评估价值策略"""
        score = 50.0  # 基准分
        
        try:
            pe_ttm = basic_info.get('pe_ttm', 0) or 0
            if pe_ttm > 0:
                if pe_ttm < 20:
                    score += 20  # 低估值加分
                elif pe_ttm < 30:
                    score += 10
                elif pe_ttm > 60:
                    score -= 15  # 高估值减分
                elif pe_ttm > 100:
                    score -= 25
            
            pb = basic_info.get('pb', 0) or 0
            if pb > 0:
                if pb < 3:
                    score += 10
                elif pb > 8:
                    score -= 10
            
            turnover = basic_info.get('turnover_pct', 0) or 0
            if 3 < turnover < 15:
                score += 5  # 换手率适中
            
        except Exception as e:
            print(f"⚠️ 价值评估失败: {e}")
        
        return max(0, min(100, score))
    
    def _evaluate_momentum_strategy(self, k_data: pd.DataFrame, market_status: Dict) -> float:
        """评估动量策略"""
        score = 50.0
        
        try:
            if k_data.empty or len(k_data) < 20:
                return score
            
            latest = k_data.iloc[-1]
            
            # 计算近期涨幅
            ma5 = k_data['close'].rolling(5).mean().iloc[-1]
            ma20 = k_data['close'].rolling(20).mean().iloc[-1]
            recent_return = (latest['close'] - k_data['close'].iloc[-5]) / k_data['close'].iloc[-5] * 100
            
            # 动量评分
            if recent_return > 5 and recent_return < 20:
                score += 20  # 适度上涨加分
            elif recent_return > 20:
                score -= 10  # 涨幅过大减分（可能回调）
            elif recent_return < -5:
                score -= 15  # 下跌减分
            
            # 均线多头排列
            if latest['close'] > ma5 > ma20:
                score += 15
            
            # 市场配合度
            if market_status['trend'] == 'bullish':
                score += 5
            elif market_status['trend'] == 'bearish':
                score -= 10
            
        except Exception as e:
            print(f"⚠️ 动量评估失败: {e}")
        
        return max(0, min(100, score))
    
    def _evaluate_technical_strategy(self, k_data: pd.DataFrame) -> float:
        """评估技术形态策略"""
        score = 50.0
        
        try:
            if k_data.empty or len(k_data) < 20:
                return score
            
            latest = k_data.iloc[-1]
            prev1 = k_data.iloc[-2]
            
            # 计算技术指标
            ma5 = k_data['close'].rolling(5).mean().iloc[-1]
            ma10 = k_data['close'].rolling(10).mean().iloc[-1]
            ma20 = k_data['close'].rolling(20).mean().iloc[-1]
            
            # MACD
            exp1 = k_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = k_data['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            dif = macd.iloc[-1]
            dea = signal.iloc[-1]
            
            # RSI
            delta = k_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            # KDJ
            low14 = k_data['low'].rolling(window=14).min()
            high14 = k_data['high'].rolling(window=14).max()
            rsv = (k_data['close'] - low14) / (high14 - low14) * 100
            k_series = rsv.ewm(com=2, adjust=False).mean()
            k_val = k_series.iloc[-1]
            d_series = k_series.ewm(com=2, adjust=False).mean()
            d_val = d_series.iloc[-1]
            
            # 技术指标评分
            # MACD
            if dif > dea and dif > 0:
                score += 15
            elif dif > dea:
                score += 5
            elif dif < dea:
                score -= 10
            
            # RSI（不是超买超卖区间最好）
            if 40 < rsi < 60:
                score += 10  # 中性区域最佳
            elif rsi > 80:
                score -= 20  # 严重超买
            elif rsi < 20:
                score += 5
            
            # KDJ
            if k_val > d_val and k_val < 80:
                score += 10
            elif k_val > 80:
                score -= 10
            
            # 布林带位置
            bb_std = k_data['close'].rolling(20).std().iloc[-1]
            bb_middle = ma20
            bb_upper = bb_middle + 2 * bb_std
            bb_lower = bb_middle - 2 * bb_std
            bb_position = (latest['close'] - bb_lower) / (bb_upper - bb_lower) * 100
            
            if 30 < bb_position < 70:
                score += 10  # 布林带中部最佳
            elif bb_position > 90:
                score -= 15  # 极度上轨
            elif bb_position < 10:
                score += 5
            
            # 成交量
            vol_ma5 = k_data['vol'].rolling(5).mean().iloc[-1]
            if latest['vol'] > vol_ma5 * 1.2:
                score += 5  # 放量加分
            
        except Exception as e:
            print(f"⚠️ 技术评估失败: {e}")
        
        return max(0, min(100, score))
    
    def _get_main_strategy_name(self, total: float, value: float, momentum: float, technical: float) -> str:
        """获取主要策略名称"""
        if value == max(value, momentum, technical):
            return 'value'
        elif momentum == max(value, momentum, technical):
            return 'momentum'
        else:
            return 'technical'
    
    def analyze_stock(self, stock_code: str, stock_name: str) -> Dict:
        """分析选中的股票，预测明日走势"""
        print(f"📊 开始分析 {stock_name}({stock_code})...")
        
        try:
            # 获取数据
            quotes_result = get_stock_quote(stock_code)
            # get_stock_quote 返回的是字典，键是股票代码，值是行情数据
            quote = quotes_result.get(stock_code, {}) if stock_code in quotes_result else {}
            basic_info = get_stock_basic_info(stock_code)
            k_data = get_historical_k_data(stock_code, period='daily', days=60)
            
            # 计算各项指标
            indicators = self._calculate_indicators(k_data)
            
            # 生成预测
            prediction = self._generate_prediction(quote, basic_info, indicators)
            
            # 生成详细分析报告
            analysis = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': quote.get('price', 0),
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'prediction': prediction,
                'indicators': indicators,
                'key_findings': self._extract_key_findings(quote, basic_info, indicators),
                'risk_factors': self._identify_risk_factors(quote, indicators),
                'support_resistance': self._calculate_support_resistance(k_data),
                'timestamp': datetime.now().isoformat()
            }
            
            # 保存分析记录
            analyses = self._load_analyses()
            analyses['analyses'].append(analysis)
            self._save_analyses(analyses)
            
            # 生成分析报告文件
            self._generate_analysis_report(analysis)
            
            print(f"✅ 分析完成: 预测{prediction['direction']}，置信度{prediction['confidence']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _calculate_indicators(self, k_data: pd.DataFrame) -> Dict:
        """计算技术指标"""
        if k_data.empty or len(k_data) < 20:
            return {}
        
        latest = k_data.iloc[-1]
        
        # 均线
        ma5 = k_data['close'].rolling(5).mean().iloc[-1]
        ma10 = k_data['close'].rolling(10).mean().iloc[-1]
        ma20 = k_data['close'].rolling(20).mean().iloc[-1]
        ma60 = k_data['close'].rolling(60).mean().iloc[-1] if len(k_data) >= 60 else ma20
        
        # MACD
        exp1 = k_data['close'].ewm(span=12, adjust=False).mean()
        exp2 = k_data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = k_data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # KDJ
        low14 = k_data['low'].rolling(window=14).min()
        high14 = k_data['high'].rolling(window=14).max()
        rsv_series = (k_data['close'] - low14) / (high14 - low14) * 100
        k_series = rsv_series.ewm(com=2, adjust=False).mean()
        k = k_series.iloc[-1]
        d_series = k_series.ewm(com=2, adjust=False).mean()
        d = d_series.iloc[-1]
        j = 3 * k - 2 * d
        
        # 布林带
        bb_middle = ma20
        bb_std = k_data['close'].rolling(20).std().iloc[-1]
        bb_upper = bb_middle + 2 * bb_std
        bb_lower = bb_middle - 2 * bb_std
        bb_position = (latest['close'] - bb_lower) / (bb_upper - bb_lower) * 100
        
        return {
            'price': latest['close'],
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma60': ma60,
            'macd_dif': macd.iloc[-1],
            'macd_dea': signal.iloc[-1],
            'macd_histogram': macd.iloc[-1] - signal.iloc[-1],
            'rsi': rsi,
            'kdj_k': k,
            'kdj_d': d,
            'kdj_j': j,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_position': bb_position,
            'volume': latest['vol'],
            'vol_ma5': k_data['vol'].rolling(5).mean().iloc[-1],
            'recent_return': (latest['close'] - k_data['close'].iloc[-5]) / k_data['close'].iloc[-5] * 100
        }
    
    def _generate_prediction(self, quote: Dict, basic_info: Dict, indicators: Dict) -> Dict:
        """生成预测"""
        score = 50  # 基准分
        factors = []
        
        try:
            # 均线系统
            if indicators['price'] > indicators['ma5'] > indicators['ma10'] > indicators['ma20']:
                score += 15
                factors.append('均线多头排列')
            
            # MACD
            if indicators['macd_dif'] > indicators['macd_dea'] and indicators['macd_dif'] > 0:
                score += 15
                factors.append('MACD零轴上方金叉')
            
            # RSI
            if 40 < indicators['rsi'] < 70:
                score += 10
                factors.append('RSI处于健康区间')
            elif indicators['rsi'] > 80:
                score -= 20
                factors.append('RSI严重超买')
            elif indicators['rsi'] < 30:
                score -= 10
                factors.append('RSI超卖')
            
            # KDJ
            if indicators['kdj_k'] > indicators['kdj_d'] and indicators['kdj_k'] < 80:
                score += 10
                factors.append('KDJ多方信号')
            elif indicators['kdj_k'] > 80:
                score -= 10
                factors.append('KDJ超买')
            
            # 布林带
            if 30 < indicators['bb_position'] < 70:
                score += 10
                factors.append('价格处于布林带中部')
            elif indicators['bb_position'] > 90:
                score -= 20
                factors.append('价格触及布林带上轨')
            
            # 成交量
            if indicators['volume'] > indicators['vol_ma5']:
                score += 5
                factors.append('成交量放大')
            
            # 近期涨幅
            if 3 < indicators['recent_return'] < 15:
                score += 5
                factors.append('适度上涨趋势')
            elif indicators['recent_return'] > 20:
                score -= 10
                factors.append('短期涨幅过大')
            
        except Exception as e:
            print(f"⚠️ 预测生成失败: {e}")
        
        # 判断方向和置信度
        if score >= 65:
            direction = '上涨'
            confidence = '高'
        elif score >= 55:
            direction = '震荡偏涨'
            confidence = '中'
        elif score >= 45:
            direction = '震荡'
            confidence = '中'
        elif score >= 35:
            direction = '震荡偏跌'
            confidence = '中'
        else:
            direction = '下跌'
            confidence = '高'
        
        return {
            'score': score,
            'direction': direction,
            'confidence': confidence,
            'factors': factors,
            'predicted_change_pct': (score - 50) / 5  # 估算涨跌百分比
        }
    
    def _extract_key_findings(self, quote: Dict, basic_info: Dict, indicators: Dict) -> List[str]:
        """提取关键发现"""
        findings = []
        
        try:
            # 价格位置
            if indicators['price'] > indicators['ma20'] * 1.2:
                findings.append('股价显著高于20日均线')
            
            # 超买超卖
            if indicators['rsi'] > 70:
                findings.append('RSI超买，注意回调风险')
            elif indicators['rsi'] < 30:
                findings.append('RSI超卖，可能存在反弹机会')
            
            # 趋势判断
            if indicators['macd_histogram'] > 0:
                findings.append('MACD柱状图为正，动能强劲')
            
            # 波动性
            if indicators['bb_position'] > 90:
                findings.append('价格接近布林带上轨')
            
        except Exception as e:
            print(f"⚠️ 关键发现提取失败: {e}")
        
        return findings
    
    def _identify_risk_factors(self, quote: Dict, indicators: Dict) -> List[str]:
        """识别风险因素"""
        risks = []
        
        try:
            if indicators['rsi'] > 80:
                risks.append('技术指标超买，回调风险大')
            
            if indicators['bb_position'] > 95:
                risks.append('极度超买，可能面临调整')
            
            if indicators['recent_return'] > 20:
                risks.append('短期涨幅过大，获利回吐压力大')
            
            if indicators['kdj_k'] > 85:
                risks.append('KDJ进入极值区域')
            
        except Exception as e:
            print(f"⚠️ 风险识别失败: {e}")
        
        return risks
    
    def _calculate_support_resistance(self, k_data: pd.DataFrame) -> Dict:
        """计算支撑位和压力位"""
        try:
            if k_data.empty or len(k_data) < 20:
                return {}
            
            latest = k_data.iloc[-1]
            ma5 = k_data['close'].rolling(5).mean().iloc[-1]
            ma10 = k_data['close'].rolling(10).mean().iloc[-1]
            ma20 = k_data['close'].rolling(20).mean().iloc[-1]
            
            return {
                'resistance_1': round(latest['high'] * 1.02, 2),
                'resistance_2': round(ma5, 2),
                'support_1': round(ma5, 2),
                'support_2': round(ma10, 2),
                'support_3': round(ma20, 2)
            }
        except:
            return {}
    
    def _generate_analysis_report(self, analysis: Dict) -> str:
        """生成分析报告文件"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"选股分析_{analysis['stock_code']}_{report_date}.md"
        
        report = f"""# 📊 选股分析报告

## 基本信息

| 项目 | 内容 |
|-----|------|
| 股票代码 | {analysis['stock_code']} |
| 股票名称 | {analysis['stock_name']} |
| 当前价格 | {analysis['current_price']} 元 |
| 分析日期 | {analysis['analysis_date']} |

---

## 预测结果

**预测方向**: {analysis['prediction']['direction']}

**置信度**: {analysis['prediction']['confidence']}

**综合评分**: {analysis['prediction']['score']} 分

**预测涨跌**: {'+' if analysis['prediction']['predicted_change_pct'] > 0 else ''}{analysis['prediction']['predicted_change_pct']:.2f}%

### 预测依据

"""
        
        for factor in analysis['prediction']['factors']:
            report += f"- {factor}\n"
        
        report += f"""

## 技术指标

| 指标 | 数值 | 说明 |
|-----|------|------|
"""
        
        indicators = analysis['indicators']
        report += f"| MA5 | {indicators.get('ma5', 0):.2f} | {'▲' if indicators['price'] > indicators.get('ma5', 0) else '▼'} |\n"
        report += f"| MA10 | {indicators.get('ma10', 0):.2f} | {'▲' if indicators['price'] > indicators.get('ma10', 0) else '▼'} |\n"
        report += f"| MA20 | {indicators.get('ma20', 0):.2f} | {'▲' if indicators['price'] > indicators.get('ma20', 0) else '▼'} |\n"
        report += f"| RSI(14) | {indicators.get('rsi', 0):.2f} | {self._interpret_rsi(indicators.get('rsi', 50))} |\n"
        report += f"| KDJ(K) | {indicators.get('kdj_k', 0):.2f} | {self._interpret_kdj(indicators.get('kdj_k', 50))} |\n"
        report += f"| MACD | {indicators.get('macd_dif', 0):.4f} | {'金叉' if indicators.get('macd_dif', 0) > indicators.get('macd_dea', 0) else '死叉'} |\n"
        report += f"| 布林带位置 | {indicators.get('bb_position', 50):.2f}% | {self._interpret_bb_position(indicators.get('bb_position', 50))} |\n"
        report += f"| 近期涨幅 | {indicators.get('recent_return', 0):.2f}% | - |\n"
        
        report += f"""

## 关键发现

"""
        
        for finding in analysis['key_findings']:
            report += f"- {finding}\n"
        
        report += f"""

## 风险因素

"""
        
        if analysis['risk_factors']:
            for risk in analysis['risk_factors']:
                report += f"- ⚠️ {risk}\n"
        else:
            report += "- 暂无明显风险\n"
        
        report += f"""

## 支撑位与压力位

"""
        
        sr = analysis['support_resistance']
        if sr:
            report += f"| 位置 | 价格 | 说明 |\n|-----|------|------|\n"
            report += f"| 压力位1 | {sr.get('resistance_1', 0):.2f} | 近期高点 |\n"
            report += f"| 压力位2 | {sr.get('resistance_2', 0):.2f} | 5日均线 |\n"
            report += f"| 支撑位1 | {sr.get('support_1', 0):.2f} | 5日均线 |\n"
            report += f"| 支撑位2 | {sr.get('support_2', 0):.2f} | 10日均线 |\n"
            report += f"| 支撑位3 | {sr.get('support_3', 0):.2f} | 20日均线 |\n"
        
        report += f"""

---

## 操作建议

### 明日操作

**预测**: {analysis['prediction']['direction']}（置信度：{analysis['prediction']['confidence']}）

**建议**:
"""
        
        if analysis['prediction']['direction'] in ['上涨', '震荡偏涨']:
            report += """
1. 若高开突破压力位，可适量介入
2. 关注成交量是否配合放大
3. 严格设置止损位（5日均线下方）
4. 盈利超过5%考虑分批止盈
"""
        else:
            report += """
1. 建议观望，等待更好的买入时机
2. 若已有持仓，可考虑减仓
3. 关注是否出现止跌信号
"""
        
        report += f"""

### 风险控制

- 止损位：{sr.get('support_3', 0):.2f} 元（20日均线）
- 止盈位：{analysis['current_price'] * 1.05:.2f} 元（+5%）
- 最大亏损容忍：{analysis['current_price'] * 0.95:.2f} 元（-5%）

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

⚠️ **风险提示**：本分析仅基于技术指标，不构成投资建议。股市有风险，投资需谨慎。
"""
        
        report_file.write_text(report, encoding='utf-8')
        print(f"✅ 分析报告已保存: {report_file.name}")
        
        return str(report_file)
    
    def _interpret_rsi(self, rsi: float) -> str:
        """解释RSI"""
        if rsi > 80:
            return "严重超买 ⚠️"
        elif rsi > 70:
            return "超买 ⚠️"
        elif rsi < 30:
            return "超卖 ✅"
        elif rsi < 20:
            return "严重超卖 ✅"
        else:
            return "正常范围"
    
    def _interpret_kdj(self, k: float) -> str:
        """解释KDJ"""
        if k > 80:
            return "超买区域"
        elif k < 20:
            return "超卖区域"
        else:
            return "正常范围"
    
    def _interpret_bb_position(self, position: float) -> str:
        """解释布林带位置"""
        if position > 95:
            return "极度上轨 ⚠️⚠️"
        elif position > 80:
            return "上轨附近 ⚠️"
        elif position < 5:
            return "极度下轨 ✅✅"
        elif position < 20:
            return "下轨附近 ✅"
        else:
            return "中部正常"
    
    def verify_prediction(self, stock_code: str) -> Dict:
        """验证预测结果"""
        print(f"🔍 验证预测: {stock_code}")
        
        try:
            # 获取今日收盘价
            quotes_result = get_stock_quote(stock_code)
            # get_stock_quote 返回的是字典，键是股票代码，值是行情数据
            quote = quotes_result.get(stock_code, {}) if stock_code in quotes_result else {}
            current_price = quote.get('price', 0)
            
            # 查找之前的选股记录
            history = self._load_history()
            selection = None
            for s in reversed(history['selections']):
                if s['stock_code'] == stock_code:
                    selection = s
                    break
            
            if not selection:
                print("⚠️ 未找到选股记录")
                return {'error': '未找到选股记录'}
            
            # 获取分析记录
            analyses = self._load_analyses()
            analysis = None
            for a in reversed(analyses['analyses']):
                if a['stock_code'] == stock_code:
                    analysis = a
                    break
            
            if not analysis:
                print("⚠️ 未找到分析记录")
                return {'error': '未找到分析记录'}
            
            # 获取预测价格（优先使用指标中的价格）
            prediction_price = analysis['indicators'].get('price', 0) if analysis.get('indicators') else analysis.get('current_price', 0)
            
            if prediction_price <= 0:
                print("⚠️ 预测价格无效")
                return {'error': '预测价格无效'}
            
            # 计算实际涨跌
            actual_change_pct = (current_price - prediction_price) / prediction_price * 100
            
            # 判断预测是否正确
            predicted_direction = analysis['prediction']['direction']
            
            if predicted_direction in ['上涨'] and actual_change_pct > 0:
                result = 'correct'
            elif predicted_direction in ['下跌'] and actual_change_pct < 0:
                result = 'correct'
            elif predicted_direction in ['震荡偏涨'] and actual_change_pct > -1:
                result = 'correct'
            elif predicted_direction in ['震荡偏跌'] and actual_change_pct < 1:
                result = 'correct'
            elif predicted_direction == '震荡' and abs(actual_change_pct) < 2:
                result = 'correct'
            else:
                result = 'incorrect'
            
            # 更新选股记录（使用分析日期匹配）
            analysis_date = analysis.get('analysis_date', '')
            for s in history['selections']:
                if s['stock_code'] == stock_code and s['selection_date'] == analysis_date:
                    s['result'] = result
                    s['actual_price'] = current_price
                    s['actual_change_pct'] = actual_change_pct
                    s['verified_date'] = datetime.now().strftime('%Y-%m-%d')
                    break
            
            self._save_history(history)
            
            # 更新准确度统计
            self._update_accuracy_stats()
            
            # 如果预测错误，记录失败案例
            if result == 'incorrect':
                self._record_failure(selection, analysis, actual_change_pct)
            else:
                self._record_success(selection, analysis, actual_change_pct)
            
            print(f"✅ 验证完成: 实际涨跌{actual_change_pct:+.2f}%，预测{'正确 ✅' if result == 'correct' else '错误 ❌'}")
            
            return {
                'result': result,
                'predicted_direction': predicted_direction,
                'actual_change_pct': actual_change_pct,
                'current_price': current_price,
                'prediction_price': prediction_price
            }
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def _record_success(self, selection: Dict, analysis: Dict, actual_change_pct: float):
        """记录成功案例"""
        analyses = self._load_analyses()
        
        success_case = {
            'stock_code': selection['stock_code'],
            'stock_name': selection['stock_name'],
            'selection_date': selection['selection_date'],
            'prediction': analysis['prediction']['direction'],
            'actual_change_pct': actual_change_pct,
            'strategy': selection['strategy'],
            'success_factors': analysis['prediction']['factors'],
            'timestamp': datetime.now().isoformat()
        }
        
        analyses['success_cases'].append(success_case)
        self._save_analyses(analyses)
        
        # 添加到知识库
        self._add_to_knowledge_base(success_case, is_success=True)
    
    def _record_failure(self, selection: Dict, analysis: Dict, actual_change_pct: float):
        """记录失败案例"""
        analyses = self._load_analyses()
        
        failure_case = {
            'stock_code': selection['stock_code'],
            'stock_name': selection['stock_name'],
            'selection_date': selection['selection_date'],
            'prediction': analysis['prediction']['direction'],
            'actual_change_pct': actual_change_pct,
            'strategy': selection['strategy'],
            'prediction_factors': analysis['prediction']['factors'],
            'risk_factors': analysis['risk_factors'],
            'timestamp': datetime.now().isoformat()
        }
        
        analyses['failure_cases'].append(failure_case)
        self._save_analyses(analyses)
        
        # 深度分析失败原因
        self._analyze_failure_reason(failure_case)
        
        # 添加到知识库
        self._add_to_knowledge_base(failure_case, is_success=False)
    
    def _analyze_failure_reason(self, failure_case: Dict) -> Dict:
        """深度分析失败原因"""
        print(f"🔍 深度分析失败原因...")
        
        reasons = []
        suggestions = []
        
        # 分析可能的原因
        indicators = failure_case.get('prediction_factors', [])
        risks = failure_case.get('risk_factors', [])
        actual_change = failure_case.get('actual_change_pct', 0)
        
        # 原因1：忽视了风险因素
        if risks and any('超买' in r for r in risks):
            reasons.append('虽然预测上涨，但忽视了超买风险')
            suggestions.append('超买指标出现时应降低仓位或回避')
        
        # 原因2：RSI过高
        if 'RSI超买' in str(indicators):
            reasons.append('RSI处于高位，技术性回调压力大')
            suggestions.append('RSI>80时应降低看涨预期')
        
        # 原因3：布林带上轨
        if any('布林带上轨' in r for r in indicators + risks):
            reasons.append('价格触及布林带上轨，回落概率大')
            suggestions.append('价格>90%布林带位置时应谨慎')
        
        # 原因4：短期涨幅过大
        if actual_change < -5:
            reasons.append('短期涨幅过大，获利回吐压力')
            suggestions.append('近期涨幅>15%的股票应等待回调')
        
        # 原因5：市场整体环境影响
        reasons.append('市场整体走势与个股预测不符')
        suggestions.append('选股时应更多考虑市场环境因素')
        
        # 生成改进建议
        improvement = {
            'failure_case': failure_case,
            'root_causes': reasons,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        # 保存改进建议
        improvement_file = self.db_dir / f"failure_analysis_{failure_case['stock_code']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        improvement_file.write_text(json.dumps(improvement, ensure_ascii=False, indent=2))
        
        print(f"✅ 失败分析完成，改进建议已保存")
        
        return improvement
    
    def _add_to_knowledge_base(self, case: Dict, is_success: bool):
        """添加到知识库"""
        try:
            knowledge_file = self.base_dir / "knowledge" / "stock_selection_knowledge.md"
            knowledge_file.parent.mkdir(exist_ok=True)
            
            if not knowledge_file.exists():
                knowledge_file.write_text("# 选股知识库\n\n", encoding='utf-8')
            
            with open(knowledge_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n## {'成功' if is_success else '失败'}案例 ({case.get('timestamp', '')[:10]})\n")
                f.write(f"- 股票: {case.get('stock_name', '')}({case.get('stock_code', '')})  \n")
                f.write(f"- 策略: {case.get('strategy', '')}  \n")
                f.write(f"- 预测: {case.get('prediction', '')}  \n")
                f.write(f"- 实际: {case.get('actual_change_pct', 0):+.2f}%  \n")
                
                if not is_success and 'root_causes' in case:
                    f.write(f"- 失败原因: {', '.join(case.get('root_causes', []))}  \n")
                    f.write(f"- 改进建议: {', '.join(case.get('suggestions', []))}  \n")
                elif is_success:
                    f.write(f"- 成功因素: {', '.join(case.get('success_factors', []))}  \n")
            
            print(f"✅ 知识库已更新")
            
        except Exception as e:
            print(f"⚠️ 更新知识库失败: {e}")
    
    def get_accuracy_stats(self) -> Dict:
        """获取准确度统计"""
        return self._load_accuracy_stats()
    
    def generate_daily_selection_report(self, selection: Dict, analysis: Dict) -> str:
        """生成每日选股报告"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"每日选股报告_{report_date}.md"
        
        report = f"""# 📊 每日选股报告

## 日期
{report_date}

---

## 今日选股

**股票**: {selection['stock_name']}({selection['stock_code']})

**当前价格**: {selection['price']:.2f} 元

**选股策略**: {self.strategies[selection['strategy']]['name'] if selection['strategy'] in self.strategies else selection['strategy']}

**策略评分**:
- 价值评分: {selection['strategy_scores'].get('value', 0):.1f}/100
- 动量评分: {selection['strategy_scores'].get('momentum', 0):.1f}/100
- 技术评分: {selection['strategy_scores'].get('technical', 0):.1f}/100

---

## 技术分析与预测

**预测方向**: {analysis['prediction']['direction']}

**置信度**: {analysis['prediction']['confidence']}

**综合评分**: {analysis['prediction']['score']}/100

**预测依据**:
"""
        
        for factor in analysis['prediction']['factors']:
            report += f"- {factor}\n"
        
        report += f"""

## 关键指标

| 指标 | 数值 |
|-----|------|
| MA5 | {analysis['indicators'].get('ma5', 0):.2f} |
| MA10 | {analysis['indicators'].get('ma10', 0):.2f} |
| MA20 | {analysis['indicators'].get('ma20', 0):.2f} |
| RSI | {analysis['indicators'].get('rsi', 0):.2f} |
| KDJ(K) | {analysis['indicators'].get('kdj_k', 0):.2f} |
| MACD | {analysis['indicators'].get('macd_dif', 0):.4f} |
| 布林带位置 | {analysis['indicators'].get('bb_position', 0):.2f}% |
| 近期涨幅 | {analysis['indicators'].get('recent_return', 0):.2f}% |

---

## 风险提示

"""
        
        if analysis['risk_factors']:
            for risk in analysis['risk_factors']:
                report += f"- ⚠️ {risk}\n"
        else:
            report += "- 暂无明显风险\n"
        
        report += f"""

## 操作建议

- 买入区间: {analysis['current_price']:.2f}-{analysis['current_price'] * 1.02:.2f} 元
- 止损位: {analysis['support_resistance'].get('support_3', 0):.2f} 元
- 止盈位: {analysis['current_price'] * 1.05:.2f} 元

---

## 准确度统计

| 指标 | 数值 |
|-----|------|
| 总预测次数 | {self._load_accuracy_stats()['total_predictions']} |
| 正确次数 | {self._load_accuracy_stats()['correct_predictions']} |
| 错误次数 | {self._load_accuracy_stats()['incorrect_predictions']} |
| 准确率 | {self._load_accuracy_stats()['accuracy_rate']:.2f}% |

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

⚠️ **风险提示**：本报告仅基于技术分析，不构成投资建议。股市有风险，投资需谨慎。
"""
        
        report_file.write_text(report, encoding='utf-8')
        print(f"✅ 每日选股报告已保存: {report_file.name}")
        
        return str(report_file)
    
    def run_daily_cycle(self) -> Dict:
        """运行完整的每日选股流程"""
        print("=" * 70)
        print("🎯 自主选股分析系统 - 每日选股流程")
        print("=" * 70)
        print()
        
        # 1. 选股
        print("【步骤1】选股")
        print("-" * 50)
        selection = self.select_stock()
        print()
        
        # 2. 分析预测
        print("【步骤2】技术分析与预测")
        print("-" * 50)
        analysis = self.analyze_stock(selection['stock_code'], selection['stock_name'])
        print()
        
        # 3. 生成报告
        print("【步骤3】生成每日选股报告")
        print("-" * 50)
        report_file = self.generate_daily_selection_report(selection, analysis)
        print()
        
        # 4. 显示准确度统计
        print("【步骤4】准确度统计")
        print("-" * 50)
        stats = self.get_accuracy_stats()
        print(f"总预测次数: {stats['total_predictions']}")
        print(f"正确次数: {stats['correct_predictions']}")
        print(f"错误次数: {stats['incorrect_predictions']}")
        print(f"准确率: {stats['accuracy_rate']:.2f}%")
        print()
        
        print("=" * 70)
        print("✅ 每日选股流程完成！")
        print("=" * 70)
        
        return {
            'selection': selection,
            'analysis': analysis,
            'report_file': report_file,
            'accuracy_stats': stats
        }


def main():
    """主函数"""
    system = StockSelectionSystem()
    system.run_daily_cycle()


if __name__ == '__main__':
    main()
