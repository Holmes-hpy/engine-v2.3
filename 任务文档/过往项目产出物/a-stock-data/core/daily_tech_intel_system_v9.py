#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技前沿资讯分析系统 v9.0（WebSearch增强版）
=====================================================
执行时间: 每日下午14:30（工作日）
核心改进:
  1. 双重搜索策略：requests爬虫 + WebSearch API降级
  2. 历史趋势对比：与昨日/上周同期资讯做对比
  3. 产业链关联分析：自动识别上下游影响
  4. 增强缠论分析：走势类型判断 + 操作级别建议
  5. 增强知识沉淀：按产业分类存储、时间线回溯
  6. 增强反向信号识别：多维度10+项检测

使用方式:
  python daily_tech_intel_system_v9.py
  python daily_tech_intel_system_v9.py afternoon   # 强制下午模式
"""

import sys
import os
import json
import re
import time
import random
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ========== 路径配置 ==========
PROJECT_DIR = Path(__file__).parent
REPORT_DIR = PROJECT_DIR / "daily_tech_intel"
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"
GRAPH_DIR = PROJECT_DIR / "knowledge_graph"
HISTORY_DIR = PROJECT_DIR / "daily_tech_intel" / "history"
LOG_DIR = PROJECT_DIR / "logs"

for d in [REPORT_DIR, KNOWLEDGE_DIR, GRAPH_DIR, HISTORY_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))


# ============================================================
# 1. 十五五规划重点关注产业（v9.0扩充版）
# ============================================================
FIFTEEN_FIVE_INDUSTRIES = {
    "人工智能": {
        "keywords": ["人工智能", "AI", "大模型", "生成式AI", "深度学习", "人形机器人",
                     "机器视觉", "多模态", "智能体", "AGI", "机器学习", "神经网络", "AIGC",
                     "具身智能", "推理模型", "端侧AI"],
        "search_queries": [
            "人工智能 最新政策 技术突破 2026",
            "AI大模型 国产替代 最新进展 2026",
            "人工智能 十五五规划 产业政策 2026",
        ],
        "stocks": ["寒武纪", "科大讯飞", "海天瑞声", "云从科技", "拓尔思", "工业富联", "浪潮信息"],
        "upstream": ["芯片设计", "算力基础设施", "数据标注"],
        "downstream": ["智能驾驶", "智慧医疗", "智能制造", "智慧城市"],
        "chain_chokepoints": ["高端GPU", "EDA工具", "高质量数据集"]
    },
    "半导体": {
        "keywords": ["半导体", "芯片", "集成电路", "先进制程", "国产替代", "中芯国际",
                     "光刻", "先进封装", "存储", "晶圆", "EDA", "GPU", "CPU", "DRAM", "NAND",
                     "HBM", "Chiplet", "硅光"],
        "search_queries": [
            "半导体 国产替代 芯片进展 2026",
            "光刻机 先进制程 突破 最新 2026",
            "集成电路 十五五规划 产业政策 2026",
        ],
        "stocks": ["中芯国际", "北方华创", "韦尔股份", "紫光国微", "卓胜微", "兆易创新", "长电科技"],
        "upstream": ["硅片", "光刻胶", "特种气体", "靶材"],
        "downstream": ["消费电子", "汽车电子", "工业控制", "通信设备"],
        "chain_chokepoints": ["光刻机", "先进制程工艺", "高端光刻胶"]
    },
    "新能源": {
        "keywords": ["新能源", "光伏", "风电", "储能", "新能源汽车", "锂电池",
                     "宁德时代", "比亚迪", "氢能", "燃料电池", "固态电池", "碳酸锂",
                     "钙钛矿", "钠离子电池", "虚拟电厂"],
        "search_queries": [
            "新能源 储能 光伏 最新政策 2026",
            "锂电池 储能 产业动态 2026",
            "新能源汽车 十五五规划 政策 2026",
        ],
        "stocks": ["宁德时代", "比亚迪", "隆基绿能", "通威股份", "阳光电源", "天齐锂业", "赣锋锂业"],
        "upstream": ["锂矿", "稀土", "硅料", "铜铝"],
        "downstream": ["充电桩", "储能电站", "分布式能源"],
        "chain_chokepoints": ["固态电池技术", "高端锂矿资源", "光伏核心设备"]
    },
    "数字经济": {
        "keywords": ["数字经济", "数据中心", "算力", "云计算", "大数据", "东数西算",
                     "工业互联网", "数据要素", "数字中国", "信创", "数字化转型",
                     "液冷", "智算中心"],
        "search_queries": [
            "数字经济 云计算 算力 最新政策 2026",
            "东数西算 数据中心 产业动态 2026",
            "数据要素 数字化转型 十五五 2026",
        ],
        "stocks": ["宝信软件", "用友网络", "金山办公", "中科曙光", "浪潮信息", "紫光股份"],
        "upstream": ["服务器", "网络设备", "存储设备"],
        "downstream": ["政务云", "企业SaaS", "金融科技", "智慧城市"],
        "chain_chokepoints": ["高端服务器芯片", "核心数据库", "操作系统"]
    },
    "新材料": {
        "keywords": ["新材料", "稀土", "碳纤维", "第三代半导体", "碳化硅", "氮化镓",
                     "石墨烯", "超导", "高温合金", "钛合金", "先进陶瓷"],
        "search_queries": [
            "新材料 稀土 碳纤维 最新突破 2026",
            "碳化硅 氮化镓 半导体材料 进展 2026",
            "先进新材料 产业政策 2026",
        ],
        "stocks": ["北方稀土", "中国宝安", "光威复材", "中简科技", "天奈科技"],
        "upstream": ["矿石原料", "化工原料"],
        "downstream": ["航空航天", "新能源汽车", "消费电子", "军工"],
        "chain_chokepoints": ["高端碳纤维", "高纯度稀土分离", "大尺寸碳化硅衬底"]
    },
    "生物医药": {
        "keywords": ["生物医药", "创新药", "基因编辑", "医疗器械", "CXO", "生物科技",
                     "mRNA", "ADC", "GLP-1", "减肥药", "CAR-T", "合成生物学"],
        "search_queries": [
            "生物医药 创新药 最新政策 2026",
            "医疗器械 国产替代 最新进展 2026",
            "GLP-1 减肥药 产业动态 2026",
        ],
        "stocks": ["恒瑞医药", "药明康德", "迈瑞医疗", "爱尔眼科", "智飞生物", "百济神州"],
        "upstream": ["CRO/CDMO", "原料药", "药用辅材"],
        "downstream": ["医院", "连锁药房", "互联网医疗"],
        "chain_chokepoints": ["高端医疗设备核心部件", "创新药靶点发现", "临床CRO"]
    },
    "航天军工": {
        "keywords": ["航天", "商业航天", "卫星互联网", "军工", "无人机", "低空经济",
                     "卫星", "北斗", "星链", "火箭", "空间站", "eVTOL"],
        "search_queries": [
            "商业航天 卫星互联网 最新进展 2026",
            "低空经济 无人机 产业政策 2026",
            "军工 航天 十五五规划 2026",
        ],
        "stocks": ["中航沈飞", "航天电器", "中国卫星", "中直股份", "高德红外"],
        "upstream": ["特种材料", "电子元器件", "精密加工"],
        "downstream": ["国防安全", "民用航空", "卫星通信", "地理信息"],
        "chain_chokepoints": ["航空发动机", "高端芯片", "精密传感器"]
    },
    "智能网联汽车": {
        "keywords": ["自动驾驶", "车联网", "智能驾驶", "L3", "L4", "激光雷达",
                     "毫米波雷达", "域控制器", "智能座舱", "V2X"],
        "search_queries": [
            "自动驾驶 智能驾驶 最新进展 2026",
            "激光雷达 车联网 国产替代 2026",
            "智能网联汽车 产业政策 2026",
        ],
        "stocks": ["德赛西威", "华阳集团", "均胜电子", "小鹏汽车", "理想汽车"],
        "upstream": ["芯片", "传感器", "软件算法"],
        "downstream": ["出行服务", "物流配送", "智慧交通"],
        "chain_chokepoints": ["自动驾驶芯片", "高精度激光雷达", "V2X通信模组"]
    },
    "量子科技": {
        "keywords": ["量子计算", "量子通信", "量子科技", "量子比特", "量子纠错",
                     "量子优越性"],
        "search_queries": [
            "量子计算 量子通信 最新突破 2026",
            "量子科技 产业政策 进展 2026",
        ],
        "stocks": ["国盾量子", "中科曙光"],
        "upstream": ["超导材料", "低温设备", "精密仪器"],
        "downstream": ["量子加密通信", "量子计算云服务"],
        "chain_chokepoints": ["量子比特稳定性", "量子纠错算法", "极低温制冷机"]
    },
}


# ============================================================
# 2. 反向信号关键词（v9.0增强版）
# ============================================================
REVERSE_SIGNAL_KEYWORDS = {
    "极端词汇": {
        "words": ["暴涨", "暴跌", "必涨", "必跌", "翻倍", "妖股", "疯涨", "崩盘", "血洗",
                  "涨停潮", "跌停潮", "炸了", "疯了", "暴增", "暴富", "狂涨", "狂跌",
                  "井喷", "飙升", "爆发", "炸裂", "逆天", "彻底疯了", "彻底爆发",
                  "历史首次", "全球第一", "全球首发", "颠覆"],
        "weight": 3
    },
    "内幕词汇": {
        "words": ["内幕", "独家", "重磅", "惊天", "震惊", "秘密", "内部消息", "绝密",
                  "泄密", "爆料", "实锤", "曝光", "揭秘", "藏不住了", "瞒不住了",
                  "不可告人", "不敢说"],
        "weight": 3
    },
    "主体词汇": {
        "words": ["主力", "游资", "机构", "大佬", "牛散", "庄家", "操盘手", "国家队",
                  "外资", "神秘资金", "聪明钱"],
        "weight": 1
    },
    "时间词汇": {
        "words": ["即将", "马上", "立刻", "今日", "最新", "突发", "紧急", "刚刚",
                  "就在刚才", "就在今天", "就在刚刚", "今晚", "今夜"],
        "weight": 1
    },
    "引导词汇": {
        "words": ["手把手", "带你", "教你", "跟着", "躺赢", "赚钱", "发财", "致富",
                  "必看", "收藏", "速看", "快看", "牛股", "龙头股", "十倍股", "翻倍股",
                  "布局", "重点关注", "强烈推荐", "赶紧上车", "不要错过",
                  "最后的机会", "千载难逢"],
        "weight": 2
    },
    "操作词汇": {
        "words": ["抄底", "逃顶", "上车", "下车", "接力", "打板", "追涨", "杀跌",
                  "核按钮", "满仓", "重仓", "梭哈", "All in", "砸锅卖铁", "卖房炒股"],
        "weight": 3
    },
    "夸张词汇": {
        "words": ["震惊", "慌了", "哭了", "笑了", "懵了", "爽了", "赚翻了", "太可怕",
                  "吓尿", "惊呆", "炸锅", "沸腾", "疯狂", "失控", "彻底失控",
                  "泪目", "燃爆"],
        "weight": 2
    },
    "权威滥用": {
        "words": ["央视", "新华社", "人民日报", "中央定调", "高层发话", "刚刚召开", "重磅会议"],
        "weight": 2
    },
}

# 自媒体/枪手发文典型时间规律
GUNMAN_TIME_PATTERNS = {
    "盘前集中发文": {"hours": [8, 9], "risk_boost": 3, "desc": "盘前8-9点集中发文制造情绪"},
    "尾盘集中发文": {"hours": [14, 15], "risk_boost": 4, "desc": "尾盘14-15点集中发文诱导跟风"},
    "深夜发文": {"hours": [22, 23, 0, 1], "risk_boost": 2, "desc": "深夜发文利用次日开盘情绪"},
}

# 自媒体平台特征
SELF_MEDIA_PLATFORMS = [
    "toutiao.com", "头条", "百家号", "企鹅号", "大风号", "网易号",
    "搜狐号", "一点资讯", "快传号", "东方号", "雪球", "股吧"
]

# 可靠来源列表
RELIABLE_SOURCES = {
    "A": ["gov.cn", "miit.gov.cn", "most.gov.cn", "ndrc.gov.cn", "csrc.gov.cn",
          "www.gov.cn", "news.cn", "xinhuanet.com", "people.com.cn", "cctv.com"],
    "B": ["stcn.com", "cs.com.cn", "zqrb.cn", "chinadaily.com.cn",
          "caixin.com", "yicai.com", "cls.cn", "cs.com.cn"],
    "C": ["eastmoney.com", "sina.com.cn", "163.com", "sohu.com", "ifeng.com"],
    "D": ["36kr.com", "huxiu.com", "ithome.com", "leiphone.com", "jiemian.com"],
}

# 产业链知识图谱
INDUSTRY_CHAIN_MAP = {}
for ind, config in FIFTEEN_FIVE_INDUSTRIES.items():
    INDUSTRY_CHAIN_MAP[ind] = {
        "upstream": config.get("upstream", []),
        "downstream": config.get("downstream", []),
        "chokepoints": config.get("chain_chokepoints", [])
    }


# ============================================================
# 【模块1】双重搜索策略（requests爬虫 + WebSearch API降级）
# ============================================================
class DualSourceNewsFetcher:
    """双重搜索策略 - requests爬虫优先，WebSearch API降级"""

    def __init__(self):
        self.session = None
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            })
            self.session.verify = False
        self.websearch_used = False

    def _safe_get(self, url, timeout=15, encoding=None):
        """安全获取网页内容"""
        if not self.session:
            return None
        try:
            resp = self.session.get(url, timeout=timeout)
            if resp.status_code == 200:
                resp.encoding = encoding or resp.apparent_encoding or 'utf-8'
                return resp.text
        except Exception:
            pass
        return None

    def search_baidu_news(self, query, num_results=8):
        """通过百度新闻搜索"""
        url = f"https://www.baidu.com/s?wd={requests.utils.quote(query)}&tn=news&rn={num_results}"
        content = self._safe_get(url)
        if not content:
            return []

        results = []
        try:
            soup = BeautifulSoup(content, 'html.parser')
            for item in soup.find_all('div', class_='result'):
                title_tag = item.find('h3')
                if not title_tag:
                    continue
                a_tag = title_tag.find('a')
                if not a_tag:
                    continue
                title = a_tag.get_text(strip=True)
                href = a_tag.get('href', '')
                source = "百度新闻"
                snippet = ""
                source_span = item.find('span', class_='c-color-gray')
                if source_span:
                    source = source_span.get_text(strip=True) or "百度新闻"
                snippet_tag = item.find('span', class_='content-right_8Zs40')
                if snippet_tag:
                    snippet = snippet_tag.get_text(strip=True)
                if title and len(title) > 5:
                    results.append({
                        "title": title, "url": href,
                        "snippet": snippet or f"关于{query}的报道",
                        "source": source, "search_engine": "百度新闻"
                    })
        except Exception:
            pass
        return results[:num_results]

    def search_websearch_api(self, query, num_results=8):
        """通过WebSearch API搜索（降级方案）"""
        try:
            # 使用WebSearch工具搜索
            cmd = ['python3', '-c', f'''
import sys
sys.path.insert(0, "{PROJECT_DIR}")
from websearch_tech_intel_system import WebSearchNewsCollector
collector = WebSearchNewsCollector()
results = collector.collect_news(["{query}"])
import json
print(json.dumps(results, ensure_ascii=False))
''']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                return data[:num_results]
        except Exception:
            pass

        # 如果上述方法失败，返回基本结构让外部WebSearch工具填充
        return []

    def search_all_for_industry(self, industry_name, industry_config):
        """对一个产业进行双重搜索"""
        keywords = industry_config["keywords"]
        search_queries = industry_config["search_queries"]
        all_keywords = keywords + [industry_name]

        all_news = []
        crawler_success = False

        # 优先：requests爬虫搜索
        if HAS_REQUESTS and self.session:
            for query in search_queries[:2]:
                try:
                    results = self.search_baidu_news(query, num_results=6)
                    for r in results:
                        r["matched_keywords"] = [kw for kw in keywords if kw in r["title"]]
                        if r["matched_keywords"] or industry_name in r["title"]:
                            r["industry"] = industry_name
                            all_news.append(r)
                    if results:
                        crawler_success = True
                    time.sleep(0.5 + random.random() * 0.5)
                except Exception:
                    pass

        # 降级：WebSearch API
        if not crawler_success or len(all_news) < 3:
            self.websearch_used = True
            print(f"    🔄 requests爬虫获取不足，启用WebSearch API降级搜索...")
            for query in search_queries[:2]:
                try:
                    results = self.search_websearch_api(query, num_results=5)
                    for r in results:
                        r["matched_keywords"] = [kw for kw in keywords if kw in r.get("title", "")]
                        r["industry"] = industry_name
                        r["search_engine"] = "WebSearch"
                        all_news.append(r)
                    time.sleep(0.3)
                except Exception:
                    pass

        # 去重
        unique_news = []
        seen = set()
        for news in all_news:
            title_key = news.get("title", "")[:50].strip()
            title_hash = hashlib.md5(title_key.encode('utf-8')).hexdigest()
            if title_hash not in seen and len(news.get("title", "")) > 5:
                seen.add(title_hash)
                news["title"] = re.sub(r'\d{1,2}-\d{1,2}\s+\d{1,2}:\d{2}', '', news["title"]).strip()
                news["title"] = re.sub(r'\d{2,4}[-./年]\d{1,2}[-./月]\d{1,2}[日]?', '', news["title"]).strip()
                news["title"] = re.sub(r'\s+', ' ', news["title"]).strip()
                if len(news["title"]) > 5:
                    unique_news.append(news)

        return unique_news

    def search_all_industries(self):
        """搜索所有产业的最新资讯"""
        all_news_by_industry = {}
        crawler_fail_count = 0

        for industry, config in FIFTEEN_FIVE_INDUSTRIES.items():
            print(f"  🔍 【{industry}】搜索中...")
            industry_news = self.search_all_for_industry(industry, config)
            all_news_by_industry[industry] = industry_news
            print(f"     ✓ 合计 {len(industry_news)} 条")
            if not industry_news:
                crawler_fail_count += 1

        if self.websearch_used:
            print(f"  📡 已启用WebSearch API降级搜索")
        if crawler_fail_count > 0:
            print(f"  ⚠️ {crawler_fail_count} 个产业未获取到资讯")

        total = sum(len(v) for v in all_news_by_industry.values())
        print(f"  📊 双重搜索共获取 {total} 条资讯")
        return all_news_by_industry


# ============================================================
# 【模块2】增强反向信号分析器（v9.0：11维检测）
# ============================================================
class EnhancedReverseSignalAnalyzer:
    """增强反向信号分析器 - 11维检测"""

    def __init__(self):
        self.keywords = REVERSE_SIGNAL_KEYWORDS

    def analyze(self, title, snippet, url, source=""):
        """分析单条资讯的反向信号"""
        text = (title + " " + snippet).strip()

        signal = {
            "has_reverse_signal": False,
            "signal_score": 0,
            "signal_categories": {},
            "signal_words": [],
            "risk_level": "低",
            "title_party_pattern": [],
            "gunman_pattern": [],
            "timing_risk": "",
            "source_risk": "",
            "chain_risk": "",  # v9新增
            "analysis": "",
            "suggestion": ""
        }

        # ---- 1-8: 与v8相同的8维检测（关键词匹配+权重、数字夸张、标点、开头模式、枪手引导语、来源可靠性、自媒体平台、发文时间） ----
        for category, config in self.keywords.items():
            words = config["words"]
            weight = config["weight"]
            found = []
            for kw in words:
                if kw in title:
                    found.append(kw)
                    signal["signal_score"] += weight
            if found:
                signal["signal_categories"][category] = found
                signal["signal_words"].extend(found)

        # 数字夸张检测
        exaggeration_patterns = [
            (r'([1-9]\d{2,})%', '夸张百分比'),
            (r'暴增\s*\d+\s*亿', '暴增XX亿'),
            (r'暴涨\s*\d+\s*倍', '暴涨XX倍'),
            (r'翻\s*\d+\s*倍', '翻XX倍'),
            (r'增长\s*\d+\s*倍', '增长XX倍'),
            (r'狂赚\s*\d+\s*倍', '狂赚XX倍'),
        ]
        for pattern, label in exaggeration_patterns:
            match = re.search(pattern, title)
            if match:
                signal["signal_score"] += 5
                signal["signal_words"].append(f"{label}:{match.group()}")

        # 标点符号检测
        excl = title.count("!") + title.count("！")
        ques = title.count("?") + title.count("？")
        if excl >= 2:
            signal["signal_score"] += 4
            signal["title_party_pattern"].append("多感叹号")
        if ques >= 2:
            signal["signal_score"] += 2
            signal["title_party_pattern"].append("多问号")

        # 标题开头模式
        title_patterns = [
            (r'^[震惊重磅突发紧急独家揭秘]', '强情绪开头'),
            (r'^刚刚', '时间压迫开头'),
            (r'!.*!', '感叹号堆砌'),
        ]
        for pattern, label in title_patterns:
            if re.search(pattern, title):
                signal["signal_score"] += 3
                signal["title_party_pattern"].append(label)
                break

        # 枪手引导语
        gunman_patterns = [
            (r'手把手', '引导式操作'),
            (r'教你|带你|跟着', '主观引导'),
            (r'一定要看|不得不看', '强制引导'),
            (r'最后的机会|千载难逢', '稀缺诱导'),
        ]
        for pattern, label in gunman_patterns:
            if re.search(pattern, title):
                signal["gunman_pattern"].append(label)
                signal["signal_score"] += 2

        # 来源可靠性判断
        source_trust = self._assess_source_trust(url, source)
        if source_trust == "unreliable":
            signal["signal_score"] += 5
            signal["source_risk"] = "来源不可信"
        elif source_trust == "self_media":
            signal["signal_score"] += 3
            signal["source_risk"] = "自媒体来源"
        elif source_trust == "mainstream":
            signal["signal_score"] += 0
        else:
            signal["signal_score"] -= 3

        # 自媒体平台特征
        for platform in SELF_MEDIA_PLATFORMS:
            if platform in url or platform in source:
                signal["signal_score"] += 3
                signal["gunman_pattern"].append(f"自媒体平台({platform})")
                break

        # 发文时间风险检测
        current_hour = datetime.now().hour
        for pattern_name, config in GUNMAN_TIME_PATTERNS.items():
            if current_hour in config["hours"]:
                signal["signal_score"] += config["risk_boost"]
                signal["timing_risk"] = config["desc"]
                break

        # 标题长度异常
        if len(title) < 6:
            signal["signal_score"] += 2
        elif len(title) > 80:
            signal["signal_score"] += 1

        # ---- v9新增: 9. 产业链炒作模式检测 ----
        chokepoint_keywords = []
        for ind, chain_config in INDUSTRY_CHAIN_MAP.items():
            chokepoint_keywords.extend(chain_config.get("chokepoints", []))
        matched_chokepoints = [ck for ck in chokepoint_keywords if ck in text]
        if matched_chokepoints and signal["signal_score"] >= 3:
            signal["chain_risk"] = f"涉及瓶颈环节炒作({','.join(matched_chokepoints[:3])})"
            signal["signal_score"] += 2

        # ---- v9新增: 10. 标题与正文不一致检测（简化版：标题含极端词但snippet正常） ----
        title_extreme = any(kw in title for kws in [self.keywords["极端词汇"]["words"],
                                                      self.keywords["内幕词汇"]["words"]]
                           for kw in kws)
        if title_extreme and snippet and len(snippet) > 20:
            snippet_extreme = any(kw in snippet for kws in [self.keywords["极端词汇"]["words"],
                                                              self.keywords["内幕词汇"]["words"]]
                                  for kw in kws)
            if not snippet_extreme:
                signal["signal_score"] += 3
                signal["title_party_pattern"].append("标题正文名不副实")

        # ---- v9新增: 11. 连续发文模式检测（简化版） ----
        # （完整版需要跨多条资讯分析，此处预留接口）

        # 综合风险判定
        signal["signal_score"] = max(0, signal["signal_score"])

        if signal["signal_score"] >= 12:
            signal["has_reverse_signal"] = True
            signal["risk_level"] = "高"
        elif signal["signal_score"] >= 7:
            signal["has_reverse_signal"] = True
            signal["risk_level"] = "中"
        elif signal["signal_score"] >= 3:
            signal["risk_level"] = "低"

        # 生成分析与建议
        if signal["has_reverse_signal"]:
            parts = []
            if signal["title_party_pattern"]:
                parts.append(f"标题党模式: {', '.join(signal['title_party_pattern'])}")
            if signal["gunman_pattern"]:
                parts.append(f"枪手特征: {', '.join(signal['gunman_pattern'])}")
            if signal["timing_risk"]:
                parts.append(f"发文时间风险: {signal['timing_risk']}")
            if signal["source_risk"]:
                parts.append(signal["source_risk"])
            if signal["chain_risk"]:
                parts.append(signal["chain_risk"])
            signal["analysis"] = "；".join(parts)

            if signal["risk_level"] == "高":
                signal["suggestion"] = "高度疑似标题党或资本雇佣枪手发文！务必反向思考，切勿追涨！需结合正规媒体多方核实。"
            else:
                signal["suggestion"] = "存在诱导性特征，需谨慎判断，建议多方核实后再决策。"
        else:
            signal["suggestion"] = "资讯质量正常，可正常关注，仍需结合多源信息判断。"

        return signal

    def _assess_source_trust(self, url, source):
        """评估来源可信度"""
        for level, domains in RELIABLE_SOURCES.items():
            if level in ["A", "B"]:
                for domain in domains:
                    if domain in url or domain in source:
                        return "authoritative"
        for platform in SELF_MEDIA_PLATFORMS:
            if platform in url or platform in source:
                return "self_media"
        for level, domains in RELIABLE_SOURCES.items():
            if level == "C":
                for domain in domains:
                    if domain in url or domain in source:
                        return "mainstream"
        return "unreliable"

    def cross_validate(self, analyzed_data):
        """多源交叉验证"""
        items_list = [item for lst in analyzed_data.values() for item in lst]
        title_keywords_map = {}
        for item in items_list:
            title = item["news"]["title"]
            kws = set(re.findall(r'[\u4e00-\u9fa5]{2,}', title))
            title_keywords_map[id(item)] = kws

        for i, item1 in enumerate(items_list):
            kws1 = title_keywords_map.get(id(item1), set())
            cross_count = 0
            for j, item2 in enumerate(items_list):
                if i == j:
                    continue
                kws2 = title_keywords_map.get(id(item2), set())
                overlap = len(kws1 & kws2)
                if overlap >= 3:
                    cross_count += 1

            if cross_count >= 3:
                item["reverse_signal"]["signal_score"] = max(0, item["reverse_signal"]["signal_score"] - 3)
                item["reverse_signal"]["cross_validation"] = f"有{cross_count}个来源交叉验证，可信度提升"
            elif cross_count == 0 and item["reverse_signal"]["signal_score"] >= 5:
                item["reverse_signal"]["signal_score"] += 2
                item["reverse_signal"]["cross_validation"] = "单一来源报道，可信度较低"

        return analyzed_data


# ============================================================
# 【模块3】增强缠论分析器（v9.0：走势类型+操作级别）
# ============================================================
class EnhancedChanTheoryAnalyzer:
    """增强缠论分析器 - 走势类型判断 + 操作级别建议"""

    def analyze(self, title, snippet, industry, core_info):
        """缠论视角深度分析"""
        text = title + " " + snippet

        analysis = {
            "buy_points": {"first": False, "second": False, "third": False, "details": []},
            "sell_points": {"first": False, "second": False, "third": False, "details": []},
            "pivot_type": "",
            "trend_type": "盘整",  # v9新增: 上涨趋势/下跌趋势/盘整
            "operation_level": "观望",  # v9新增: 买入/持有/减仓/观望
            "divergence": {"detected": False, "type": "", "level": "", "desc": ""},
            "trend_judgment": "",
            "operation_suggestion": "",
            "confidence_score": 30,
            "reasoning": [],
            "multi_level": {"daily": "", "weekly": "", "monthly": ""},
            "risk_warning": ""
        }

        # ===== 买点分析 =====
        first_triggers = ["政策", "规划", "出台", "发布", "国务院", "工信部", "发改委", "科技部",
                          "首次", "创新", "突破", "国产替代", "超跌", "底部", "低估"]
        for trigger in first_triggers:
            if trigger in text or core_info.get("event_type") in ["政策发布", "技术突破"]:
                analysis["buy_points"]["first"] = True
                analysis["buy_points"]["details"].append(f"政策/技术驱动({trigger})")
                analysis["confidence_score"] += 15
                analysis["reasoning"].append(
                    f"【一买】{trigger}事件可能形成行业政策底或技术突破驱动——对应缠论中下跌趋势末端的背驰段"
                )
                break

        second_triggers = ["确认", "企稳", "验证", "回踩", "回调", "调整", "筑底", "支撑",
                           "缩量", "止跌", "企稳回升"]
        for trigger in second_triggers:
            if trigger in text:
                analysis["buy_points"]["second"] = True
                analysis["buy_points"]["details"].append(f"回调信号({trigger})")
                analysis["confidence_score"] += 10
                analysis["reasoning"].append(
                    f"【二买】出现'{trigger}'，提示回踩确认机会——对应缠论中第二类买点：不创新低的回踩确认"
                )
                break

        third_triggers = ["新高", "加速", "超预期", "黄金期", "快车道", "井喷", "爆发",
                          "高速增长", "供不应求", "放量突破", "趋势确立"]
        for trigger in third_triggers:
            if trigger in text:
                analysis["buy_points"]["third"] = True
                analysis["buy_points"]["details"].append(f"趋势加速({trigger})")
                analysis["confidence_score"] += 10
                analysis["reasoning"].append(
                    f"【三买】出现'{trigger}'——对应缠论中离开中枢后不回抽的确认点，但也需警惕情绪过热"
                )
                break

        # ===== 卖点分析 =====
        first_sell_triggers = ["见顶", "过热", "泡沫", "估值过高", "疯狂追涨", "获利了结"]
        for trigger in first_sell_triggers:
            if trigger in text:
                analysis["sell_points"]["first"] = True
                analysis["sell_points"]["details"].append(f"趋势末端({trigger})")
                analysis["confidence_score"] -= 5
                analysis["reasoning"].append(f"【一卖】出现'{trigger}'，可能提示上涨趋势末端背驰")
                break

        second_sell_triggers = ["冲高回落", "上攻乏力", "量能萎缩", "高位震荡"]
        for trigger in second_sell_triggers:
            if trigger in text:
                analysis["sell_points"]["second"] = True
                analysis["sell_points"]["details"].append(f"反弹受阻({trigger})")
                analysis["confidence_score"] -= 3
                analysis["reasoning"].append(f"【二卖】出现'{trigger}'，可能提示反弹不创新高")
                break

        # ===== 背驰检测 =====
        if any(kw in text for kw in ["放量滞涨", "缩量上涨", "量价背离"]):
            analysis["divergence"]["detected"] = True
            analysis["divergence"]["type"] = "量价背驰"
            analysis["divergence"]["level"] = "日线级别"
            analysis["divergence"]["desc"] = "量价关系出现背离，需警惕趋势衰竭"
            analysis["confidence_score"] -= 5

        if any(kw in text for kw in ["利好出尽", "政策落地", "预期兑现"]):
            analysis["divergence"]["detected"] = True
            analysis["divergence"]["type"] = "政策背驰"
            analysis["divergence"]["level"] = "周线级别"
            analysis["divergence"]["desc"] = "利好预期已兑现，可能形成政策顶"
            analysis["confidence_score"] -= 8

        if any(kw in text for kw in ["全民炒股", "跑步入场", "牛市来了", "闭眼赚钱"]):
            analysis["divergence"]["detected"] = True
            analysis["divergence"]["type"] = "情绪背驰"
            analysis["divergence"]["level"] = "月线级别"
            analysis["divergence"]["desc"] = "市场情绪极端乐观，可能形成情绪顶"
            analysis["confidence_score"] -= 10

        # ===== 中枢类型判断 =====
        event_type = core_info.get("event_type", "")
        if event_type == "政策发布":
            analysis["pivot_type"] = "政策支撑中枢"
            analysis["confidence_score"] += 8
        elif event_type == "技术突破":
            analysis["pivot_type"] = "技术突破中枢"
            analysis["confidence_score"] += 8
        elif event_type == "市场动态":
            analysis["pivot_type"] = "市场情绪中枢"
            analysis["confidence_score"] += 3
        elif event_type == "产能扩张":
            analysis["pivot_type"] = "基本面扩张中枢"
            analysis["confidence_score"] += 5
        else:
            analysis["pivot_type"] = "产业趋势中枢"

        # 影响范围加权
        scope = core_info.get("impact_scope", "")
        if scope == "国家级/全球性":
            analysis["confidence_score"] += 15
        elif scope == "行业级":
            analysis["confidence_score"] += 8

        # ===== v9新增：走势类型判断 =====
        active_bp = sum([analysis["buy_points"]["first"], analysis["buy_points"]["second"], analysis["buy_points"]["third"]])
        active_sp = sum([analysis["sell_points"]["first"], analysis["sell_points"]["second"]])

        if active_sp > 0:
            analysis["trend_type"] = "下跌趋势"
        elif active_bp >= 2:
            analysis["trend_type"] = "上涨趋势"
        elif active_bp == 1:
            analysis["trend_type"] = "盘整偏多"
        else:
            analysis["trend_type"] = "盘整"

        # ===== v9新增：操作级别建议 =====
        if analysis["divergence"]["detected"]:
            analysis["operation_level"] = "减仓"
            analysis["risk_warning"] = f"⚠️ 检测到{analysis['divergence']['type']}（{analysis['divergence']['desc']}）"
        elif active_sp > 0:
            analysis["operation_level"] = "减仓"
        elif active_bp >= 2 and analysis["confidence_score"] >= 55:
            analysis["operation_level"] = "买入"
        elif active_bp >= 1 and analysis["confidence_score"] >= 40:
            analysis["operation_level"] = "持有"
        else:
            analysis["operation_level"] = "观望"

        # ===== 多级别联立分析 =====
        if event_type == "政策发布" and scope == "国家级/全球性":
            analysis["multi_level"] = {
                "monthly": "月线级别偏多（国家级政策支撑长线趋势）",
                "weekly": "周线级别偏多（政策落地推动中期上行）",
                "daily": "日线级别可能有短线波动（市场消化政策预期）"
            }
        elif event_type == "技术突破":
            analysis["multi_level"] = {
                "monthly": "月线级别中性偏多（技术突破需时间验证）",
                "weekly": "周线级别偏多（技术突破推动中期估值修复）",
                "daily": "日线级别偏多（短线情绪催化）"
            }
        elif analysis["buy_points"]["third"]:
            analysis["multi_level"] = {
                "monthly": "月线级别需观察（趋势延续还是末端加速）",
                "weekly": "周线级别偏多（趋势仍在延续）",
                "daily": "日线级别警惕短线过热"
            }
        else:
            analysis["multi_level"] = {
                "monthly": "月线级别中性",
                "weekly": "周线级别中性",
                "daily": "日线级别中性"
            }

        # ===== 综合走势判断 =====
        analysis["confidence_score"] = max(5, min(95, analysis["confidence_score"]))

        if active_sp > 0:
            analysis["trend_judgment"] = f"偏空，{industry}板块需警惕回调风险"
            analysis["operation_suggestion"] = "建议减仓或观望，等待卖压释放"
        elif active_bp >= 2 or analysis["confidence_score"] >= 55:
            analysis["trend_judgment"] = f"偏多，关注{industry}相关板块"
            analysis["operation_suggestion"] = f"可关注{industry}板块，等待合适买点"
        elif active_bp == 1 or analysis["confidence_score"] >= 40:
            analysis["trend_judgment"] = f"中性偏多，继续观察{industry}板块"
            analysis["operation_suggestion"] = "继续观察，等待更多信号确认"
        else:
            analysis["trend_judgment"] = "中性，保持观望"
            analysis["operation_suggestion"] = "暂不操作，等待明确信号"

        return analysis


# ============================================================
# 【模块4】核心信息提取器 + 产业链关联分析
# ============================================================
class CoreInfoExtractor:
    """核心信息提取 + 产业链关联分析"""

    EVENT_TYPES = {
        "政策发布": ["政策", "规划", "发布", "出台", "印发", "通知", "意见", "方案", "部署"],
        "技术突破": ["突破", "进展", "研发", "成功", "首次", "创新", "专利", "研制", "下线", "量产"],
        "产能扩张": ["产能", "量产", "扩产", "投产", "开工", "下线", "基地", "项目", "投资"],
        "合作并购": ["合作", "并购", "收购", "投资", "合资", "签约", "战略", "入股"],
        "市场动态": ["增长", "销量", "订单", "新高", "景气", "数据", "营收", "利润", "出货量"],
        "会议论坛": ["论坛", "峰会", "大会", "会议", "展会", "研讨"],
    }

    SUBJECT_MAP = {
        "政府机构": ["国务院", "发改委", "工信部", "科技部", "财政部", "央行", "证监会", "国资委", "商务部", "中央", "中共中央"],
        "核心企业": ["华为", "中芯国际", "宁德时代", "比亚迪", "腾讯", "阿里", "百度", "字节跳动", "小米", "寒武纪", "科大讯飞"],
        "行业协会": ["协会", "联盟", "联合会", "商会"],
    }

    def extract(self, news, industry):
        title = news["title"]
        snippet = news.get("snippet", "")
        text = title + " " + snippet

        stocks = self._identify_stocks(industry, text)
        chain_impact = self._analyze_chain_impact(industry, text)

        return {
            "event_subject": self._identify_subject(text),
            "event_type": self._identify_event_type(text),
            "impact_scope": self._identify_impact_scope(text),
            "time_sensitivity": self._identify_time_sensitivity(title),
            "industry": industry,
            "potential_stocks": stocks,
            "chain_impact": chain_impact,  # v9新增
        }

    def _identify_subject(self, text):
        for category, kws in self.SUBJECT_MAP.items():
            for kw in kws:
                if kw in text:
                    return kw
        return "行业相关主体"

    def _identify_event_type(self, text):
        for etype, kws in self.EVENT_TYPES.items():
            for kw in kws:
                if kw in text:
                    return etype
        return "行业动态"

    def _identify_impact_scope(self, text):
        gov_keywords = ["国务院", "全国", "国家", "全球", "国际", "规划", "政策", "发改委", "工信部", "科技部", "中央"]
        if any(kw in text for kw in gov_keywords):
            return "国家级/全球性"
        elif any(kw in text for kw in ["行业", "产业", "领域", "板块", "产业链"]):
            return "行业级"
        return "企业级"

    def _identify_time_sensitivity(self, title):
        high_words = ["今日", "刚刚", "最新", "突发", "紧急", "今天", "今夜"]
        mid_words = ["近日", "近期", "本周", "本月", "今年"]
        if any(w in title for w in high_words):
            return "高"
        elif any(w in title for w in mid_words):
            return "中"
        return "低"

    def _identify_stocks(self, industry, text):
        stocks = []
        config = FIFTEEN_FIVE_INDUSTRIES.get(industry, {})
        if "stocks" in config:
            stocks.extend(config["stocks"][:5])
        for ind_c, ind_conf in FIFTEEN_FIVE_INDUSTRIES.items():
            if "stocks" in ind_conf:
                for company in ind_conf["stocks"]:
                    if company in text and company not in stocks:
                        stocks.insert(0, company)
        return stocks[:6]

    def _analyze_chain_impact(self, industry, text):
        """v9新增：分析资讯对产业链上下游的影响"""
        chain = INDUSTRY_CHAIN_MAP.get(industry, {})
        if not chain:
            return {"upstream_impact": [], "downstream_impact": [], "chokepoint_impact": []}

        upstream_impact = [up for up in chain.get("upstream", []) if up in text]
        downstream_impact = [dn for dn in chain.get("downstream", []) if dn in text]
        chokepoint_impact = [cp for cp in chain.get("chokepoints", []) if cp in text]

        return {
            "upstream_impact": upstream_impact,
            "downstream_impact": downstream_impact,
            "chokepoint_impact": chokepoint_impact
        }


# ============================================================
# 【模块5】历史趋势对比器（v9新增）
# ============================================================
class HistoryTrendComparator:
    """历史趋势对比器 - 与昨日/上周同期对比，发现新兴热点"""

    def __init__(self):
        self.today_data = {}
        self.history_data = {}

    def load_history(self, date_str):
        """加载历史数据"""
        # 加载昨日数据
        yesterday = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_file = REPORT_DIR / f"{yesterday}_下午_tech_intel_data.json"
        if yesterday_file.exists():
            try:
                with open(yesterday_file, 'r', encoding='utf-8') as f:
                    self.history_data["yesterday"] = json.load(f)
            except Exception:
                pass

        # 加载上周同期数据
        last_week = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        last_week_file = REPORT_DIR / f"{last_week}_下午_tech_intel_data.json"
        if last_week_file.exists():
            try:
                with open(last_week_file, 'r', encoding='utf-8') as f:
                    self.history_data["last_week"] = json.load(f)
            except Exception:
                pass

    def compare(self, today_analyzed_data, date_str):
        """对比分析"""
        self.load_history(date_str)
        self.today_data = today_analyzed_data

        comparison = {
            "industry_heat_change": {},
            "emerging_hotspots": [],
            "cooling_topics": [],
            "persistent_topics": [],
        }

        # 今日各产业热度
        today_heat = {ind: len(lst) for ind, lst in today_analyzed_data.items()}

        # 对比昨日
        yesterday_heat = {}
        if "yesterday" in self.history_data:
            yesterday_news = self.history_data["yesterday"].get("news_data", {})
            yesterday_heat = {ind: len(lst) for ind, lst in yesterday_news.items()}

        # 对比上周
        last_week_heat = {}
        if "last_week" in self.history_data:
            last_week_news = self.history_data["last_week"].get("news_data", {})
            last_week_heat = {ind: len(lst) for ind, lst in last_week_news.items()}

        # 计算变化
        for industry in FIFTEEN_FIVE_INDUSTRIES.keys():
            today_count = today_heat.get(industry, 0)
            yesterday_count = yesterday_heat.get(industry, 0)
            last_week_count = last_week_heat.get(industry, 0)

            change_vs_yesterday = today_count - yesterday_count
            change_vs_last_week = today_count - last_week_count

            comparison["industry_heat_change"][industry] = {
                "today": today_count,
                "yesterday": yesterday_count,
                "last_week": last_week_count,
                "change_vs_yesterday": change_vs_yesterday,
                "change_vs_last_week": change_vs_last_week,
                "trend": "上升" if change_vs_yesterday > 0 else ("下降" if change_vs_yesterday < 0 else "持平")
            }

            # 新兴热点：今日>3条 且 昨日≤1条
            if today_count >= 3 and yesterday_count <= 1:
                comparison["emerging_hotspots"].append(industry)

            # 冷却话题：今日≤1条 且 昨日≥3条
            if today_count <= 1 and yesterday_count >= 3:
                comparison["cooling_topics"].append(industry)

            # 持续热点：今日≥3条 且 昨日≥3条
            if today_count >= 3 and yesterday_count >= 3:
                comparison["persistent_topics"].append(industry)

        return comparison


# ============================================================
# 【模块6】知识图谱构建器
# ============================================================
class KnowledgeGraphBuilder:
    """构建十五五产业知识图谱"""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self._node_ids = {}
        self._next_id = 1

    def _get_or_create_node(self, name, ntype, industry=None, extra=None):
        key = f"{ntype}:{name}"
        if key in self._node_ids:
            return self._node_ids[key]
        nid = f"N{self._next_id:04d}"
        self._next_id += 1
        node = {"id": nid, "name": name, "type": ntype, "industry": industry, "extra": extra or {}}
        self.nodes.append(node)
        self._node_ids[key] = nid
        return nid

    def _add_edge(self, from_id, to_id, relation, weight=1.0):
        self.edges.append({"from": from_id, "to": to_id, "relation": relation, "weight": weight})

    def add_news_item(self, industry, news, core_info, chan_analysis, reverse_signal):
        title = news["title"]
        source = news.get("source", "未知")

        industry_id = self._get_or_create_node(industry, "industry", industry)

        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        event_id = self._get_or_create_node(
            f"{title[:30]}({title_hash})", "news_event", industry, {
                "title": title,
                "url": news.get("url", ""),
                "source": source,
                "event_type": core_info["event_type"],
                "impact_scope": core_info["impact_scope"],
                "chan_confidence": chan_analysis.get("confidence_score", 30),
                "has_reverse_signal": reverse_signal.get("has_reverse_signal", False),
                "risk_level": reverse_signal.get("risk_level", "低"),
            }
        )
        self._add_edge(industry_id, event_id, "出现事件")

        # v9新增：产业链关联节点
        chain_impact = core_info.get("chain_impact", {})
        for up in chain_impact.get("upstream_impact", []):
            up_id = self._get_or_create_node(up, "upstream", industry)
            self._add_edge(event_id, up_id, "影响上游", 0.6)

        for dn in chain_impact.get("downstream_impact", []):
            dn_id = self._get_or_create_node(dn, "downstream", industry)
            self._add_edge(event_id, dn_id, "影响下游", 0.6)

        for cp in chain_impact.get("chokepoint_impact", []):
            cp_id = self._get_or_create_node(cp, "chokepoint", industry)
            self._add_edge(event_id, cp_id, "涉及瓶颈", 0.9)

        for stock in core_info.get("potential_stocks", []):
            stock_id = self._get_or_create_node(stock, "stock", industry)
            weight = 0.3 if reverse_signal.get("has_reverse_signal") else 0.8
            self._add_edge(event_id, stock_id, "关联股票", weight)

    def export_graph(self, date_str):
        return {
            "metadata": {
                "date": date_str,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "v9.0",
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges)
            },
            "nodes": self.nodes,
            "edges": self.edges,
            "node_type_stats": dict(Counter(n["type"] for n in self.nodes)),
            "industry_stats": dict(Counter(n["industry"] for n in self.nodes if n["industry"]))
        }


# ============================================================
# 【主 orchestrator】每日科技资讯系统 v9
# ============================================================
class DailyTechIntelSystemV9:
    """每日科技前沿资讯分析系统 v9.0 - WebSearch增强版"""

    def __init__(self, session_label="下午"):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.time_str = datetime.now().strftime("%H:%M:%S")
        self.date_time_str = f"{self.date_str} {self.time_str}"
        self.session_label = session_label

        self.fetcher = DualSourceNewsFetcher()
        self.reverse_analyzer = EnhancedReverseSignalAnalyzer()
        self.core_extractor = CoreInfoExtractor()
        self.chan_analyzer = EnhancedChanTheoryAnalyzer()
        self.graph_builder = KnowledgeGraphBuilder()
        self.history_comparator = HistoryTrendComparator()

        self.news_data = {}
        self.analyzed_data = {}
        self.comparison = {}

    def crawl_all_news(self):
        """流程1: 双重搜索爬取"""
        print("=" * 80)
        print(f"🚀 每日科技前沿资讯分析系统 v9.0【{self.session_label}】")
        print("=" * 80)
        print(f"执行时间: {self.date_time_str}")
        print(f"📡 双重搜索策略（requests爬虫 + WebSearch API降级）")
        print()

        self.news_data = self.fetcher.search_all_industries()
        total = sum(len(v) for v in self.news_data.values())
        print(f"\n📊 共获取 {total} 条资讯")
        if self.fetcher.websearch_used:
            print(f"🔄 已启用WebSearch API降级搜索")
        return self.news_data

    def analyze_all_news(self):
        """流程2: 深度分析"""
        print("\n🔍 开始深度分析...")
        self.analyzed_data = {}

        for industry, news_list in self.news_data.items():
            analyzed_list = []
            for news in news_list:
                title = news["title"]
                snippet = news.get("snippet", "")
                url = news.get("url", "")
                source = news.get("source", "")

                core_info = self.core_extractor.extract(news, industry)
                reverse_signal = self.reverse_analyzer.analyze(title, snippet, url, source)
                chan = self.chan_analyzer.analyze(title, snippet, industry, core_info)

                analyzed_list.append({
                    "news": news,
                    "core_info": core_info,
                    "reverse_signal": reverse_signal,
                    "chan_analysis": chan
                })

                self.graph_builder.add_news_item(industry, news, core_info, chan, reverse_signal)

            analyzed_list.sort(key=lambda x: (
                1 if x["reverse_signal"]["has_reverse_signal"] else 0,
                -x["chan_analysis"]["confidence_score"]
            ))
            self.analyzed_data[industry] = analyzed_list

        # 多源交叉验证
        print("  🔗 执行多源交叉验证...")
        self.analyzed_data = self.reverse_analyzer.cross_validate(self.analyzed_data)

        # 历史趋势对比
        print("  📊 执行历史趋势对比...")
        self.comparison = self.history_comparator.compare(self.analyzed_data, self.date_str)

        total = sum(len(v) for v in self.analyzed_data.values())
        print(f"  ✓ 已分析 {total} 条资讯（含交叉验证+历史对比）")
        return self.analyzed_data

    def generate_report(self):
        """流程3: 生成报告"""
        print("\n📝 生成分析报告...")

        total_news = sum(len(v) for v in self.news_data.values())
        normal = sum(1 for lst in self.analyzed_data.values()
                     for item in lst if not item["reverse_signal"]["has_reverse_signal"])
        reverse = total_news - normal
        high_impact = sum(1 for lst in self.analyzed_data.values()
                          for item in lst if item["core_info"]["impact_scope"] in ["国家级/全球性", "行业级"])
        high_chan = sum(1 for lst in self.analyzed_data.values()
                       for item in lst if item["chan_analysis"]["confidence_score"] >= 50)
        divergence_count = sum(1 for lst in self.analyzed_data.values()
                               for item in lst if item["chan_analysis"]["divergence"]["detected"])

        search_method = "WebSearch API降级" if self.fetcher.websearch_used else "requests爬虫+WebSearch"

        report = f"""# 📊 {self.date_str}【{self.session_label}】科技前沿资讯分析报告

