# 知识索引

## 项目: V8发动机

本文件由启动包自动生成，用于快速定位认知闭环中的知识条目。

## 知识层级概览

| 层级 | 名称 | 条目数 |
|------|------|--------|
| 1 | 事实层 | - |
| 2 | 模式层 | - |
| 3 | 原则层 | - |
| 4 | 策略层 | - |
| 5 | 智慧层 | - |

## 核心概念索引

- [项目启动包](.memory/knowledge.db) — 可移植的项目初始化模板集合
- [认知闭环](.memory/knowledge.db) — 基于 Markdown+SQLite+FTS5 的本地知识管理系统
- [规则体系](.memory/knowledge.db) — 项目运行期的行为规范集合
- [专家库](.memory/knowledge.db) — 可复用的领域专家定义和工作流模板
- [任务状态管理](.memory/knowledge.db) — 基于状态机的任务生命周期管理

## 最近更新

- 2026-07-16 — 项目初始化完成，种子数据已填充

## 使用说明

使用 SQLite 查询知识库：

```bash
sqlite3 .memory/knowledge.db "SELECT name, type, layer FROM entities;"
```

使用 FTS5 全文搜索：

```bash
sqlite3 .memory/knowledge.db "SELECT * FROM fts_entities WHERE fts_entities MATCH '关键词';"
```
