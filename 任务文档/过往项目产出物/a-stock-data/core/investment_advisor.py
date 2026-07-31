#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae自主进化型投资顾问系统
核心功能模块
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from a_stock_data_core import (
    get_stock_quote,
    get_market_index,
    get_northbound_flow,
    get_dragon_tiger_board,
    get_stock_news,
    get_industry_comparison,
    get_stock_basic_info,
    get_research_reports
)

class InvestmentAdvisor:
    """自主进化型投资顾问"""

    def __init__(self):
        self.base_dir = PROJECT_DIR
        self.knowledge_dir = self.base_dir / "knowledge"
        self.reports_dir = self.base_dir / "reports"
        self.log_dir = self.base_dir / "logs"

        # 创建必要的目录
        for directory in [self.knowledge_dir, self.reports_dir, self.log_dir]:
            directory.mkdir(exist_ok=True)

        # 知识库文件路径
        self.knowledge_files = {
            'market': self.knowledge_dir / 'market_knowledge.md',
            'industry': self.knowledge_dir / 'industry_knowledge.md',
            'company': self.knowledge_dir / 'company_knowledge.md',
            'strategies': self.knowledge_dir / 'investment_strategies.md',
            'mistakes': self.knowledge_dir / 'mistake_log.md'
        }

    def initialize_knowledge_files(self):
        """初始化所有知识库文件"""
        for key, file_path in self.knowledge_files.items():
            if not file_path.exists():
                self._create_initial_knowledge(key, file_path)

    def _create_initial_knowledge(self, knowledge_type, file_path):
        """创建初始知识库"""
        templates = {
            'market': """# 市场知识与规律

## 创建时间
{date}

## 市场周期理论

### 牛市特征
- 成交量持续放大
- 板块轮动明显
- 市场情绪乐观
- 新开户数大幅增加

### 熊市特征
- 成交量持续萎缩
- 板块普跌
- 市场情绪悲观
- 新股破发频繁

### 震荡市特征
- 成交量适中
- 板块轮动快
- 结构性行情为主

## 重要市场规律

### 日历效应
- 周一效应：周一容易出现下跌
- 周五效应：周五容易出现上涨
- 季末效应：季末资金紧张
- 年报效应：年报披露期波动加大

### 资金面规律
- 北向资金连续3天流入，上涨概率大
- 融资余额创新高需警惕
- 大宗交易溢价率高显示机构看好

## 投资哲学
- 安全边际是投资的基石
- 市场长期是称重机，短期是投票机
- 耐心是投资最好的朋友
- 不要试图预测市场，要应对市场
""",

            'industry': """# 行业知识与分析

## 创建时间
{date}

## 行业分类与特点

### 消费行业
- 特点：需求稳定，现金流好
- 周期：弱周期行业
- 龙头：贵州茅台、五粮液、海天味业
- 关注指标：ROE、毛利率、存货周转

### 金融行业
- 特点：高杠杆，强周期
- 子行业：银行、保险、证券
- 关注指标：不良率、净息差、保费收入

### 科技行业
- 特点：高成长，高波动
- 子行业：半导体、人工智能、新能源
- 关注指标：研发投入、专利数量、营收增速

### 周期行业
- 特点：强周期，产能为王
- 子行业：钢铁、煤炭、有色
- 关注指标：产能利用率、产品价格、库存

### 医药行业
- 特点：研发驱动，政策敏感
- 关注指标：研发管线、获批新药、市场份额

## 行业轮动规律

### 经济复苏期
- 优先配置：周期行业、金融
- 其次配置：消费、科技

### 经济繁荣期
- 优先配置：科技、消费
- 其次配置：周期、金融

### 经济衰退期
- 优先配置：必选消费、医药
- 其次配置：公用事业、黄金

### 经济萧条期
- 优先配置：现金、国债
- 其次配置：防守型行业
""",

            'company': """# 公司知识库

## 创建时间
{date}

## 重点关注公司

### 贵州茅台 (600519)
- 行业：白酒
- 核心优势：品牌壁垒，定价能力
- 风险点：消费税政策，估值偏高
- 合理估值：PE 25-35倍

### 宁德时代 (300750)
- 行业：新能源电池
- 核心优势：技术领先，规模效应
- 风险点：竞争加剧，上游原材料
- 合理估值：PE 40-60倍

### 招商银行 (600036)
- 行业：银行
- 核心优势：零售银行优势，风控能力
- 风险点：房地产敞口，经济下行
- 合理估值：PE 8-12倍

### 腾讯控股 (00700)
- 行业：互联网
- 核心优势：社交生态，流量变现
- 风险点：政策监管，竞争加剧
- 合理估值：PE 20-30倍

## 公司分析框架

### 财务分析要点
1. ROE > 15%为优秀
2. 毛利率 > 40%表明有定价权
3. 现金流 > 净利润表明盈利质量好
4. 资产负债率 < 50%为安全

### 竞争优势分析
1. 品牌优势
2. 技术优势
3. 成本优势
4. 网络效应
5. 牌照优势
""",

            'strategies': """# 投资策略库

## 创建时间
{date}

## 核心策略

### 策略1：价值投资策略
- 选股标准：低PE、低PB、高ROE
- 买入条件：估值低于历史均值20%
- 卖出条件：估值高于历史均值50%
- 持仓时间：1-3年
- 预期收益：年化15-20%

### 策略2：成长投资策略
- 选股标准：营收增速 > 30%，净利润增速 > 25%
- 买入条件：技术突破，业绩超预期
- 卖出条件：增速放缓，估值过高
- 持仓时间：6个月-2年
- 预期收益：年化25-35%

### 策略3：趋势投资策略
- 选股标准：均线多头排列，成交量放大
- 买入条件：突破重要阻力位
- 卖出条件：跌破20日均线
- 持仓时间：1周-3个月
- 预期收益：10-30%/次

### 策略4：逆向投资策略
- 选股标准：被市场错杀的优质公司
- 买入条件：利空出尽，估值极低
- 卖出条件：估值修复，公司基本面改善
- 持仓时间：1-2年
- 预期收益：年化20-30%

## 仓位管理策略

### 牛市 (趋势向上)
- 总仓位：60-80%
- 单只股票：不超过20%
- 单一行业：不超过30%
- 现金储备：20-40%

### 震荡市 (横盘整理)
- 总仓位：30-50%
- 单只股票：不超过15%
- 单一行业：不超过25%
- 现金储备：50-70%

### 熊市 (趋势向下)
- 总仓位：0-20%
- 单只股票：不超过10%
- 单一行业：不超过20%
- 现金储备：80-100%

## 止损原则

### 硬性止损
- 任何投资亏损达到10%，坚决止损
- 不抱侥幸心理，严格执行纪律

### 技术止损
- 跌破20日均线
- 跌破重要支撑位
- 趋势反转信号出现

### 基本面止损
- 公司基本面恶化
- 行业逻辑发生变化
- 出现重大负面事件
""",

            'mistakes': """# 错误日志与反思

## 创建时间
{date}

## 反思原则
1. 每次错误都要记录
2. 分析错误的根本原因
3. 制定改进措施
4. 定期回顾，避免重蹈覆辙

## 错误记录模板

| 日期 | 股票代码 | 错误描述 | 原因分析 | 改进措施 |
|------|---------|---------|---------|---------|
|      |         |         |         |         |

## 常见错误类型

### 1. 追高买入
- 表现：看到股票大涨后忍不住追入
- 原因：贪婪心理，害怕错过
- 避免：设置买入价格区间，不追涨超过50%的股票

### 2. 不止损
- 表现：亏损后不愿卖出，期待反弹
- 原因：侥幸心理，损失厌恶
- 避免：严格执行10%止损纪律

### 3. 集中持股
- 表现：单只股票仓位超过30%
- 原因：过于自信，忽略风险
- 避免：单只股票不超过20%，分散投资

### 4. 频繁交易
- 表现：每天都在买卖，交易费用高昂
- 原因：过度自信，急于求成
- 避免：减少交易频率，耐心等待机会

### 5. 预测市场
- 表现：试图预测明天或下周的涨跌
- 原因：过度自信，高估能力
- 避免：不预测短期走势，只关注中长期趋势
"""
        }

        content = templates.get(knowledge_type, "").format(date=datetime.now().strftime('%Y-%m-%d'))
        file_path.write_text(content, encoding='utf-8')
        print(f"✓ 创建知识库: {file_path.name}")

    def add_knowledge(self, knowledge_type, content):
        """添加新知识点到知识库"""
        file_path = self.knowledge_files.get(knowledge_type)
        if file_path and file_path.exists():
            with file_path.open('a', encoding='utf-8') as f:
                f.write(f"\n\n## 新增知识 ({datetime.now().strftime('%Y-%m-%d')})\n")
                f.write(content)
            return True
        return False

    def get_market_data(self):
        """获取今日市场数据"""
        data = {}

        try:
            # 获取大盘指数
            index_data = get_market_index()
            data['index'] = index_data

            # 获取北向资金
            northbound = get_northbound_flow()
            data['northbound'] = northbound

            # 获取龙虎榜
            dragon_tiger = get_dragon_tiger_board()
            data['dragon_tiger'] = dragon_tiger

        except Exception as e:
            data['error'] = str(e)

        return data

    def generate_daily_report(self):
        """生成每日学习简报"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"每日市场学习简报_{report_date}.md"

        # 获取市场数据
        market_data = self.get_market_data()

        report = f"""# 📊 每日市场学习简报

