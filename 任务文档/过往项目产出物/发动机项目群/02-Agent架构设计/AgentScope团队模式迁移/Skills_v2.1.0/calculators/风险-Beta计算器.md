# 风险-Beta计算器

## name
风险-Beta计算器

## description
计算个股或投资组合相对于市场的系统性风险系数Beta。Beta衡量资产收益率对市场整体波动的敏感程度，Beta>1表示资产波动性高于市场，Beta<1表示低于市场。适用于投资组合风险评估、CAPM模型定价、对冲策略构建等场景。触发词：Beta、贝塔系数、系统性风险、CAPM、市场敏感度。排除词：Alpha、超额收益、夏普比率。

## category
atomic-calculator

## sub_category
风险

## domain
金融风险管理

## formula_reference
concept_registry.风险.Beta

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| individual_returns | array[float] | 个股或投资组合的日/周/月收益率序列 | [0.02, -0.01, 0.015, 0.03, -0.005, ...] |
| market_returns | array[float] | 对应时间段的市场基准指数收益率序列 | [0.015, -0.005, 0.01, 0.02, -0.008, ...] |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| time_period | string | 计算周期(daily/weekly/monthly) | 默认使用daily；若数据点为月度数据则自动设为monthly |
| lookback_days | int | 回看天数 | 默认取最近252个交易日（约1年）；若数据不足则取全部可用数据 |

## formula
Beta = Cov(R_i, R_m) / Var(R_m)

其中：
- Cov(R_i, R_m): 个股收益率与市场收益率之间的协方差
- Var(R_m): 市场收益率的方差
- R_i: 个股收益率序列
- R_m: 市场收益率序列

计算步骤：
1. 计算个股收益率序列的均值 μ_i = mean(R_i)
2. 计算市场收益率序列的均值 μ_m = mean(R_m)
3. 计算协方差 Cov(R_i, R_m) = Σ[(R_i - μ_i)(R_m - μ_m)] / (n - 1)
4. 计算市场方差 Var(R_m) = Σ[(R_m - μ_m)²] / (n - 1)
5. Beta = Cov(R_i, R_m) / Var(R_m)

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| beta | float | Beta系数值 |
| interpretation | string | Beta含义解读（防御型/中性/进攻型） |
| r_squared | float | 拟合优度R²，衡量Beta的可靠性 |
| standard_error | float | Beta的标准误差 |
| confidence_interval | array[float] | Beta的95%置信区间 |

## example
**输入：**
```
individual_returns: [0.020, -0.010, 0.015, 0.030, -0.005, 0.012, -0.018, 0.025, 0.008, -0.022]
market_returns:    [0.015, -0.005, 0.010, 0.020, -0.008, 0.008, -0.012, 0.018, 0.005, -0.015]
time_period: "daily"
```

**计算过程：**
1. μ_i = mean([0.020, -0.010, 0.015, 0.030, -0.005, 0.012, -0.018, 0.025, 0.008, -0.022]) = 0.0055
2. μ_m = mean([0.015, -0.005, 0.010, 0.020, -0.008, 0.008, -0.012, 0.018, 0.005, -0.015]) = 0.0036
3. Cov(R_i, R_m) = 0.000289
4. Var(R_m) = 0.000183
5. Beta = 0.000289 / 0.000183 = 1.579

**输出：**
```
beta: 1.579
interpretation: "进攻型资产——该股票波动性约为市场的1.58倍，市场上涨1%时该股票平均上涨约1.58%"
r_squared: 0.82
standard_error: 0.12
confidence_interval: [1.34, 1.82]
```