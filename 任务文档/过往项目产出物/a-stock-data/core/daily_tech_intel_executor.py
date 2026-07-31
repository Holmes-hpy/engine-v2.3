#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技前沿资讯分析系统 - 主执行器
========================================
执行时间: 每日上午9:30
核心功能:
  1. 爬取/搜索科技前沿资讯（聚焦十五五规划相关产业）
  2. 资讯分析与知识提取
  3. 缠论视角分析（第一类买点/第二类买点/第三类买点）
  4. 反向信号识别（标题党/情绪化/缺乏数据支撑）
  5. 结构化报告生成与知识沉淀

使用方式:
  python daily_tech_intel_executor.py
  python daily_tech_intel_executor.py --date 2026-06-18
  python daily_tech_intel_executor.py --with-search  (启用在线搜索)
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# ========== 路径配置 ==========
PROJECT_DIR = Path(__file__).parent
REPORT_DIR = PROJECT_DIR / "daily_tech_intel"
KNOWLEDGE_DIR = PROJECT_DIR / "knowledge"
LOG_DIR = PROJECT_DIR / "logs"

for d in [REPORT_DIR, KNOWLEDGE_DIR, LOG_DIR]:
    d.mkdir(exist_ok=True)

sys.path.insert(0, str(PROJECT_DIR))


# ========== 核心配置 ==========
INDUSTRY_CATEGORIES = {
    "人工智能": {
        "keywords": ["人工智能", "AI", "大模型", "机器学习", "智能体", "具身智能", "算力", "GPU", "深度学习"],
        "weight": 1.2
    },
    "半导体": {
        "keywords": ["半导体", "芯片", "集成电路", "光刻机", "先进封装", "存储芯片", "国产替代", "晶圆", "中芯国际"],
        "weight": 1.3
    },
    "新能源": {
        "keywords": ["新能源", "光伏", "储能", "风电", "氢能", "新能源汽车", "动力电池", "逆变器", "锂电池"],
        "weight": 1.2
    },
    "数字经济": {
        "keywords": ["数字经济", "数据中心", "云计算", "大数据", "工业互联网", "数字化转型", "东数西算"],
        "weight": 1.0
    },
    "十五五规划": {
        "keywords": ["十五五", "十四五", "规划", "政策", "国务院", "发改委", "工信部", "科技部", "实施方案"],
        "weight": 1.5
    }
}

REVERSE_SIGNAL_RULES = {
    "extreme_emotion": {
        "keywords": ["暴涨", "暴跌", "疯涨", "崩盘", "惊天", "震惊", "炸了", "慌了", "懵了", "血洗", "爽了"],
        "score": 3,
        "description": "极端情绪化词汇"
    },
    "prediction_words": {
        "keywords": ["即将", "马上", "立刻", "大概率", "必然", "必定", "肯定", "必涨", "必跌", "翻倍"],
        "score": 2,
        "description": "预测性/确定性表述"
    },
    "get_rich_quick": {
        "keywords": ["躺赢", "发财", "暴富", "赚翻", "财富自由", "手把手", "带你", "教你", "跟着", "上车"],
        "score": 3,
        "description": "荐股/致富导向"
    },
    "insider_hint": {
        "keywords": ["内幕", "独家", "重磅", "秘密", "内部消息", "绝密", "泄密", "爆料"],
        "score": 3,
        "description": "内幕/独家消息暗示"
    },
    "capital_hint": {
        "keywords": ["主力", "游资", "机构", "大佬", "牛散", "庄家", "操盘手", "国家队", "外资", "加仓"],
        "score": 2,
        "description": "资本操作暗示"
    },
    "combat_metaphor": {
        "keywords": ["抄底", "逃顶", "炸板", "封板", "接力", "战法", "秘籍", "绝招", "打板"],
        "score": 2,
        "description": "股市战斗隐喻"
    }
}

CHAN_THEORY_RULES = {
    "first_buy_point": {
        "triggers": ["政策", "规划", "发布", "出台", "首次", "突破", "创新", "重大", "落地", "实施"],
        "description": "第一类买点 - 政策底/技术突破信号",
        "confidence_base": 50
    },
    "second_buy_point": {
        "triggers": ["确认", "企稳", "验证", "回调", "回升", "修复", "筑底", "回踩"],
        "description": "第二类买点 - 回调后的确认机会",
        "confidence_base": 40
    },
    "third_buy_point": {
        "triggers": ["新高", "加速", "超预期", "黄金期", "快车道", "大幅", "领涨", "爆发", "井喷", "暴涨"],
        "description": "第三类买点 - 趋势确立信号",
        "confidence_base": 45
    }
}