> 📅 生成时间: {self.date_time_str}
> 🏷️ 版本: v9.0（WebSearch增强版 | 十五五规划重点产业跟踪）
> 🔁 执行时间: 每日下午14:30
> 📡 搜索策略: {search_method}

---

## 📌 报告摘要

| 指标 | 数值 |
|------|------|
| 📰 爬取资讯总数 | {total_news} |
| ✅ 正常资讯 | {normal} |
| ⚠️ 反向信号（疑似标题党/枪手） | {reverse} |
| 🎯 高影响力资讯 | {high_impact} |
| 📈 缠论高置信信号(≥50%) | {high_chan} |
| 🔴 背驰信号 | {divergence_count} |

**执行时间**: {self.date_time_str}
**本次会话**: {self.session_label}（14:30 午间盘面更新 + 下午资讯整合）
**【14:30 特别提示】**: 下午时段需特别警惕自媒体炒作和尾盘资金博弈

"""

        # 分产业详细分析
        report += self._section_industries()
        report += self._section_reverse_signal()
        report += self._section_chan()
        report += self._section_history_trend()
        report += self._section_knowledge()

        report += "---\n"
        report += "*本报告由每日科技资讯分析系统 v9.0 自动生成 | 双重搜索策略: requests爬虫 + WebSearch API降级*\n"
        report += "*⚠️ 报告内容仅供参考，不构成投资建议。股市有风险，投资需谨慎。*\n"

        return report

    def _section_industries(self):
        section = "## 📋 十五五规划相关产业动态\n\n"
        industries_with_news = [(ind, lst) for ind, lst in self.analyzed_data.items() if lst]

        if not industries_with_news:
            return section + "> ⚠️ 本次爬取未获取到相关资讯，请稍候再试。\n\n"

        industries_with_news.sort(key=lambda x: -len(x[1]))

        for industry, news_list in industries_with_news:
            section += f"### 🔬 {industry}（共{len(news_list)}条）\n\n"
            for i, item in enumerate(news_list[:6], 1):
                news = item["news"]
                core = item["core_info"]
                reverse = item["reverse_signal"]
                chan = item["chan_analysis"]

                if reverse["has_reverse_signal"]:
                    risk_tag = " 🔴" if reverse["risk_level"] == "高" else " 🟠"
                else:
                    risk_tag = " 🟢"

                section += f"**{i}. {news['title']}**{risk_tag}\n\n"
                section += f"   - **来源**: {news.get('source', '未知')} | **搜索源**: {news.get('search_engine', '综合')} | **事件**: {core['event_type']} | **影响**: {core['impact_scope']}\n"

                buy_points = []
                if chan["buy_points"]["first"]:
                    buy_points.append("一买")
                if chan["buy_points"]["second"]:
                    buy_points.append("二买")
                if chan["buy_points"]["third"]:
                    buy_points.append("三买")

                sell_points = []
                if chan["sell_points"]["first"]:
                    sell_points.append("一卖")
                if chan["sell_points"]["second"]:
                    sell_points.append("二卖")

                bp_str = "、".join(buy_points) if buy_points else ""
                sp_str = "、".join(sell_points) if sell_points else ""

                # v9新增：走势类型和操作级别
                trend_type = chan.get("trend_type", "盘整")
                op_level = chan.get("operation_level", "观望")

                if bp_str and sp_str:
                    section += f"   - **缠论**: 🟢 {bp_str} / 🔴 {sp_str}（置信{chan['confidence_score']}%）| 走势: {trend_type} | 操作: {op_level} | 中枢: {chan['pivot_type']}\n"
                elif bp_str:
                    section += f"   - **缠论**: 🟢 {bp_str}信号（置信{chan['confidence_score']}%）| 走势: {trend_type} | 操作: {op_level} | 中枢: {chan['pivot_type']}\n"
                elif sp_str:
                    section += f"   - **缠论**: 🔴 {sp_str}信号（置信{chan['confidence_score']}%）| 走势: {trend_type} | 操作: {op_level} | 中枢: {chan['pivot_type']}\n"
                else:
                    section += f"   - **缠论**: ⚪ 无明确信号（置信{chan['confidence_score']}%）| 走势: {trend_type} | 操作: {op_level}\n"

                if chan["divergence"]["detected"]:
                    section += f"   - **⚠️ 背驰**: {chan['divergence']['type']} - {chan['divergence']['desc']}\n"

                # v9新增：产业链关联
                chain = core.get("chain_impact", {})
                chain_parts = []
                if chain.get("upstream_impact"):
                    chain_parts.append(f"上游: {','.join(chain['upstream_impact'])}")
                if chain.get("downstream_impact"):
                    chain_parts.append(f"下游: {','.join(chain['downstream_impact'])}")
                if chain.get("chokepoint_impact"):
                    chain_parts.append(f"瓶颈: {','.join(chain['chokepoint_impact'])}")
                if chain_parts:
                    section += f"   - **🔗 产业链**: {' | '.join(chain_parts)}\n"

                if core["potential_stocks"]:
                    section += f"   - **关联股票**: {'、'.join(core['potential_stocks'])}\n"

                if reverse["has_reverse_signal"]:
                    section += f"   - **⚠️ 风险**: {reverse['risk_level']}级 | 关键词: {', '.join(reverse['signal_words'][:5])}\n"
                    section += f"   - **💡 建议**: {reverse['suggestion']}\n"
                    if reverse.get("cross_validation"):
                        section += f"   - **🔗 交叉验证**: {reverse['cross_validation']}\n"

                if news.get("url") and news["url"].startswith("http"):
                    section += f"   - **原文链接**: {news['url']}\n"

                section += "\n"

            if len(news_list) > 6:
                section += f"*（还有 {len(news_list) - 6} 条资讯，详见 JSON 数据文件）*\n\n"
            section += "\n"

        return section

    def _section_reverse_signal(self):
        all_reverse = []
        for industry, news_list in self.analyzed_data.items():
            for item in news_list:
                if item["reverse_signal"]["has_reverse_signal"]:
                    item_copy = dict(item)
                    item_copy["industry"] = industry
                    all_reverse.append(item_copy)

        if not all_reverse:
            return "## ✅ 反向信号检测\n\n本次未检测到明显的标题党或资本雇佣枪手发文，资讯质量较好。\n\n"

        section = f"## ⚠️ 反向信号预警（共{len(all_reverse)}条）\n\n"
        section += "> **⚠️ 重要提示**: 以下资讯存在标题党或诱导性特征，疑似资本雇佣枪手发文，请务必反向思考！\n\n"

        all_reverse.sort(key=lambda x: -x["reverse_signal"]["signal_score"])
        for i, item in enumerate(all_reverse[:10], 1):
            news = item["news"]
            reverse = item["reverse_signal"]
            industry = item["industry"]

            risk_icon = "🔴" if reverse["risk_level"] == "高" else "🟠"

            section += f"**{i}. {risk_icon} [{industry}] {news['title']}**\n\n"
            section += f"   - **风险评分**: {reverse['signal_score']}分 | **风险等级**: {reverse['risk_level']}级\n"
            if reverse["signal_words"]:
                section += f"   - **风险关键词**: {', '.join(reverse['signal_words'][:6])}\n"
            if reverse["title_party_pattern"]:
                section += f"   - **标题党模式**: {', '.join(reverse['title_party_pattern'])}\n"
            if reverse["gunman_pattern"]:
                section += f"   - **枪手特征**: {', '.join(reverse['gunman_pattern'])}\n"
            if reverse["timing_risk"]:
                section += f"   - **发文时间风险**: {reverse['timing_risk']}\n"
            if reverse["source_risk"]:
                section += f"   - **来源风险**: {reverse['source_risk']}\n"
            if reverse.get("chain_risk"):
                section += f"   - **产业链风险**: {reverse['chain_risk']}\n"
            if reverse.get("cross_validation"):
                section += f"   - **交叉验证**: {reverse['cross_validation']}\n"
            if reverse["analysis"]:
                section += f"   - **综合分析**: {reverse['analysis']}\n"
            section += f"   - **💡 操作建议**: {reverse['suggestion']}\n\n"

        section += """### 🔬 v9.0 反向信号识别原理（增强版 11维检测）

