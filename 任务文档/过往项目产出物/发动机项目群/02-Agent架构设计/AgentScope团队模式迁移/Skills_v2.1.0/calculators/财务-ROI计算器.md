# 财务-ROI计算器

## name
财务-ROI计算器

## description
计算单个项目或单项投资的回报率（Return on Investment），衡量投资效率。适用于项目投资决策、营销活动ROI、设备采购评估、单项投资回报分析。触发词：ROI、投资回报率、单项目、投资回报、Return on Investment、项目ROI。排除词：多项目、组合、IT项目、组合ROI、ROE、ROA、ROIC。

## category
atomic-calculator

## sub_category
财务

## domain
财务指标

## formula_reference
concept_registry.财务.ROI

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| net_return | number | 净收益（投资总收益 - 投资成本） | 150000 |
| investment_cost | number | 投资成本（总投资额） | 500000 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| investment_period | string | 投资周期 | 默认"total"（全周期）。若用户提供具体时间周期，则需标注ROI为对应周期的回报率。可选值：monthly（月度）/ annual（年度）/ total（全周期） |
| total_return | number | 投资总收益（含本金回收） | 若用户提供total_return而非net_return，则LLM计算：net_return = total_return - investment_cost |
| benchmark_roi | number | 基准ROI（如行业平均或无风险利率） | 默认无。可参考：无风险利率约3-5%（国债）；权益类投资期望ROI通常>8-10%；风险投资期望ROI>15-20%。用于对比参考 |

## formula
ROI = net_return / investment_cost

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| roi | number | 投资回报率（小数形式） |
| roi_percentage | number | 投资回报率（百分比形式） |
| net_return | number | 回显净收益 |
| investment_cost | number | 回显投资成本 |
| investment_period | string | 回显投资周期 |
| is_profitable | boolean | 是否盈利（ROI > 0） |
| payback_multiple | number | 回报倍数 = (net_return + investment_cost) / investment_cost |

## example
**输入：**
- 净收益：$150,000
- 投资成本：$500,000
- 投资周期：全周期

**计算过程：**
ROI = 150,000 / 500,000 = 0.30

回报倍数 = (150,000 + 500,000) / 500,000 = 1.30

**输出：**
- ROI：0.30
- ROI百分比：30%
- 净收益：$150,000
- 投资成本：$500,000
- 投资周期：全周期
- 是否盈利：是
- 回报倍数：1.30x（即每投入$1，收回$1.30）

**解读：**
ROI=30%、回报倍数1.30x，说明该投资在覆盖全部成本后还获得了30%的净回报。这个ROI水平需要结合投资周期来评价：如果是一年内的回报，30%相当不错；如果是5年期的总回报，年化ROI仅约5.4%，相对一般。建议将ROI与投资周期结合，计算年化ROI以便跨项目比较。

**年化ROI近似计算：**
若投资周期为3年，年化ROI ≈ (1 + 0.30)^(1/3) - 1 ≈ 9.14%