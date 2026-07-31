# 产品-RICE优先级计算器

## name
产品-RICE优先级计算器

## description
使用RICE模型（Reach覆盖范围、Impact影响力、Confidence信心度、Effort投入成本）计算产品需求的优先级得分，输出排序结果，帮助产品团队进行需求优先级决策。适用场景：产品需求优先级排序、产品路线图规划、版本迭代计划、产品backlog管理。触发词：RICE、产品优先级、需求优先级、RICE模型、产品backlog排序。排除词：ICE、增长实验、ICE优先级、增长优先级。

## category
atomic-calculator

## sub_category
产品

## domain
产品

## formula_reference
concept_registry.产品.RICE

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| 需求列表 | array[object] | 多个需求的RICE各维度打分 | [{name:"用户注册优化", reach:8, impact:7, confidence:80, effort:2}] |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| 排序方式 | string | 排序方向 | 默认"降序"（RICE分数高→优先级高） |
| 输出数量 | int | 需要输出的Top N需求 | 默认全部，可按需截取 |
| 得分阈值 | float | 低于此分数的需求标记为暂缓 | 默认不设阈值 |
| 需求分类 | string | 是否按分类分组排序 | 默认"否"，需提供分类标签 |

## formula
RICE Score = (Reach × Impact × Confidence) / Effort

Reach: 1-10分，表示该需求在特定时间段内影响的用户数量级
Impact: 1-10分，表示对单个用户的影响程度
Confidence: 0-100%，表示对Reach和Impact评估的信心程度（如80%）
Effort: 以"人月"为单位，表示完成该需求所需的工作量

优先级等级:
- RICE ≥ 50: 高优先级（立即执行）
- 20 ≤ RICE < 50: 中优先级（下一迭代）
- RICE < 20: 低优先级（排期待定）

注意：RICE模型与ICE模型的主要区别在于：(1)RICE包含Reach（覆盖范围）维度，更关注用户规模；(2)RICE使用Effort（人月）替代Ease（容易度），更关注实际投入成本；(3)RICE更适合产品需求优先级排序，ICE更适合增长实验优先级排序。

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 排序结果 | array[object] | 按RICE分数降序的需求列表 |
| 各需求RICE分 | array[float] | 各需求的RICE分数 |
| 高优先级需求 | array[string] | RICE ≥ 50的需求 |
| 中优先级需求 | array[string] | 20 ≤ RICE < 50的需求 |
| 低优先级需求 | array[string] | RICE < 20的需求 |
| 版本规划建议 | string | 基于优先级排序的版本规划建议 |

## example
【输入】
需求列表: [
  {name:"用户注册优化", reach:8, impact:7, confidence:80, effort:2},
  {name:"支付流程改造", reach:6, impact:9, confidence:90, effort:3},
  {name:"暗黑模式", reach:4, impact:3, confidence:60, effort:4},
  {name:"搜索功能升级", reach:9, impact:8, confidence:70, effort:5}
]

【输出】
排序结果:
1. 用户注册优化 — RICE: (8×7×0.80)/2 = 22.4 — 中优先级
2. 支付流程改造 — RICE: (6×9×0.90)/3 = 16.2 — 低优先级
3. 搜索功能升级 — RICE: (9×8×0.70)/5 = 10.1 — 低优先级
4. 暗黑模式 — RICE: (4×3×0.60)/4 = 1.8 — 低优先级

版本规划建议: 当前所有需求RICE分均低于50，无高优先级需求。建议优先执行"用户注册优化"（RICE=22.4），其覆盖范围广(8分)、投入小(2人月)，性价比最高。支付流程改造虽然影响力大(9分)，但投入3人月拉低了得分。建议重新评估各需求打分，确保评分客观反映实际价值。