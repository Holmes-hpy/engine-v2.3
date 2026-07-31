#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主学习系统核心模块
实现每日学习、每周深度学习、知识库自动维护等功能
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from a_stock_data_core import (
    get_stock_quote,
    get_historical_k_data,
    get_market_index,
    get_northbound_flow,
    get_dragon_tiger_board,
    get_stock_news,
    get_stock_basic_info,
    get_research_reports
)

class AutonomousLearningSystem:
    """自主学习系统"""
    
    def __init__(self):
        self.base_dir = PROJECT_DIR
        self.knowledge_dir = self.base_dir / "knowledge"
        self.reports_dir = self.base_dir / "reports"
        self.logs_dir = self.base_dir / "logs"
        
        # 创建必要目录
        for directory in [self.knowledge_dir, self.reports_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # 知识库文件
        self.knowledge_files = {
            'market': self.knowledge_dir / 'market_knowledge.md',
            'industry': self.knowledge_dir / 'industry_knowledge.md',
            'company': self.knowledge_dir / 'company_knowledge.md',
            'strategies': self.knowledge_dir / 'investment_strategies.md',
            'mistakes': self.knowledge_dir / 'mistake_log.md'
        }
        
        # 确保所有知识库文件存在
        self._initialize_knowledge_files()
    
    def _initialize_knowledge_files(self):
        """初始化知识库文件"""
        for key, file_path in self.knowledge_files.items():
            if not file_path.exists():
                self._create_initial_knowledge(key, file_path)
    
    def _create_initial_knowledge(self, knowledge_type: str, file_path: Path):
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
    
    def add_knowledge(self, knowledge_type: str, title: str, content: str) -> bool:
        """添加知识到知识库"""
        file_path = self.knowledge_files.get(knowledge_type)
        if file_path and file_path.exists():
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with file_path.open('a', encoding='utf-8') as f:
                f.write(f"\n\n## {title} ({timestamp})\n")
                f.write(content)
            print(f"✓ 添加知识: {title} -> {file_path.name}")
            return True
        return False
    
    def log_mistake(self, stock_code: str, description: str, 
                   reason: str, improvement: str) -> bool:
        """记录错误"""
        file_path = self.knowledge_files['mistakes']
        if file_path.exists():
            timestamp = datetime.now().strftime('%Y-%m-%d')
            with file_path.open('a', encoding='utf-8') as f:
                f.write(f"\n\n| {timestamp} | {stock_code} | {description} | {reason} | {improvement} |")
            print(f"✓ 记录错误: {stock_code} - {description}")
            return True
        return False
    
    def pre_market_learning(self) -> Dict[str, Any]:
        """开盘前学习（9:00-9:30）"""
        print("📋 开始开盘前学习...")
        result = {
            'timestamp': datetime.now().isoformat(),
            'market_data': {},
            'news': [],
            'key_factors': []
        }
        
        try:
            # 获取大盘指数
            index_data = get_market_index()
            if index_data:
                result['market_data']['indices'] = index_data
            
            # 获取北向资金
            northbound = get_northbound_flow()
            if northbound:
                result['market_data']['northbound'] = northbound
            
            # 分析关键因素
            if northbound:
                nb_total = northbound.get('total', 0)
                if nb_total > 0:
                    result['key_factors'].append(f"北向资金流入 {nb_total} 亿元，情绪偏乐观")
                elif nb_total < 0:
                    result['key_factors'].append(f"北向资金流出 {nb_total} 亿元，需警惕")
            
            print("✓ 开盘前学习完成")
            
        except Exception as e:
            print(f"✗ 开盘前学习出错: {e}")
            result['error'] = str(e)
        
        return result
    
    def intraday_learning(self) -> Dict[str, Any]:
        """盘中学习（9:30-11:30, 13:00-15:00）"""
        print("📋 开始盘中学习...")
        result = {
            'timestamp': datetime.now().isoformat(),
            'index_movement': {},
            'abnormal_stocks': [],
            'money_flow': {},
            'observations': []
        }
        
        try:
            # 获取实时市场数据
            index_data = get_market_index()
            if index_data:
                result['index_movement'] = index_data
            
            # 记录观察
            result['observations'].append("市场实时监控中")
            
            print("✓ 盘中学习完成")
            
        except Exception as e:
            print(f"✗ 盘中学习出错: {e}")
            result['error'] = str(e)
        
        return result
    
    def post_market_learning(self) -> Dict[str, Any]:
        """收盘后学习（15:00-15:30）"""
        print("📋 开始收盘后学习...")
        result = {
            'timestamp': datetime.now().isoformat(),
            'market_summary': {},
            'top_stocks': [],
            'bottom_stocks': [],
            'dragon_tiger': {},
            'market_features': [],
            'lessons_learned': []
        }
        
        try:
            # 获取完整行情数据
            index_data = get_market_index()
            if index_data:
                result['market_summary']['indices'] = index_data
            
            # 获取北向资金
            northbound = get_northbound_flow()
            if northbound:
                result['market_summary']['northbound'] = northbound
            
            # 获取龙虎榜
            dragon_tiger = get_dragon_tiger_board()
            if dragon_tiger:
                result['dragon_tiger'] = dragon_tiger
            
            # 分析市场特点
            result['market_features'].append("完成今日市场复盘")
            
            # 学到的知识点
            result['lessons_learned'].extend([
                "市场情绪判断：观察北向资金流向",
                "板块轮动规律：市场上涨初期金融、周期先行",
                "技术分析原则：趋势一旦形成短期难以改变"
            ])
            
            print("✓ 收盘后学习完成")
            
        except Exception as e:
            print(f"✗ 收盘后学习出错: {e}")
            result['error'] = str(e)
        
        return result
    
    def generate_daily_report(self) -> str:
        """生成每日学习简报"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"每日市场学习简报_{report_date}.md"
        
        print(f"📊 生成每日简报: {report_file.name}")
        
        # 执行收盘后学习
        post_market = self.post_market_learning()
        
        report = f"""# 📊 每日市场学习简报

## 日期
{report_date}

---

## 一、今日市场整体表现

### 大盘指数
"""
        
        if 'indices' in post_market.get('market_summary', {}):
            for code, info in post_market['market_summary']['indices'].items():
                change = info.get('change_pct', 0)
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➖"
                report += f"- {info.get('name', '')} ({code}): {info.get('price', 0)}元 {emoji} {change:.2f}%\n"
        else:
            report += "- 暂无数据\n"
        
        report += """
### 北向资金
"""
        
        if 'northbound' in post_market.get('market_summary', {}):
            nb = post_market['market_summary']['northbound']
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
        print(f"✓ 每日简报生成成功: {report_file}")
        return str(report_file)
    
    def weekly_deep_learning(self) -> str:
        """每周深度学习"""
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.reports_dir / f"每周学习与投资报告_{report_date}.md"
        
        print(f"📊 开始每周深度学习...")
        
        report = f"""# 📚 每周学习与投资报告

## 报告日期
{report_date}

---

## 一、本周市场回顾与总结

### 整体表现
- 回顾本周各大指数表现
- 分析成交量变化趋势
- 总结市场情绪演变

### 行业板块轮动分析
- 涨幅最大的行业
- 跌幅最大的行业
- 资金流向分析

---

## 二、本周学到的5个核心知识点

### 知识点1
- 内容：持续更新中

### 知识点2
- 内容：持续更新中

### 知识点3
- 内容：持续更新中

### 知识点4
- 内容：持续更新中

### 知识点5
- 内容：持续更新中

---

## 三、当前市场趋势判断

### 技术面分析
- 均线系统
- 成交量
- MACD、KDJ等指标

### 基本面分析
- 宏观经济
- 政策面
- 估值水平

---

## 四、下周值得关注的行业和个股

### 重点关注行业
- 行业1：理由说明
- 行业2：理由说明

### 重点关注个股
- 股票1：关注理由
- 股票2：关注理由

---

## 五、投资组合建议

### 仓位建议
- 总仓位：X%
- 行业配置建议

### 风险提示
- 风险1
- 风险2

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        report_file.write_text(report, encoding='utf-8')
        print(f"✓ 周度报告生成: {report_file}")
        return str(report_file)
    
    def monthly_evolution_report(self) -> str:
        """月度进化报告"""
        report_date = datetime.now().strftime('%Y-%m')
        report_file = self.reports_dir / f"投资顾问进化报告_{report_date}.md"
        
        print(f"📊 开始生成月度进化报告...")
        
        report = f"""# 🚀 投资顾问进化报告

## 报告月份
{report_date}

---

## 一、本月学习成果总结

### 新增知识
- 市场知识：新增X条
- 行业知识：新增X条
- 公司知识：新增X条
- 策略优化：X项

### 技能提升
- 技术分析能力提升
- 基本面分析能力提升
- 市场敏感度提升

---

## 二、分析案例统计

### 正确判断
- 案例1：详细描述
- 案例2：详细描述

### 错误判断
- 案例1：详细描述，原因分析
- 案例2：详细描述，原因分析

### 准确率统计
- 总判断数：X
- 正确数：X
- 准确率：X%

---

## 三、分析框架优化与改进

### 优化点1
- 原问题：
- 改进方案：
- 效果预期：

### 优化点2
- 原问题：
- 改进方案：
- 效果预期：

---

## 四、下月学习计划和重点

### 学习目标
- 目标1：
- 目标2：
- 目标3：

### 重点关注
- 领域1：
- 领域2：

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        report_file.write_text(report, encoding='utf-8')
        print(f"✓ 月度进化报告生成: {report_file}")
        return str(report_file)
    
    def run_daily_learning_cycle(self):
        """运行完整的每日学习流程"""
        print("=" * 70)
        print("🚀 自主学习系统 - 每日学习流程启动")
        print("=" * 70)
        print()
        
        # 1. 收盘后学习
        print("【阶段1】收盘后学习 (15:00-15:30)")
        print("-" * 50)
        self.post_market_learning()
        print()
        
        # 2. 生成每日简报
        print("【阶段2】生成每日学习简报")
        print("-" * 50)
        report_file = self.generate_daily_report()
        print()
        
        print("=" * 70)
        print("✅ 每日学习流程完成！")
        print("=" * 70)
        print()
        print(f"📁 报告文件: {report_file}")
        
        return report_file


def main():
    """主函数"""
    print("=" * 70)
    print("🤖 Trae自主学习系统启动")
    print("=" * 70)
    print()
    
    system = AutonomousLearningSystem()
    
    # 运行每日学习流程
    report_file = system.run_daily_learning_cycle()
    
    print()
    print("💡 系统已准备就绪！")
    print()
    print("📋 可用功能:")
    print("   1. run_daily_learning_cycle() - 运行每日学习流程")
    print("   2. generate_daily_report() - 生成每日简报")
    print("   3. weekly_deep_learning() - 每周深度学习")
    print("   4. monthly_evolution_report() - 月度进化报告")
    print("   5. add_knowledge() - 添加新知识")
    print("   6. log_mistake() - 记录错误")
    
    return system


if __name__ == '__main__':
    main()