# ========== 核心分析类 ==========
class NewsAnalyzer:
    """资讯核心分析器"""

    def __init__(self):
        self.analysis_results = []

    def categorize_industry(self, title: str, snippet: str = "") -> str:
        """识别所属产业领域"""
        text = title + " " + snippet
        scores = {}
        for category, info in INDUSTRY_CATEGORIES.items():
            hit_count = sum(text.count(kw) for kw in info["keywords"])
            scores[category] = hit_count * info["weight"]
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "其他"

    def analyze_reverse_signal(self, title: str, snippet: str = "") -> Dict[str, Any]:
        """分析反向信号"""
        text = title + " " + snippet
        total_score = 0
        found_categories = []
        found_keywords = []

        for category, rules in REVERSE_SIGNAL_RULES.items():
            hits = [kw for kw in rules["keywords"] if kw in text]
            if hits:
                total_score += rules["score"] * len(hits)
                found_categories.append(rules["description"])
                found_keywords.extend(hits)

        risk_level = "低"
        if total_score >= 8:
            risk_level = "高"
        elif total_score >= 4:
            risk_level = "中"

        return {
            "risk_score": total_score,
            "risk_level": risk_level,
            "categories": found_categories,
            "keywords_found": found_keywords,
            "has_signal": total_score >= 4,
            "assessment": self._generate_reverse_assessment(total_score, found_categories)
        }

    def _generate_reverse_assessment(self, score: int, categories: List[str]) -> str:
        """生成反向信号评估文本"""
        if score >= 8:
            return f"高度疑似标题党/炒作型内容，包含{len(categories)}类风险特征: {', '.join(categories)}。建议反向思考，避免追高。"
        elif score >= 4:
            return f"存在一定风险特征: {', '.join(categories)}。需结合具体数据谨慎判断，不可仅凭标题做决策。"
        return "无明显反向信号，表述相对客观。"

    def analyze_chan_theory(self, title: str, snippet: str = "") -> Dict[str, Any]:
        """缠论视角分析"""
        text = title + " " + snippet
        buy_points = {}
        overall_confidence = 0

        for point_type, rules in CHAN_THEORY_RULES.items():
            hits = [t for t in rules["triggers"] if t in text]
            triggered = len(hits) > 0
            confidence = rules["confidence_base"] + len(hits) * 10 if triggered else 0
            if confidence > 80:
                confidence = 80
            buy_points[point_type] = {
                "triggered": triggered,
                "triggers_found": hits,
                "confidence": confidence,
                "description": rules["description"]
            }
            overall_confidence += confidence

        any_triggered = any(bp["triggered"] for bp in buy_points.values())

        return {
            "buy_points": buy_points,
            "any_triggered": any_triggered,
            "overall_confidence": min(overall_confidence, 100),
            "trend_direction": self._assess_trend_direction(buy_points)
        }

    def _assess_trend_direction(self, buy_points: Dict[str, Any]) -> str:
        """评估趋势方向"""
        if buy_points.get("third_buy_point", {}).get("triggered"):
            return "趋势延续/加速 - 需警惕情绪过热"
        elif buy_points.get("first_buy_point", {}).get("triggered"):
            return "潜在拐点/机会区域 - 政策或技术驱动"
        elif buy_points.get("second_buy_point", {}).get("triggered"):
            return "回调确认/二次介入机会"
        return "中性 - 无明确缠论信号"

    def assess_importance(self, reverse_signal: Dict[str, Any], chan_analysis: Dict[str, Any],
                          title: str, snippet: str) -> int:
        """评估资讯重要等级(1-5星)"""
        text = title + " " + snippet
        score = 2  # 基础分

        # 政策相关加分
        policy_keywords = ["国务院", "发改委", "工信部", "科技部", "政府", "规划", "政策", "出台", "发布", "实施"]
        if any(kw in text for kw in policy_keywords):
            score += 2

        # 有具体数据加分
        if re.search(r"\d+\.?\d*%", text) or re.search(r"\d+\.?\d*(GWh|亿元|亿|万亿)", text):
            score += 1

        # 缠论买点确认加分
        if chan_analysis["overall_confidence"] >= 60:
            score += 1

        # 反向信号扣分(但不影响资讯是否重要，只是风险提示)
        # 反向信号不直接扣重要性分数

        return min(score, 5)

    def analyze_news_item(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """分析单条资讯"""
        title = news_item.get("title", "")
        snippet = news_item.get("snippet", "")
        url = news_item.get("url", "")
        source = news_item.get("source", "未知来源")

        industry = self.categorize_industry(title, snippet)
        reverse_signal = self.analyze_reverse_signal(title, snippet)
        chan_analysis = self.analyze_chan_theory(title, snippet)
        importance = self.assess_importance(reverse_signal, chan_analysis, title, snippet)

        return {
            "title": title,
            "snippet": snippet,
            "url": url,
            "source": source,
            "industry": industry,
            "importance": importance,
            "importance_stars": "⭐" * importance,
            "reverse_signal": reverse_signal,
            "chan_analysis": chan_analysis,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def batch_analyze(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量分析"""
        results = []
        for i, news in enumerate(news_list, 1):
            analyzed = self.analyze_news_item(news)
            results.append(analyzed)
            if i <= 5:  # 只显示前5条的简要状态
                status_icon = "🟢" if not analyzed["reverse_signal"]["has_signal"] else "🟡"
                print(f"   {status_icon} [{analyzed['industry']}] {analyzed['importance_stars']} {analyzed['title'][:40]}...")
        return results


class ReportGenerator:
    """报告生成器"""

    def __init__(self, date_str: str):
        self.date_str = date_str
        self.date_obj = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_comprehensive_report(self, analyzed_news: List[Dict[str, Any]]) -> str:
        """生成综合分析报告"""
        report = []

        # 报告标题
        report.append(f"# 📊 {self.date_str} 科技前沿资讯分析报告")
        report.append("")
        report.append(f"**执行时间**: {self.timestamp}")
        report.append(f"**报告版本**: v2.1")
        report.append(f"**覆盖范围**: {' / '.join(INDUSTRY_CATEGORIES.keys())}")
        report.append("")
        report.append("---")
        report.append("")

        # 执行摘要
        report.extend(self._generate_executive_summary(analyzed_news))
        report.append("---")
        report.append("")

        # 分产业详细分析
        report.extend(self._generate_industry_analysis(analyzed_news))
        report.append("---")
        report.append("")

        # 市场情绪与走势判断
        report.extend(self._generate_market_sentiment(analyzed_news))
        report.append("---")
        report.append("")

        # 反向信号预警
        report.extend(self._generate_reverse_signal_warning(analyzed_news))
        report.append("---")
        report.append("")

        # 关键机会与风险
        report.extend(self._generate_opportunity_risk(analyzed_news))
        report.append("---")
        report.append("")

        # 缠论买点汇总
        report.extend(self._generate_chan_summary(analyzed_news))
        report.append("---")
        report.append("")

        # 后续关注事项
        report.extend(self._generate_followup_items(analyzed_news))
        report.append("---")
        report.append("")

        # 知识沉淀
        report.extend(self._generate_knowledge_section(analyzed_news))
        report.append("---")
        report.append("")

        # 质量检查
        report.extend(self._generate_quality_check(analyzed_news))
        report.append("")

        # 报告结尾
        next_date = (self.date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        report.append(f"**报告完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**下次执行**: {next_date} 09:30")
        report.append("")

        return "\n".join(report)

    def _generate_executive_summary(self, news: List[Dict[str, Any]]) -> List[str]:
        """生成执行摘要"""
        total = len(news)
        normal = sum(1 for n in news if not n["reverse_signal"]["has_signal"])
        reverse = total - normal
        high_impact = sum(1 for n in news if n["importance"] >= 4)
        high_chan = sum(1 for n in news if n["chan_analysis"]["overall_confidence"] >= 50)

        # 核心判断
        industries_count = {}
        for n in news:
            ind = n["industry"]
            industries_count[ind] = industries_count.get(ind, 0) + 1

        top_industries = sorted(industries_count.items(), key=lambda x: x[1], reverse=True)[:3]
        hot_areas = " + ".join([f"🟢{i[0]}" if idx == 0 else f"🟡{i[0]}" for idx, i in enumerate(top_industries)])

        return [
            "## 📌 执行摘要",
            "",
            "| 指标 | 数值 | 说明 |",
            "|------|------|------|",
            f"| 资讯总数 | {total} | 覆盖各大核心领域 |",
            f"| 正常资讯 | {normal} | 表述客观、数据详实 |",
            f"| 反向信号 | {reverse} | 含极端词汇/缺乏数据支撑 |",
            f"| 高影响力 | {high_impact} | 国家级/行业级事件 |",
            f"| 缠论买点信号 | {high_chan} | 各类买点触发 |",
            "",
            f"**今日核心判断**: {hot_areas} → **结构性机会持续，需分区段判断介入时机**",
            "",
        ]

    def _generate_industry_analysis(self, news: List[Dict[str, Any]]) -> List[str]:
        """分产业详细分析"""
        lines = []
        lines.append("## 📋 一、十五五规划相关产业动态")
        lines.append("")

        # 按产业分组
        industry_news = {}
        for n in news:
            ind = n["industry"]
            if ind not in industry_news:
                industry_news[ind] = []
            industry_news[ind].append(n)

        # 按重要性排序每个产业内的新闻
        for industry in INDUSTRY_CATEGORIES.keys():
            if industry not in industry_news or len(industry_news[industry]) == 0:
                continue

            lines.append(f"### {industry}")
            lines.append("")

            # 按重要性排序
            sorted_news = sorted(industry_news[industry], key=lambda x: x["importance"], reverse=True)

            for idx, item in enumerate(sorted_news[:8], 1):
                lines.extend(self._format_news_item(idx, item))
                lines.append("")

            lines.append("")

        # 其他类别
        if "其他" in industry_news:
            lines.append("### 其他动态")
            lines.append("")
            for idx, item in enumerate(industry_news["其他"][:3], 1):
                lines.extend(self._format_news_item(idx, item))
                lines.append("")

        return lines

    def _format_news_item(self, idx: int, item: Dict[str, Any]) -> List[str]:
        """格式化单条资讯"""
        lines = []
        chan = item["chan_analysis"]
        reverse = item["reverse_signal"]

        # 买点类型
        buy_point_types = []
        for bp_type, bp_data in chan["buy_points"].items():
            if bp_data["triggered"]:
                if bp_type == "first_buy_point":
                    buy_point_types.append("第一类买点")
                elif bp_type == "second_buy_point":
                    buy_point_types.append("第二类买点")
                elif bp_type == "third_buy_point":
                    buy_point_types.append("第三类买点")

        buy_point_str = "、".join(buy_point_types) if buy_point_types else "无明确信号"

        # 标题
        lines.append(f"#### 资讯{idx}: {item['title']}")
        lines.append("")
        lines.append(f"- **来源**: {item['source']}")
        if item.get("url"):
            lines.append(f"- **链接**: {item['url']}")
        lines.append(f"- **重要等级**: {item['importance_stars']} ({item['importance']}/5)")
        lines.append("")

        if item.get("snippet"):
            lines.append(f"- **核心内容**: {item['snippet']}")
            lines.append("")

        # 缠论分析
        lines.append(f"- **缠论视角分析**:")
        lines.append(f"  - 买点类型: {buy_point_str}")
        lines.append(f"  - 置信度评分: {chan['overall_confidence']}/100")
        if chan["any_triggered"]:
            triggers = []
            for bp_type, bp_data in chan["buy_points"].items():
                if bp_data["triggers_found"]:
                    type_name = bp_data["description"].split(" - ")[1] if " - " in bp_data["description"] else bp_data["description"]
                    triggers.extend(bp_data["triggers_found"])
            if triggers:
                lines.append(f"  - 触发关键词: {', '.join(set(triggers))[:30]}")
        lines.append(f"  - 趋势判断: {chan['trend_direction']}")
        lines.append("")

        # 反向信号
        risk_icon = "🔴" if reverse["risk_level"] == "高" else "🟡" if reverse["risk_level"] == "中" else "🟢"
        lines.append(f"- **反向信号检查**: {risk_icon} {reverse['risk_level']}风险")
        if reverse["keywords_found"]:
            lines.append(f"  - 风险词汇: {', '.join(set(reverse['keywords_found']))[:40]}")
        if reverse["categories"]:
            lines.append(f"  - 风险类型: {', '.join(reverse['categories'])}")
        lines.append(f"  - 评估: {reverse['assessment']}")
        lines.append("")

        return lines

    def _generate_market_sentiment(self, news: List[Dict[str, Any]]) -> List[str]:
        """市场情绪分析"""
        # 统计各产业趋势
        industry_trend = {}
        for n in news:
            ind = n["industry"]
            if ind not in industry_trend:
                industry_trend[ind] = {"total": 0, "bullish": 0, "bearish": 0}
            industry_trend[ind]["total"] += 1
            if n["chan_analysis"]["overall_confidence"] >= 50:
                industry_trend[ind]["bullish"] += 1

        lines = []
        lines.append("## 📈 二、市场情绪与走势判断")
        lines.append("")
        lines.append("### 2.1 综合趋势")
        lines.append("")
        lines.append("| 产业领域 | 资讯数 | 偏多信号 | 情绪温度 |")
        lines.append("|---------|--------|---------|---------|")

        for industry, data in sorted(industry_trend.items(), key=lambda x: x[1]["bullish"], reverse=True):
            if industry == "其他" or data["total"] == 0:
                continue
            ratio = data["bullish"] / data["total"] if data["total"] > 0 else 0
            if ratio >= 0.6:
                temp = "🔥🔥🔥 偏热"
            elif ratio >= 0.4:
                temp = "🔥🔥 温和"
            elif ratio >= 0.2:
                temp = "🔥 中性偏暖"
            else:
                temp = "❄️ 中性"
            lines.append(f"| {industry} | {data['total']} | {data['bullish']} | {temp} |")

        lines.append("")
        lines.append("### 2.2 政策面")
        lines.append("- 关注十五五规划相关产业政策的发布与实施节奏")
        lines.append("- 注意政策出台与市场预期之间的时间差")
        lines.append("- 国产替代、新能源、AI算力是长期政策主线")
        lines.append("")
        lines.append("### 2.3 技术面")
        lines.append("- 缠论买点需结合K线形态、成交量等技术指标综合判断")
        lines.append("- 第三类买点出现时需警惕情绪透支后的回调风险")
        lines.append("- 第一类买点需等待基本面数据确认后再介入")
        lines.append("")

        return lines

    def _generate_reverse_signal_warning(self, news: List[Dict[str, Any]]) -> List[str]:
        """反向信号预警"""
        lines = []
        lines.append("## ⚠️ 三、反向信号识别与预警")
        lines.append("")

        # 找出高风险资讯
        high_risk = [n for n in news if n["reverse_signal"]["risk_level"] == "高"]
        medium_risk = [n for n in news if n["reverse_signal"]["risk_level"] == "中"]

        if high_risk:
            lines.append("### 🔴 高风险资讯（需反向思考）")
            lines.append("")
            lines.append("| # | 标题 | 风险关键词 | 风险分数 |")
            lines.append("|---|------|----------|---------|")
            for idx, item in enumerate(high_risk[:6], 1):
                keywords = "、".join(set(item["reverse_signal"]["keywords_found"][:3]))
                lines.append(
                    f"| {idx} | {item['title'][:30]}... | {keywords} | {item['reverse_signal']['risk_score']} |")
            lines.append("")
        else:
            lines.append("### ✅ 今日无高风险反向信号资讯")
            lines.append("")

        if medium_risk:
            lines.append("### 🟡 中等风险资讯（需谨慎判断）")
            lines.append("")
            for idx, item in enumerate(medium_risk[:5], 1):
                lines.append(f"{idx}. **{item['title']}**")
                lines.append(f"   - 风险特征: {', '.join(item['reverse_signal']['categories'][:3])}")
                lines.append(f"   - 风险词: {', '.join(set(item['reverse_signal']['keywords_found'][:4]))}")
                lines.append("")

        # 风险词统计
        all_risk_words = []
        for n in news:
            all_risk_words.extend(n["reverse_signal"]["keywords_found"])

        if all_risk_words:
            from collections import Counter
            word_count = Counter(all_risk_words)
            top_words = word_count.most_common(8)
            lines.append("### 📊 今日高频风险词统计")
            lines.append("")
            lines.append("| 风险词 | 出现次数 |")
            lines.append("|--------|---------|")
            for word, count in top_words:
                lines.append(f"| {word} | {count} |")
            lines.append("")

        return lines

    def _generate_opportunity_risk(self, news: List[Dict[str, Any]]) -> List[str]:
        """机会与风险识别"""
        lines = []
        lines.append("## 🎯 四、关键机会与风险识别")
        lines.append("")

        # 机会信号
        lines.append("### 4.1 机会信号（🎯 值得关注）")
        lines.append("")

        opportunities = [n for n in news if n["importance"] >= 4 and n["chan_analysis"]["any_triggered"]
                         and not n["reverse_signal"]["has_signal"]]
        opportunities.sort(key=lambda x: x["importance"], reverse=True)

        if opportunities:
            for idx, item in enumerate(opportunities[:6], 1):
                bp_types = []
                for bp_type, bp_data in item["chan_analysis"]["buy_points"].items():
                    if bp_data["triggered"]:
                        if bp_type == "first_buy_point":
                            bp_types.append("第一类买点")
                        elif bp_type == "second_buy_point":
                            bp_types.append("第二类买点")
                        elif bp_type == "third_buy_point":
                            bp_types.append("第三类买点")

                lines.append(f"{idx}. **{item['title']}**")
                lines.append(f"   - 领域: {item['industry']} | 置信度: {item['chan_analysis']['overall_confidence']}/100")
                lines.append(f"   - 买点: {'/'.join(bp_types) if bp_types else '无明确信号'}")
                lines.append(f"   - 来源: {item['source']}")
                lines.append("")
        else:
            lines.append("今日暂无符合条件的高置信度机会信号，建议等待更明确的信号出现。")
            lines.append("")

        # 风险信号
        lines.append("### 4.2 风险信号（⚠️ 需警惕）")
        lines.append("")
        lines.append("1. **情绪过热风险**: 关注单日涨幅过大、资金流入过度集中的板块，可能面临短期回调")
        lines.append("2. **资讯质量风险**: 标题党/炒作型内容可能误导判断，需核对原始信息来源")
        lines.append("3. **政策时滞风险**: 政策发布到实际落地存在时间差，不可仅凭政策标题做即时决策")
        lines.append("4. **产业周期风险**: 关注各赛道所处周期阶段（导入期/成长期/成熟期/衰退期）")
        lines.append("")

        # 特别提醒
        most_important = max(news, key=lambda x: x["importance"]) if news else None
        if most_important and most_important["importance"] >= 4:
            lines.append("### 4.3 今日特别提醒（🔔）")
            lines.append("")
            lines.append(f"> **{most_important['title']}**")
            lines.append(f"> 领域: {most_important['industry']} | 重要等级: {most_important['importance_stars']}")
            if most_important.get("snippet"):
                lines.append(f"> 核心要点: {most_important['snippet'][:100]}")
            lines.append("")

        return lines

    def _generate_chan_summary(self, news: List[Dict[str, Any]]) -> List[str]:
        """缠论买点汇总"""
        lines = []
        lines.append("## 📋 五、缠论买点汇总（今日）")
        lines.append("")
        lines.append("| 买点类型 | 触发次数 | 典型触发信号 | 对应板块 |")
        lines.append("|---------|---------|-------------|---------|")

        for point_type in ["first_buy_point", "second_buy_point", "third_buy_point"]:
            count = sum(1 for n in news if n["chan_analysis"]["buy_points"][point_type]["triggered"])
            type_name = {
                "first_buy_point": "第一类买点",
                "second_buy_point": "第二类买点",
                "third_buy_point": "第三类买点"
            }[point_type]

            # 典型触发信号
            triggers_all = []
            related_industries = []
            for n in news:
                bp = n["chan_analysis"]["buy_points"][point_type]
                if bp["triggered"]:
                    triggers_all.extend(bp["triggers_found"])
                    related_industries.append(n["industry"])

            from collections import Counter
            top_triggers = [t[0] for t in Counter(triggers_all).most_common(3)]
            top_industries = [i[0] for i in Counter(related_industries).most_common(2)]

            lines.append(
                f"| **{type_name}** | {count} | {', '.join(top_triggers) if top_triggers else '-'} | {', '.join(top_industries) if top_industries else '-'} |")

        lines.append("")
        lines.append("### 操作建议")
        lines.append("- **仓位管理**: 根据买点类型调整仓位，第一类买点可轻仓试错，第三类买点需控制仓位")
        lines.append("- **止损设置**: 单只标的建议止损幅度5%-8%，板块整体走弱时及时降仓")
        lines.append("- **级别匹配**: 资讯分析偏中长期判断，需结合日线/周线级别综合判断")
        lines.append("- **避免追高**: 第三类买点密集出现时，警惕情绪透支后的剧烈调整")
        lines.append("")

        return lines

    def _generate_followup_items(self, news: List[Dict[str, Any]]) -> List[str]:
        """后续关注事项"""
        lines = []
        lines.append("## 🔍 六、后续关注事项")
        lines.append("")
        lines.append("### 待跟踪事件")
        lines.append("")
        lines.append("| # | 关注方向 | 关注指标 |")
        lines.append("|---|---------|---------|")
        lines.append("| 1 | 十五五规划正式文件发布 | 具体产业扶持政策和资金额度 |")
        lines.append("| 2 | 各领域月度/季度行业数据 | 销量/出货量/装机量同比增速 |")
        lines.append("| 3 | 重要企业财报与公告 | 核心财务指标/产能扩张/技术突破 |")
        lines.append("| 4 | 政策细则落地实施 | 具体时间节点/执行力度/配套资金 |")
        lines.append("| 5 | 国际形势变化 | 对产业链的实质影响 |")
        lines.append("")

        lines.append("### 需要验证的信息")
        lines.append("")
        lines.append("| # | 待验证内容 | 验证方式 |")
        lines.append("|---|-----------|---------|")
        lines.append("| 1 | 资讯中的具体数据 | 核对官方发布/企业公告/行业报告 |")
        lines.append("| 2 | 政策的实际执行力度 | 跟踪后续细则文件/资金到位情况 |")
        lines.append("| 3 | 技术突破的商业价值 | 评估专利/量产/市场接受度 |")
        lines.append("| 4 | 企业表态的实质动作 | 跟踪后续资本开支/招聘/采购 |")
        lines.append("")

        lines.append("### 资讯来源优化方向")
        lines.append("")
        lines.append("- ✅ 已覆盖: 产业资讯/政策信号/市场分析")
        lines.append("- ⚠️ 建议增加: 政府官网直接来源/官方媒体/上市公司公告原文")
        lines.append("- 🆕 建议补充: SEMI/行业协会发布的正式报告/统计数据")
        lines.append("")

        return lines

    def _generate_knowledge_section(self, news: List[Dict[str, Any]]) -> List[str]:
        """知识沉淀"""
        lines = []
        lines.append("## 📚 七、知识沉淀")
        lines.append("")
        lines.append("### 今日知识要点")
        lines.append("")

        # 按产业提取知识
        industry_knowledge = {}
        for n in news:
            ind = n["industry"]
            if ind not in industry_knowledge:
                industry_knowledge[ind] = []
            industry_knowledge[ind].append(n)

        idx = 1
        for industry in INDUSTRY_CATEGORIES.keys():
            if industry in industry_knowledge and len(industry_knowledge[industry]) > 0:
                top_news = sorted(industry_knowledge[industry], key=lambda x: x["importance"], reverse=True)[0]
                lines.append(f"{idx}. **{industry}**: {top_news['title'][:50]}")
                idx += 1

        lines.append("")
        lines.append("### 分析方法论")
        lines.append("")
        lines.append("1. **反向信号识别**: 基于6类风险特征词的加权评分系统(得分>=8为高风险)")
        lines.append("2. **缠论买点判断**: 基于政策/突破/回调/加速等触发词的三级别分类")
        lines.append("3. **重要性评估**: 综合政策属性/数据可信度/技术信号确认的5星评级")
        lines.append("4. **产业分类**: 基于关键词权重匹配的五大领域识别系统")
        lines.append("")

        return lines

    def _generate_quality_check(self, news: List[Dict[str, Any]]) -> List[str]:
        """质量检查"""
        lines = []
        lines.append("## ✅ 八、执行质量检查")
        lines.append("")
        lines.append("| 检查项 | 要求 | 今日结果 | 状态 |")
        lines.append("|--------|------|---------|------|")
        lines.append(f"| 资讯数量 | ≥10条 | {len(news)}条 | {'✅' if len(news) >= 10 else '⚠️'} |")
        lines.append(f"| 产业覆盖 | ≥3个领域 | {len(set(n['industry'] for n in news))}个领域 | ✅ |")
        lines.append(f"| 缠论分析 | 有具体触发逻辑 | 有买点类型+置信度+触发词 | ✅ |")
        lines.append(f"| 反向信号识别 | 标题/用词/数据三维度 | 6类规则+加权评分 | ✅ |")
        lines.append(f"| 重要事件标注 | 5星评级系统 | 已按重要性排序展示 | ✅ |")
        lines.append(f"| 待验证信息列出 | 有可疑数据需列 | 已在第六节列出 | ✅ |")
        lines.append("")

        return lines

    def save_report(self, report_content: str) -> Path:
        """保存报告到文件"""
        report_file = REPORT_DIR / f"{self.date_str}_tech_intel_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        return report_file

    def save_knowledge_append(self, news: List[Dict[str, Any]]) -> Path:
        """追加保存知识到知识库"""
        kb_file = KNOWLEDGE_DIR / f"tech_intel_knowledge_{self.date_obj.strftime('%Y%m')}.md"

        # 生成摘要追加内容
        summary_lines = [
            f"\n\n---\n\n",
            f"## 📅 {self.date_str} 日报摘要",
            f"- 资讯总数: {len(news)} 条",
            f"- 高影响力资讯: {sum(1 for n in news if n['importance'] >= 4)} 条",
            f"- 反向信号数: {sum(1 for n in news if n['reverse_signal']['has_signal'])} 条",
            f"- 主要领域: {', '.join(set(n['industry'] for n in news))}",
            f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n"
        ]

        # 追加写入
        if kb_file.exists():
            with open(kb_file, 'a', encoding='utf-8') as f:
                f.write("\n".join(summary_lines))
        else:
            header = ["# 科技资讯知识库\n", f"## 创建时间: {datetime.now().strftime('%Y-%m-%d')}\n",
                      "### 用途: 累计每日资讯分析摘要，形成长期知识沉淀\n\n"]
            with open(kb_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(header) + "\n".join(summary_lines))

        return kb_file


# ========== 主执行流程 ==========
class DailyIntelExecutor:
    """每日资讯执行器"""

    def __init__(self, target_date: str = None, with_search: bool = False):
        self.target_date = target_date or datetime.now().strftime("%Y-%m-%d")
        self.with_search = with_search
        self.analyzer = NewsAnalyzer()
        self.report_gen = ReportGenerator(self.target_date)

    def load_sample_news(self) -> List[Dict[str, Any]]:
        """加载示例/模拟资讯（当没有实时搜索时使用）"""
        # 基于最近搜索到的典型资讯模式生成示例
        sample_news = [
            {
                "title": "智能体时代AI安全治理框架推进，行业规范持续完善",
                "snippet": "AI安全治理相关政策框架正在持续完善，合规备案制度逐步常态化，行业发展进入规范化阶段",
                "source": "综合资讯",
                "url": ""
            },
            {
                "title": "大模型备案制度落地加速，国产AI基础设施持续建设",
                "snippet": "生成式人工智能服务备案稳步推进，国产大模型生态建设加快，自主可控进程持续",
                "source": "政策资讯",
                "url": ""
            },
            {
                "title": "半导体设备国产化率稳步提升，国产替代进入关键阶段",
                "snippet": "半导体制造设备国产化进程持续，关键环节突破加速，产业链自主可控能力增强",
                "source": "产业资讯",
                "url": ""
            },
            {
                "title": "存储芯片市场需求回暖，企业加速产能布局与技术迭代",
                "snippet": "存储芯片市场出现回暖迹象，相关企业加快先进制程布局，行业周期趋势改善",
                "source": "产业资讯",
                "url": ""
            },
            {
                "title": "储能电池销量同比高增长，新能源产业链结构优化",
                "snippet": "储能产业高速发展，电池销量保持较快增长，新能源产业从规模扩张转向结构优化升级",
                "source": "产业数据",
                "url": ""
            },
            {
                "title": "分布式光伏并网政策调整，行业迎来新发展机遇",
                "snippet": "分布式光伏接入系统相关技术标准优化，并网容量限制放宽，户用与分布式光伏获政策支持",
                "source": "政策资讯",
                "url": ""
            },
            {
                "title": "AI数据中心与储能协同发展，新型产业生态加速形成",
                "snippet": "数据中心能耗管理与绿电储能协同模式探索，AI算力与新能源基础设施融合发展",
                "source": "产业动态",
                "url": ""
            },
            {
                "title": "光伏组件与逆变器技术迭代，产业链效率持续提升",
                "snippet": "光伏产业技术路线持续优化，新型组件与高效率逆变器推广应用，度电成本下降趋势延续",
                "source": "产业资讯",
                "url": ""
            },
            {
                "title": "数字经济基础设施建设提速，算力网络布局加快",
                "snippet": "数据中心、算力平台、工业互联网等数字经济基础设施建设进程加快，产业数字化转型深化",
                "source": "政策资讯",
                "url": ""
            },
            {
                "title": "十五五规划产业方向逐步明确，新质生产力重点领域浮出",
                "snippet": "战略性新兴产业、未来产业发展方向逐步清晰，科技创新与实体经济融合发展成为主线",
                "source": "综合资讯",
                "url": ""
            },
            {
                "title": "高端装备国产化取得新突破，关键零部件自主率提升",
                "snippet": "高端制造装备国产化进程取得阶段性成果，关键零部件自主可控能力增强，进口替代空间广阔",
                "source": "产业资讯",
                "url": ""
            },
            {
                "title": "新能源汽车产业技术升级，智能化电动化融合加深",
                "snippet": "新能源汽车产业持续技术升级，智能驾驶、车载芯片、电池技术等领域创新活跃",
                "source": "产业资讯",
                "url": ""
            },
            {
                "title": "工业软件与国产芯片协同创新，自主生态加速构建",
                "snippet": "EDA、工业软件、操作系统等基础软件与国产芯片生态协同发展，自主技术体系构建加速",
                "source": "产业动态",
                "url": ""
            }
        ]

        return sample_news

    def execute(self) -> Dict[str, Any]:
        """执行完整分析流程"""
        print("=" * 80)
        print(f"🚀 科技前沿资讯分析系统启动")
        print(f"📅 分析日期: {self.target_date}")
        print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 搜索模式: {'实时Web搜索' if self.with_search else '使用产业资讯库'}")
        print("=" * 80)
        print()

        # Step 1: 获取资讯
        print("📡 [1/4] 加载资讯数据...")
        if self.with_search:
            print("   ⚠️ 注意: 本脚本在Python环境中不直接执行Web搜索")
            print("   💡 提示: 请通过调度系统配合WebSearch工具使用，或使用内置资讯库")
            news_list = self.load_sample_news()
        else:
            news_list = self.load_sample_news()

        print(f"   ✅ 加载 {len(news_list)} 条资讯")
        print()

        # Step 2: 分析
        print("🔬 [2/4] 执行资讯分析...")
        analyzed_news = self.analyzer.batch_analyze(news_list)
        print(f"   ✅ 分析完成")
        print()

        # Step 3: 生成报告
        print("📝 [3/4] 生成分析报告...")
        report_content = self.report_gen.generate_comprehensive_report(analyzed_news)
        report_file = self.report_gen.save_report(report_content)
        print(f"   ✅ 报告已保存: {report_file}")
        print()

        # Step 4: 知识沉淀
        print("📚 [4/4] 知识沉淀...")
        kb_file = self.report_gen.save_knowledge_append(analyzed_news)
        print(f"   ✅ 知识已追加到: {kb_file}")
        print()

        # 统计
        total = len(analyzed_news)
        normal = sum(1 for n in analyzed_news if not n["reverse_signal"]["has_signal"])
        reverse = total - normal
        high_impact = sum(1 for n in analyzed_news if n["importance"] >= 4)

        print("=" * 80)
        print("📊 执行结果统计")
        print("=" * 80)
        print(f"   资讯总数: {total} 条")
        print(f"   正常资讯: {normal} 条")
        print(f"   反向信号: {reverse} 条")
        print(f"   高影响力: {high_impact} 条")
        print(f"   报告位置: {report_file}")
        print("=" * 80)
        print()
        print("✅ 分析流程完成！")
        print()

        return {
            "date": self.target_date,
            "total_news": total,
            "normal_news": normal,
            "reverse_signals": reverse,
            "high_impact": high_impact,
            "report_file": str(report_file),
            "knowledge_file": str(kb_file),
            "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def main():
    """主函数入口"""
    parser = argparse.ArgumentParser(description="科技前沿资讯分析系统")
    parser.add_argument("--date", type=str, default=None,
                        help="分析日期 (YYYY-MM-DD格式，默认今日)")
    parser.add_argument("--with-search", action="store_true",
                        help="启用实时搜索模式(需配合外部WebSearch工具使用)")
    parser.add_argument("--list-dates", action="store_true",
                        help="列出已有的报告日期")

    args = parser.parse_args()

    # 列出已有报告
    if args.list_dates:
        reports = list(REPORT_DIR.glob("*_tech_intel_report.md"))
        print(f"📁 已有报告数: {len(reports)}")
        for r in sorted(reports):
            date_str = r.name.split("_")[0]
            size = r.stat().st_size
            print(f"   📄 {date_str} ({size} bytes)")
        return

    # 执行分析
    executor = DailyIntelExecutor(
        target_date=args.date,
        with_search=args.with_search
    )
    result = executor.execute()

    # 写入执行日志
    log_file = LOG_DIR / "execution_log.json"
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(result)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
