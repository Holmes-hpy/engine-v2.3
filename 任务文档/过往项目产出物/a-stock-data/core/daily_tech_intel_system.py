#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技前沿资讯分析系统
- 每天上午9:30执行
- 爬取并分析科技前沿资讯
- 聚焦十五五规划相关产业
- 结合缠论进行知识沉淀
- 识别反向信号
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# 报告保存目录
REPORT_DIR = PROJECT_DIR / "daily_tech_intel"
REPORT_DIR.mkdir(exist_ok=True)

# 搜索关键词配置
SEARCH_KEYWORDS = {
    "人工智能": [
        "人工智能 最新政策",
        "人工智能 技术突破",
        "site:gov.cn 人工智能",
        "site:xinhuanet.com 人工智能",
        "site:36kr.com 人工智能"
    ],
    "半导体": [
        "半导体 国产替代",
        "芯片 最新进展",
        "site:gov.cn 半导体",
        "site:people.com.cn 芯片",
        "site:36kr.com 半导体"
    ],
    "新能源": [
        "新能源 汽车 储能 光伏",
        "site:gov.cn 新能源",
        "site:xinhuanet.com 新能源",
        "site:weibo.com 新能源"
    ],
    "数字经济": [
        "数字经济 政策 产业动态",
        "site:gov.cn 数字经济",
        "site:people.com.cn 数字经济"
    ],
    "十五五规划": [
        "十五五规划 相关解读",
        "site:gov.cn 十五五",
        "site:xinhuanet.com 十五五规划"
    ]
}

# 反向信号关键词
REVERSE_SIGNAL_WORDS = [
    "震惊", "惊人", "刚刚", "内幕", "独家", "重磅", "惊天", "秘密",
    "暴涨", "暴跌", "必涨", "必跌", "翻倍", "妖股",
    "主力", "游资", "机构", "大佬", "牛散",
    "即将", "马上", "立刻",
    "手把手", "带你", "教你", "跟着", "躺赢",
    "定律", "战法", "秘籍", "绝招", "心法",
    "抄底", "逃顶", "上车", "下车", "接力"
]

