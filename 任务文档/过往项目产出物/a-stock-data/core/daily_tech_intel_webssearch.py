#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技前沿资讯分析系统 - WebSearch增强版
==========================================
执行时间: 每日上午9:30
核心功能:
  1. 使用WebSearch工具搜索科技前沿资讯（聚焦十五五规划相关产业）
  2. 资讯分析与知识提取
  3. 缠论视角分析（第一类买点/第二类买点/第三类买点）
  4. 反向信号识别（标题党/情绪化/缺乏数据支撑）
  5. 结构化报告生成与知识沉淀

使用方式:
  python daily_tech_intel_webssearch.py
  python daily_tech_intel_webssearch.py --search  # 强制执行WebSearch（需要网络）
"""

import sys
import os
import json
import re
import time
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ========== 路径配置 ==========
PROJECT_DIR = Path(__file__).parent
REPORT_DIR = PROJECT_DIR / "daily_tech_intel"
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"
LOG_DIR = PROJECT_DIR / "logs"

for d in [REPORT_DIR, KNOWLEDGE_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))


# ============================================================
# 1. 十五五规划重点关注产业 + 搜索关键词
# ============================================================
FIFTEEN_FIVE_INDUSTRIES = {
    "人工智能": {
        "keywords": ["人工智能", "AI", "大模型", "生成式AI", "深度学习", "人形机器人", "机器视觉", "多模态", "智能体", "AGI"],
        "search_queries": [
            "人工智能 最新政策 技术突破 2026",
            "AI大模型 国产替代 最新进展",
            "人工智能 十五五规划 产业政策"
        ]
    },
    "半导体": {
        "keywords": ["半导体", "芯片", "集成电路", "先进制程", "国产替代", "中芯国际", "光刻", "先进封装", "存储", "晶圆", "EDA", "GPU", "CPU"],
        "search_queries": [
            "半导体 国产替代 芯片进展 2026",
            "光刻机 先进制程 突破 最新",
            "集成电路 十五五规划 产业政策"
        ]
    },
    "新能源": {
        "keywords": ["新能源", "光伏", "风电", "储能", "新能源汽车", "锂电池", "宁德时代", "比亚迪", "氢能", "燃料电池"],
        "search_queries": [
            "新能源 汽车 储能 光伏 最新政策",
            "锂电池 储能 产业动态 2026",
            "新能源汽车 十五五规划 政策"
        ]
    },
    "数字经济": {
        "keywords": ["数字经济", "数据中心", "算力", "云计算", "大数据", "东数西算", "工业互联网", "数据要素", "数字中国", "信创"],
        "search_queries": [
            "数字经济 云计算 大数据 最新政策",
            "东数西算 算力 产业动态 2026",
            "数据要素 数字化转型 十五五"
        ]
    },
    "新材料": {
        "keywords": ["新材料", "稀土", "碳纤维", "第三代半导体", "碳化硅", "氮化镓", "石墨烯", "超导"],
        "search_queries": [
            "新材料 稀土 碳纤维 最新突破",
            "碳化硅 氮化镓 半导体材料 进展",
            "先进新材料 产业政策 2026"
        ]
    },
    "生物医药": {
        "keywords": ["生物医药", "创新药", "基因编辑", "医疗器械", "CXO", "生物科技", "mRNA", "ADC", "GLP-1"],
        "search_queries": [
            "生物医药 创新药 最新政策",
            "医疗器械 国产替代 最新进展",
            "GLP-1 减肥药 产业动态"
        ]
    },
    "航天军工": {
        "keywords": ["航天", "商业航天", "卫星互联网", "军工", "无人机", "低空经济", "卫星", "北斗"],
        "search_queries": [
            "商业航天 卫星互联网 最新进展",
            "低空经济 无人机 产业政策",
            "军工 航天 十五五规划"
        ]
    },
    "智能网联汽车": {
        "keywords": ["自动驾驶", "车联网", "智能驾驶", "L3", "L4", "激光雷达", "毫米波雷达", "域控制器"],
        "search_queries": [
            "自动驾驶 智能驾驶 最新进展",
            "激光雷达 毫米波雷达 国产替代",
            "智能网联汽车 产业政策 2026"
        ]
    },
    "量子科技": {
        "keywords": ["量子计算", "量子通信", "量子科技", "量子比特"],
        "search_queries": [
            "量子计算 量子通信 最新突破",
            "量子科技 产业政策 进展"
        ]
    }
}


# ============================================================
# 2. 反向信号关键词（标题党/枪手特征识别）
# ============================================================
REVERSE_SIGNAL_KEYWORDS = {
    "极端词汇": ["暴涨", "暴跌", "必涨", "必跌", "翻倍", "妖股", "疯涨", "崩盘", "血洗", "涨停潮", "跌停潮",
                "炸了", "疯了", "暴增", "暴富", "狂涨", "狂跌", "井喷", "飙升", "爆发", "炸裂", "逆天",
                "彻底疯了", "彻底爆发", "历史首次", "全球第一", "全球首发", "行业第一", "彻底改变", "颠覆"],
    "内幕词汇": ["内幕", "独家", "重磅", "惊天", "震惊", "秘密", "内部消息", "绝密", "泄密", "爆料", "实锤",
                "曝光", "揭秘", "藏不住了", "瞒不住了", "不可告人", "不敢说"],
    "主体词汇": ["主力", "游资", "机构", "大佬", "牛散", "庄家", "操盘手", "国家队", "外资", "神秘资金", "聪明钱"],
    "时间词汇": ["即将", "马上", "立刻", "今日", "最新", "突发", "紧急", "刚刚", "就在刚才", "就在今天", "周末",
                "就在刚刚", "今晚", "今夜"],
    "引导词汇": ["手把手", "带你", "教你", "跟着", "躺赢", "赚钱", "发财", "致富", "必看", "收藏", "速看", "快看",
                "牛股", "龙头股", "十倍股", "翻倍股", "布局", "重点关注", "强烈推荐", "赶紧上车", "不要错过",
                "最后的机会", "千载难逢"],
    "操作词汇": ["抄底", "逃顶", "上车", "下车", "接力", "打板", "追涨", "杀跌", "核按钮", "满仓", "重仓", "梭哈",
                "All in", "砸锅卖铁", "卖房炒股"],
    "夸张词汇": ["震惊", "慌了", "哭了", "笑了", "懵了", "爽了", "赚翻了", "太可怕", "吓尿", "惊呆", "炸锅", "沸腾",
                "疯狂", "失控", "彻底失控", "泪目", "燃爆", "炸裂"],
    "权威滥用": ["央视", "新华社", "人民日报", "中央定调", "高层发话", "刚刚召开", "重磅会议"]
}


# ============================================================
# 3. 可靠来源列表
# ============================================================
RELIABLE_SOURCES = [
    "gov.cn", "miit.gov.cn", "most.gov.cn", "ndrc.gov.cn", "csrc.gov.cn",
    "www.gov.cn", "news.cn", "xinhuanet.com", "people.com.cn", "cctv.com",
    "stcn.com", "cs.com.cn", "zqrb.cn", "chinadaily.com.cn",
    "caixin.com", "yicai.com", "cls.cn",
]


# ============================================================
# 【模块1】WebSearch 模拟器（通过Google News RSS获取真实搜索结果）
# ============================================================
class WebSearchSimulator:
    """模拟WebSearch工具 - 通过Google News RSS获取真实搜索结果"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml,application/xml,text/html;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def search(self, query: str, num_results: int = 8) -> List[Dict[str, str]]:
        """通过Google News RSS搜索并返回结构化结果"""
        # 使用Google News RSS
        search_url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

        try:
            response = self.session.get(search_url, timeout=15, verify=False)
            response.encoding = 'utf-8'

            # 解析XML格式的RSS
            soup = BeautifulSoup(response.text, 'xml')

            results = []
            items = soup.find_all('item')

            for i, item in enumerate(items):
                if i >= num_results:
                    break

                title = self._get_text(item, 'title')
                link = self._get_text(item, 'link')
                description = self._get_text(item, 'description')

                # 清理HTML标签获取纯文本
                if description:
                    desc_soup = BeautifulSoup(description, 'html.parser')
                    description = desc_soup.get_text(strip=True)

                # 提取来源（pubDate中的来源或从标题推断）
                source = self._get_text(item, 'source') or self._extract_source_from_title(title)

                if title and len(title) > 5:
                    results.append({
                        "title": title,
                        "url": link,
                        "snippet": description or f"关于{query}的相关报道",
                        "source": source
                    })

            return results

        except Exception as e:
            print(f"   ⚠️ 搜索失败 [{query[:30]}...]: {e}")
            return []

    def _get_text(self, elem, tag):
        """安全获取XML标签文本"""
        found = elem.find(tag)
        return found.get_text(strip=True) if found else ""

    def _extract_source_from_title(self, title: str) -> str:
        """从标题中提取来源"""
        # 常见来源标识
        sources = [
            "新华网", "人民网", "央视", "人民日报", "新华社",
            "澎湃新闻", "财新", "财经", "第一财经", "21世纪经济",
            "证券时报", "上海证券报", "中国证券报", "经济观察报",
            "36氪", "虎嗅", "钛媒体", "界面新闻", "新浪", "腾讯", "网易", "凤凰网"
        ]
        for s in sources:
            if s in title:
                return s
        return "网络来源"

    def _extract_domain(self, url: str) -> str:
        """从URL提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return "未知来源"


# ============================================================
# 【模块2】反向信号分析器
# ============================================================
class ReverseSignalAnalyzer:
    """反向信号分析器 - 智能识别标题党和资本雇佣枪手发文"""

    def __init__(self):
        self.keywords = REVERSE_SIGNAL_KEYWORDS
        self.category_weights = {
            "极端词汇": 3,
            "内幕词汇": 3,
            "操作词汇": 3,
            "引导词汇": 2,
            "夸张词汇": 2,
            "主体词汇": 1,
            "时间词汇": 1,
            "权威滥用": 2
        }

    def analyze(self, title: str, snippet: str, url: str) -> Dict[str, Any]:
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
            "analysis": "",
            "suggestion": ""
        }

        # 1. 关键词匹配
        for category, kws in self.keywords.items():
            found = []
            for kw in kws:
                if kw in title:
                    found.append(kw)
                    signal["signal_score"] += self.category_weights.get(category, 2)
            if found:
                signal["signal_categories"][category] = found
                signal["signal_words"].extend(found)

        # 2. 数字夸张检测
        exaggeration_patterns = [
            (r'([1-9]\d{2,})%', '夸张百分比'),
            (r'暴增\s*\d+\s*亿', '暴增XX亿'),
            (r'暴涨\s*\d+\s*倍', '暴涨XX倍'),
            (r'翻\s*\d+\s*倍', '翻XX倍'),
        ]
        for pattern, label in exaggeration_patterns:
            match = re.search(pattern, title)
            if match:
                signal["signal_score"] += 5
                signal["signal_words"].append(f"{label}:{match.group()}")

        # 3. 标点符号检测
        excl = title.count("!") + title.count("！")
        if excl >= 2:
            signal["signal_score"] += 4
            signal["title_party_pattern"].append("多感叹号")

        # 4. 标题开头模式检测
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

        # 5. 来源可靠性判断
        is_reliable = any(rs in url or rs in signal.get("source", "") for rs in RELIABLE_SOURCES)
        if not is_reliable:
            signal["signal_score"] += 3

        # 6. 综合风险判定
        if signal["signal_score"] >= 10:
            signal["has_reverse_signal"] = True
            signal["risk_level"] = "高"
        elif signal["signal_score"] >= 6:
            signal["has_reverse_signal"] = True
            signal["risk_level"] = "中"
        elif signal["signal_score"] >= 3:
            signal["risk_level"] = "低"

        # 7. 生成建议
        if signal["has_reverse_signal"]:
            if signal["risk_level"] == "高":
                signal["suggestion"] = "高度疑似标题党或资本雇佣枪手发文，建议反向思考，切勿追涨！"
            else:
                signal["suggestion"] = "存在一定诱导性特征，需谨慎判断，建议多方核实。"
        else:
            signal["suggestion"] = "资讯质量正常，可正常关注。"

        return signal


# ============================================================
# 【模块3】缠论分析器
# ============================================================
class ChanTheoryAnalyzer:
    """缠论视角深度分析 - 判断买卖点、中枢类型、趋势判断"""

    def analyze(self, title: str, snippet: str, industry: str) -> Dict[str, Any]:
        text = title + " " + snippet

        analysis = {
            "buy_points": {"first": False, "second": False, "third": False, "details": []},
            "pivot_type": "",
            "trend_judgment": "",
            "operation_suggestion": "",
            "confidence_score": 30,
            "reasoning": []
        }

        # 第一类买点（政策驱动/技术突破）
        first_triggers = ["政策", "规划", "出台", "发布", "国务院", "工信部", "发改委", "科技部", "首次", "创新", "突破", "国产替代"]
        for trigger in first_triggers:
            if trigger in text:
                analysis["buy_points"]["first"] = True
                analysis["buy_points"]["details"].append(f"政策/技术驱动({trigger})")
                analysis["confidence_score"] += 15
                analysis["reasoning"].append(f"【一买】{trigger}事件可能形成行业政策底或技术突破驱动")
                break

        # 第二类买点（回调确认）
        second_triggers = ["确认", "企稳", "验证", "回踩", "回调", "调整", "筑底"]
        for trigger in second_triggers:
            if trigger in text:
                analysis["buy_points"]["second"] = True
                analysis["buy_points"]["details"].append(f"回调信号({trigger})")
                analysis["confidence_score"] += 10
                analysis["reasoning"].append(f"【二买】出现'{trigger}'，可能提示回踩确认机会")
                break

        # 第三类买点（趋势加速）
        third_triggers = ["新高", "加速", "超预期", "黄金期", "快车道", "井喷", "爆发", "高速增长", "供不应求"]
        for trigger in third_triggers:
            if trigger in text:
                analysis["buy_points"]["third"] = True
                analysis["buy_points"]["details"].append(f"趋势加速({trigger})")
                analysis["confidence_score"] += 10
                analysis["reasoning"].append(f"【三买】出现'{trigger}'，需警惕情绪过热，也可能是趋势延续")
                break

        # 中枢类型判断
        if any(kw in text for kw in ["政策", "规划", "出台", "发布"]):
            analysis["pivot_type"] = "政策支撑中枢"
            analysis["confidence_score"] += 8
        elif any(kw in text for kw in ["突破", "首次", "创新", "研发"]):
            analysis["pivot_type"] = "技术突破中枢"
            analysis["confidence_score"] += 8
        elif any(kw in text for kw in ["产能", "量产", "扩产"]):
            analysis["pivot_type"] = "基本面扩张中枢"
            analysis["confidence_score"] += 5
        else:
            analysis["pivot_type"] = "产业趋势中枢"

        # 综合走势判断
        active_bp = sum([analysis["buy_points"]["first"], analysis["buy_points"]["second"], analysis["buy_points"]["third"]])

        if active_bp >= 2 or analysis["confidence_score"] >= 55:
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
# 【模块4】核心信息提取器
# ============================================================
class CoreInfoExtractor:
    """核心信息提取 - 事件主体/类型/影响范围"""

    EVENT_TYPES = {
        "政策发布": ["政策", "规划", "发布", "出台", "印发", "通知", "意见", "方案"],
        "技术突破": ["突破", "进展", "研发", "成功", "首次", "创新", "专利", "研制", "下线", "量产"],
        "产能扩张": ["产能", "量产", "扩产", "投产", "开工", "下线", "基地", "项目"],
        "合作并购": ["合作", "并购", "收购", "投资", "合资", "签约", "战略", "入股"],
        "市场动态": ["增长", "销量", "订单", "新高", "景气", "数据", "营收", "利润"],
    }

    SUBJECT_MAP = {
        "政府机构": ["国务院", "发改委", "工信部", "科技部", "财政部", "央行", "证监会", "国资委", "商务部", "中央"],
        "核心企业": ["华为", "中芯国际", "宁德时代", "比亚迪", "腾讯", "阿里", "百度", "字节跳动", "小米"],
    }

    def extract(self, news: Dict, industry: str) -> Dict[str, Any]:
        title = news["title"]
        snippet = news.get("snippet", "")
        text = title + " " + snippet

        return {
            "event_subject": self._identify_subject(text),
            "event_type": self._identify_event_type(text),
            "impact_scope": self._identify_impact_scope(text),
            "time_sensitivity": self._identify_time_sensitivity(title),
            "industry": industry,
        }

    def _identify_subject(self, text: str) -> str:
        for category, kws in self.SUBJECT_MAP.items():
            for kw in kws:
                if kw in text:
                    return kw
        return "行业相关主体"

    def _identify_event_type(self, text: str) -> str:
        for etype, kws in self.EVENT_TYPES.items():
            for kw in kws:
                if kw in text:
                    return etype
        return "行业动态"

    def _identify_impact_scope(self, text: str) -> str:
        gov_keywords = ["国务院", "全国", "国家", "全球", "国际", "规划", "政策", "发改委", "工信部", "科技部", "中央"]
        if any(kw in text for kw in gov_keywords):
            return "国家级/全球性"
        elif any(kw in text for kw in ["行业", "产业", "领域", "板块", "产业链"]):
            return "行业级"
        return "企业级"

    def _identify_time_sensitivity(self, title: str) -> str:
        high_words = ["今日", "刚刚", "最新", "突发", "紧急", "今天", "今夜"]
        mid_words = ["近日", "近期", "本周", "本月", "今年"]
        if any(w in title for w in high_words):
            return "高"
        elif any(w in title for w in mid_words):
            return "中"
        return "低"


# ============================================================
# 【模块5】知识沉淀器
# ============================================================
class KnowledgeGraphBuilder:
    """构建十五五产业知识图谱"""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self._node_ids = {}
        self._next_id = 1

    def _get_or_create_node(self, name: str, ntype: str, industry: str = None, extra: Dict = None) -> str:
        key = f"{ntype}:{name}"
        if key in self._node_ids:
            return self._node_ids[key]
        nid = f"N{self._next_id:04d}"
        self._next_id += 1
        node = {"id": nid, "name": name, "type": ntype, "industry": industry, "extra": extra or {}}
        self.nodes.append(node)
        self._node_ids[key] = nid
        return nid

    def _add_edge(self, from_id: str, to_id: str, relation: str, weight: float = 1.0):
        self.edges.append({"from": from_id, "to": to_id, "relation": relation, "weight": weight})

    def add_news_item(self, industry: str, news: Dict, core_info: Dict, chan_analysis: Dict, reverse_signal: Dict):
        title = news["title"]
        source = news.get("source", "未知")

        industry_id = self._get_or_create_node(industry, "industry", industry)

        title_hash = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
        event_id = self._get_or_create_node(f"{title[:30]}({title_hash})", "news_event", industry, {
            "title": title,
            "url": news.get("url", ""),
            "source": source,
            "event_type": core_info["event_type"],
            "impact_scope": core_info["impact_scope"],
            "chan_confidence": chan_analysis.get("confidence_score", 30),
            "has_reverse_signal": reverse_signal.get("has_reverse_signal", False)
        })
        self._add_edge(industry_id, event_id, "出现事件")

    def export_graph(self, date_str: str) -> Dict:
        return {
            "metadata": {
                "date": date_str,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "WebSearch增强版",
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges)
            },
            "nodes": self.nodes,
            "edges": self.edges
        }


# ============================================================
# 【主 orchestrator】每日科技资讯系统 WebSearch增强版
# ============================================================
class DailyTechIntelWebSearchSystem:
    """每日科技前沿资讯分析系统 - WebSearch增强版"""

    def __init__(self, session_label: str = "上午"):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.time_str = datetime.now().strftime("%H:%M:%S")
        self.date_time_str = f"{self.date_str} {self.time_str}"
        self.session_label = session_label

        self.searcher = WebSearchSimulator()
        self.reverse_analyzer = ReverseSignalAnalyzer()
        self.core_extractor = CoreInfoExtractor()
        self.chan_analyzer = ChanTheoryAnalyzer()
        self.graph_builder = KnowledgeGraphBuilder()

        self.news_data = {}
        self.analyzed_data = {}

    def search_all_industries(self) -> Dict[str, List[Dict]]:
        """搜索所有行业的最新资讯"""
        print("=" * 80)
        print(f"🚀 每日科技前沿资讯分析系统【WebSearch增强版】启动【{self.session_label}】")
        print("=" * 80)
        print(f"执行时间: {self.date_time_str}")
        print(f"📡 开始搜索十五五规划相关产业资讯...")
        print()

        all_news_by_industry = {}

        for industry, config in FIFTEEN_FIVE_INDUSTRIES.items():
            print(f"🔍 【{industry}】搜索中...")
            industry_news = []

            for query in config["search_queries"][:2]:  # 每个产业最多2个搜索查询
                try:
                    results = self.searcher.search(query, num_results=6)
                    for r in results:
                        # 检查是否匹配产业关键词
                        matched_kws = [kw for kw in config["keywords"] if kw in r["title"]]
                        if matched_kws or any(kw in r["title"] for kw in [industry] + config["keywords"][:3]):
                            r["matched_keywords"] = matched_kws or [industry]
                            r["industry"] = industry
                            industry_news.append(r)
                            print(f"   ✓ {r['title'][:40]}...")
                    time.sleep(1 + random.random())
                except Exception as e:
                    print(f"   ⚠️ 搜索失败: {e}")

            # 去重
            seen_titles = set()
            unique_news = []
            for news in industry_news:
                title_key = news["title"][:40].strip()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_news.append(news)

            all_news_by_industry[industry] = unique_news
            print(f"   ✓ {industry} 合计 {len(unique_news)} 条")
            print()

        total = sum(len(v) for v in all_news_by_industry.values())
        print(f"📊 共获取 {total} 条资讯")
        return all_news_by_industry

    def analyze_all_news(self, news_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """分析所有资讯"""
        print("🔍 正在分析每条资讯...")

        analyzed_data = {}

        for industry, news_list in news_data.items():
            analyzed_list = []
            for news in news_list:
                title = news["title"]
                snippet = news.get("snippet", "")
                url = news.get("url", "")

                core_info = self.core_extractor.extract(news, industry)
                reverse_signal = self.reverse_analyzer.analyze(title, snippet, url)
                chan = self.chan_analyzer.analyze(title, snippet, industry)

                analyzed_item = {
                    "news": news,
                    "core_info": core_info,
                    "reverse_signal": reverse_signal,
                    "chan_analysis": chan
                }
                analyzed_list.append(analyzed_item)

                # 添加到知识图谱
                self.graph_builder.add_news_item(industry, news, core_info, chan, reverse_signal)

            # 排序：正常资讯在前，按缠论置信度降序
            analyzed_list.sort(key=lambda x: (
                1 if x["reverse_signal"]["has_reverse_signal"] else 0,
                -x["chan_analysis"]["confidence_score"]
            ))
            analyzed_data[industry] = analyzed_list

        total = sum(len(v) for v in analyzed_data.values())
        print(f"   ✓ 已分析 {total} 条资讯")
        return analyzed_data

    def generate_report(self, news_data: Dict, analyzed_data: Dict) -> str:
        """生成Markdown分析报告"""
        report = f"""# 📊 {self.date_str}【{self.session_label}】科技前沿资讯分析报告