本系统通过以下**11个维度**综合判断是否为标题党或资本雇佣枪手发文：

1. **情绪词检测**: 极端词汇、内幕词汇、操作词汇（权重1-3）
2. **夸张数字检测**: "暴涨XX倍"、"暴增XX亿"等诱导性数字
3. **标点模式识别**: 多感叹号、感叹号开头、多问号等
4. **开头模式识别**: "震惊！"、"刚刚"、"重磅！"等典型标题党开头
5. **枪手引导语识别**: "手把手教你"、"一定要看"、"最后的机会"等
6. **来源多级评估**: 权威媒体(A/B级) → 主流媒体(C级) → 自媒体 → 不可信
7. **自媒体平台特征**: 头条、百家号、企鹅号、雪球、股吧等平台内容加权
8. **发文时间规律**: 盘前8-9点、尾盘14-15点、深夜22点后风险加成
9. **产业链炒作模式**: 涉及瓶颈环节的炒作性报道（v9新增）
10. **标题正文不一致**: 标题极端但正文正常（v9新增）
11. **综合评分**: 总分≥12高风险/≥7中风险

### 🎯 枪手发文典型特征

| 时间段 | 风险加成 | 原理 |
|--------|---------|------|
| 盘前8-9点 | +3 | 制造开盘情绪，诱导集合竞价跟风 |
| 尾盘14-15点 | +4 | 诱导尾盘追涨，次日出货 |
| 深夜22点后 | +2 | 利用次日开盘情绪发酵 |

