# 财务-MRR计算器

## name
财务-MRR计算器

## description
计算SaaS企业的月度经常性收入（Monthly Recurring Revenue）。适用于SaaS订阅制企业的收入预测、增长分析和财务建模。触发词：MRR、月度经常性收入、月度订阅收入、Monthly Recurring Revenue、SaaS收入。排除词：ARR、年化收入、年度经常性收入、一次性收入、非订阅收入。

## category
atomic-calculator

## sub_category
财务

## domain
SaaS财务指标

## formula_reference
concept_registry.SaaS.MRR

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| paying_customers | number | 月付费客户数 | 500 |
| arpu | number | 每客户月均收入（Average Revenue Per User） | 100 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| industry_avg_mrr | number | 行业平均MRR | 按时规模估算：初创期（<1年）月MRR通常$5K-$50K；成长期（1-3年）$50K-$500K；成熟期（>3年）$500K以上。可根据客户数量和ARPU反推 |

## formula
MRR = paying_customers × arpu

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| mrr | number | 月度经常性收入（MRR） |
| paying_customers | number | 回显付费客户数 |
| arpu | number | 回显每客户月均收入 |

## example
**输入：**
- 月付费客户数：500
- ARPU：$100

**计算过程：**
MRR = 500 × 100 = $50,000

**输出：**
- MRR：$50,000
- 月付费客户数：500
- ARPU：$100