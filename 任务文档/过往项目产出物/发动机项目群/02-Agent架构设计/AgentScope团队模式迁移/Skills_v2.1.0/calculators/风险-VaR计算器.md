# 风险-VaR计算器

## name
风险-VaR计算器

## description
计算投资组合在给定置信水平和持有期内的最大可能损失（Value at Risk）。VaR是金融风险管理中最常用的风险度量指标之一，回答"在正常市场条件下，投资组合在特定时间段内最多可能亏损多少"这一核心问题。适用于银行资本充足率计算、基金风险限额管理、交易策略风险控制等场景。触发词：VaR、在险价值、风险价值、最大损失、置信水平、巴塞尔协议。排除词：CVaR、条件风险价值、预期损失ES。

## category
atomic-calculator

## sub_category
风险

## domain
金融风险管理

## formula_reference
concept_registry.风险.VaR

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| returns | array[float] | 投资组合的日/周/月收益率序列 | [0.012, -0.008, 0.005, -0.015, 0.022, ...] |
| confidence_level | float | 置信水平，取值范围0.95-0.999 | 0.95, 0.99, 0.999 |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| holding_period | int | 持有期天数 | 默认1天；若未指定则按日VaR计算，多日VaR需乘以sqrt(持有期) |
| method | string | 计算方法(parametric/historical/monte_carlo) | 默认使用parametric参数法；若收益率序列不满足正态分布则自动回退到historical历史模拟法 |
| portfolio_value | float | 投资组合当前市值 | 默认1000000（100万）；用于将百分比VaR转换为金额VaR |

## formula
VaR = μ + σ × Z_α

其中：
- μ: 收益率序列的均值
- σ: 收益率序列的标准差
- Z_α: 在给定置信水平α下的标准正态分布分位数
  - α=95% → Z_α = -1.645
  - α=99% → Z_α = -2.326
  - α=99.9% → Z_α = -3.090

多日VaR换算：VaR_N = VaR_1 × sqrt(N)

计算步骤：
1. 计算收益率均值 μ = mean(returns)
2. 计算收益率标准差 σ = std(returns)
3. 根据置信水平查表获取Z_α分位数
4. 计算日VaR = μ + σ × Z_α
5. 若持有期>1天，VaR_N = 日VaR × sqrt(holding_period)
6. 金额VaR = 百分比VaR × portfolio_value

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| var_percent | float | 百分比VaR（如0.05表示5%） |
| var_amount | float | 金额VaR |
| confidence_level | float | 使用的置信水平 |
| holding_period | int | 持有期天数 |
| method | string | 使用的计算方法 |
| interpretation | string | VaR结果解读 |

## example
**输入：**
```
returns: [0.012, -0.008, 0.005, -0.015, 0.022, -0.010, 0.018, -0.003, 0.008, -0.012]
confidence_level: 0.95
holding_period: 1
portfolio_value: 5000000
method: "parametric"
```

**计算过程：**
1. μ = mean([0.012, -0.008, 0.005, -0.015, 0.022, -0.010, 0.018, -0.003, 0.008, -0.012]) = 0.0017
2. σ = std([0.012, -0.008, 0.005, -0.015, 0.022, -0.010, 0.018, -0.003, 0.008, -0.012]) = 0.0133
3. 置信水平95% → Z_α = -1.645
4. 日VaR = 0.0017 + 0.0133 × (-1.645) = 0.0017 - 0.0219 = -0.0202
5. 持有期=1天，无需调整
6. 金额VaR = 0.0202 × 5,000,000 = 101,000

**输出：**
```
var_percent: 0.0202
var_amount: 101000
confidence_level: 0.95
holding_period: 1
method: "parametric"
interpretation: "在95%置信水平下，该投资组合在1天内最大损失不会超过2.02%（即101,000元），有5%的概率损失可能超过该值"
```