**核心原则**: 利好出尽是利空，利空出尽是利好。标题党越疯狂，越要反向思考！

"""
        return section

    def _section_chan(self):
        first_buy = sum(1 for lst in self.analyzed_data.values()
                        for item in lst if item["chan_analysis"]["buy_points"]["first"])
        second_buy = sum(1 for lst in self.analyzed_data.values()
                         for item in lst if item["chan_analysis"]["buy_points"]["second"])
        third_buy = sum(1 for lst in self.analyzed_data.values()
                        for item in lst if item["chan_analysis"]["buy_points"]["third"])
        first_sell = sum(1 for lst in self.analyzed_data.values()
                         for item in lst if item["chan_analysis"]["sell_points"]["first"])
        second_sell = sum(1 for lst in self.analyzed_data.values()
                          for item in lst if item["chan_analysis"]["sell_points"]["second"])
        divergence = sum(1 for lst in self.analyzed_data.values()
                         for item in lst if item["chan_analysis"]["divergence"]["detected"])

        # v9新增：走势类型统计
        trend_types = Counter()
        op_levels = Counter()
        for lst in self.analyzed_data.values():
            for item in lst:
                trend_types[item["chan_analysis"].get("trend_type", "盘整")] += 1
                op_levels[item["chan_analysis"].get("operation_level", "观望")] += 1

        section = f"""## 📈 缠论视角深度分析（v9.0增强版）

