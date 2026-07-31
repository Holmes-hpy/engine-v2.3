# 财务-NDR计算器

## name
财务-NDR计算器

## description
计算SaaS企业的净收入留存率（Net Dollar Retention），衡量现有客户群体的收入增长或收缩情况。适用于SaaS企业健康度评估、投资者尽调、客户成功团队KPI考核。触发词：NDR、净收入留存率、Net Dollar Retention、净留存率、收入留存、净金额留存。排除词：logo留存率、客户数留存、GRR（毛收入留存率）。

## category
atomic-calculator

## sub_category
财务

## domain
SaaS财务指标

## formula_reference
concept_registry.SaaS.NDR

## inputs
### 必填参数（用户必须提供）
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| beginning_arr | number | 期初ARR（即期初客户群体的年化收入） | 1000000 |
| expansion_arr | number | 扩张ARR（老客户升级/增购带来的新增ARR） | 150000 |
| contraction_arr | number | 收缩ARR（老客户降级/减购导致的ARR减少） | 30000 |
| churned_arr | number | 流失ARR（老客户流失导致的ARR减少） | 50000 |

### 可选参数（用户可提供，不提供则LLM估值）
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| 无 | — | — | 本计算器四个核心参数均为必填，无法估值。若用户缺少某参数，提示用户提供具体数据 |

## formula
NDR = (beginning_arr + expansion_arr - contraction_arr - churned_arr) / beginning_arr

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| ndr | number | 净收入留存率（通常以百分比表示，如1.07表示107%） |
| ndr_percentage | number | 净收入留存率（百分比格式） |
| beginning_arr | number | 回显期初ARR |
| net_change | number | 净变化额 = expansion_arr - contraction_arr - churned_arr |

## example
**输入：**
- 期初ARR：$1,000,000
- 扩张ARR：$150,000
- 收缩ARR：$30,000
- 流失ARR：$50,000

**计算过程：**
NDR = (1,000,000 + 150,000 - 30,000 - 50,000) / 1,000,000
    = 1,070,000 / 1,000,000
    = 1.07

**输出：**
- NDR：1.07
- NDR百分比：107%
- 期初ARR：$1,000,000
- 净变化额：$70,000（即老客户收入净增长$70,000）

**解读：**
NDR = 107% 表示老客户群体的收入不仅没有流失，反而净增长了7%，说明产品具有较强粘性和扩张能力，属于优秀SaaS公司的特征（通常NDR > 120%为卓越，>100%为健康，<100%需关注）。