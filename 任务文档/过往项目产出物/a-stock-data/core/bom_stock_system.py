# -*- coding: utf-8 -*-
"""
BOM产业链自动选股系统 - 主入口
整合所有模块，提供一键执行接口

使用方式:
    python bom_stock_system.py [screen | monitor | backtest | dashboard | all]
    screen  - 执行选股
    monitor - 执行监测
    backtest - 执行回测
    dashboard - 生成可视化报告
    all - 执行完整工作流
"""

import sys
import json
import time
import re
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from three_high_engine import ThreeHighEngine, StockEvaluation
from daily_bom_monitor import DailyMonitoringSystem
from bom_backtest_engine import BOMBacktestEngine


class BOMStockSystem:
    """BOM产业链选股系统主类"""

    def __init__(self):
        self.engine = ThreeHighEngine()
        self.monitor = DailyMonitoringSystem()
        self.backtest = BOMBacktestEngine()
        self.results = []

    # ============= 选股接口 =============

    def run_stock_selection(self, top_n: int = 20) -> List[StockEvaluation]:
        """执行选股"""
        print("\n" + "🚀"*40)
        print("🚀 【模式1】BOM产业链三高环节选股")
        print("🚀"*40)

        results = self.engine.run_screening(top_n=top_n)
        self.results = results

        # 保存选股结果
        self.save_selection_results(results)

        # 展示最终推荐
        self.show_final_recommendations(results)

        return results

    def save_selection_results(self, results: List[StockEvaluation]):
        """保存选股结果到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_dir = PROJECT_DIR / "bom_stock_data"
        data_dir.mkdir(exist_ok=True)

        output = {
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "strategy": "BOM产业链三高选股法",
            "total_stocks": len(results),
            "stocks": [
                {
                    "rank": i + 1,
                    "code": r.code,
                    "name": r.name,
                    "node_name": r.node_name,
                    "category": r.category,
                    "level": r.level,
                    "barrier_score": round(r.barrier_score, 2),
                    "growth_score": round(r.growth_score, 2),
                    "profit_score": round(r.profit_score, 2),
                    "supply_demand_score": round(r.supply_demand_score, 2),
                    "total_score": round(r.total_score, 2),
                    "reason": r.reason,
                    "price": r.quote.get('price', 0) if r.quote else 0,
                    "change_pct": r.quote.get('change_pct', 0) if r.quote else 0,
                    "pe_ttm": r.quote.get('pe_ttm', 0) if r.quote else 0,
                    "mcap_yi": r.quote.get('mcap_yi', 0) if r.quote else 0,
                }
                for i, r in enumerate(results)
            ]
        }

        file_path = data_dir / f"selection_{timestamp}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 选股结果已保存: {file_path}")

    def show_final_recommendations(self, results: List[StockEvaluation]):
        """展示最终推荐"""
        print("\n" + "🎯"*30)
        print("🎯  最终选股推荐 (TOP 10)")
        print("🎯"*30)

        for i, r in enumerate(results[:10], 1):
            print(f"\n{i}. {r.name} ({r.code})")
            print(f"   📍 环节: {r.node_name} ({r.category}·{r.level})")
            print(f"   📊 评分: 壁垒{r.barrier_score:.0f} · 增长{r.growth_score:.0f} · "
                  f"利润{r.profit_score:.0f} · 供需{r.supply_demand_score:.0f} · "
                  f"总分{r.total_score:.0f}")
            if r.quote:
                print(f"   💰 现价:{r.quote.get('price',0):.2f} | "
                      f"涨跌:{r.quote.get('change_pct',0):+.2f}% | "
                      f"PE:{r.quote.get('pe_ttm',0):.1f} | "
                      f"市值:{r.quote.get('mcap_yi',0):.0f}亿")
            print(f"   💡 选股理由: {r.reason}")

    # ============= 监测接口 =============

    def run_monitoring(self):
        """执行每日监测"""
        print("\n" + "📈"*40)
        print("📈 【模式2】每日涨幅监测")
        print("📈"*40)

        self.monitor.run_full_workflow()

    # ============= 回测接口 =============

    def run_backtest(self):
        """执行策略回测"""
        print("\n" + "🔬"*40)
        print("🔬 【模式3】策略有效性回测验证")
        print("🔬"*40)

        results = self.backtest.run_multi_period_backtest(
            periods=[5, 10, 20, 30]
        )
        return results

    # ============= 可视化面板 =============

    def generate_dashboard(self, results: Optional[List[StockEvaluation]] = None):
        """生成HTML可视化监控面板"""
        if results is None:
            results = self.engine.run_screening(top_n=20)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 生成股票表格HTML
        stock_rows = ""
        for i, r in enumerate(results[:20], 1):
            price = r.quote.get('price', 0) if r.quote else 0
            change = r.quote.get('change_pct', 0) if r.quote else 0
            pe = r.quote.get('pe_ttm', 0) if r.quote else 0
            mcap = r.quote.get('mcap_yi', 0) if r.quote else 0

            # 根据涨跌幅设置颜色
            change_color = "#27ae60" if change > 0 else ("#e74c3c" if change < 0 else "#95a5a6")

            # 根据总分设置星级
            stars = "⭐" * min(int(r.total_score / 20) + 1, 5)

            stock_rows += f"""
            <tr class="stock-row">
                <td class="rank">{i}</td>
                <td class="name">{r.name}</td>
                <td class="code">{r.code}</td>
                <td class="node">{r.node_name}</td>
                <td class="category">{r.category}</td>
                <td class="level">{r.level}</td>
                <td class="score-barrier">{int(r.barrier_score)}</td>
                <td class="score-growth">{int(r.growth_score)}</td>
                <td class="score-profit">{int(r.profit_score)}</td>
                <td class="score-sd">{int(r.supply_demand_score)}</td>
                <td class="score-total">{stars} {int(r.total_score)}</td>
                <td class="price">{price:.2f}</td>
                <td class="change" style="color:{change_color}">{change:+.2f}%</td>
                <td class="pe">{pe:.1f}</td>
                <td class="mcap">{int(mcap)}亿</td>
                <td class="reason">{r.reason}</td>
            </tr>
            """

        # 生成图表数据
        score_data = []
        category_count = {}
        for r in results[:15]:
            score_data.append({
                "name": r.name,
                "barrier": int(r.barrier_score),
                "growth": int(r.growth_score),
                "profit": int(r.profit_score),
                "supply": int(r.supply_demand_score),
                "total": int(r.total_score),
            })
            category_count[r.category] = category_count.get(r.category, 0) + 1

        category_data = [
            {"name": k, "count": v} for k, v in category_count.items()
        ]

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BOM产业链选股系统 - 监控面板</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        .header {{
            background: white; border-radius: 12px; padding: 24px;
            margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        .header h1 {{ color: #2c3e50; font-size: 28px; margin-bottom: 8px; }}
        .header p {{ color: #7f8c8d; font-size: 14px; }}
        .strategy-badge {{
            display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; padding: 8px 16px; border-radius: 20px;
            font-size: 13px; margin-top: 10px;
        }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{
            background: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{ color: #2c3e50; font-size: 16px; margin-bottom: 15px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
        .metric-value {{ font-size: 36px; font-weight: bold; margin: 10px 0; }}
        .metric-barrier .metric-value {{ color: #e74c3c; }}
        .metric-growth .metric-value {{ color: #27ae60; }}
        .metric-profit .metric-value {{ color: #f39c12; }}
        .metric-supply .metric-value {{ color: #9b59b6; }}
        .metric-total .metric-value {{ color: #2980b9; font-size: 42px; }}
        .metric-desc {{ color: #7f8c8d; font-size: 12px; margin-top: 5px; }}
        .table-container {{
            background: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th {{ background: #f8f9fa; padding: 12px 10px; text-align: left; color: #2c3e50;
            border-bottom: 2px solid #e0e0e0; font-weight: 600; }}
        td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
        .stock-row:hover {{ background: #f8f9fa; }}
        .rank {{ font-weight: bold; color: #2980b9; font-size: 16px; }}
        .name {{ font-weight: 600; color: #2c3e50; font-size: 14px; }}
        .code {{ color: #7f8c8d; font-family: monospace; }}
        .node {{ color: #34495e; }}
        .category, .level {{ color: #95a5a6; font-size: 12px; }}
        .score-barrier {{ color: #e74c3c; font-weight: 600; }}
        .score-growth {{ color: #27ae60; font-weight: 600; }}
        .score-profit {{ color: #f39c12; font-weight: 600; }}
        .score-sd {{ color: #9b59b6; font-weight: 600; }}
        .score-total {{ color: #2980b9; font-weight: bold; background: #ecf0f1; border-radius: 4px; padding: 4px 8px; }}
        .reason {{ color: #7f8c8d; font-size: 11px; }}
        .chart-section {{
            background: white; border-radius: 12px; padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-top: 20px;
        }}
        .chart-section h3 {{ color: #2c3e50; font-size: 18px; margin-bottom: 20px; }}
        canvas {{ max-width: 100%; margin-bottom: 20px; }}
        .methodology {{
            background: linear-gradient(135deg, #f39c12 0%, #e74c3c 100%);
            color: white; border-radius: 12px; padding: 24px; margin-top: 20px;
        }}
        .methodology h3 {{ font-size: 18px; margin-bottom: 15px; }}
        .methodology li {{ margin: 8px 0; line-height: 1.6; }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 BOM产业链选股系统 - 监控面板</h1>
            <p>通过产业链拆解(BOM) + 三高筛选(高壁垒·高增长·高利润·供需失衡)的科学选股方法</p>
            <span class="strategy-badge">⏰ 生成时间: {timestamp}</span>
            <span class="strategy-badge" style="margin-left:10px;">🎯 选出 {len(results)} 只股票</span>
        </div>

        <div class="grid-container">
            <div class="metric-card metric-barrier">
                <h3>🛡️ 高壁垒评分</h3>
                <div class="metric-value">{sum(r.barrier_score for r in results[:10])/10:.1f}</div>
                <div class="metric-desc">技术壁垒·专利壁垒·资源壁垒</div>
            </div>
            <div class="metric-card metric-growth">
                <h3>📈 高增长评分</h3>
                <div class="metric-value">{sum(r.growth_score for r in results[:10])/10:.1f}</div>
                <div class="metric-desc">行业增长·企业增速·市场空间</div>
            </div>
            <div class="metric-card metric-profit">
                <h3>💰 高利润评分</h3>
                <div class="metric-value">{sum(r.profit_score for r in results[:10])/10:.1f}</div>
                <div class="metric-desc">市场份额·龙头地位·利润空间</div>
            </div>
            <div class="metric-card metric-supply">
                <h3>⚖️ 供需失衡评分</h3>
                <div class="metric-value">{sum(r.supply_demand_score for r in results[:10])/10:.1f}</div>
                <div class="metric-desc">国产替代·供需紧张·定价权</div>
            </div>
            <div class="metric-card metric-total">
                <h3>🏆 综合评分</h3>
                <div class="metric-value">{sum(r.total_score for r in results[:10])/10:.1f}</div>
                <div class="metric-desc">四维度加权综合评估</div>
            </div>
        </div>

        <div class="table-container">
            <h3 style="color:#2c3e50;font-size:18px;margin-bottom:20px;">📊 选股详情表</h3>
            <table>
                <thead>
                    <tr>
                        <th>排名</th><th>名称</th><th>代码</th><th>产业链环节</th>
                        <th>行业</th><th>层级</th><th>壁垒</th><th>增长</th>
                        <th>利润</th><th>供需</th><th>总分</th><th>现价</th>
                        <th>涨跌</th><th>PE</th><th>市值</th><th>选股理由</th>
                    </tr>
                </thead>
                <tbody>{stock_rows}</tbody>
            </table>
        </div>

        <div class="chart-section">
            <h3>📈 四维评分雷达图 (TOP 10)</h3>
            <canvas id="radarChart" height="120"></canvas>

            <h3>🏭 行业分布图</h3>
            <canvas id="pieChart" height="120"></canvas>
        </div>

        <div class="methodology">
            <h3>🧭 选股方法论</h3>
            <ul>
                <li><strong>BOM产业链拆解:</strong> 将半导体、新能源、医药等行业按上游/中游/下游拆解，识别关键环节</li>
                <li><strong>高壁垒筛选:</strong> 识别技术、专利、资源壁垒高的环节，优先选择难以替代的核心节点</li>
                <li><strong>高增长筛选:</strong> 评估行业增长空间、政策支持、市场规模扩张潜力</li>
                <li><strong>高利润筛选:</strong> 评估龙头企业市场份额、毛利率、净利润率及利润弹性</li>
                <li><strong>供需失衡分析:</strong> 寻找"需求扩张 × 供给受限"的环节，优先国产替代空间大的领域</li>
                <li><strong>龙头识别:</strong> 在三高环节中选择全球/国内市场份额领先的企业</li>
            </ul>
        </div>
    </div>

    <script>
        const scoreData = {json.dumps(score_data, ensure_ascii=False)};
        const categoryData = {json.dumps(category_data, ensure_ascii=False)};

        // 雷达图
        const avgBarrier = scoreData.reduce((s, d) => s + d.barrier, 0) / scoreData.length;
        const avgGrowth = scoreData.reduce((s, d) => s + d.growth, 0) / scoreData.length;
        const avgProfit = scoreData.reduce((s, d) => s + d.profit, 0) / scoreData.length;
        const avgSupply = scoreData.reduce((s, d) => s + d.supply, 0) / scoreData.length;

        new Chart(document.getElementById('radarChart'), {{
            type: 'radar',
            data: {{
                labels: ['高壁垒', '高增长', '高利润', '供需失衡'],
                datasets: [{{
                    label: 'TOP 10 平均',
                    data: [avgBarrier, avgGrowth, avgProfit, avgSupply],
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: '#667eea',
                    borderWidth: 3,
                    pointBackgroundColor: '#764ba2',
                    pointBorderColor: '#fff',
                    pointRadius: 6,
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{ beginAtZero: true, max: 100 }}
                }}
            }}
        }});

        // 饼图
        new Chart(document.getElementById('pieChart'), {{
            type: 'doughnut',
            data: {{
                labels: categoryData.map(d => d.name),
                datasets: [{{
                    data: categoryData.map(d => d.count),
                    backgroundColor: ['#667eea', '#764ba2', '#2980b9', '#27ae60', '#f39c12', '#e74c3c'],
                }}]
            }},
            options: {{ responsive: true }}
        }});
    </script>
</body>
</html>
"""

        # 保存HTML
        dashboard_path = PROJECT_DIR / "bom_dashboard.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"\n💾 可视化面板已生成: {dashboard_path}")
        print(f"💡 请在浏览器中打开: file://{dashboard_path}")

        return str(dashboard_path)

    # ============= 完整工作流 =============

    def run_full_workflow(self):
        """执行完整工作流: 选股→监测→回测→可视化"""
        print("\n" + "="*80)
        print("🚀 BOM产业链选股系统 - 完整自动工作流")
        print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Step 1: 选股
        print("\n\n[1/4] 执行三高环节选股...")
        results = self.run_stock_selection(top_n=20)

        # Step 2: 监测
        print("\n\n[2/4] 执行每日涨幅监测...")
        self.run_monitoring()

        # Step 3: 回测 (可选)
        print("\n\n[3/4] 执行策略回测验证...")
        self.run_backtest()

        # Step 4: 可视化
        print("\n\n[4/4] 生成可视化监控面板...")
        dashboard_path = self.generate_dashboard(results)

        print("\n" + "✅"*40)
        print("✅ 完整工作流执行完成！")
        print("✅"*40)
        print(f"\n📊 输出文件:")
        print(f"   - 选股结果: ./bom_stock_data/")
        print(f"   - 可视化面板: {dashboard_path}")
        print(f"   - 回测数据: ./bom_backtest_data/")


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "all"

    print("🏭"*40)
    print("🏭 BOM产业链自动选股系统")
    print("🏭 基于产业链拆解+三高筛选的科学选股方法")
    print("🏭"*40)

    system = BOMStockSystem()

    if mode == "screen":
        system.run_stock_selection(top_n=20)
    elif mode == "monitor":
        system.run_monitoring()
    elif mode == "backtest":
        system.run_backtest()
    elif mode == "dashboard":
        system.generate_dashboard()
    else:  # all
        system.run_full_workflow()


if __name__ == "__main__":
    main()