> 📅 生成时间: {self.date_time_str}
> 🏷️ 版本: WebSearch增强版（十五五规划重点产业跟踪）
> 🔁 执行时间: 每日上午9:30 & 下午14:30

---

## 一、十五五规划相关产业动态

"""

        total_news = sum(len(v) for v in news_data.values())
        normal_count = sum(1 for lst in analyzed_data.values() for item in lst if not item["reverse_signal"]["has_reverse_signal"])
        reverse_count = total_news - normal_count
        high_impact = sum(1 for lst in analyzed_data.values() for item in lst if item["core_info"]["impact_scope"] in ["国家级/全球性", "行业级"])
        high_chan = sum(1 for lst in analyzed_data.values() for item in lst if item["chan_analysis"]["confidence_score"] >= 50)

        report += f"""### 报告摘要

| 指标 | 数值 |
|------|------|
| 📰 爬取资讯总数 | {total_news} |
| ✅ 正常资讯 | {normal_count} |
| ⚠️ 反向信号（疑似标题党） | {reverse_count} |
| 🎯 高影响力资讯 | {high_impact} |
| 📈 缠论高置信信号(≥50%) | {high_chan} |

"""

        # 分产业详细分析
        for industry, analyzed_list in analyzed_data.items():
            if not analyzed_list:
                continue

            report += f"### {industry}（共{len(analyzed_list)}条）\n\n"

            for i, item in enumerate(analyzed_list[:6], 1):
                news = item["news"]
                core = item["core_info"]
                reverse = item["reverse_signal"]
                chan = item["chan_analysis"]

                risk_tag = " 🔴" if reverse["risk_level"] == "高" else " 🟡" if reverse["risk_level"] == "中" else " 🟢"

                report += f"**{i}. {news['title']}**{risk_tag}\n\n"
                report += f"   - **来源**: {news.get('source', '未知')} | **事件**: {core['event_type']} | **影响**: {core['impact_scope']}\n"

                buy_points = []
                if chan["buy_points"]["first"]:
                    buy_points.append("一买")
                if chan["buy_points"]["second"]:
                    buy_points.append("二买")
                if chan["buy_points"]["third"]:
                    buy_points.append("三买")

                if buy_points:
                    bp_str = "、".join(buy_points)
                    report += f"   - **缠论**: 🟢 {bp_str}信号（置信{chan['confidence_score']}%）| 中枢: {chan['pivot_type']}\n"
                else:
                    report += f"   - **缠论**: ⚪ 无明确信号（置信{chan['confidence_score']}%）\n"

                if reverse["has_reverse_signal"]:
                    report += f"   - **⚠️ 风险**: {reverse['risk_level']}级 | {reverse['suggestion']}\n"

                if news.get("url"):
                    report += f"   - **链接**: {news['url']}\n"

                report += "\n"

        # 反向信号预警
        report += "\n---\n\n## 二、反向信号预警\n\n"

        all_reverse = [item for lst in analyzed_data.values() for item in lst if item["reverse_signal"]["has_reverse_signal"]]

        if all_reverse:
            report += f"> ⚠️ 检测到 {len(all_reverse)} 条疑似标题党或资本雇佣枪手发文，请务必反向思考！\n\n"
            all_reverse.sort(key=lambda x: -x["reverse_signal"]["signal_score"])

            for i, item in enumerate(all_reverse[:8], 1):
                news = item["news"]
                reverse = item["reverse_signal"]
                risk_icon = "🔴" if reverse["risk_level"] == "高" else "🟡"
                report += f"**{i}. {risk_icon} {news['title']}**\n"
                report += f"   - 风险评分: {reverse['signal_score']}分 | {reverse['suggestion']}\n\n"
        else:
            report += "✅ 本次未检测到明显的标题党或反向信号资讯。\n\n"

        # 缠论视角分析
        report += "\n---\n\n## 三、缠论视角深度分析\n\n"

        first_buy = sum(1 for lst in analyzed_data.values() for item in lst if item["chan_analysis"]["buy_points"]["first"])
        second_buy = sum(1 for lst in analyzed_data.values() for item in lst if item["chan_analysis"]["buy_points"]["second"])
        third_buy = sum(1 for lst in analyzed_data.values() for item in lst if item["chan_analysis"]["buy_points"]["third"])

        report += f"""### 核心买点信号统计