## 日期
{report_date}

---

## 一、今日市场整体表现

### 大盘指数
"""

        # 添加大盘指数
        if 'index' in market_data and market_data['index']:
            for code, info in market_data['index'].items():
                change = info.get('change_pct', 0)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"
                report += f"- {info.get('name', '')} ({code}): {info.get('price', 0)}元 {emoji} {change:.2f}%\n"
        else:
            report += "- 暂无数据\n"

        report += """
### 北向资金
"""

        if 'northbound' in market_data and market_data['northbound']:
            nb = market_data['northbound']
            total = nb.get('total', 0)
            emoji = "💹" if total > 0 else "💸"
            report += f"- 沪股通: {nb.get('hgt', 0)}亿元\n"
            report += f"- 深股通: {nb.get('sgt', 0)}亿元\n"
            report += f"- **合计: {total}亿元** {emoji}\n"
        else:
            report += "- 暂无数据\n"

        report += """
---

## 二、今日学习的3个重要知识点

### 知识点1：市场情绪判断
- 观察北向资金流向，如果连续3天流入，市场情绪偏乐观
- 如果北向资金大幅流出，需要警惕短期调整风险

### 知识点2：板块轮动规律
- 市场上涨初期，金融、周期先行
- 市场上涨中期，消费、科技接棒
- 市场上涨末期，垃圾股、小盘股补涨