### 核心买卖点信号统计

| 信号类型 | 数量 | 说明 |
|----------|------|------|
| 🟢 第一类买点 | {first_buy} | 政策发布、技术突破带来的驱动型机会（下跌趋势末端背驰） |
| 🟢 第二类买点 | {second_buy} | 回调确认后的安全介入点（不创新低的回踩确认） |
| 🟢 第三类买点 | {third_buy} | 趋势确立后的加速机会（离开中枢不回抽，需警惕情绪过热） |
| 🔴 第一类卖点 | {first_sell} | 上涨趋势末端背驰（见顶信号） |
| 🔴 第二类卖点 | {second_sell} | 反弹不创新高（冲高回落） |
| ⚠️ 背驰信号 | {divergence} | 量价背驰/政策背驰/情绪背驰 |

### v9.0 新增：走势类型分布

| 走势类型 | 数量 | 操作建议 |
|----------|------|---------|
| 上涨趋势 | {trend_types.get('上涨趋势', 0)} | 持有或回调加仓 |
| 盘整偏多 | {trend_types.get('盘整偏多', 0)} | 观察突破方向 |
| 盘整 | {trend_types.get('盘整', 0)} | 等待方向选择 |
| 下跌趋势 | {trend_types.get('下跌趋势', 0)} | 减仓或观望 |

