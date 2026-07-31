"""
市场动态深度分析系统
专注于挖掘"低调提及"的信息，识别反向信号
分析逻辑：
1. 关注官方媒体"顺带一提"的内容
2. 识别自媒体热炒的反向信号
3. 挖掘政策文件中的隐含信息
4. 关注行业会议中的低调发言
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from collections import Counter

class MarketDynamicAnalyzer:
    """市场动态深度分析器"""
    
    def __init__(self):
        self.news_data = []
        self.analysis_results = []
    
    def load_news_data(self, news_list):
        """加载新闻数据"""
        self.news_data = news_list
    
    def analyze_low_key_signals(self):
        """分析低调提及的信号"""
        results = []
        
        for news in self.news_data:
            analysis = {
                'title': news.get('title', ''),
                'source': news.get('source', ''),
                'content': news.get('content', ''),
                'publish_time': news.get('publish_time', ''),
                'low_key_score': 0,
                'keywords': [],
                'potential_value': 'neutral',
                'confidence': 0,
                'analysis': '',
                'action': 'monitor',
            }
            
            # 分析标题中的低调信号
            title = news.get('title', '')
            content = news.get('content', '')
            
            # 关键词权重
            low_key_words = {
                '提及': 10,
                '提到': 10,
                '表示': 10,
                '指出': 10,
                '强调': 10,
                '推进': 15,
                '部署': 15,
                '加快': 15,
                '支持': 20,
                '印发': 25,
                '发布': 25,
                '出台': 25,
                '规划': 30,
                '政策': 30,
                '意见': 30,
                '通知': 30,
                '方案': 30,
            }
            
            tech_keywords = [
                '人工智能', 'AI', '大模型', '算力', '半导体', '芯片',
                '量子', '新能源', '光伏', '储能', '氢能', '充电桩',
                '数字经济', '数据要素', '工业互联网', '智能制造',
                '碳达峰', '碳中和', '绿色发展', '低空经济', '卫星互联网'
            ]
            
            # 计算低调提及分数
            score = 0
            keywords_found = []
            
            for word, weight in low_key_words.items():
                if word in title or word in content:
                    score += weight
                    keywords_found.append(word)
            
            # 检查官方来源（官方媒体的低调提及更有价值）
            official_sources = ['新华社', '人民日报', '央视', '发改委', '工信部', '科技部']
            for source in official_sources:
                if source in news.get('source', '') or source in content:
                    score += 30
                    analysis['potential_value'] = 'high'
            
            # 检查科技关键词
            for tech in tech_keywords:
                if tech in title or tech in content:
                    score += 10
                    keywords_found.append(tech)
            
            analysis['low_key_score'] = score
            analysis['keywords'] = list(set(keywords_found))
            
            # 评估潜在价值
            if score >= 80:
                analysis['potential_value'] = 'high'
                analysis['confidence'] = min(95, score)
                analysis['analysis'] = f"⚠️ 高度关注！官方低调提及关键领域，可能蕴含重大机会"
                analysis['action'] = 'focus'
            elif score >= 50:
                analysis['potential_value'] = 'medium'
                analysis['confidence'] = min(75, score)
                analysis['analysis'] = f"📌 值得关注！涉及重要政策或技术方向"
                analysis['action'] = 'monitor'
            else:
                analysis['potential_value'] = 'low'
                analysis['confidence'] = min(50, score)
                analysis['analysis'] = "一般信息，继续观察"
                analysis['action'] = 'watch'
            
            results.append(analysis)
        
        results.sort(key=lambda x: x['low_key_score'], reverse=True)
        return results
    
    def analyze_hype_signals(self):
        """分析热炒信号（反向指标）"""
        results = []
        
        hype_patterns = [
            ('重磅', 10), ('炸裂', 15), ('震惊', 15), ('暴涨', 10),
            ('翻倍', 15), ('妖王', 20), ('龙头', 10), ('妖股', 20),
            ('必看', 5), ('干货', 5), ('深度', 5), ('独家', 10),
            ('揭秘', 10), ('真相', 10), ('爆发', 15), ('风口', 15),
            ('利好', 10), ('利空', 10), ('涨停', 10), ('跌停', 10),
        ]
        
        for news in self.news_data:
            title = news.get('title', '')
            content = news.get('content', '')
            
            hype_score = 0
            hype_words = []
            
            for pattern, weight in hype_patterns:
                if pattern in title:
                    hype_score += weight * 2
                    hype_words.append(pattern)
                elif pattern in content:
                    hype_score += weight
                    hype_words.append(pattern)
            
            if hype_score >= 30:
                results.append({
                    'title': title,
                    'source': news.get('source', ''),
                    'hype_score': hype_score,
                    'hype_words': hype_words,
                    'risk_level': 'high' if hype_score >= 50 else 'medium',
                    'analysis': f"⚠️ 警惕！过度炒作迹象明显，可能是反向指标",
                    'action': 'avoid' if hype_score >= 50 else 'cautious',
                })
        
        results.sort(key=lambda x: x['hype_score'], reverse=True)
        return results
    
    def analyze_policy_implications(self):
        """分析政策隐含信息"""
        results = []
        
        policy_keywords = {
            '支持': ['力度加大', '持续推进', '深入实施'],
            '发展': ['高质量', '新质生产力', '现代化'],
            '改革': ['深化', '攻坚', '突破'],
            '规划': ['十四五', '十五五', '中长期'],
            '投资': ['加大', '引导', '鼓励'],
            '补贴': ['延续', '提高', '扩大'],
        }
        
        for news in self.news_data:
            content = news.get('content', '')
            title = news.get('title', '')
            
            policy_score = 0
            found_items = []
            
            for main_keyword, indicators in policy_keywords.items():
                if main_keyword in title or main_keyword in content:
                    policy_score += 15
                    found_items.append(main_keyword)
                    
                    for indicator in indicators:
                        if indicator in content:
                            policy_score += 10
                            found_items.append(indicator)
            
            if policy_score >= 30:
                results.append({
                    'title': title,
                    'policy_score': policy_score,
                    'keywords': list(set(found_items)),
                    'analysis': f"📊 政策信号！涉及重要政策方向调整",
                    'action': 'research',
                })
        
        results.sort(key=lambda x: x['policy_score'], reverse=True)
        return results
    
    def generate_daily_report(self):
        """生成每日市场动态分析报告"""
        if not self.news_data:
            return "暂无市场动态数据"
        
        low_key_results = self.analyze_low_key_signals()
        hype_results = self.analyze_hype_signals()
        policy_results = self.analyze_policy_implications()
        
        report = f"""
