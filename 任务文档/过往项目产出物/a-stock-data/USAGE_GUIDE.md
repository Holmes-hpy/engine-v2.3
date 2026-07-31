# 🤖 自主学习系统 - 使用说明

## 系统概述

Trae自主学习系统是一个完整的A股投资学习与分析平台，能够自动进行每日学习、每周深度学习、维护知识库，并生成专业的分析报告。

## 系统架构

```
a-stock-data/
├── autonomous_learning_system.py    # 核心学习系统
├── schedule_manager.py              # 定时任务管理
├── a_stock_data_core.py             # 数据获取核心
├── knowledge/                       # 知识库目录
│   ├── market_knowledge.md          # 市场知识
│   ├── industry_knowledge.md        # 行业知识
│   ├── company_knowledge.md         # 公司知识
│   ├── investment_strategies.md     # 投资策略
│   └── mistake_log.md               # 错误日志
└── reports/                         # 报告目录
    ├── 每日市场学习简报_YYYY-MM-DD.md
    ├── 每周学习与投资报告_YYYY-MM-DD.md
    └── 投资顾问进化报告_YYYY-MM.md
```

## 核心功能

### 1. 每日学习流程

| 阶段 | 时间 | 功能 |
|------|------|------|
| 开盘前学习 | 9:00-9:30 | 隔夜行情、财经新闻、北向资金分析 |
| 盘中学习 | 9:30-15:00 | 实时监控、异常记录、资金流向 |
| 收盘后学习 | 15:00-15:30 | 完整复盘、涨跌分析、龙虎榜 |

### 2. 报告生成

| 报告类型 | 频率 | 内容 |
|---------|------|------|
| 每日市场学习简报 | 每个交易日 | 市场表现、知识点、明日展望 |
| 每周学习与投资报告 | 每周日 | 周度回顾、学习心得、下周建议 |
| 投资顾问进化报告 | 每月末 | 学习总结、案例分析、框架优化 |

### 3. 知识库自动维护

系统会自动维护5个知识库文件，并在学习过程中持续更新：

- **market_knowledge.md**: 市场规律、周期理论、投资哲学
- **industry_knowledge.md**: 行业特点、龙头公司、发展趋势
- **company_knowledge.md**: 重点公司分析、竞争优势
- **investment_strategies.md**: 验证过的投资策略
- **mistake_log.md**: 错误案例和原因总结

## 快速开始

### 方式1：立即运行每日学习

```bash
cd /Users/houpengyuan/Documents/trae_projects/a-stock-data
python3 autonomous_learning_system.py
```

### 方式2：使用管理工具

```bash
# 初始化配置
python3 schedule_manager.py init

# 查看定时任务
python3 schedule_manager.py show

# 测试并立即运行
python3 schedule_manager.py test --now
```

## API 使用示例

```python
from autonomous_learning_system import AutonomousLearningSystem

# 初始化系统
system = AutonomousLearningSystem()

# 运行完整每日学习流程
system.run_daily_learning_cycle()

# 生成每日简报
system.generate_daily_report()

# 每周深度学习
system.weekly_deep_learning()

# 月度进化报告
system.monthly_evolution_report()

# 添加新知识
system.add_knowledge('market', '新发现规律', '详细内容...')

# 记录错误
system.log_mistake('600584', '追高买入', '贪婪情绪', '设置价格区间')
```

## 定时任务配置

系统使用Cron表达式配置定时任务（需配合外部调度器如cron或launchd）：

| 任务 | Cron表达式 | 说明 |
|------|-----------|------|
| 每日学习 | `30 15 * * 1-5` | 每个交易日15:30 |
| 每周学习 | `0 20 * * 0` | 每周日20:00 |
| 月度报告 | `0 20 L * *` | 每月最后一天20:00 |

## 文件位置说明

| 文件 | 路径 | 说明 |
|------|------|------|
| 核心系统 | [autonomous_learning_system.py](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/autonomous_learning_system.py) | 主要功能模块 |
| 定时管理 | [schedule_manager.py](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/schedule_manager.py) | 任务管理工具 |
| 每日简报 | [reports/每日市场学习简报_2026-05-21.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/reports/每日市场学习简报_2026-05-21.md) | 最新报告 |
| 知识库 | [knowledge/](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/knowledge/) | 知识存储目录 |

## 下一步

1. ✅ 系统已部署并生成第一份简报
2. ⏰ 配置您的系统调度器（cron/launchd）
3. 📚 持续添加知识到知识库
4. 📊 定期查看生成的报告

## 注意事项

- 所有分析仅供参考，不构成投资建议
- 定时任务需要配置系统级调度器
- 知识库会随着学习自动更新
- 请定期备份重要报告

---

*自主学习系统 v1.0 - 2026-05-21*
