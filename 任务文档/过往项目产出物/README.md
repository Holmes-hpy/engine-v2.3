# 过往项目产出物

> 迁移时间：2026-07-31 10:59:29
> 迁移目的：将所有项目产出物统一管理，原始项目将删除

## 目录结构

```
过往项目产出物/
├── README.md                    # 本文件
├── 综合报告_trae_projects全量分析.md    # 全量项目分析报告
├── 发动机项目群/                  # V8、V8.1、V8.2 发动机项目合并
│   ├── 01-产品与业务分析/         # 沟通记录、产品工作梳理、功能清单
│   ├── 02-Agent架构设计/         # Agent-Skill拆分、元协议、元框架、深度学习
│   ├── 03-可研报告生成系统/       # 可研报告生成流水线（多版本）
│   ├── 04-团队管理/              # QBR、团队任务总结
│   ├── 05-申报与评审/            # 智能体操作系统申报、评审文档
│   ├── 06-平台发展规划/          # 发展规划、专利检索、调研对比
│   ├── 07-可视化与Demo/          # 前端原型、HTML制品、部署Demo
│   ├── 08-专家库/               # Agency Agents 专家库（V8.2最新版）
│   ├── 09-记忆系统/             # 决策记录、模式库、核心原则
│   └── 10-捡破烂/               # 对话记录归档
├── LLM学习/                      # LLM知识库与学习资料
│   ├── llm-expert-knowledge-base/    # 知识库（200+已处理资料）
│   ├── 05_papers/                    # 论文学术资料
│   ├── agent-platform-whitepaper/    # 智能体平台白皮书
│   └── 项目文档/                     # 弹药清单、核心规则
└── a-stock-data/                 # A股数据分析系统
    ├── core/                        # Python核心代码
    ├── knowledge/                   # 投资知识库
    ├── daily_tech_intel/           # 科技情报日报
    └── agents/                      # Agent定义
```

## 迁移规则

1. **合并原则**：发动机项目V8、V8.1、V8.2按主题合并，不再保留原始项目名称
2. **去重原则**：专家库、记忆系统等重复内容保留最新版本（V8.2）
3. **排除项**：.git、__pycache__、.DS_Store、.uploads、node_modules等已排除
4. **原始数据**：JSON原始数据、知识图谱数据等已排除（用户有原始存储）
5. **个人笔记**：保留在原始位置，未迁移

## 源项目

| 项目 | 路径 |
|------|------|
| V8发动机 | `/Users/houpengyuan/Documents/trae_projects/V8发动机/` |
| V8.1发动机 | `/Users/houpengyuan/Documents/trae_projects/0-A-V8.1发动机/` |
| V8.2发动机 | `/Users/houpengyuan/Documents/trae_projects/01-V8.2发动机/` |
| LLM学习 | `/Users/houpengyuan/Documents/trae_projects/LLM学习/` |
| a-stock-data | `/Users/houpengyuan/Documents/trae_projects/a-stock-data/` |
