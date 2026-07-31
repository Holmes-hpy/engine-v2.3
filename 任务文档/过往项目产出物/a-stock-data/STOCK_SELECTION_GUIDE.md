# 🎯 自主选股分析系统 - 使用说明

## 系统概述

这是一个**完全自主运行**的选股分析系统，每天自动：
1. 从候选股票池选择一只股票
2. 进行多维度技术分析
3. 预测次日走势
4. 记录结果并验证预测
5. 分析失败原因，持续优化策略
6. 评估准确度并追踪提升

## 系统架构

```
a-stock-data/
├── stock_selection_system.py       # 核心选股系统
├── autonomous_learning_system.py  # 自主学习系统
├── schedule_manager.py           # 定时任务管理
├── stock_selection_db/           # 选股数据库
│   ├── selection_history.json     # 选股历史记录
│   ├── analysis_records.json      # 分析记录
│   └── accuracy_stats.json        # 准确度统计
├── reports/                      # 报告目录
│   ├── 每日选股报告_YYYY-MM-DD.md # 每日选股报告
│   └── 选股分析_代码_YYYY-MM-DD.md # 单股分析报告
└── knowledge/                    # 知识库
    └── stock_selection_knowledge.md # 选股知识库
```

## 核心功能

### 1. 智能选股

**候选股票池**：10只优质A股（茅台、银行、新能源、医药等）

**选股策略**（加权评分）：

| 策略 | 权重 | 说明 |
|-----|------|------|
| 价值策略 | 30% | PE、PB、换手率等估值指标 |
| 动量策略 | 30% | 近期涨幅、均线排列、市场配合度 |
| 技术策略 | 40% | MACD、RSI、KDJ、布林带、成交量 |

**策略自适应**：
- 市场上涨时：增加动量和技术的权重
- 市场下跌时：增加价值策略的权重
- 震荡市：均衡配置

### 2. 技术分析

**分析维度**：
- 均线系统（MA5/10/20/60）
- MACD指标（DIF/DEA/柱状图）
- KDJ指标（K/D/J值）
- RSI指标（相对强弱）
- 布林带（位置/带宽）
- 成交量分析

**预测生成**：
基于综合评分，预测明日走势：
- 上涨（置信度：高/中）
- 震荡偏涨
- 震荡
- 震荡偏跌
- 下跌（置信度：高/中）

### 3. 结果验证与反思

**验证机制**：
- 次日收盘后自动验证预测是否正确
- 计算实际涨跌幅度
- 判断预测方向的准确性

**失败分析**：
- 深度分析失败原因
- 识别被忽视的风险因素
- 生成改进建议
- 自动更新到知识库

### 4. 准确度评估

**追踪指标**：
- 总预测次数
- 正确次数 / 错误次数
- 整体准确率
- 各策略准确率（价值/动量/技术）

**进化机制**：
- 记录成功案例，归纳成功因素
- 记录失败案例，分析失败原因
- 持续优化选股策略权重
- 每月生成准确度提升报告

## 快速开始

### 方式1：手动运行每日选股

```bash
cd /Users/houpengyuan/Documents/trae_projects/a-stock-data
python3 stock_selection_system.py
```

### 方式2：运行完整系统

```bash
# 选股系统
python3 stock_selection_system.py

# 自主学习系统
python3 autonomous_learning_system.py
```

### 方式3：验证昨日预测

```python
from stock_selection_system import StockSelectionSystem

system = StockSelectionSystem()

# 验证昨日选股的预测结果
result = system.verify_prediction('600036')  # 替换为昨日选中的股票代码

print(f"预测结果: {result['result']}")
print(f"实际涨跌: {result['actual_change_pct']:.2f}%")
```

## API 使用示例

```python
from stock_selection_system import StockSelectionSystem

# 初始化系统
system = StockSelectionSystem()

# 1. 运行完整每日选股流程
result = system.run_daily_cycle()

# 2. 获取准确度统计
stats = system.get_accuracy_stats()
print(f"当前准确率: {stats['accuracy_rate']:.2f}%")

# 3. 查看选股历史
history = system._load_history()
print(f"总选股次数: {len(history['selections'])}")

# 4. 查看成功/失败案例
analyses = system._load_analyses()
print(f"成功案例: {len(analyses['success_cases'])}")
print(f"失败案例: {len(analyses['failure_cases'])}")
```

