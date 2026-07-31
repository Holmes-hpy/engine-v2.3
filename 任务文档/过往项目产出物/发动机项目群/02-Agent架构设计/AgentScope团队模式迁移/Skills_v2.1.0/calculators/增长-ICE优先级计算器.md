# 增长-ICE优先级计算器

## name
增长-ICE优先级计算器

## description
使用ICE模型（Impact影响力、Confidence信心度、Ease容易度）计算增长实验的优先级得分，输出排序结果，帮助增长团队快速决策实验执行顺序。适用场景：增长实验优先级排序、增长黑客策略、AB测试实验规划、增长机会评估。触发词：ICE、增长实验优先级、ICE模型、增长实验排序、growth experiment。排除词：RICE、产品优先级、RICE模型、产品backlog。

## category
atomic-calculator

## sub_category
增长

## domain
增长

## formula_reference
concept_registry.产品.ICE

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| 实验列表 | array[object] | 多个增长实验的ICE各维度打分 | [{name:"落地页A/B测试", impact:8, confidence:7, ease:9}] |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| 排序方式 | string | 排序方向 | 默认"降序"（ICE分数高→优先级高） |
| 输出数量 | int | 需要输出的Top N实验 | 默认全部，可按需截取 |
| 得分阈值 | float | 低于此分数的实验标记为暂缓 | 默认不设阈值 |
| 实验阶段 | string | 实验所处的阶段 | 默认"计划"，可选"计划"/"进行中"/"已完成" |

## formula
ICE Score = Impact × Confidence × Ease

Impact: 1-10分，表示实验成功对核心指标的影响程度
Confidence: 1-10分，表示对实验成功的信心程度
Ease: 1-10分，表示实验的执行容易程度（10分为最容易）

优先级等级:
- ICE ≥ 400: 高优先级（立即执行）
- 200 ≤ ICE < 400: 中优先级（本周执行）
- 100 ≤ ICE < 200: 低优先级（排期执行）
- ICE < 100: 暂缓

注意：ICE模型与RICE模型的核心区别在于：(1)ICE没有Reach（覆盖范围）维度，更聚焦于实验本身的效果；(2)ICE使用Ease（容易度，1-10分）替代RICE的Effort（人月），更适合快速评估和轻量级决策；(3)ICE是增长实验领域最常用的优先级模型，适合快速试错场景。

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| 排序结果 | array[object] | 按ICE分数降序的实验列表 |
| 各实验ICE分 | array[float] | 各实验的ICE分数 |
| 高优先级实验 | array[string] | ICE ≥ 400的实验 |
| 中优先级实验 | array[string] | 200 ≤ ICE < 400的实验 |
| 低优先级实验 | array[string] | 100 ≤ ICE < 200的实验 |
| 暂缓实验 | array[string] | ICE < 100的实验 |
| 实验规划建议 | string | 基于优先级排序的实验执行建议 |

## example
【输入】
实验列表: [
  {name:"落地页A/B测试", impact:8, confidence:7, ease:9},
  {name:"注册流程简化", impact:9, confidence:8, ease:5},
  {name:"推送文案优化", impact:5, confidence:9, ease:8},
  {name:"推荐算法升级", impact:10, confidence:6, ease:3}
]

【输出】
排序结果:
1. 落地页A/B测试 — ICE: 8×7×9 = 504 — 高优先级
2. 推送文案优化 — ICE: 5×9×8 = 360 — 中优先级
3. 注册流程简化 — ICE: 9×8×5 = 360 — 中优先级
4. 推荐算法升级 — ICE: 10×6×3 = 180 — 低优先级

实验规划建议: 落地页A/B测试以504分排名第一，兼具高影响力(8分)、高信心(7分)和高易行性(9分)，建议立即启动。推送文案优化和注册流程简化并列360分，但推送文案优化更容易执行(8分 vs 5分)，可优先安排。推荐算法升级虽然影响力最大(10分)，但执行难度高(3分)且信心不足(6分)，建议降低实验复杂度后再评估。