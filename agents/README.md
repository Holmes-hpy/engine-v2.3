# 自定义 Agent

> 在此目录下创建你的自定义 Agent 定义文件。

## 使用方式

1. 在 `agents/` 下创建 `.md` 文件定义 Agent
2. 参考 `expert-library/` 中的格式
3. Agent 会在任务执行时自动加载

## 示例

```markdown
# 我的数据分析师

- 角色：数据分析专家
- 技能：Python、Pandas、SQL
- 触发条件：用户提到"数据分析"、"图表"
```