# 财务-现金流Runway计算器

## name
财务-现金流Runway计算器

## description
计算企业在当前烧钱速度下现金储备可维持的运营月数（Runway）。适用于创业公司现金流管理、融资时机判断、预算规划、财务预警。触发词：Runway、现金流跑道、现金流持续期、Cash Runway、烧钱速度、资金链、还能撑多久。排除词：投资回报期、回本周期、Payback Period。

## category
atomic-calculator

## sub_category
财务

## domain
财务指标

## formula_reference
concept_registry.财务.Runway

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| cash_balance | number | 当前现金余额（含现金及现金等价物） | 2000000 |
| monthly_net_burn | number | 月净烧钱率（月净现金流出 = 月支出 - 月收入，若月收入>支出则为负数表示现金流为正） | 150000 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| monthly_revenue | number | 月收入 | 若用户未提供月净烧钱率但提供了月收入和月支出，则LLM计算：月净烧钱率 = 月支出 - 月收入 |
| monthly_expense | number | 月支出 | 同上 |
| revenue_growth_rate | number | 月收入增长率 | 默认0%。若提供，则Runway需考虑收入增长对烧钱率的影响，按月动态计算 |
| safety_margin_months | number | 安全边际（月） | 默认3个月。建议Runway低于安全边际时启动融资，输出时给出预警 |

## formula
Runway（月） = cash_balance / monthly_net_burn

（注：若monthly_net_burn <= 0，则表示现金流为正，Runway为无限大，不需要额外融资。）

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| runway_months | number | 现金流可维持月数 |
| runway_years | number | 现金流可维持年数（= runway_months / 12） |
| cash_balance | number | 回显现金余额 |
| monthly_net_burn | number | 回显月净烧钱率 |
| survival_date | string | 预计资金耗尽日期（基于当前日期推算） |
| warning_level | string | 预警级别：green（>18个月）/ yellow（12-18个月）/ orange（6-12个月）/ red（<6个月） |

## example
**输入：**
- 现金余额：$2,000,000
- 月净烧钱率：$150,000

**计算过程：**
Runway = 2,000,000 / 150,000 = 13.3个月

**输出：**
- Runway：13.3个月
- Runway年数：1.1年
- 现金余额：$2,000,000
- 月净烧钱率：$150,000
- 预计资金耗尽日期：2027年9月（基于2026年7月计算）
- 预警级别：yellow（12-18个月，建议在未来6个月内启动融资）