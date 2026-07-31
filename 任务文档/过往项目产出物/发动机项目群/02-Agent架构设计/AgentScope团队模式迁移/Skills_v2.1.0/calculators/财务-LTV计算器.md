# 财务-LTV计算器

## name
财务-LTV计算器

## description
计算SaaS企业单个客户的全生命周期价值（Lifetime Value），基于ARPU、毛利率和月流失率。适用于评估客户盈利能力、CAC/LTV比对、定价策略优化、获客渠道ROI分析。触发词：LTV、客户生命周期价值、Lifetime Value、用户终身价值、客户价值。排除词：CLV（Customer Lifetime Value，虽然同义但为避免冲突，CLV场景路由到电商-LTV计算器）、客户满意度、NPS。

## category
atomic-calculator

## sub_category
财务

## domain
SaaS财务指标

## formula_reference
concept_registry.SaaS.LTV

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| arpu | number | 每客户月均收入（Average Revenue Per User） | 100 |
| gross_margin | number | 毛利率（小数形式，如0.80表示80%） | 0.80 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| monthly_churn_rate | number | 月流失率（小数形式） | 按公司规模阶段性估算：初创期（A轮前）5-8%；成长期（A-B轮）3-5%；成熟期（C轮后/上市）1-3%。若用户提供具体数据则优先使用。注意：月流失率不可为0，若为0则LTV无穷大，需提示用户 |

## formula
LTV = arpu × gross_margin / monthly_churn_rate

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| ltv | number | 客户生命周期价值 |
| arpu | number | 回显每客户月均收入 |
| gross_margin | number | 回显毛利率 |
| monthly_churn_rate | number | 回显月流失率（若为LLM估值则标注） |
| avg_lifetime_months | number | 平均客户生命周期（月）= 1 / monthly_churn_rate |

## example
**输入：**
- ARPU：$100/月
- 毛利率：80%（0.80）
- 月流失率：成长期企业，LLM估值3%（0.03）

**计算过程：**
LTV = 100 × 0.80 / 0.03
    = 80 / 0.03
    = $2,666.67

平均客户生命周期 = 1 / 0.03 ≈ 33.3个月

**输出：**
- LTV：$2,666.67
- ARPU：$100/月
- 毛利率：80%
- 月流失率：3%（LLM估值，基于成长期企业）
- 平均客户生命周期：33.3个月

**解读：**
该客户在整个生命周期内预计贡献约$2,667的收入。若已知CAC（客户获取成本），可计算LTV/CAC比率。通常LTV/CAC > 3为健康，< 1为危险。