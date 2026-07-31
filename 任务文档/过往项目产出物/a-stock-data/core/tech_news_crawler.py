#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科技前沿资讯爬虫系统
- 每天上午9:30、下午14:30爬取科技类前沿资讯
- 关注十五五规划相关产业
- 结合缠论进行知识沉淀
- 识别反向信号（自媒体、标题党、资本雇佣枪手）
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# 可靠资讯来源配置
RELIABLE_SOURCES = {
    "国家层面": [
        {"name": "工信部", "url": "https://www.miit.gov.cn/", "type": "government"},
        {"name": "科技部", "url": "https://www.most.gov.cn/", "type": "government"},
        {"name": "发改委", "url": "https://www.ndrc.gov.cn/", "type": "government"},
        {"name": "中国政府网", "url": "http://www.gov.cn/", "type": "government"},
    ],
    "行业权威": [
        {"name": "电子信息产业网", "url": "http://www.cena.com.cn/", "type": "industry"},
        {"name": "中国半导体行业协会", "url": "http://www.csia.net.cn/", "type": "industry"},
        {"name": "中国电子报", "url": "http://www.cena.com.cn/", "type": "industry"},
    ],
    "大企业官网": [
        {"name": "华为", "url": "https://www.huawei.com/cn/", "type": "enterprise"},
        {"name": "中兴", "url": "https://www.zte.com.cn/", "type": "enterprise"},
        {"name": "中芯国际", "url": "https://www.smic.com/", "type": "enterprise"},
        {"name": "宁德时代", "url": "https://www.catl.com/", "type": "enterprise"},
        {"name": "比亚迪", "url": "https://www.byd.com/", "type": "enterprise"},
    ],
    "专业财经媒体": [
        {"name": "财新网", "url": "https://www.caixin.com/", "type": "finance"},
        {"name": "第一财经", "url": "https://www.yicai.com/", "type": "finance"},
        {"name": "证券时报", "url": "https://www.stcn.com/", "type": "finance"},
        {"name": "上海证券报", "url": "http://www.cnstock.com/", "type": "finance"},
    ],
    "科技媒体": [
        {"name": "36氪", "url": "https://36kr.com/", "type": "tech"},
        {"name": "虎嗅", "url": "https://www.huxiu.com/", "type": "tech"},
        {"name": "科技日报", "url": "http://www.stdaily.com/", "type": "tech"},
    ]
}

# 十五五重点关注领域
FIFTEEN_FIVE_FIELDS = [
    "人工智能", "AI", "大模型", "机器人", "人形机器人",
    "半导体", "芯片", "集成电路", "先进封装", "光刻",
    "新能源", "光伏", "风电", "储能", "氢能",
    "数字经济", "数据中心", "算力", "云计算", "大数据",
    "工业互联网", "智能制造", "工业4.0",
    "生物医药", "创新药", "基因编辑",
    "航天", "商业航天", "卫星互联网",
    "量子", "量子计算", "量子通信",
    "新材料", "稀土", "碳纤维", "石墨烯",
    "智能汽车", "自动驾驶", "车联网",
    "低空经济", "无人机", "通用航空"
]

# 反向信号关键词（标题党、资本雇佣枪手特征）
REVERSE_SIGNAL_KEYWORDS = [
    "暴涨", "暴跌", "必涨", "必跌", "翻倍", "妖股",
    "内幕", "独家", "重磅", "惊天", "震惊", "秘密",
    "主力", "游资", "机构", "大佬", "牛散",
    "即将", "马上", "立刻", "今日", "最新",
    "手把手", "带你", "教你", "跟着", "躺赢",
    "定律", "战法", "秘籍", "绝招", "心法",
    "抄底", "逃顶", "上车", "下车", "接力"
]