## 定时任务配置

系统已配置自动执行定时任务：

| 任务 | 执行时间 | 说明 |
|------|---------|------|
| 每日选股 | 交易日 15:30 | 自动选股、分析、生成报告 |
| 验证预测 | 交易日 15:30 | 验证昨日预测是否正确 |

## 报告文件说明

### 每日选股报告
**位置**：[reports/每日选股报告_2026-05-21.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/reports/每日选股报告_2026-05-21.md)

**内容**：
- 今日选股信息
- 技术分析与预测
- 关键指标数据
- 风险提示
- 操作建议
- 准确度统计

### 单股分析报告
**位置**：[reports/选股分析_600036_2026-05-21.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/reports/选股分析_600036_2026-05-21.md)

**内容**：
- 详细技术指标
- 预测依据
- 关键发现
- 风险因素
- 支撑位与压力位
- 操作建议

## 数据库说明

### selection_history.json
```json
{
  "selections": [
    {
      "stock_code": "600036",
      "stock_name": "招商银行",
      "selection_date": "2026-05-21",
      "strategy": "value",
      "prediction": "震荡偏跌",
      "result": "correct/incorrect",
      "actual_change_pct": 1.23
    }
  ],
  "total_count": 10
}
```

### analysis_records.json
```json
{
  "analyses": [...],
  "success_cases": [...],  // 成功案例详情
  "failure_cases": [...]    // 失败案例详情及原因分析
}
```

### accuracy_stats.json
```json
{
  "total_predictions": 10,
  "correct_predictions": 6,
  "incorrect_predictions": 4,
  "accuracy_rate": 60.0,
  "strategy_accuracy": {
    "value": {"accuracy": 65.0, "total": 5},
    "momentum": {"accuracy": 55.0, "total": 5},
    "technical": {"accuracy": 60.0, "total": 5}
  }
}
```

## 选股知识库

**位置**：[knowledge/stock_selection_knowledge.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/knowledge/stock_selection_knowledge.md)

**内容**：
- 成功案例与成功因素
- 失败案例与失败原因
- 改进建议总结
- 策略优化方向

## 第一性原理的应用

本系统应用**第一性原理**进行选股：

### 传统思维 vs 第一性原理

| 传统思维 | 第一性原理 |
|---------|-----------|
| "这只股票涨了很多" | "为什么涨？基本面变了还是情绪炒作？" |
| "RSI超买了要跌" | "RSI只是现象，真正的原因是什么？" |
| "跟着北向资金买" | "北向资金的决策依据是什么？" |

### 选股决策流程

```
第一步：本质分析（最重要）
├── 这家公司创造现金流的能力如何？
├── 行业前景和竞争优势？
└── 当前估值合理吗？

第二步：技术验证
├── 趋势是否向上？
├── 动能是否强劲？
└── 风险是否可控？

第三步：时机选择
├── 当前是好时机吗？
├── 止损位在哪里？
└── 预期收益是多少？
```

## 准确度提升路径

### 第1阶段（准确率 40-50%）
- 基础技术指标评分
- 简单策略组合

### 第2阶段（准确率 50-60%）
- 加入市场环境判断
- 优化策略权重
- 风险因素识别

### 第3阶段（准确率 60-70%）
- 失败案例深度分析
- 策略持续优化
- 知识库积累

### 第4阶段（准确率 70%+）
- 多策略融合
- 机器学习辅助
- 完善知识图谱

## 注意事项

1. **数据延迟**：实时行情可能有1-5分钟延迟
2. **市场休市**：非交易日不执行选股任务
3. **风险控制**：系统仅供学习，实盘需谨慎
4. **知识积累**：系统会随时间不断学习和进化

## 系统文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 核心系统 | [stock_selection_system.py](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/stock_selection_system.py) | 选股系统主模块 |
| 数据库 | [stock_selection_db/](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/stock_selection_db/) | 数据存储目录 |
| 今日报告 | [每日选股报告_2026-05-21.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/reports/每日选股报告_2026-05-21.md) | 最新报告 |

---

*自主选股分析系统 v1.0 - 2026-05-21*
*基于第一性原理的智能选股系统*