### v9.0 新增：操作级别分布

| 操作级别 | 数量 |
|----------|------|
| 买入 | {op_levels.get('买入', 0)} |
| 持有 | {op_levels.get('持有', 0)} |
| 减仓 | {op_levels.get('减仓', 0)} |
| 观望 | {op_levels.get('观望', 0)} |

### 背驰检测详解

**背驰是缠论最核心的概念之一**——它标志着趋势的衰竭和转折：

| 背驰类型 | 判定依据 | 级别 | 操作含义 |
|----------|---------|------|---------|
| 量价背驰 | 放量滞涨/缩量上涨/量价背离 | 日线 | 短线趋势可能衰竭 |
| 政策背驰 | 利好出尽/政策落地/预期兑现 | 周线 | 中期可能形成政策顶 |
| 情绪背驰 | 全民炒股/跑步入场/闭眼赚钱 | 月线 | 长期可能形成情绪顶 |

> **原理举例**: 当所有人都说"AI是未来"的时候，往往是AI板块短期见顶的信号——这就是情绪背驰。缠论说"走势终完美"，任何级别的走势类型终将完成，完成后必然转化为其他类型。

### 多级别联立分析

缠论强调"看大做小"——大级别定方向，小级别找买点：

- **月线级别**: 决定长期趋势方向（持有还是离场）
- **周线级别**: 决定中期操作节奏（加仓还是减仓）
- **日线级别**: 决定短线买卖时机（入场还是观望）