class TechNewsCrawler:
    """科技资讯爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        })
        self.news_cache = {}
        
    def crawl_news(self, source_name, url, source_type):
        """爬取单个来源的新闻"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据不同类型提取新闻
            news_items = []
            
            if source_type == 'government':
                news_items = self._parse_government(soup, source_name)
            elif source_type == 'enterprise':
                news_items = self._parse_enterprise(soup, source_name)
            elif source_type == 'finance':
                news_items = self._parse_finance(soup, source_name)
            elif source_type == 'tech':
                news_items = self._parse_tech(soup, source_name)
            elif source_type == 'industry':
                news_items = self._parse_industry(soup, source_name)
            
            return news_items
            
        except Exception as e:
            print(f"❌ 爬取 {source_name} 失败: {e}")
            return []
    
    def _parse_government(self, soup, source_name):
        """解析政府网站"""
        news_items = []
        titles = soup.find_all(['h1', 'h2', 'h3', 'a'], href=True)
        
        for title in titles[:20]:
            text = title.get_text(strip=True)
            if len(text) > 5 and len(text) < 100:
                link = title.get('href', '')
                if link:
                    if not link.startswith('http'):
                        link = f"https://www.miit.gov.cn{link}"
                news_items.append({
                    'title': text,
                    'url': link,
                    'source': source_name,
                    'type': 'government',
                    'crawl_time': datetime.now().isoformat()
                })
        return news_items
    
    def _parse_enterprise(self, soup, source_name):
        """解析企业官网"""
        news_items = []
        titles = soup.find_all(['h1', 'h2', 'h3', 'a'], href=True)
        
        for title in titles[:15]:
            text = title.get_text(strip=True)
            if len(text) > 5 and len(text) < 100:
                link = title.get('href', '')
                if link:
                    if not link.startswith('http'):
                        link = f"https://www.huawei.com{link}" if 'huawei' in source_name.lower() else link
                news_items.append({
                    'title': text,
                    'url': link,
                    'source': source_name,
                    'type': 'enterprise',
                    'crawl_time': datetime.now().isoformat()
                })
        return news_items
    
    def _parse_finance(self, soup, source_name):
        """解析财经媒体"""
        news_items = []
        titles = soup.find_all(['h1', 'h2', 'h3', 'a'], href=True)
        
        for title in titles[:20]:
            text = title.get_text(strip=True)
            if len(text) > 10 and len(text) < 120:
                link = title.get('href', '')
                if link and link.startswith('http'):
                    news_items.append({
                        'title': text,
                        'url': link,
                        'source': source_name,
                        'type': 'finance',
                        'crawl_time': datetime.now().isoformat()
                    })
        return news_items
    
    def _parse_tech(self, soup, source_name):
        """解析科技媒体"""
        news_items = []
        titles = soup.find_all(['h1', 'h2', 'h3', 'a'], href=True)
        
        for title in titles[:25]:
            text = title.get_text(strip=True)
            if len(text) > 10 and len(text) < 120:
                link = title.get('href', '')
                if link and link.startswith('http'):
                    news_items.append({
                        'title': text,
                        'url': link,
                        'source': source_name,
                        'type': 'tech',
                        'crawl_time': datetime.now().isoformat()
                    })
        return news_items
    
    def _parse_industry(self, soup, source_name):
        """解析行业网站"""
        news_items = []
        titles = soup.find_all(['h1', 'h2', 'h3', 'a'], href=True)
        
        for title in titles[:15]:
            text = title.get_text(strip=True)
            if len(text) > 8 and len(text) < 100:
                link = title.get('href', '')
                if link:
                    if not link.startswith('http'):
                        link = f"http://www.csia.net.cn{link}"
                news_items.append({
                    'title': text,
                    'url': link,
                    'source': source_name,
                    'type': 'industry',
                    'crawl_time': datetime.now().isoformat()
                })
        return news_items
    
    def filter_relevant_news(self, all_news):
        """筛选与十五五相关的新闻"""
        relevant = []
        for news in all_news:
            title = news['title'].lower()
            
            # 过滤无效标题
            if len(title.strip()) < 3 or len(title) > 100:
                continue
            # 过滤非中文标题（简单判断）
            if all(ord(c) < 128 for c in title):
                continue
            
            # 检查是否包含十五五相关领域关键词
            for field in FIFTEEN_FIVE_FIELDS:
                if field.lower() in title:
                    news['relevant_field'] = field
                    relevant.append(news)
                    break
        return relevant
    
    def analyze_reverse_signal(self, news):
        """分析反向信号（标题党、资本雇佣枪手）"""
        title = news['title']
        signal_score = 0
        signal_keywords = []
        
        for keyword in REVERSE_SIGNAL_KEYWORDS:
            if keyword in title:
                signal_score += 1
                signal_keywords.append(keyword)
        
        news['reverse_signal_score'] = signal_score
        news['reverse_signal_keywords'] = signal_keywords
        news['is_reverse_signal'] = signal_score >= 3
        
        return news
    
    def extract_knowledge(self, news):
        """提取知识要点"""
        title = news['title']
        knowledge = {
            'keywords': [],
            'industry': '',
            'impact_level': 'low',
            'potential_stocks': []
        }
        
        # 提取关键词
        for field in FIFTEEN_FIVE_FIELDS:
            if field in title:
                knowledge['keywords'].append(field)
                knowledge['industry'] = field
        
        # 判断影响级别
        if any(keyword in title for keyword in ['政策', '规划', '国务院', '发改委', '工信部', '科技部', '成立', '发布', '出台', '正式']):
            knowledge['impact_level'] = 'high'
        elif any(keyword in title for keyword in ['技术突破', '研发', '专利', '创新', '新一代', '首次']):
            knowledge['impact_level'] = 'medium'
        
        # 关联股票
        field_stocks = {
            '半导体': ['600584', '002156', '688347', '002185'],
            '人工智能': ['300750', '000977', '300454', '603019'],
            '新能源': ['300750', '002594', '600438', '688599'],
            '光伏': ['601012', '002594', '300274', '600438'],
            '机器人': ['300024', '002527', '600580', '300376'],
            '数据中心': ['000977', '300779', '603019', '300383'],
            '算力': ['002156', '600584', '300750', '688012'],
        }
        
        for field, stocks in field_stocks.items():
            if field in title or any(keyword in title for keyword in ['AI', '大模型', '芯片']):
                knowledge['potential_stocks'].extend(stocks)
        
        news['knowledge'] = knowledge
        return news
    
    def run_crawl(self):
        """执行完整爬取流程"""
        print("=" * 70)
        print("🚀 科技前沿资讯爬虫启动")
        print("=" * 70)
        print(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        all_news = []
        
        # 爬取所有来源
        for category, sources in RELIABLE_SOURCES.items():
            print(f"📡 正在爬取 {category}...")
            for source in sources:
                print(f"   🔍 {source['name']}")
                news_items = self.crawl_news(source['name'], source['url'], source['type'])
                all_news.extend(news_items)
                print(f"      获取 {len(news_items)} 条新闻")
        
        # 去重
        unique_news = []
        seen_titles = set()
        for news in all_news:
            title = news['title']
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        print(f"\n📊 共获取 {len(unique_news)} 条不重复新闻")
        
        # 筛选相关新闻
        relevant_news = self.filter_relevant_news(unique_news)
        print(f"🎯 与十五五相关的新闻: {len(relevant_news)} 条")
        
        # 分析每条新闻
        analyzed_news = []
        for news in relevant_news:
            news = self.analyze_reverse_signal(news)
            news = self.extract_knowledge(news)
            analyzed_news.append(news)
        
        # 分离正常新闻和反向信号
        normal_news = [n for n in analyzed_news if not n['is_reverse_signal']]
        reverse_news = [n for n in analyzed_news if n['is_reverse_signal']]
        
        print(f"✅ 正常资讯: {len(normal_news)} 条")
        print(f"⚠️ 反向信号: {len(reverse_news)} 条")
        
        # 保存结果
        result = {
            'crawl_time': datetime.now().isoformat(),
            'total_news': len(unique_news),
            'relevant_news': len(relevant_news),
            'normal_news': normal_news,
            'reverse_signals': reverse_news,
            'knowledge_extracted': len([n for n in analyzed_news if n['knowledge']['impact_level'] == 'high'])
        }
        
        # 保存到文件
        output_file = PROJECT_DIR / "reports" / f"tech_news_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 结果已保存到: {output_file}")
        
        # 生成知识沉淀报告
        self.generate_knowledge_report(result)
        
        return result
    
    def generate_knowledge_report(self, result):
        """生成知识沉淀报告"""
        report = f"""# 科技资讯知识沉淀报告
\n## 📅 报告信息
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **爬取新闻总数**: {result['total_news']}
- **十五五相关**: {result['relevant_news']}
- **高影响力资讯**: {result['knowledge_extracted']}
- **反向信号警告**: {len(result['reverse_signals'])}
\n## 🎯 今日重点资讯
\n### 高影响力资讯
\n"""
        
        high_impact = [n for n in result['normal_news'] if n['knowledge']['impact_level'] == 'high']
        for i, news in enumerate(high_impact[:5], 1):
            report += f"{i}. **{news['title']}**\n"
            report += f"   - 来源: {news['source']}\n"
            report += f"   - 领域: {news['knowledge']['industry']}\n"
            report += f"   - 关联股票: {', '.join(news['knowledge']['potential_stocks'])}\n\n"
        
        report += """### 中等影响力资讯
\n"""
        medium_impact = [n for n in result['normal_news'] if n['knowledge']['impact_level'] == 'medium']
        for i, news in enumerate(medium_impact[:5], 1):
            report += f"{i}. {news['title']} - {news['source']}\n"
        
        report += f"""\n## ⚠️ 反向信号警告 ({len(result['reverse_signals'])}条)
\n"""
        for i, news in enumerate(result['reverse_signals'][:5], 1):
            report += f"{i}. **{news['title']}**\n"
            report += f"   - 风险关键词: {', '.join(news['reverse_signal_keywords'])}\n"
            report += f"   - ⚠️ 可能是资本雇佣枪手发文，建议反向思考\n\n"
        
        report += """## 💡 缠论视角分析
\n### 趋势参数参考
\n1. **政策面**: 关注政策出台对相关板块的影响
2. **资金面**: 结合北向资金流向判断市场情绪
3. **技术面**: 等待中枢形成后的方向选择
4. **风险提示**: 反向信号出现时需谨慎追高
\n### 操作建议
\n- 高影响力政策资讯出现时，观察相关板块的反应
- 反向信号密集出现时，考虑减仓或对冲
- 结合缠论级别判断，选择合适的操作周期
\n---
*报告由科技资讯爬虫系统自动生成*
"""
        
        report_file = PROJECT_DIR / "reports" / f"tech_knowledge_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📝 知识沉淀报告已保存: {report_file}")

def main():
    """主函数"""
    crawler = TechNewsCrawler()
    crawler.run_crawl()

if __name__ == '__main__':
    main()