class DailyTechIntelSystem:
    """每日科技资讯分析系统"""
    
    def __init__(self):
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.news_data = {}
        
    def search_news(self, query):
        """使用WebSearch搜索新闻"""
        try:
            # 这里我们模拟WebSearch的结果
            # 在实际运行中，会调用真实的WebSearch工具
            # 为了演示，我们返回一些示例数据
            print(f"🔍 正在搜索: {query}")
            
            # 示例数据结构
            sample_results = [
                {
                    "title": "工信部发布人工智能创新发展行动计划",
                    "url": "https://www.miit.gov.cn/example1",
                    "snippet": "工信部近日印发《人工智能创新发展行动计划（2025-2027年）》，提出多项支持政策..."
                },
                {
                    "title": "国产7nm芯片取得重大突破",
                    "url": "https://www.people.com.cn/example2",
                    "snippet": "中芯国际宣布在先进制程领域取得重要进展，产能提升30%..."
                }
            ]
            
            return sample_results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []
    
    def crawl_all_news(self):
        """爬取所有领域的新闻"""
        print("=" * 70)
        print("🚀 每日科技前沿资讯分析系统启动")
        print("=" * 70)
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for category, keywords in SEARCH_KEYWORDS.items():
            print(f"📡 正在爬取 {category} 领域...")
            category_news = []
            
            for keyword in keywords:
                results = self.search_news(keyword)
                for result in results:
                    result["category"] = category
                    result["search_keyword"] = keyword
                    category_news.append(result)
            
            # 去重
            unique_news = []
            seen_titles = set()
            for news in category_news:
                if news["title"] not in seen_titles:
                    seen_titles.add(news["title"])
                    unique_news.append(news)
            
            self.news_data[category] = unique_news
            print(f"   共获取 {len(unique_news)} 条新闻")
        
        return self.news_data
    
    def extract_core_info(self, news):
        """提取核心信息"""
        analysis = {
            "event_subject": "",
            "key_policy_tech": "",
            "impact_scope": "",
            "raw_news": news
        }
        
        title = news["title"]
        snippet = news.get("snippet", "")
        
        # 识别事件主体
        if "工信部" in title or "工信部" in snippet:
            analysis["event_subject"] = "工信部"
        elif "发改委" in title or "发改委" in snippet:
            analysis["event_subject"] = "发改委"
        elif "科技部" in title or "科技部" in snippet:
            analysis["event_subject"] = "科技部"
        elif "中芯国际" in title or "中芯国际" in snippet:
            analysis["event_subject"] = "中芯国际"
        elif "华为" in title or "华为" in snippet:
            analysis["event_subject"] = "华为"
        elif "比亚迪" in title or "比亚迪" in snippet:
            analysis["event_subject"] = "比亚迪"
        elif "宁德时代" in title or "宁德时代" in snippet:
            analysis["event_subject"] = "宁德时代"
        else:
            analysis["event_subject"] = "未知主体"
        
        # 提取关键政策或技术突破
        if "政策" in title or "规划" in title or "行动计划" in title:
            analysis["key_policy_tech"] = "政策发布"
        elif "突破" in title or "进展" in title or "研发" in title:
            analysis["key_policy_tech"] = "技术突破"
        elif "产能" in title or "量产" in title:
            analysis["key_policy_tech"] = "产能提升"
        else:
            analysis["key_policy_tech"] = "产业动态"
        
        # 判断影响范围
        if "全国" in title or "国家" in title:
            analysis["impact_scope"] = "全国性"
        elif "行业" in title or "产业" in title:
            analysis["impact_scope"] = "行业级"
        else:
            analysis["impact_scope"] = "企业级"
        
        return analysis
    
    def analyze_chan_theory(self, news, core_info):
        """缠论视角分析"""
        title = news["title"]
        snippet = news.get("snippet", "")
        
        chan_analysis = {
            "first_buy_point": False,
            "second_buy_point": False,
            "third_buy_point": False,
            "pivot_analysis": "",
            "support_level": ""
        }
        
        # 第一类买点：政策底/技术突破点
        if any(keyword in title or keyword in snippet for keyword in ["政策", "规划", "发布", "出台", "突破"]):
            chan_analysis["first_buy_point"] = True
            chan_analysis["pivot_analysis"] = "可能形成政策底或技术突破型底部"
        
        # 第二类买点：回调后的确认机会
        if any(keyword in title or keyword in snippet for keyword in ["回调", "调整", "企稳", "确认"]):
            chan_analysis["second_buy_point"] = True
            chan_analysis["pivot_analysis"] += "，关注回调后的确认机会"
        
        # 第三类买点：趋势确立信号
        if any(keyword in title or keyword in snippet for keyword in ["趋势确立", "上涨", "加速", "放量"]):
            chan_analysis["third_buy_point"] = True
            chan_analysis["pivot_analysis"] += "，趋势确立信号出现"
        
        # 中枢分析
        if core_info["key_policy_tech"] == "政策发布":
            chan_analysis["support_level"] = "政策支撑位"
        elif core_info["key_policy_tech"] == "技术突破":
            chan_analysis["support_level"] = "技术突破支撑位"
        
        return chan_analysis
    
    def check_reverse_signal(self, news):
        """检查反向信号"""
        title = news["title"]
        snippet = news.get("snippet", "")
        
        signal_check = {
            "has_reverse_signal": False,
            "signal_words": [],
            "reason": ""
        }
        
        # 检查标题党词汇
        for word in REVERSE_SIGNAL_WORDS:
            if word in title:
                signal_check["signal_words"].append(word)
        
        # 检查是否有非官方"内幕"消息
        if "内幕" in title or "独家" in title or "秘密" in title:
            signal_check["reason"] += "包含非官方消息词汇；"
        
        # 检查是否缺乏具体数据
        if len(snippet) < 30 and not any(keyword in snippet for keyword in ["亿", "万", "%", "元"]):
            signal_check["reason"] += "缺乏具体数据支撑；"
        
        if len(signal_check["signal_words"]) >= 3 or signal_check["reason"]:
            signal_check["has_reverse_signal"] = True
        
        return signal_check
    
    def analyze_all_news(self):
        """分析所有新闻"""
        analyzed_data = {}
        
        for category, news_list in self.news_data.items():
            analyzed_list = []
            for news in news_list:
                core_info = self.extract_core_info(news)
                chan_analysis = self.analyze_chan_theory(news, core_info)
                reverse_signal = self.check_reverse_signal(news)
                
                analyzed_list.append({
                    "news": news,
                    "core_info": core_info,
                    "chan_analysis": chan_analysis,
                    "reverse_signal": reverse_signal
                })
            
            analyzed_data[category] = analyzed_list
        
        return analyzed_data
    
    def generate_report(self, analyzed_data):
        """生成结构化报告"""
        report = f"# {self.date_str} 科技前沿资讯分析报告\n\n"
        
        # 第一部分：十五五规划相关产业动态
        report += "## 一、十五五规划相关产业动态\n\n"
        
        for category, news_list in analyzed_data.items():
            report += f"### {category}\n"
            
            if not news_list:
                report += "- 今日无重大更新\n\n"
                continue
            
            for i, item in enumerate(news_list[:5], 1):
                news = item["news"]
                core_info = item["core_info"]
                chan_analysis = item["chan_analysis"]
                reverse_signal = item["reverse_signal"]
                
                report += f"- 资讯{i}: {news['title']}\n"
                report += f"  - 来源: {news['url']}\n"
                report += f"  - 核心内容: {news.get('snippet', '待获取')}\n"
                
                # 缠论视角
                chan_points = []
                if chan_analysis["first_buy_point"]:
                    chan_points.append("第一类买点信号")
                if chan_analysis["second_buy_point"]:
                    chan_points.append("第二类买点信号")
                if chan_analysis["third_buy_point"]:
                    chan_points.append("第三类买点信号")
                
                report += f"  - 缠论视角: {', '.join(chan_points) if chan_points else '无明显买卖点信号'}"
                if chan_analysis["pivot_analysis"]:
                    report += f"。{chan_analysis['pivot_analysis']}"
                report += "\n"
                
                # 反向信号检查
                if reverse_signal["has_reverse_signal"]:
                    report += f"  - 反向信号检查: ⚠️ 存在反向信号 - 关键词: {', '.join(reverse_signal['signal_words'])}。{reverse_signal['reason']}\n"
                else:
                    report += "  - 反向信号检查: ✅ 未发现明显反向信号\n"
                
                report += "\n"
        
        # 第二部分：市场情绪与走势判断
        report += "## 二、市场情绪与走势判断\n\n"
        
        # 统计分析
        total_news = sum(len(news_list) for news_list in analyzed_data.values())
        policy_news = sum(1 for clist in analyzed_data.values() for item in clist if item['core_info']['key_policy_tech'] == '政策发布')
        tech_news = sum(1 for clist in analyzed_data.values() for item in clist if item['core_info']['key_policy_tech'] == '技术突破')
        reverse_signals = sum(1 for clist in analyzed_data.values() for item in clist if item['reverse_signal']['has_reverse_signal'])
        
        report += f"- 政策面: 今日共获取 {policy_news} 条政策相关资讯\n"
        report += f"- 技术面: 今日共获取 {tech_news} 条技术突破相关资讯\n"
        report += f"- 情绪面: 反向信号数量: {reverse_signals}，整体情绪: {'偏谨慎' if reverse_signals > 3 else '偏乐观'}\n\n"
        
        # 第三部分：关键识别与预警
        report += "## 三、关键识别与预警\n\n"
        
        opportunity_signals = []
        risk_signals = []
        titleparty_signals = []
        
        for category, news_list in analyzed_data.items():
            for item in news_list:
                news = item["news"]
                chan_analysis = item["chan_analysis"]
                reverse_signal = item["reverse_signal"]
                
                if chan_analysis["first_buy_point"] or chan_analysis["second_buy_point"] or chan_analysis["third_buy_point"]:
                    opportunity_signals.append(f"{category}: {news['title']}")
                
                if reverse_signal["has_reverse_signal"]:
                    risk_signals.append(f"{category}: {news['title']}")
                    if len(reverse_signal["signal_words"]) >= 3:
                        titleparty_signals.append(f"{category}: {news['title']}")
        
        report += "- 机会信号:\n"
        if opportunity_signals:
            for sig in opportunity_signals[:5]:
                report += f"  ✓ {sig}\n"
        else:
            report += "  无明显机会信号\n"
        
        report += "- 风险信号:\n"
        if risk_signals:
            for sig in risk_signals[:5]:
                report += f"  ⚠️ {sig}\n"
        else:
            report += "  无明显风险信号\n"
        
        report += "- 标题党预警:\n"
        if titleparty_signals:
            for sig in titleparty_signals[:5]:
                report += f"  🚨 {sig}\n"
        else:
            report += "  无标题党预警\n"
        
        report += "\n"
        
        # 第四部分：后续关注事项
        report += "## 四、后续关注事项\n\n"
        report += "- 待跟踪事件: 持续关注十五五规划相关政策发布进度\n"
        report += "- 需要验证的信息: 技术突破资讯的具体细节待进一步确认\n"
        
        return report
    
    def save_report(self, report):
        """保存报告到文件"""
        report_file = REPORT_DIR / f"{self.date_str}_tech_intel_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📁 报告已保存到: {report_file}")
        return report_file
    
    def run(self):
        """执行完整流程"""
        # 1. 爬取新闻
        self.crawl_all_news()
        
        # 2. 分析新闻
        analyzed_data = self.analyze_all_news()
        
        # 3. 生成报告
        report = self.generate_report(analyzed_data)
        
        # 4. 保存报告
        self.save_report(report)
        
        print("\n✅ 分析完成！")
        return report


def main():
    """主函数"""
    system = DailyTechIntelSystem()
    system.run()


if __name__ == '__main__':
    main()

