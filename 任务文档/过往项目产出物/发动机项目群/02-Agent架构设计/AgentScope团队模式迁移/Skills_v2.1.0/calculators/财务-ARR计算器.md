# 财务-ARR计算器

## name
财务-ARR计算器

## description
计算SaaS企业的年度经常性收入（Annual Recurring Revenue），基于MRR年化得出。适用于SaaS企业的年度收入预测、估值分析、对标准则。触发词：ARR、年度经常性收入、Annual Recurring Revenue、年化收入、SaaS年收入。排除词：MRR、月度、年度总收入（含一次性收入）、Non-recurring。

## category
atomic-calculator

## sub_category
财务

## domain
SaaS财务指标

## formula_reference
concept_registry.SaaS.ARR

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| mrr | number | 月度经常性收入（MRR），通常由财务-MRR计算器输出 | 50000 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| monthly_growth_rate | number | 月环比增长率 | 若用户未提供，默认按0%计算（即简化计算ARR = MRR × 12）。若已知月增长率，则需按复合增长年化：ARR = MRR × Σ(1+r)^(i-1), i=1..12 |

## formula
ARR = mrr × 12

（注：简化计算假设MRR在12个月内保持不变。若用户提供月增长率，则需使用复合年化公式：ARR = MRR × [(1+r)^12 - 1] / r，其中r为月环比增长率。）

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| arr | number | 年度经常性收入（ARR） |
| mrr | number | 回显月度经常性收入 |
| monthly_growth_rate | number | 回显月增长率（若估值则标注"LLM估值"） |

## example
**输入：**
- MRR：$50,000
- 月增长率：未提供（默认0%）

**计算过程：**
ARR = 50,000 × 12 = $600,000

**输出：**
- ARR：$600,000
- MRR：$50,000
- 月增长率：0%（默认简化计算）