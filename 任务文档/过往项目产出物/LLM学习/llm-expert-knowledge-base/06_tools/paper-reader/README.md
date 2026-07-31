# 论文精读与复现Skill

## 概述

这是一个自动化论文精读与复现系统，专注于大模型领域的顶级学术论文，帮助您高效地筛选、精读、复现和沉淀前沿研究成果。

## 核心功能

### 1. 论文筛选
- 从过去7天采集的论文中筛选
- 优先顶级会议论文（ICML、NeurIPS、ICLR、ACL等）
- 优先顶级机构论文（OpenAI、Google DeepMind、Meta AI等）
- 优先有官方代码的论文
- 综合评分排序

### 2. 论文精读
- 自动获取论文详细信息（标题、作者、摘要等）
- 深度解读报告生成，包括：
  - 问题背景与研究动机
  - 核心贡献与创新点
  - 技术细节详解
  - 实验设计与结果分析
  - 优势与不足
  - 实际应用价值

### 3. 实验复现
- 自动克隆GitHub仓库
- 创建独立的Python虚拟环境
- 安装项目依赖
- 运行示例代码
- 复现核心实验
- 生成详细的复现报告

### 4. 知识整合
- 从论文解读中提取核心技术点
- 创建结构化的知识文档
- 建立双向链接
- 更新知识库索引

### 5. 周度报告
- 自动扫描本周精读的论文
- 生成周度研究报告
- 提供推送摘要

## 目录结构

```
paper-reader/
├── config/
│   └── config.json           # 配置文件
├── src/
│   ├── paper_filter.py      # 论文筛选模块
│   ├── paper_reader.py      # 论文精读模块
│   ├── paper_reproducer.py   # 实验复现模块
│   ├── knowledge_integrator.py  # 知识整合模块
│   └── weekly_reporter.py   # 周度报告模块
├── templates/
│   └── paper_analysis_template.md  # 论文解读模板
├── logs/
│   └── .gitkeep
└── README.md
```

## 安装依赖

```bash
pip install arxiv tqdm requests
```

## 使用方法

### 基本使用

```python
from paper_filter import PaperFilter
from paper_reader import PaperReader
from paper_reproducer import PaperReproducer
from knowledge_integrator import KnowledgeIntegrator
from weekly_reporter import WeeklyReporter

# 1. 论文筛选
filter_module = PaperFilter("config/config.json")
selected_papers = filter_module.run_weekly_selection()

# 2. 论文精读
reader = PaperReader("config/config.json")
analyses = reader.read_papers(selected_papers)

# 3. 实验复现
reproducer = PaperReproducer("config/config.json")
repro_result = reproducer.reproduce(paper_info)

# 4. 知识整合
integrator = KnowledgeIntegrator("config/config.json")
knowledge_files = integrator.integrate_knowledge(analysis, paper_file)

# 5. 周度报告
reporter = WeeklyReporter("config/config.json")
result = reporter.generate_weekly_report_all()
```

### 命令行使用

```bash
# 论文筛选
python3 src/paper_filter.py

# 周度报告
python3 src/weekly_reporter.py
```

## 配置说明

在 `config/config.json` 中可以配置：

- `filtering.weekly_paper_count`: 每周筛选论文数量（默认5篇）
- `filtering.top_conferences`: 顶级会议列表
- `filtering.top_institutions`: 顶级机构列表
- `reproduction.max_dataset_size_gb`: 最大数据集大小（默认10GB）
- `reproduction.timeout_minutes`: 超时时间（默认120分钟）

## 输出结果

### 论文解读报告
保存到 `05_papers/` 目录：
- 包含完整的论文解读内容
- 详细的实验分析
- 个人总结与评价

### 复现报告
- 环境配置信息
- 代码验证结果
- 实验复现过程
- 遇到的问题和解决方案

### 知识文档
保存到 `04_permanent/` 对应分类目录：
- 基础理论
- 模型架构
- 训练技术
- 推理优化
- 应用开发
- 部署工程
- 行业动态

### 周度报告
保存到 `05_papers/` 目录：
- 本周精读论文列表
- 主要技术进展
- 对领域发展的影响分析

## 质量控制

1. 论文解读必须准确反映原文内容
2. 技术细节必须准确无误
3. 实验复现必须如实记录
4. 评价必须客观中立
5. 所有引用必须注明来源

## 触发规则

### 1. 定时触发
- **时间**：每周六凌晨 1:00 自动执行
- **行为**：自动筛选过去7天内最有价值的3-5篇大模型论文进行精读
- **配置**：可在 `config/config.json` 中修改 `weekly_paper_count` 参数

### 2. 手动触发
- **指定论文链接**：`python3 src/main.py --manual --arxiv-url <链接>`
- **指定论文标题**：`python3 src/main.py --manual --paper-title <标题>`
- **指定数量**：`--count N`
- **设置优先级**：`--priority conference|institution|code|auto`

### 3. 错误处理
- 错误信息保存到 `../05_papers/error.log`
- 自动记录错误时间、错误信息和堆栈跟踪
- 命令行输出错误提示

### 4. 定时任务管理

使用任务调度器管理定时任务：

```bash
# 设置定时任务
python3 ../task_scheduler/src/paper_reader_scheduler.py --setup

# 查看任务状态
python3 ../task_scheduler/src/paper_reader_scheduler.py --status

# 移除定时任务
python3 ../task_scheduler/src/paper_reader_scheduler.py --remove

# 手动触发（通过调度器）
python3 ../task_scheduler/src/paper_reader_scheduler.py --manual --count 3
```

## 注意事项

1. 确保网络连接正常，能够访问arXiv和GitHub
2. 复现实验需要足够的磁盘空间和计算资源
3. 部分论文可能因为缺少代码或数据而无法复现
4. 建议定期运行周度报告，追踪学习进度

## 许可证

MIT License

## 作者

LLM学习项目组
