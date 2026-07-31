# 咨询-ESN利润计算器

## name
咨询-ESN利润计算器

## description
基于TJM brut（日费率），计算法国咨询行业三种企业形态（portage salarial、micro-entreprise、SASU）下的净收入和各项扣减，输出各路径的净收入对比，帮助独立咨询顾问选择最优企业形态。适用场景：法国独立咨询顾问企业形态选择、自由职业者收入规划、咨询行业税务优化。触发词：ESN利润、portage salarial、micro-entreprise、SASU、法国咨询、TJM brut。排除词：CDI、CDD、salariat。

## category
atomic-calculator

## sub_category
咨询

## domain
咨询

## formula_reference
concept_registry.咨询.ESN

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| TJM brut | float | 日费率（欧元，不含税） | 500 |
| 工作天数 | int | 年均实际工作天数 | 218 |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| 年假天数 | int | 带薪年假天数 | 默认25天（法国法定） |
| 公共假日 | int | 公共假日天数 | 默认10天（法国平均） |
| Portage管理费率 | float | Portage公司的管理费比例 | 默认8%，行业通常在5%-10% |
| 会计师费用 | float | 会计年费（欧元） | 默认2000欧元/年 |
| 职业保险 | float | 职业责任险年费（欧元） | 默认1500欧元/年 |
| 退休金 | float | 补充退休金年缴（欧元） | 默认3000欧元/年（仅SASU） |
| 运营费用 | float | 其他运营费用（欧元） | 默认3000欧元/年 |

## formula
年营业额 CA = TJM brut × 工作天数

Portage Salarial:
- 管理费 = CA × 管理费率
- 雇主社保分摊 = CA × 约42%
- 净收入 = CA - 管理费 - 雇主社保分摊 - 雇员社保分摊
- 等效净月薪 = 净收入 / 12

Micro-entreprise:
- 年营业额上限 = 77700 EUR（2026年服务类）
- 社保分摊 = CA × 22%（服务类）
- 所得税（若选prélèvement libératoire）= CA × 2.2%
- 净收入 = CA - 社保分摊 - 所得税
- 注意：若CA超过上限，则不能享受micro-entreprise优惠

SASU:
- 公司运营成本 = 会计师费 + 职业保险 + 退休金 + 运营费用
- 可税前扣除费用 = 公司运营成本
- 公司税 IS = (CA - 可扣除费用) × 15%（前42500 EUR）/ 25%（超出部分）
- 可分配利润 = CA - 可扣除费用 - IS
- 分红 = 可分配利润 × 分红比例
- 净收入 = 薪资 + 分红 - 个人所得税 - 社保分摊

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 年营业额 | float | 年总营业额（欧元） |
| Portage净收入 | float | Portage Salarial路径的年净收入 |
| Portage等效月薪 | float | Portage路径的等效月薪 |
| Micro净收入 | float | Micro-entreprise路径的年净收入 |
| Micro等效月薪 | float | Micro路径的等效月薪 |
| SASU净收入 | float | SASU路径的年净收入 |
| SASU等效月薪 | float | SASU路径的等效月薪 |
| 最优路径 | string | 净收入最高的企业形态 |
| 各路径对比表 | array[object] | 三种路径的详细对比 |
| 选择建议 | string | 基于净收入和具体情况的建议 |

## example
【输入】
TJM brut: 500 EUR
工作天数: 218天
Portage管理费率: 8%
会计师费用: 2000 EUR
职业保险: 1500 EUR
退休金: 3000 EUR
运营费用: 3000 EUR

【输出】
年营业额: 500 × 218 = 109000 EUR

Portage Salarial:
- 管理费: 109000 × 8% = 8720 EUR
- 净收入: 约46800 EUR/年
- 等效月薪: 约3900 EUR/月

Micro-entreprise:
- 社保分摊: 109000 × 22% = 23980 EUR
- 注意：CA=109000 > 77700上限，超额！不适用Micro-entreprise
- 结论: 此路径不可用

SASU:
- 公司运营成本: 2000 + 1500 + 3000 + 3000 = 9500 EUR
- 可分配利润: 约99500 - IS
- 净收入: 约52000-58000 EUR/年
- 等效月薪: 约4300-4800 EUR/月

最优路径: SASU（净收入最高）
选择建议: 由于TJM brut=500 EUR，年营业额109000 EUR超过Micro-entreprise上限，Micro路径不可用。SASU路径净收入最高，且有更多税务优化空间，但管理复杂度也更高。Portage是入门级选择，管理简单但有管理费支出。