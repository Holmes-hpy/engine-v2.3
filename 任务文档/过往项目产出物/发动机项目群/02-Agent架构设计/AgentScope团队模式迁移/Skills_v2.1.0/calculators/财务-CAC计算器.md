# 财务-CAC计算器

## name
财务-CAC计算器

## description
计算SaaS企业获取单个新客户的成本（Customer Acquisition Cost）。适用于获客效率评估、营销预算分配、渠道ROI分析、LTV/CAC比对。触发词：CAC、客户获取成本、获客成本、Customer Acquisition Cost、营销获客成本。排除词：CPA（每次行动成本，路由到广告-CPA计算器）、CPC、CPM、广告投放成本。

## category
atomic-calculator

## sub_category
财务

## domain
SaaS财务指标

## formula_reference
concept_registry.SaaS.CAC

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| sales_marketing_expense | number | 销售和营销总费用（含人员薪酬、广告投放、工具软件、活动费用等） | 500000 |
| new_customers | number | 同期新获取的付费客户数 | 200 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| period | string | 费用统计周期 | 默认"月度"。若用户未说明，按月度计算。可选值：月度、季度、年度。若为季度或年度，需同步确认new_customers是否为同周期数据 |

## formula
CAC = sales_marketing_expense / new_customers

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| cac | number | 单个客户获取成本（CAC） |
| sales_marketing_expense | number | 回显销售营销总费用 |
| new_customers | number | 回显新获客户数 |
| period | string | 统计周期 |
| cac_payback_months | number | CAC回收期（月）= CAC / ARPU（若已知ARPU则计算） |

## example
**输入：**
- 销售营销总费用：$500,000/月
- 新获客户数：200个/月
- 周期：月度

**计算过程：**
CAC = 500,000 / 200 = $2,500

**输出：**
- CAC：$2,500
- 销售营销总费用：$500,000/月
- 新获客户数：200个/月
- 周期：月度

**解读：**
每个新客户的平均获取成本为$2,500。若ARPU为$100/月，则CAC回收期 = 2,500/100 = 25个月。建议结合LTV指标：LTV/CAC = 2666.67/2500 ≈ 1.07，略低于健康水平（>3），需要优化获客效率或提升客户价值。