# 📊 市场动态深度分析报告
**报告日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 一、低调提及信号（重点关注）

{self._format_section(low_key_results[:5], 'low_key')}

---

## 二、热炒信号预警（反向指标）

{self._format_section(hype_results[:3], 'hype')}

---

## 三、政策隐含信息

{self._format_section(policy_results[:3], 'policy')}

---

## 四、今日重点关注

{self._generate_summary(low_key_results, hype_results)}

---

## 五、投资建议

{self._generate_investment_advice(low_key_results, hype_results)}

---

**免责声明**: 本报告仅供参考，不构成投资建议
"""
        
        return report
    
    def _format_section(self, items, section_type):
        """格式化报告章节"""
        if not items:
            return "暂无数据"
        
        formatted = ""
        for i, item in enumerate(items, 1):
            if section_type == 'low_key':
                emoji = '🔥' if item['potential_value'] == 'high' else '📌' if item['potential_value'] == 'medium' else '💡'
                formatted += f"{i}. {emoji} **{item['title']}**\n"
                formatted += f"   - 来源: {item['source']}\n"
                formatted += f"   - 评分: {item['low_key_score']}\n"
                formatted += f"   - 关键词: {', '.join(item['keywords'])}\n"
                formatted += f"   - 分析: {item['analysis']}\n\n"
            elif section_type == 'hype':
                emoji = '💥' if item['risk_level'] == 'high' else '⚠️'
                formatted += f"{i}. {emoji} **{item['title']}**\n"
                formatted += f"   - 热度评分: {item['hype_score']}\n"
                formatted += f"   - 风险等级: {item['risk_level']}\n"
                formatted += f"   - 分析: {item['analysis']}\n\n"
            elif section_type == 'policy':
                formatted += f"{i}. 📊 **{item['title']}**\n"
                formatted += f"   - 政策评分: {item['policy_score']}\n"
                formatted += f"   - 关键词: {', '.join(item['keywords'])}\n"
                formatted += f"   - 分析: {item['analysis']}\n\n"
        
        return formatted
    
    def _generate_summary(self, low_key, hype):
        """生成总结"""
        summary = ""
        
        high_value_items = [i for i in low_key if i['potential_value'] == 'high']
        high_risk_items = [i for i in hype if i['risk_level'] == 'high']
        
        if high_value_items:
            summary += f"✅ **重点机会**: 今日发现 {len(high_value_items)} 个高价值低调信号\n"
            for item in high_value_items[:3]:
                summary += f"   - {item['title'][:30]}...\n"
        
        if high_risk_items:
            summary += f"\n❌ **风险预警**: 今日发现 {len(high_risk_items)} 个高风险热炒信号\n"
            for item in high_risk_items[:2]:
                summary += f"   - {item['title'][:30]}...\n"
        
        if not high_value_items and not high_risk_items:
            summary = "今日市场动态较为平稳，继续观察"
        
        return summary
    
    def _generate_investment_advice(self, low_key, hype):
        """生成投资建议"""
        advice = ""
        
        high_value_items = [i for i in low_key if i['potential_value'] == 'high']
        high_risk_items = [i for i in hype if i['risk_level'] == 'high']
        
        if high_value_items:
            advice += "📈 **关注方向**: "
            keywords = []
            for item in high_value_items:
                keywords.extend(item['keywords'])
            top_keywords = [k[0] for k in Counter(keywords).most_common(5)]
            advice += ", ".join(top_keywords) + "\n\n"
        
        if high_risk_items:
            advice += "⚠️ **规避方向**: "
            hype_words = []
            for item in high_risk_items:
                hype_words.extend(item['hype_words'])
            top_hype = [k[0] for k in Counter(hype_words).most_common(3)]
            advice += ", ".join(top_hype) + "\n\n"
        
        advice += """💡 **操作建议**:
   1. 对高价值低调信号进行深度研究
   2. 对热炒信号保持警惕，避免追高
   3. 结合技术分析确认入场时机
   4. 严格执行止损纪律