| 买点类型 | 信号数量 | 说明 |
|----------|----------|------|
| 🟢 第一类买点 | {first_buy} | 政策发布、技术突破带来的驱动型机会 |
| 🟢 第二类买点 | {second_buy} | 回调确认后的安全介入点 |
| 🟢 第三类买点 | {third_buy} | 趋势确立后的加速机会（需警惕情绪过热） |

### 缠论核心原理简述

- **第一类买点**: 由下跌趋势背离产生，通常出现在政策底或业绩底
- **第二类买点**: 不创新低的回调确认点，安全性较高
- **第三类买点**: 离开中枢后的不回抽确认点，属于趋势延续信号
- **关键原则**: "买点买，卖点卖"，严格按照级别操作

"""

        # 产业热度排行
        report += "\n---\n\n## 四、产业热度排行\n\n"

        heat_data = [(ind, len(lst)) for ind, lst in analyzed_data.items() if lst]
        heat_data.sort(key=lambda x: -x[1])

        for rank, (ind, count) in enumerate(heat_data[:8], 1):
            bar = "█" * min(count, 15)
            report += f"{rank}. {ind:<10} {bar} {count}条\n"

        report += f"""

---
*本报告由每日科技资讯分析系统 WebSearch增强版 自动生成*
*⚠️ 报告内容仅供参考，不构成投资建议。股市有风险，投资需谨慎。*
"""

        return report

    def save_results(self, report: str, analyzed_data: Dict):
        """保存结果"""
        # Markdown报告
        report_file = REPORT_DIR / f"{self.date_str}_{self.session_label}_tech_intel_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📁 分析报告: {report_file}")

        # JSON数据
        data_file = REPORT_DIR / f"{self.date_str}_{self.session_label}_tech_intel_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": self.date_str,
                "datetime": self.date_time_str,
                "session": self.session_label,
                "version": "WebSearch增强版",
                "news_data": self.news_data,
                "analyzed_data": self.analyzed_data
            }, f, ensure_ascii=False, indent=2)
        print(f"📁 分析数据: {data_file}")

        # 知识图谱
        graph_data = self.graph_builder.export_graph(self.date_str)
        graph_file = PROJECT_DIR / "knowledge_graph" / f"{self.date_str}_{self.session_label}_knowledge_graph.json"
        graph_file.parent.mkdir(exist_ok=True)
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        print(f"📁 知识图谱: {graph_file}")

        return report_file, data_file

    def run(self):
        """执行完整流程"""
        # Step 1: 搜索
        self.news_data = self.search_all_industries()

        if sum(len(v) for v in self.news_data.values()) == 0:
            print("\n⚠️ 未获取到任何资讯，将生成空报告。")
            self.analyzed_data = {}
        else:
            # Step 2: 分析
            print("\n🔍 开始分析资讯...")
            self.analyzed_data = self.analyze_all_news(self.news_data)

        # Step 3: 生成报告
        print("\n📝 生成分析报告...")
        report = self.generate_report(self.news_data, self.analyzed_data)

        # Step 4: 保存
        print("\n💾 保存结果...")
        self.save_results(report, self.analyzed_data)

        print("\n" + "=" * 80)
        print("✅ 分析完成！")
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

    system = DailyTechIntelWebSearchSystem(session_label=session)
    system.run()


if __name__ == '__main__':
    main()