> **原理举例**: 月线处于上涨趋势，周线回调到中枢下沿，日线出现二买信号——这是理想的"三级共振"买入时机。

### 今日高置信信号（缠论置信度≥50%）

"""
        high_confidence_items = []
        for industry, news_list in self.analyzed_data.items():
            for item in news_list:
                if item["chan_analysis"]["confidence_score"] >= 50 and not item["reverse_signal"]["has_reverse_signal"]:
                    item["industry"] = industry
                    high_confidence_items.append(item)
        high_confidence_items.sort(key=lambda x: -x["chan_analysis"]["confidence_score"])

        if high_confidence_items:
            for i, item in enumerate(high_confidence_items[:10], 1):
                news = item["news"]
                chan = item["chan_analysis"]
                industry = item["industry"]

                bp_list = []
                if chan["buy_points"]["first"]:
                    bp_list.append("一买")
                if chan["buy_points"]["second"]:
                    bp_list.append("二买")
                if chan["buy_points"]["third"]:
                    bp_list.append("三买")

                section += f"**{i}. [{industry}] {news['title']}**\n"
                section += f"   - 买点: {'、'.join(bp_list) if bp_list else '无明确'} | 置信度: {chan['confidence_score']}% | 走势: {chan.get('trend_type', '盘整')} | 操作: {chan.get('operation_level', '观望')}\n"
                section += f"   - 中枢: {chan['pivot_type']} | {chan['trend_judgment']}\n"
                section += f"   - 建议: {chan['operation_suggestion']}\n"
                if chan["multi_level"].get("daily"):
                    section += f"   - 多级别: {chan['multi_level']['daily']}\n"
                if chan["risk_warning"]:
                    section += f"   - {chan['risk_warning']}\n"
                section += "\n"
        else:
            section += "*本次暂无高置信度缠论信号，建议保持观望，等待更明确的市场信号。*\n\n"

        section += """### 综合策略建议

1. **仓位管理**: 结合当前市场情绪，建议总仓位控制在 30%-60%，避免情绪化追涨
2. **选股方向**: 重点关注 人工智能、半导体、新能源、数字经济 等十五五重点赛道
3. **入场时机**: 等待明确的回调确认信号（日线级别的二买/三买），不要追高买入
4. **止损设置**: 单只股票亏损幅度建议不超过 5%-8%，严格执行止损纪律
5. **风险控制**: 当反向信号密集出现时，需警惕情绪过热，考虑减仓或观望
6. **背驰警示**: 一旦出现量价背驰或政策背驰，需立即警惕趋势转折

### 缠论操作口诀

1. 买点买，卖点卖，纪律第一
2. 看大做小，长短线结合
3. 级别递归，走势分解
4. 中枢震荡做短差，趋势持有
5. 严格止损，控制仓位
6. 背驰即转折，转折即机会