"""
        
        return advice


def run_market_analysis(news_data):
    """运行市场动态分析"""
    analyzer = MarketDynamicAnalyzer()
    analyzer.load_news_data(news_data)
    report = analyzer.generate_daily_report()
    return report


if __name__ == "__main__":
    # 示例数据
    sample_news = [
        {
            'title': '发改委：将加快推进新型信息基础设施建设',
            'source': '新华社',
            'content': '发改委有关负责人表示，将加快推进新型信息基础设施建设，支持人工智能、大数据等技术发展。',
            'publish_time': '2026-05-26 09:30',
        },
        {
            'title': '炸裂！某AI龙头业绩暴增1000%，下周必看！',
            'source': '某自媒体',
            'content': '独家揭秘！这只AI龙头即将翻倍，错过再等一年！',
            'publish_time': '2026-05-26 10:00',
        },
        {
            'title': '工信部：支持半导体产业高质量发展',
            'source': '工信部官网',
            'content': '工信部表示，将继续支持半导体产业高质量发展，完善产业链布局。',
            'publish_time': '2026-05-26 11:00',
        },
        {
            'title': '重磅！低空经济迎来政策利好',
            'source': '某财经媒体',
            'content': '低空经济概念爆发！这些龙头股即将起飞！',
            'publish_time': '2026-05-26 14:00',
        },
        {
            'title': '科技部：提及量子计算技术研发进展',
            'source': '科技部',
            'content': '科技部有关负责人在会议上提及量子计算技术研发取得新进展。',
            'publish_time': '2026-05-26 15:00',
        },
    ]
    
    report = run_market_analysis(sample_news)
    print(report)
