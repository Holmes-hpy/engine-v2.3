# 自定义工作流

> 在此目录下创建你的自定义工作流定义文件。

## 使用方式

1. 在 `workflows/` 下创建 `.yaml` 文件定义工作流
2. 参考 `expert-library/agency-orchestrator/` 中的格式
3. 工作流会在任务执行时自动匹配

## 示例

```yaml
name: 数据分析工作流
steps:
  - name: 数据采集
    agent: data-collector
  - name: 数据清洗
    agent: data-cleaner
  - name: 可视化
    agent: visualization-expert
```