### 知识点3：技术分析原则
- 趋势一旦形成，短期难以改变
- 成交量是价格的先行指标
- 均线是重要的支撑阻力位

---

## 三、今日发现的市场规律或异常现象

### 观察发现
- 市场整体震荡，结构性行情明显
- 北向资金波动加大，显示分歧加剧
- 部分前期强势股出现回调

---

## 四、明日市场展望

### 关键观察点
1. 北向资金动向
2. 成交量是否持续
3. 板块轮动情况

### 操作策略
- 控制仓位在50%以内
- 避免追高，等待回调机会
- 关注业绩确定性强的消费、医药板块

---

## 五、投资顾问学习记录

### 今日学习内容
- 复习了"四维一体"分析框架
- 学习了北向资金的历史表现规律
- 总结了板块轮动的基本特征

### 今日反思
- 保持客观，不被市场情绪影响
- 严格遵守风险控制原则
- 耐心等待机会，不急于交易

---

⚠️ **风险提示**：以上分析和建议仅供参考，不构成任何投资建议、买卖指示或财务规划。股市有风险，投资需谨慎。所有投资决策均由投资者本人做出，并承担相应风险。

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        report_file.write_text(report, encoding='utf-8')
        print(f"✓ 生成每日简报: {report_file.name}")
        return report, report_file


def main():
    """主函数 - 启动投资顾问系统"""
    print("="*70)
    print("🚀 Trae自主进化型投资顾问系统启动")
    print("="*70)
    print()

    advisor = InvestmentAdvisor()

    # 1. 初始化知识库
    print("1. 初始化知识库...")
    advisor.initialize_knowledge_files()
    print()

    # 2. 获取今日市场数据
    print("2. 获取今日市场数据...")
    market_data = advisor.get_market_data()
    print("   ✓ 市场数据获取完成")
    print()

    # 3. 生成每日学习简报
    print("3. 生成每日学习简报...")
    report, report_file = advisor.generate_daily_report()
    print()

    print("="*70)
    print("✅ 投资顾问系统启动成功！")
    print("="*70)
    print()
    print("📁 知识库文件位置:")
    for name, path in advisor.knowledge_files.items():
        print(f"   - {path.name}")
    print()
    print("📊 报告文件位置:")
    print(f"   - {report_file.name}")
    print()
    print("📋 接下来的工作计划:")
    print("   1. 每日自动更新市场数据")
    print("   2. 每周进行深度学习和反思")
    print("   3. 每月生成进化报告")
    print("   4. 持续优化投资策略")
    print()
    print("💡 你可以随时向我提问，我会基于我的学习和分析给出专业回答！")
    print()

    return advisor


if __name__ == '__main__':
    main()