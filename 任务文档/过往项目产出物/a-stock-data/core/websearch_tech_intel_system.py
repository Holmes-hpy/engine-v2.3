#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技前沿资讯分析系统 - WebSearch增强版
使用WebSearch工具获取真实新闻
关注十五五规划相关产业，结合缠论进行知识沉淀，识别反向信号
"""

import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# 报告保存目录
REPORT_DIR = PROJECT_DIR / "daily_tech_intel"
REPORT_DIR.mkdir(exist_ok=True)
KNOWLEDGE_BASE_DIR = PROJECT_DIR / "knowledge"
KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)

# 十五五规划重点关注领域及搜索关键词
FIFTEEN_FIVE_INDUSTRIES = {
    "人工智能": [
        "人工智能 最新政策 2026 site:gov.cn",
        "AI 大模型 技术突破 2026",
        "人形机器人 产业政策 2026"
    ],
    "半导体": [
        "半导体 国产替代 芯片进展 2026",
        "中芯国际 先进制程 突破 2026",
        "光刻机 国产化 突破 2026"
    ],
    "新能源": [
        "十五五规划 新能源 光伏 储能 2026",
        "新能源汽车 比亚迪 宁德时代 2026",
        "光伏风电 储能产业 政策 2026"
    ],
    "数字经济": [
        "数字经济 数据中心 算力 2026 政策",
        "东数西算 云计算 大数据 2026",
        "工业互联网 数字化转型 2026"
    ],
    "十五五规划": [
        "十五五规划 高质量发展 政策 2026",
        "战略性新兴产业 政策 支持 2026",
        "现代化产业体系 规划 2026"
    ]
}

# 反向信号关键词
REVERSE_SIGNAL_KEYWORDS = {
    "极端词汇": ["暴涨", "暴跌", "必涨", "必跌", "翻倍", "妖股", "疯涨", "崩盘", "血洗"],
    "内幕词汇": ["内幕", "独家", "重磅", "惊天", "震惊", "秘密", "内部消息", "绝密", "泄密", "爆料"],
    "主体词汇": ["主力", "游资", "机构", "大佬", "牛散", "庄家", "操盘手", "国家队", "外资"],
    "时间词汇": ["即将", "马上", "立刻", "今日", "最新", "突发", "紧急", "刚刚"],
    "引导词汇": ["手把手", "带你", "教你", "跟着", "躺赢", "赚钱", "发财", "暴富"],
    "夸张词汇": ["震惊", "炸了", "疯了", "慌了", "哭了", "笑了", "懵了", "爽了", "赚翻了"]
}


class WebSearchNewsCollector:
    """使用WebSearch工具收集新闻"""

    def __init__(self):
        self.news_data = []

    def collect_news(self, search_queries: List[str]) -> List[Dict[str, Any]]:
        """
        收集新闻（实际使用时由外部调用WebSearch工具）
        这里生成模拟数据，实际执行时会用WebSearch结果替换
        """
        print(f"🔍 开始收集新闻，共 {len(search_queries)} 个搜索词...")

        all_news = []

        # 模拟数据（实际使用时会被WebSearch结果替换）
        mock_news = {
            "人工智能 最新政策 2026 site:gov.cn": [
                {
                    "title": "科技部发布人工智能发展规划，明确十五五期间重点任务",
                    "url": "https://www.most.gov.cn/kjzc/",
                    "source": "科技部官网",
                    "snippet": "规划提出加快通用人工智能、具身智能等领域核心技术攻关"
                },
                {
                    "title": "工信部：人工智能算力基础设施建设提速，支撑产业数字化转型",
                    "url": "https://www.miit.gov.cn/",
                    "source": "工信部官网",
                    "snippet": "加快智算中心布局，推动AI与传统产业深度融合"
                }
            ],
            "半导体 国产替代 芯片进展 2026": [
                {
                    "title": "2026开年爆发！功率半导体国产替代进入决胜期",
                    "url": "http://m.toutiao.com/group/7598520672042517044/",
                    "source": "今日头条",
                    "snippet": "国产第三代功率半导体(SiC/GaN)迎来密集技术突破"
                },
                {
                    "title": "中国半导体设备国产化率加速提升，2026年预计达45%",
                    "url": "http://m.toutiao.com/group/7606157492179190313/",
                    "source": "今日头条",
                    "snippet": "AI算力需求+十五五规划+大基金三期落地推动国产替代提速"
                }
            ],
            "十五五规划 新能源 光伏 储能 2026": [
                {
                    "title": "《政府工作报告》指明能源方向：2026年发力氢能、新型储能和绿电应用",
                    "url": "http://m.toutiao.com/group/7613978622122066483/",
                    "source": "今日头条",
                    "snippet": "风电、光伏、储能及电动汽车赛道有望在十五五期间实现大幅增长"
                },
                {
                    "title": "2026光伏风电、储能项目全流程开发规范发布",
                    "url": "http://m.toutiao.com/group/7648849525800534562/",
                    "source": "今日头条",
                    "snippet": "十五五规划开局之年，新能源行业步入高质量发展新阶段"
                }
            ]
        }

        for query in search_queries:
            if query in mock_news:
                all_news.extend(mock_news[query])
            else:
                # 通用处理
                all_news.append({
                    "title": f"{query}相关资讯",
                    "url": "",
                    "source": "WebSearch",
                    "snippet": f"关于{query}的最新资讯"
                })

        # 去重
        seen = set()
        unique_news = []
        for news in all_news:
            title_key = news["title"][:50] if len(news["title"]) > 50 else news["title"]
            if title_key not in seen:
                seen.add(title_key)
                unique_news.append(news)

        return unique_news


class TechIntelAnalyzer:
    """资讯分析器"""

    def __init__(self):
        self.news_data = []
        self.analyzed_data = []

    def analyze_reverse_signal(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """分析反向信号"""
        title = news.get("title", "")
        snippet = news.get("snippet", "")
        text = title + snippet

        signal_analysis = {
            "has_reverse_signal": False,
            "signal_score": 0,
            "signal_categories": [],
            "signal_words": [],
            "risk_level": "低",
            "analysis": ""
        }

        # 检查关键词
        for category, keywords in REVERSE_SIGNAL_KEYWORDS.items():
            found = [kw for kw in keywords if kw in text]
            if found:
                signal_analysis["signal_categories"].append(category)
                signal_analysis["signal_words"].extend(found)
                signal_analysis["signal_score"] += len(found) * 2

        # 判定风险等级
        if signal_analysis["signal_score"] >= 8:
            signal_analysis["has_reverse_signal"] = True
            signal_analysis["risk_level"] = "高"
            signal_analysis["analysis"] = "高度疑似标题党，建议反向思考"
        elif signal_analysis["signal_score"] >= 4:
            signal_analysis["has_reverse_signal"] = True
            signal_analysis["risk_level"] = "中"
            signal_analysis["analysis"] = "存在一定风险，需谨慎判断"

        return signal_analysis

    def analyze_chan_theory(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """缠论视角分析"""
        title = news.get("title", "")
        snippet = news.get("snippet", "")
        text = title + snippet

        chan_analysis = {
            "buy_points": {"first": False, "second": False, "third": False},
            "confidence_score": 30,
            "trend_judgment": "中性",
            "operation_suggestion": "继续观察"
        }

        # 第一类买点
        first_triggers = ["政策", "规划", "突破", "发布", "首次", "创新", "重大"]
        if any(trigger in text for trigger in first_triggers):
            chan_analysis["buy_points"]["first"] = True
            chan_analysis["confidence_score"] += 20

        # 第二类买点
        second_triggers = ["确认", "企稳", "验证", "回调"]
        if any(trigger in text for trigger in second_triggers):
            chan_analysis["buy_points"]["second"] = True
            chan_analysis["confidence_score"] += 10

        # 第三类买点
        third_triggers = ["新高", "加速", "超预期", "黄金期", "快车道", "大幅"]
        if any(trigger in text for trigger in third_triggers):
            chan_analysis["buy_points"]["third"] = True
            chan_analysis["confidence_score"] += 15

        # 走势判断
        buy_count = sum(chan_analysis["buy_points"].values())
        if buy_count >= 2:
            chan_analysis["trend_judgment"] = "偏多"
            chan_analysis["operation_suggestion"] = "可关注相关板块"
        elif buy_count == 1:
            chan_analysis["trend_judgment"] = "中性偏多"
            chan_analysis["operation_suggestion"] = "继续观察"

        return chan_analysis

    def analyze_news(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """综合分析"""
        reverse_signal = self.analyze_reverse_signal(news)
        chan_analysis = self.analyze_chan_theory(news)

        return {
            "news": news,
            "reverse_signal": reverse_signal,
            "chan_analysis": chan_analysis,
            "core_info": {
                "event_type": self._identify_event_type(news),
                "impact_scope": self._identify_impact_scope(news)
            }
        }

    def _identify_event_type(self, news: Dict[str, Any]) -> str:
        """识别事件类型"""
        text = news.get("title", "") + news.get("snippet", "")

        event_types = {
            "政策发布": ["政策", "规划", "发布", "出台", "通知"],
            "技术突破": ["突破", "研发", "首次", "创新", "技术"],
            "市场动态": ["增长", "销量", "新高", "产业"],
            "产业分析": ["行业", "分析", "展望", "趋势"]
        }

        for event_type, keywords in event_types.items():
            if any(kw in text for kw in keywords):
                return event_type
        return "行业动态"

    def _identify_impact_scope(self, news: Dict[str, Any]) -> str:
        """识别影响范围"""
        text = news.get("title", "") + news.get("snippet", "")

        if any(kw in text for kw in ["全国", "国家", "全球", "规划", "政府"]):
            return "国家级/全球性"
        elif any(kw in text for kw in ["行业", "产业", "板块", "领域"]):
            return "行业级"
        return "企业级"


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.date_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_report(self, analyzed_data: List[Dict[str, Any]], industry: str) -> str:
        """生成行业资讯报告"""

        report = f"# 📊 {self.date_str} 科技前沿资讯分析报告\n\n"
        report += f"**执行时间**: {self.date_time_str}\n\n"
        report += "---\n\n"

        # 报告摘要
        total = len(analyzed_data)
        normal = sum(1 for item in analyzed_data if not item["reverse_signal"]["has_reverse_signal"])
        reverse = total - normal
        high_impact = sum(1 for item in analyzed_data
                         if item["core_info"]["impact_scope"] in ["国家级/全球性", "行业级"])
        high_chan = sum(1 for item in analyzed_data
                        if item["chan_analysis"]["confidence_score"] >= 50)

        report += "## 📌 报告摘要\n\n"
        report += f"| 指标 | 数值 |\n"
        report += f"|------|------|\n"
        report += f"| 资讯总数 | {total} |\n"
        report += f"| 正常资讯 | {normal} |\n"
        report += f"| 反向信号 | {reverse} |\n"
        report += f"| 高影响力 | {high_impact} |\n"
        report += f"| 缠论高置信 | {high_chan} |\n\n"

        # 行业动态
        report += f"## 📋 {industry}产业动态\n\n"

        for i, item in enumerate(analyzed_data[:5], 1):
            news = item["news"]
            reverse = item["reverse_signal"]
            chan = item["chan_analysis"]
            core = item["core_info"]

            report += f"### {i}. {news['title']}\n\n"
            report += f"- **来源**: {news.get('source', '未知')} | "
            report += f"**类型**: {core['event_type']} | "
            report += f"**范围**: {core['impact_scope']}\n"

            # 缠论买点
            buy_points = []
            if chan["buy_points"]["first"]:
                buy_points.append("一买")
            if chan["buy_points"]["second"]:
                buy_points.append("二买")
            if chan["buy_points"]["third"]:
                buy_points.append("三买")

            if buy_points:
                report += f"- **缠论**: 🟢 {','.join(buy_points)} | "
            else:
                report += f"- **缠论**: ⚪ 无明确信号 | "
            report += f"{chan['trend_judgment']}\n"

            # 风险提示
            if reverse["has_reverse_signal"]:
                report += f"- **风险**: 🔴 {reverse['risk_level']} | {reverse['analysis']}\n"
            else:
                report += f"- **风险**: 🟢 正常\n"

            report += f"- **链接**: {news.get('url', 'N/A')}\n\n"

        # 反向信号预警
        reverse_news = [item for item in analyzed_data if item["reverse_signal"]["has_reverse_signal"]]
        if reverse_news:
            report += "## ⚠️ 反向信号预警\n\n"
            for i, item in enumerate(reverse_news[:3], 1):
                news = item["news"]
                reverse = item["reverse_signal"]
                report += f"**{i}. {news['title']}**\n"
                report += f"- 风险等级: 🔴 {reverse['risk_level']}\n"
                if reverse["signal_words"]:
                    report += f"- 风险词: {', '.join(reverse['signal_words'][:5])}\n"
                report += f"- 建议: {reverse['analysis']}\n\n"

        # 缠论分析
        report += "## 📈 缠论视角分析\n\n"
        first_count = sum(1 for item in analyzed_data if item["chan_analysis"]["buy_points"]["first"])
        second_count = sum(1 for item in analyzed_data if item["chan_analysis"]["buy_points"]["second"])
        third_count = sum(1 for item in analyzed_data if item["chan_analysis"]["buy_points"]["third"])

        report += f"| 买点类型 | 信号数量 |\n"
        report += f"|----------|----------|\n"
        report += f"| 第一类买点 | {first_count} |\n"
        report += f"| 第二类买点 | {second_count} |\n"
        report += f"| 第三类买点 | {third_count} |\n\n"

        # 策略建议
        report += "### 策略建议\n\n"
        report += "- **仓位**: 建议50%-70%\n"
        report += "- **方向**: 重点关注十五五重点赛道\n"
        report += "- **时机**: 等待回调确认，避免追高\n"
        report += "- **止损**: 单只建议不超5%-8%\n\n"

        # 知识沉淀
        report += "## 🧠 知识沉淀\n\n"
        report += "### 今日要点\n\n"
        report += "1. 十五五规划重点支持战略性新兴产业发展\n"
        report += "2. 人工智能、半导体、新能源是长期黄金赛道\n"
        report += "3. 缠论买点需结合政策面、基本面综合判断\n\n"

        report += "### 后续关注\n\n"
        report += "- 持续跟踪政策落地进展\n"
        report += "- 关注行业数据验证\n"
        report += "- 警惕市场情绪过热\n\n"

        return report

    def save_report(self, report: str, industry: str):
        """保存报告"""
        # 主报告
        report_file = REPORT_DIR / f"{self.date_str}_tech_intel_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📁 报告已保存: {report_file}")

        # 知识沉淀
        knowledge_file = KNOWLEDGE_BASE_DIR / "tech_intel_history.md"
        entry = f"\n\n---\n\n## {self.date_str} - {industry}\n{report[:600]}...\n"

        if knowledge_file.exists():
            with open(knowledge_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                f.write("# 科技资讯知识沉淀库\n" + entry)
        print(f"📚 知识已沉淀: {knowledge_file}")


def main(industry: str, search_results: List[Dict[str, Any]]):
    """
    主函数 - 由自动化任务调用

    Args:
        industry: 行业名称
        search_results: WebSearch返回的结果列表
    """
    print("=" * 80)
    print(f"🚀 科技前沿资讯分析系统 - {industry}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 分析新闻
    analyzer = TechIntelAnalyzer()
    analyzed_data = [analyzer.analyze_news(news) for news in search_results]

    # 生成报告
    generator = ReportGenerator()
    report = generator.generate_report(analyzed_data, industry)

    # 保存
    generator.save_report(report, industry)

    print("\n✅ 分析完成！")
    return report


if __name__ == '__main__':
    # 测试用
    collector = WebSearchNewsCollector()
    test_queries = list(FIFTEEN_FIVE_INDUSTRIES.values())[0]
    news = collector.collect_news(test_queries)
    main("人工智能", news)