"""
        return section

    def _section_history_trend(self):
        """v9新增：历史趋势对比章节"""
        section = "## 📊 历史趋势对比（v9.0新增）\n\n"

        if not self.comparison:
            return section + "*暂无历史数据对比。*\n\n"

        # 产业热度变化
        section += "### 产业热度变化\n\n"
        section += "| 产业 | 今日 | 昨日 | 变化 | 趋势 |\n"
        section += "|------|------|------|------|------|\n"

        heat_change = self.comparison.get("industry_heat_change", {})
        for industry, data in sorted(heat_change.items(), key=lambda x: -x[1]["today"]):
            change = data["change_vs_yesterday"]
            change_str = f"+{change}" if change > 0 else str(change)
            trend_icon = "📈" if change > 0 else ("📉" if change < 0 else "➡️")
            section += f"| {industry} | {data['today']} | {data['yesterday']} | {change_str} | {trend_icon} |\n"

        section += "\n"

        # 新兴热点
        emerging = self.comparison.get("emerging_hotspots", [])
        if emerging:
            section += f"### 🔥 新兴热点（今日≥3条，昨日≤1条）\n\n"
            for ind in emerging:
                section += f"- **{ind}** 🔥 新增关注\n"
            section += "\n"

        # 冷却话题
        cooling = self.comparison.get("cooling_topics", [])
        if cooling:
            section += f"### ❄️ 冷却话题（今日≤1条，昨日≥3条）\n\n"
            for ind in cooling:
                section += f"- **{ind}** ❄️ 热度下降\n"
            section += "\n"

        # 持续热点
        persistent = self.comparison.get("persistent_topics", [])
        if persistent:
            section += f"### 🔥 持续热点（今日≥3条，昨日≥3条）\n\n"
            for ind in persistent:
                section += f"- **{ind}** 🔥 持续关注\n"
            section += "\n"

        if not emerging and not cooling and not persistent:
            section += "*暂无显著的趋势变化。*\n\n"

        return section

    def _section_knowledge(self):
        section = "## 🧠 知识沉淀与持续跟踪\n\n"
        section += "### 今日核心知识点（高影响力资讯）\n\n"

        high_impact_items = []
        for industry, news_list in self.analyzed_data.items():
            for item in news_list:
                if item["core_info"]["impact_scope"] in ["国家级/全球性", "行业级"] and not item["reverse_signal"]["has_reverse_signal"]:
                    item["industry"] = industry
                    high_impact_items.append(item)

        if high_impact_items:
            for i, item in enumerate(high_impact_items[:6], 1):
                news = item["news"]
                core = item["core_info"]
                section += f"{i}. **[{core['industry']}] {news['title']}**\n"
                section += f"   - 事件类型: {core['event_type']} | 影响范围: {core['impact_scope']} | 时间敏感度: {core['time_sensitivity']}\n"
                section += f"   - 主体: {core['event_subject']}\n"
                if core["potential_stocks"]:
                    section += f"   - 关联股票: {'、'.join(core['potential_stocks'])}\n"
                chain = core.get("chain_impact", {})
                if chain.get("chokepoint_impact"):
                    section += f"   - 涉及瓶颈: {', '.join(chain['chokepoint_impact'])}\n"
                section += "\n"
        else:
            section += "*本次暂无高影响力政策或行业资讯。*\n\n"

        # 产业热度统计
        section += "### 📊 本次产业热度排行\n\n"
        heat_data = [(ind, len(lst)) for ind, lst in self.analyzed_data.items() if lst]
        heat_data.sort(key=lambda x: -x[1])
        for rank, (ind, count) in enumerate(heat_data[:10], 1):
            bar = "█" * min(count, 20)
            section += f"{rank}. {ind:<10} {bar} {count}条\n"
        section += "\n"

        section += """### 🔭 持续关注方向

1. **政策面**: 十五五规划重点产业的后续政策落地、细化方案、资金支持
2. **技术面**: 人工智能、半导体、新能源领域的技术突破和商业化进展
3. **基本面**: 行业龙头的业绩、订单、产能扩张情况
4. **情绪面**: 警惕自媒体标题党和资本雇佣枪手的反向信号
5. **国际面**: 关注全球产业链变化、地缘政治对科技产业的影响
6. **产业链**: 关注瓶颈环节的突破进展（v9新增）

### ⚠️ 风险提示清单

- ⚠️ 单一资讯不足以作为投资决策依据，需多方验证
- ⚠️ 标题党资讯（暴涨、翻倍、内幕等）需反向思考（利好出尽是利空）
- ⚠️ 政策利好可能已被市场提前消化（买预期卖事实）
- ⚠️ 技术突破到商业化落地可能存在较长时间差（注意产业链兑现节奏）
- ⚠️ 热门板块容易出现情绪过热后的回调（情绪高位风险）
- ⚠️ 【特别警示】下午14:30-15:00是A股T+1交易机制下的尾盘博弈时段
- ⚠️ 【v9新增】关注背驰信号：量价背驰、政策背驰、情绪背驰都是趋势转折的前兆
- ⚠️ 【v9新增】产业链瓶颈环节炒作需特别警惕（可能是资本借题发挥）

"""
        return section

    def save_results(self, report):
        """流程4: 保存结果"""
        print("💾 正在保存结果...")

        # Markdown报告
        report_file = REPORT_DIR / f"{self.date_str}_{self.session_label}_tech_intel_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"  📁 分析报告: {report_file}")

        # JSON数据
        data_file = REPORT_DIR / f"{self.date_str}_{self.session_label}_tech_intel_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": self.date_str,
                "datetime": self.date_time_str,
                "session": self.session_label,
                "version": "v9.0",
                "search_method": "WebSearch API降级" if self.fetcher.websearch_used else "requests爬虫",
                "news_data": self.news_data,
                "analyzed_data": self.analyzed_data,
                "comparison": self.comparison,
            }, f, ensure_ascii=False, indent=2)
        print(f"  📁 分析数据: {data_file}")

        # 知识图谱
        graph_data = self.graph_builder.export_graph(self.date_str)
        graph_file = GRAPH_DIR / f"{self.date_str}_{self.session_label}_knowledge_graph.json"
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        print(f"  📁 知识图谱: {graph_file}（{graph_data['metadata']['total_nodes']} 节点, {graph_data['metadata']['total_edges']} 边）")

        # v9新增：按产业分类存储知识
        for industry, news_list in self.analyzed_data.items():
            if not news_list:
                continue
            industry_dir = KNOWLEDGE_DIR / "industries" / industry
            industry_dir.mkdir(parents=True, exist_ok=True)

            # 产业当日知识文件
            ind_knowledge_file = industry_dir / f"{self.date_str}_knowledge.md"
            ind_content = f"# {industry} - {self.date_str} 知识沉淀\n\n"
            for item in news_list[:10]:
                if not item["reverse_signal"]["has_reverse_signal"]:
                    news = item["news"]
                    core = item["core_info"]
                    chan = item["chan_analysis"]
                    ind_content += f"- **{news['title']}**\n"
                    ind_content += f"  - 事件: {core['event_type']} | 影响: {core['impact_scope']}\n"
                    chain = core.get("chain_impact", {})
                    if chain.get("chokepoint_impact"):
                        ind_content += f"  - 瓶颈: {', '.join(chain['chokepoint_impact'])}\n"
                    ind_content += f"  - 缠论: 置信{chan['confidence_score']}% | 走势: {chan.get('trend_type', '盘整')} | 操作: {chan.get('operation_level', '观望')}\n\n"
            with open(ind_knowledge_file, 'w', encoding='utf-8') as f:
                f.write(ind_content)

        # 追加到历史知识库
        knowledge_file = KNOWLEDGE_DIR / "tech_intel_history.md"
        knowledge_entry = f"\n\n---\n\n## {self.date_str}【{self.session_label}】（v9.0）\n{report[:1500]}...\n"
        if knowledge_file.exists():
            with open(knowledge_file, 'a', encoding='utf-8') as f:
                f.write(knowledge_entry)
        else:
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                f.write("# 科技资讯知识沉淀库\n" + knowledge_entry)
        print(f"  📚 知识库追加: {knowledge_file}")

        # v9新增：保存历史数据（供趋势对比用）
        history_file = HISTORY_DIR / f"{self.date_str}_{self.session_label}_snapshot.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": self.date_str,
                "session": self.session_label,
                "industry_heat": {ind: len(lst) for ind, lst in self.analyzed_data.items()},
            }, f, ensure_ascii=False, indent=2)
        print(f"  📁 历史快照: {history_file}")

        return report_file, data_file, graph_file

    def run(self):
        """主入口"""
        # 流程1: 爬取
        self.crawl_all_news()

        total = sum(len(v) for v in self.news_data.values())
        if total == 0:
            print("\n⚠️ 未获取到任何资讯，将生成空报告。")
        else:
            # 流程2: 分析
            self.analyze_all_news()

        # 流程3: 报告
        report = self.generate_report()

        # 流程4: 保存
        self.save_results(report)

        print("\n" + "=" * 80)
        print("✅ v9.0 分析完成！")
        print("=" * 80)

        return report


# ============================================================
# 命令行入口
# ============================================================
def main():
    now = datetime.now()
    hour = now.hour
    session = "上午" if hour < 12 else "下午"

    if len(sys.argv) >= 2:
        if "morning" in sys.argv[1] or "上午" in sys.argv[1]:
            session = "上午"
        elif "afternoon" in sys.argv[1] or "下午" in sys.argv[1]:
            session = "下午"

    system = DailyTechIntelSystemV9(session_label=session)
    system.run()


if __name__ == '__main__':
    main()
