#!/usr/bin/env python3
"""
大模型信息雷达 - 自动采集大模型领域最新信息
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
import re
import time

import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path(__file__).parent.parent / 'logs' / f'llm-info-radar-{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LLMAgent:
    def __init__(self, config_path=None):
        # 获取项目根目录 - 从 llm-info-radar/src/main.py 向上4级到达 llm-expert-knowledge-base
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.inbox_dir = self.project_root / '01_inbox'
        self.raw_dir = self.project_root / '02_raw'
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 确保目录存在
        self.inbox_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        
        # 已存在的内容哈希
        self.existing_hashes = set()
        self._load_existing_hashes()
        
        # 今日采集的内容
        self.collected_items = []
        
        # 失败的来源
        self.failed_sources = []
    
    def _load_config(self, config_path=None):
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'config.json'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 未找到，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "sources": [
                {"name": "arXiv cs.CL", "url": "https://arxiv.org/list/cs.CL/recent", "type": "arxiv"},
                {"name": "arXiv cs.LG", "url": "https://arxiv.org/list/cs.LG/recent", "type": "arxiv"},
                {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog", "type": "blog"},
                {"name": "Hugging Face Papers", "url": "https://huggingface.co/papers", "type": "papers"},
                {"name": "OpenAI Blog", "url": "https://openai.com/blog", "type": "blog"},
                {"name": "Anthropic Research", "url": "https://www.anthropic.com/research", "type": "blog"},
                {"name": "DeepMind Blog", "url": "https://deepmind.google/discover/blog/", "type": "blog"},
                {"name": "GitHub Trending Python", "url": "https://github.com/trending/python?since=daily", "type": "github"},
                {"name": "GitHub Trending ML", "url": "https://github.com/trending/machine-learning?since=daily", "type": "github"},
                {"name": "机器之心", "url": "https://www.jiqizhixin.com/", "type": "blog"},
                {"name": "量子位", "url": "https://www.qbitai.com/", "type": "blog"},
                {"name": "InfoQ AI", "url": "https://www.infoq.cn/topic/AI", "type": "blog"}
            ],
            "max_summary_length": 3000,
            "request_timeout": 30,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def _load_existing_hashes(self):
        """加载已存在内容的哈希值（过去7天）"""
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        for dir_path in [self.inbox_dir, self.raw_dir]:
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.glob('*.md'):
                try:
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time >= seven_days_ago:
                        content = file_path.read_text(encoding='utf-8')
                        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
                        self.existing_hashes.add(content_hash)
                except Exception as e:
                    logger.warning(f"读取文件 {file_path} 失败: {e}")
    
    def _is_duplicate(self, content):
        """检查内容是否重复"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        return content_hash in self.existing_hashes
    
    def _fetch_url(self, url):
        """获取网页内容"""
        headers = {
            'User-Agent': self.config.get('user_agent', 'Mozilla/5.0')
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=self.config.get('request_timeout', 30))
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            logger.error(f"访问 {url} 失败: {e}")
            return None
    
    def _parse_arxiv(self, source):
        """解析arXiv页面"""
        items = []
        html = self._fetch_url(source['url'])
        if not html:
            return items
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            entries = soup.find_all('dd')
            
            for entry in entries[:20]:
                try:
                    title_elem = entry.find('div', class_='list-title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True).replace('Title:', '').strip()
                    link_elem = entry.find_previous('dt').find('a', href=re.compile(r'/abs/'))
                    link = f"https://arxiv.org{link_elem['href']}" if link_elem else source['url']
                    
                    authors_elem = entry.find('div', class_='list-authors')
                    authors = authors_elem.get_text(strip=True).replace('Authors:', '').strip() if authors_elem else ''
                    
                    abstract_elem = entry.find('p', class_='abstract')
                    abstract = abstract_elem.get_text(strip=True) if abstract_elem else ''
                    
                    item = {
                        'title': title,
                        'url': link,
                        'source': source['name'],
                        'author': authors,
                        'publish_time': datetime.now().strftime('%Y-%m-%d'),
                        'summary': abstract[:self.config.get('max_summary_length', 3000)],
                        'importance': self._calculate_importance(title, abstract, authors)
                    }
                    
                    if not self._is_duplicate(title + abstract):
                        items.append(item)
                        self.existing_hashes.add(hashlib.md5((title + abstract).encode('utf-8')).hexdigest())
                except Exception as e:
                    logger.warning(f"解析arXiv条目失败: {e}")
                    continue
        except Exception as e:
            logger.error(f"解析 {source['name']} 失败: {e}")
        
        return items
    
    def _parse_blog(self, source):
        """解析博客页面"""
        items = []
        html = self._fetch_url(source['url'])
        if not html:
            return items
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 尝试找到文章链接 - 这是通用逻辑，不同网站可能需要调整
            article_links = soup.find_all('a', href=True)
            for link in article_links[:30]:
                try:
                    href = link['href']
                    if not href.startswith('http'):
                        href = urljoin(source['url'], href)
                    
                    text = link.get_text(strip=True)
                    if len(text) < 10:
                        continue
                    
                    item = {
                        'title': text,
                        'url': href,
                        'source': source['name'],
                        'author': '',
                        'publish_time': datetime.now().strftime('%Y-%m-%d'),
                        'summary': '',
                        'importance': 3
                    }
                    
                    if not self._is_duplicate(text + href):
                        items.append(item)
                        self.existing_hashes.add(hashlib.md5((text + href).encode('utf-8')).hexdigest())
                except Exception as e:
                    continue
        except Exception as e:
            logger.error(f"解析 {source['name']} 失败: {e}")
        
        return items[:15]
    
    def _parse_github(self, source):
        """解析GitHub Trending"""
        items = []
        html = self._fetch_url(source['url'])
        if not html:
            return items
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            repos = soup.find_all('article', class_='Box-row')
            
            for repo in repos[:15]:
                try:
                    name_elem = repo.find('h2', class_='h3')
                    if not name_elem:
                        continue
                    
                    repo_name = name_elem.get_text(strip=True).replace(' ', '')
                    link = f"https://github.com/{repo_name}"
                    
                    desc_elem = repo.find('p', class_='col-9')
                    description = desc_elem.get_text(strip=True) if desc_elem else ''
                    
                    stars_elem = repo.find('a', href=re.compile(r'/stargazers'))
                    stars_text = stars_elem.get_text(strip=True) if stars_elem else '0'
                    
                    item = {
                        'title': repo_name,
                        'url': link,
                        'source': source['name'],
                        'author': '',
                        'publish_time': datetime.now().strftime('%Y-%m-%d'),
                        'summary': description[:self.config.get('max_summary_length', 3000)],
                        'importance': self._calculate_github_importance(stars_text)
                    }
                    
                    if not self._is_duplicate(repo_name + description):
                        items.append(item)
                        self.existing_hashes.add(hashlib.md5((repo_name + description).encode('utf-8')).hexdigest())
                except Exception as e:
                    logger.warning(f"解析GitHub条目失败: {e}")
                    continue
        except Exception as e:
            logger.error(f"解析 {source['name']} 失败: {e}")
        
        return items
    
    def _calculate_importance(self, title, abstract, authors):
        """计算重要性评分"""
        score = 3
        
        # 检查关键词
        high_impact_keywords = ['GPT', 'Claude', 'Gemini', 'LLaMA', 'transformer', 'breakthrough', 'state-of-the-art', 'SOTA']
        for keyword in high_impact_keywords:
            if keyword.lower() in (title + abstract).lower():
                score += 1
        
        # 检查顶级机构
        top_institutions = ['OpenAI', 'DeepMind', 'Google', 'Meta', 'Anthropic', 'Microsoft', 'Stanford', 'MIT', 'CMU']
        for inst in top_institutions:
            if inst in authors:
                score += 1
        
        return min(5, score)
    
    def _calculate_github_importance(self, stars_text):
        """计算GitHub项目重要性"""
        try:
            stars = int(stars_text.replace(',', ''))
            if stars > 1000:
                return 5
            elif stars > 500:
                return 4
            elif stars > 200:
                return 3
            elif stars > 100:
                return 2
            else:
                return 1
        except:
            return 3
    
    def _save_item(self, item, index):
        """保存单个条目"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_str}-{index:03d}-{item['title'][:50].replace('/', '_').replace(' ', '_')}.md"
        filepath = self.inbox_dir / filename
        
        content = f"# {item['title']}\n\n"
        content += f"- **来源**: {item['source']}\n"
        content += f"- **链接**: {item['url']}\n"
        content += f"- **发布时间**: {item['publish_time']}\n"
        if item.get('author'):
            content += f"- **作者**: {item['author']}\n"
        content += f"- **重要性**: {'★' * item['importance']}\n\n"
        content += "## 摘要\n\n"
        content += item.get('summary', '')
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"保存条目: {filename}")
    
    def _generate_daily_report(self):
        """生成每日信息简报"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        report_path = self.inbox_dir / f"{date_str}-每日信息简报.md"
        
        content = f"# 大模型领域每日信息简报 - {date_str}\n\n"
        content += f"- **采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"- **采集来源数量**: {len(self.config['sources'])}\n"
        
        if self.failed_sources:
            content += f"- **失败来源**: {', '.join(self.failed_sources)}\n"
        
        content += f"- **筛选后内容数量**: {len(self.collected_items)}\n\n"
        
        # 按重要性排序
        sorted_items = sorted(self.collected_items, key=lambda x: -x['importance'])
        
        content += "## 内容列表\n\n"
        for i, item in enumerate(sorted_items, 1):
            content += f"### {i}. {item['title']}\n"
            content += f"- **来源**: {item['source']}\n"
            content += f"- **链接**: {item['url']}\n"
            content += f"- **重要性**: {'★' * item['importance']}\n"
            content += f"- **一句话摘要**: {item['summary'][:100]}...\n\n"
        
        report_path.write_text(content, encoding='utf-8')
        logger.info(f"生成每日简报: {report_path}")
        
        return report_path
    
    def run(self):
        """运行信息采集"""
        logger.info("=" * 50)
        logger.info("开始大模型信息雷达采集")
        logger.info("=" * 50)
        
        for source in self.config['sources']:
            logger.info(f"正在采集: {source['name']}")
            
            try:
                source_type = source.get('type', 'blog')
                
                if source_type == 'arxiv':
                    items = self._parse_arxiv(source)
                elif source_type == 'github':
                    items = self._parse_github(source)
                else:
                    items = self._parse_blog(source)
                
                if items:
                    logger.info(f"从 {source['name']} 获取了 {len(items)} 条内容")
                    self.collected_items.extend(items)
                else:
                    logger.info(f"从 {source['name']} 未获取到内容")
                
                # 遵守访问频率限制
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"采集 {source['name']} 失败: {e}")
                self.failed_sources.append(source['name'])
        
        # 保存内容
        logger.info(f"总共采集 {len(self.collected_items)} 条内容")
        for i, item in enumerate(self.collected_items, 1):
            self._save_item(item, i)
        
        # 生成简报
        report_path = self._generate_daily_report()
        
        logger.info("=" * 50)
        logger.info("采集完成")
        logger.info("=" * 50)
        
        return report_path


def main():
    non_interactive = len(sys.argv) > 1 and sys.argv[1] == '--non-interactive'
    
    agent = LLMAgent()
    report_path = agent.run()
    
    print("\n" + "=" * 50)
    print("信息采集完成！")
    print(f"共采集 {len(agent.collected_items)} 条内容")
    print(f"每日简报已保存至: {report_path}")
    print("=" * 50)
    
    # 非交互模式下不询问用户
    if not non_interactive:
        # 询问是否进行知识蒸馏
        response = input("\n是否需要立即进行知识蒸馏？(y/n): ").strip().lower()
        if response == 'y':
            print("\n知识蒸馏功能开发中...")


if __name__ == '__main__':
    main()

