# Serenity A股投资分析系统

基于紫苏叶理论的科技产业瓶颈投资分析系统，提供完整的六步漏斗式选股流程。

## ✨ 核心功能

### 瓶颈投资分析
- 八层逆向产业链深度拆解
- 物理四问硬性筛选（一票否决）
- 商业化落地验证（三级证据体系）
- 红队证伪与三维风险评估

### 实时监控
- 价格预警监控（红/黄预警阈值）
- 新闻公告监控
- 资金流向监控（北向资金、龙虎榜）

### 数据服务
- 实时行情获取
- 基本面数据采集
- 研报与新闻数据
- MCP协议支持

## 📁 项目结构

```
a-stock-data/
├── agents/                    # Agent提示词模板
│   ├── __init__.py
│   ├── serenity_chokepoint_agent.md
│   ├── knowledge_tagging_agent.md
│   ├── announcement_analyzer_agent.md
│   ├── risk_assessment_agent.md
│   ├── market_monitor_agent.md
│   └── data_fetcher_agent.md
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── stock_data.py          # A股数据核心模块
│   ├── chain_database.py      # 产业链数据库
│   ├── data_fetcher.py        # 真实数据接入
│   ├── risk_assessment.py     # 红队风险评估
│   ├── enhanced_analyzer.py   # 增强分析框架
│   ├── backtest_engine.py     # 回测引擎
│   ├── announcement_analyzer.py # 公告分析
│   └── mcp_server.py          # MCP服务入口
├── monitors/                  # 监控模块
│   ├── __init__.py
│   ├── monitor_engine.py      # 监控引擎
│   ├── bom_monitor.py         # BOM监控
│   ├── alert_check.py         # 预警检查
│   ├── run_monitor.py         # 监控运行器
│   └── run_daily_monitor.py   # 每日监控运行器
├── data/                      # 数据存储
│   ├── monitor/               # 监控数据
│   └── stock/                 # 股票数据
├── knowledge_graph/           # 知识图谱
│   ├── tagging_agent.py
│   ├── schema.py
│   └── ...
├── scripts/                   # 脚本工具
├── config/                    # 配置文件
├── README.md
├── USAGE_GUIDE.md
└── STOCK_SELECTION_GUIDE.md
```

## 🧠 Agent体系

| Agent名称 | 职责 | 核心能力 |
|-----------|------|----------|
| Serenity瓶颈投资分析专家 | 六步漏斗选股 | 产业链拆解、物理四问、投资决策 |
| 知识图谱打标专家 | 知识提取与构建 | 实体识别、关系抽取、图谱构建 |
| 公告深度解读专家 | 公告分析验证 | 证据评级、订单解析、认证验证 |
| 红队风险评估专家 | 证伪与风险评估 | 三维风险、概率评估、评级调整 |
| 市场实时监控专家 | 实时监控预警 | 价格监控、新闻监控、资金监控 |
| 数据采集专家 | 数据获取 | 行情、基本面、研报、新闻 |

## 🔧 快速开始

### 安装依赖

```bash
pip install requests pandas mootdx
```

### 基本使用

```python
# 导入核心模块
from core.stock_data import get_stock_quote, get_market_index
from core.chain_database import get_chain_database, list_all_tracks
from core.risk_assessment import get_redteam_assessor

# 获取股票行情
quote = get_stock_quote("600519")

# 获取产业链数据库
db = get_chain_database()
tracks = list_all_tracks()

# 获取风险评估器
assessor = get_redteam_assessor()
```

### MCP服务使用

直接在支持MCP的环境中使用，通过自然语言提问即可：

- "贵州茅台今天的股价和PE是多少？"
- "今天北向资金流入多少？"
- "比亚迪属于什么概念板块？"

## 📊 六步漏斗选股流程

1. **锚定确定性超级大趋势** - 验证资本开支计划、真实数据、趋势不可逆性
2. **八层逆向产业链深度拆解** - 从终端到原材料的完整拆解
3. **物理四问硬性筛选** - 物理必需、供给刚性、格局垄断、市场忽视
4. **商业化落地验证** - 强/中/弱三级证据体系
5. **红队证伪与风险评估** - 技术替代、供给突破、需求不及预期
6. **投资决策输出** - 评级、预期收益、仓位建议

## ⚠️ 重要说明

- 数据仅供参考，不构成投资建议
- A股交易时间：周一至周五 9:30-11:30, 13:00-15:00
- 部分API有调用频率限制，请合理使用

## 📝 许可证

本项目仅供学习交流使用。

---

**免责声明：投资有风险，入市需谨慎！**