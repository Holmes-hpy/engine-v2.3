#!/usr/bin/env python3
"""
每日科技前沿资讯爬取与分析脚本
执行时间：每日上午9:30
功能：爬取AI/半导体/新能源/数字经济/十五五规划相关资讯，结构化输出分析报告
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 项目路径
PROJECT_DIR = Path("/Users/houpengyuan/Documents/trae_projects/a-stock-data")
OUTPUT_DIR = PROJECT_DIR / "daily_tech_intel"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 搜索关键词配置
SEARCH_QUERIES = {
    "人工智能": [
        "人工智能 最新政策 技术突破",
        "AI 大模型 产业应用",
        "人工智能+ 国家政策",
    ],
    "半导体": [
        "半导体 国产替代 芯片进展",
        "功率半导体 涨价 国产化",
        "芯片 制程 EDA 光刻",
    ],
    "新能源": [
        "新能源汽车 销量 政策",
        "储能 光伏 装机量",
        "新型能源体系 十五五",
    ],
    "数字经济": [
        "数字经济 政策 产业动态",
        "数据要素 数字化转型",
        "数字人民币 金融科技",
    ],
    "十五五规划": [
        "十五五规划 产业 解读",
        "十五五 新质生产力",
        "十五五规划 科技创新",
    ],
}

# 反向信号关键词
REVERSE_SIGNAL_KEYWORDS = {
    "极端情绪词": [
        "震惊", "惊人", "刚刚", "突发", "重磅炸弹", "史诗级", "彻底",
        "绝对", "必然", "一定", "100%", "稳赚", "暴富", "吃肉",
        "全趴窝", "没人要", "崩盘", "血洗", "惨烈",
    ],
    "伪确定性": [
        "大局已定", "确定性", "铁定", "毫无悬念", "板上钉钉",
        "不出意外", "十拿九稳",
    ],
    "内幕暗示": [
        "内幕", "独家", "秘密", "悄悄", "偷偷", "私下",
    ],
}


def fetch_news_ddg(query, max_results=5):
    """使用DuckDuckGo搜索获取资讯"""
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # 优先尝试新版ddgs包
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region="cn-zh", max_results=max_results))
            return results
    except ImportError:
        pass
    except Exception as e:
        print(f"[WARN] ddgs搜索失败: {e}")

    # 回退到旧版duckduckgo_search
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region="cn-zh", max_results=max_results))
            return results
    except ImportError:
        print("[WARN] duckduckgo_search未安装，尝试使用requests备用方案")
        return fetch_news_requests(query)
    except Exception as e:
        print(f"[ERROR] DuckDuckGo搜索失败: {e}")
        return fetch_news_requests(query)


def fetch_news_requests(query):
    """备用方案：使用requests + 百度搜索"""
    try:
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        url = f"https://www.baidu.com/s?wd={query}&rn=10"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"

        # 简单提取搜索结果
        results = []
        title_pattern = re.compile(r'<h3[^>]*class="[^"]*t[^"]*"[^>]*>(.*?)</h3>', re.DOTALL)
        href_pattern = re.compile(r'href="(https?://[^"]*)"')
        snippet_pattern = re.compile(r'<span[^>]*class="[^"]*content-right_[^"]*"[^>]*>(.*?)</span>', re.DOTALL)

        titles = title_pattern.findall(resp.text)
        for i, title_html in enumerate(titles[:5]):
            clean_title = re.sub(r'<[^>]+>', '', title_html).strip()
            if clean_title:
                results.append({
                    "title": clean_title,
                    "href": "",
                    "body": "",
                })
        return results
    except Exception as e:
        print(f"[ERROR] 百度搜索备用方案失败: {e}")
        return []


def check_reverse_signals(title, content=""):
    """检查反向信号"""
    full_text = title + " " + content
    signals = {
        "极端情绪词": [],
        "伪确定性": [],
        "内幕暗示": [],
    }

    for category, keywords in REVERSE_SIGNAL_KEYWORDS.items():
        for kw in keywords:
            if kw in full_text:
                signals[category].append(kw)

    return signals


def assess_source_reliability(url, title):
    """评估来源可靠性"""
    reliable_domains = [
        "gov.cn", "xinhuanet.com", "people.com.cn", "cctv.com",
        "ndrc.gov.cn", "miit.gov.cn", "most.gov.cn",
        "cfi.cn", "eastmoney.com", "cs.com.cn", "stcn.com",
        "yicai.com", "caixin.com", "21jingji.com",
    ]

    caution_domains = [
        "toutiao.com", "baijiahao.baidu.com", "zhihu.com",
        "xueqiu.com", "guba.eastmoney.com",
    ]

    if not url:
        return "未知", "⚠️"

    for domain in reliable_domains:
        if domain in url:
            return "权威", "✅"

    for domain in caution_domains:
        if domain in url:
            return "需谨慎", "⚠️"

    return "自媒体", "❌"


def chanlun_analysis(category, news_items):
    """缠论视角分析（基于规则的模板分析）"""
    analysis = {}

    if category == "人工智能":
        analysis = {
            "买点类型": "关注第一类买点——政策底/技术突破点",
            "中枢判断": "AI板块经历高位回调后进入震荡中枢，等待催化突破",
            "关键观察": "WAIC等大型会议催化、政策落地节奏、大模型商业化进展",
        }
    elif category == "半导体":
        analysis = {
            "买点类型": "第二类买点确认——涨价潮验证周期反转",
            "中枢判断": "半导体板块走出18个月下降中枢，涨价潮为突破信号",
            "关键观察": "涨价持续性、国产替代进度、大基金投资节奏",
        }
    elif category == "新能源":
        analysis = {
            "买点类型": "第一类买点构筑——政策底已现，等待市场底确认",
            "中枢判断": "新能源板块长期下降中枢末端，十五五规划提供基本面支撑",
            "关键观察": "装机数据验证、产业链价格企稳、政策配套资金到位",
        }
    elif category == "数字经济":
        analysis = {
            "买点类型": "事件驱动型买点——大会催化可能触发中枢突破",
            "中枢判断": "数据要素概念调整后接近前低，事件催化可能形成突破",
            "关键观察": "数据要素确权政策、数字人民币进展、AI+数字经济融合",
        }
    elif category == "十五五规划":
        analysis = {
            "买点类型": "战略布局型买点——政策方向确定，逢低布局",
            "中枢判断": "五年规划开局年通常对应政策行情，但需区分政策底与市场底",
            "关键观察": "各细分领域规划发布节奏、财政配套力度、地方执行方案",
        }

    return analysis


def generate_report(date_str, all_news):
    """生成结构化分析报告"""
    report_lines = [
        f"# {date_str} 科技前沿资讯分析报告",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"数据来源：WebSearch多源爬取 | 分析框架：缠论+反向信号识别",
        "",
        "---",
        "",
    ]

    # === 第一部分：产业动态 ===
    report_lines.append("## 一、十五五规划相关产业动态\n")

    total_news_count = 0
    important_count = 0
    all_reverse_signals = []

    for category, news_items in all_news.items():
        report_lines.append(f"### {category}\n")

        if not news_items:
            report_lines.append("- 今日未爬取到相关资讯，请手动补充\n")
            continue

        chanlun = chanlun_analysis(category, news_items)

        for i, item in enumerate(news_items, 1):
            total_news_count += 1
            title = item.get("title", "未知标题")
            url = item.get("href", item.get("link", ""))
            body = item.get("body", item.get("snippet", ""))
            source_reliability, source_icon = assess_source_reliability(url, title)

            # 检查反向信号
            reverse_signals = check_reverse_signals(title, body)
            has_signals = any(v for v in reverse_signals.values())

            # 判断重要性
            is_important = source_reliability == "权威" or any(
                kw in title for kw in ["十五五", "规划", "政策", "发改委", "国务院", "工信部"]
            )
            if is_important:
                important_count += 1

            important_tag = " 【重要】" if is_important else ""

            report_lines.extend([
                f"- **资讯{i}：{title}**{important_tag}",
                f"  - 来源：[{source_reliability}]{source_icon} {url[:80]}",
                f"  - 核心内容：{body[:200]}" if body else "  - 核心内容：待获取详情",
                f"  - 缠论视角：",
                f"    - 买点类型：{chanlun['买点类型']}",
                f"    - 中枢判断：{chanlun['中枢判断']}",
                f"    - 关键观察：{chanlun['关键观察']}",
            ])

            # 反向信号
            if has_signals:
                signal_strs = []
                for cat, kws in reverse_signals.items():
                    if kws:
                        signal_strs.append(f"{cat}({','.join(kws)})")
                report_lines.append(f"  - 反向信号检查：⚠️ {', '.join(signal_strs)}")
                all_reverse_signals.append({
                    "title": title,
                    "signals": signal_strs,
                    "category": category,
                })
            else:
                report_lines.append(f"  - 反向信号检查：✅ 未发现明显反向信号")

            report_lines.append("")

        report_lines.append("---\n")

    # === 第二部分：市场情绪与走势判断 ===
    report_lines.extend([
        "## 二、市场情绪与走势判断\n",
        "### 政策面",
        f"- 本日爬取资讯{total_news_count}条，其中重要资讯{important_count}条",
        "- [需AI助手补充：结合当日政策面综合判断]\n",
        "### 技术面",
        "- [需AI助手补充：结合当日行情数据进行缠论技术分析]\n",
        "### 情绪面",
        "- [需AI助手补充：结合资讯情绪和市场情绪综合判断]\n",
        "---\n",
    ])

    # === 第三部分：关键识别与预警 ===
    report_lines.append("## 三、关键识别与预警\n")
    report_lines.append("### 机会信号\n")
    report_lines.append("- [需AI助手补充：基于缠论分析的机会信号]\n")
    report_lines.append("### 风险信号\n")

    if all_reverse_signals:
        report_lines.append("| 文章标题 | 预警类型 | 风险等级 |")
        report_lines.append("|---------|---------|---------|")
        for sig in all_reverse_signals:
            title_short = sig["title"][:40] + "..." if len(sig["title"]) > 40 else sig["title"]
            signal_type = ", ".join(sig["signals"])
            risk = "🔴高" if len(sig["signals"]) >= 2 else "🟡中"
            report_lines.append(f"| {title_short} | {signal_type} | {risk} |")
    else:
        report_lines.append("- 今日未发现明显标题党或操控信号\n")

    report_lines.append("\n---\n")

    # === 第四部分：后续关注事项 ===
    report_lines.extend([
        "## 四、后续关注事项\n",
        "### 待跟踪事件",
        "- [需AI助手补充：基于今日资讯的后续跟踪事件]\n",
        "### 需要验证的信息",
        "- [需AI助手补充：基于今日资讯的待验证信息]\n",
        "---\n",
        f"*本报告由自动化脚本生成于{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}，"
        f"部分分析需AI助手补充完善。不构成投资建议。*\n",
    ])

    return "\n".join(report_lines)


def main():
    """主函数"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"========== 每日科技前沿资讯爬取 ==========")
    print(f"日期：{today}")
    print(f"=" * 50)

    all_news = {}

    for category, queries in SEARCH_QUERIES.items():
        print(f"\n[{category}] 正在爬取资讯...")
        category_news = []

        for query in queries:
            print(f"  搜索：{query}")
            results = fetch_news_ddg(query, max_results=3)

            for r in results:
                # 去重
                title = r.get("title", "")
                if title and not any(n.get("title") == title for n in category_news):
                    category_news.append(r)

            import time
            time.sleep(1)  # 避免请求过快

        # 每个类别最多保留8条
        category_news = category_news[:8]
        all_news[category] = category_news
        print(f"  获取到 {len(category_news)} 条资讯")

    # 生成报告
    print(f"\n正在生成分析报告...")
    report = generate_report(today, all_news)

    # 保存报告
    report_path = OUTPUT_DIR / f"{today}_tech_intel_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n报告已保存至：{report_path}")
    print(f"=" * 50)

    # 同时保存原始JSON数据
    json_path = OUTPUT_DIR / f"{today}_tech_intel_raw.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    print(f"原始数据已保存至：{json_path}")

    return str(report_path)


if __name__ == "__main__":
    main()
