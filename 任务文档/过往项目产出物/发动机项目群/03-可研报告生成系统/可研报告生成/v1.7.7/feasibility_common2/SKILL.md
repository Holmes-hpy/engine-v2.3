---
name: feasibility_common2
description: "可研报告团队通用质量规范，所有Worker必须遵循"
version: "1.1"
---

# 可研报告通用质量规范

## 1. 数据来源优先级（铁律）

优先级：U(用户上传材料) > M(MCP接口) > W(联网检索)

- 同一数据在多个来源中出现时，以高优先级来源为准
- U级来源的原始材料数据为基准，M级和W级仅用于补充
- 三级来源均无数据时，标记【待补充】，禁止编造
- 【注意】[U][M][W]是内部工作标记，仅用于信息表和团队内部沟通，严禁写入最终报告正文

## 2. 财务数据零容忍

所有财务数值禁止估算：
- 禁止用"约""大约""左右"修饰财务数据
- 禁止用历史数据推算预测数据（除非是材料中已有的预测）
- 无真实数据的财务字段必须标记【待补充】，不可以用0或近似值替代
- 财务比率必须基于原始数据计算，不可直接引用第三方比率

## 3. 输出格式规范

- 纯文本输出，禁止Markdown格式（#标题、**加粗、-列表等全部禁止）
- 章节标题格式：第X章 章节名称（全角空格分隔）
- 二级标题格式：X.X 二级标题名称（点号+全角空格）
- 三级标题格式：X.X.X 三级标题名称
- 表格格式：使用|分隔列，使用-分隔表头行，示例：
  | 列1 | 列2 | 列3 |
  |-----|-----|-----|
  | 数据 | 数据 | 数据 |
- 正文段落首行不缩进
- 段落之间空一行

## 4. 语言风格

- 使用正式、客观的书面语体
- 避免口语化表达（"咱们""其实""基本上"等）
- 避免主观评价（"非常好""极为出色"等），改为事实描述（"市场占有率达到XX%"）
- 禁止模糊词汇：可能、大概、或许、差不多、应该、也许、估计、预计、有望、约为、左右、以上以下（当表示不确定范围时）
- 模糊词替换规则：
  - "可能" → 删除或改为具体数据支撑
  - "预计""有望" → 改为"根据XX数据预测""按XX计划"
  - "约为""左右" → 改为精确数值或删除
  - "以上""以下" → 给出具体范围或精确值
- 数据引用必须带单位和具体数值，不使用模糊量词

## 5. 引用规范

- 引用政策文件时标注文号：《关于促进智能体产业发展的指导意见》（国发〔2025〕11号）
- 引用行业数据时标注来源机构和年份
- 禁止在正文中使用[U][M][W]来源标记——这些是内部工作标记，不得出现在最终报告的正文中
- 数据引用只写数值+单位，不需要标注来源类型（如：营业收入20,595.16万元，而非 营业收入20,595.16万元[U]）

## 6. MCP接口调用规范

### 6.1 调用原则
- 仅在信息表对应字段为空（用户材料中无法提取）时调用MCP接口补全
- MCP调用结果在信息表中标记来源为M（内部标记，不写入最终报告）
- MCP返回空结果时不标记blocked，而是标记【待补充】
- MCP接口不可用时不标记blocked，而是降级到联网检索[W]
- 优先使用MCP补全，其次联网检索，最后标注【待补充】

### 6.2 可用MCP接口清单（共6个服务器27个接口）

**通用工具server（3个接口）**：
- `search_company_id`：企业实体匹配，通过企业名称获得准确企业ID
- `search_industry_id`：产业匹配，获得产业及环节名称
- `search_region_id`：区域匹配，获得准确区域名称

**产业全景洞察server（6个接口）**：
- `get_industry_chain_graph`：产业链图谱，了解产业全景，快速定位环节优势企业
- `get_industry_tech_hotspots`：产业技术热点，获取产业链环节关键技术方向
- `get_industry_region_ranking`：产业区域发展排行榜，识别产业高地和潜力区域
- `get_industry_company_ranking`：产业企业竞争排行榜，快速锁定头部与潜力选手
- `query_understanding`：问题理解，将自然语言需求转为结构化输入
- `company_recall`：企业召回，根据维度权重召回企业名单

**产业分析指标server（3个接口）**：
- `get_industry_chain_structure_metrics`：产业链环节结构指标，量化产业链各环节现状
- `get_industry_region_structure_metrics`：产业区域结构指标，描绘产业空间格局
- `get_industry_listed_operation_metrics`：产业链上市企业运行指标，把脉产业真实运行状态

**知识产权server（1个接口）**：
- `get_company_ipr_assets`：知识产权资产，盘点企业知产家底，评估技术护城河

**企业关系网络server（2个接口）**：
- `get_company_shareholder_relations`：股东关系，穿透股权网络
- `get_company_innovation_relations`：创新协作关系，挖掘产学研合作网络

**企业动态追踪server（12个接口）**：
- `get_company_recruit_events`：招聘动态事件
- `get_company_investment_establishment_events`：投资设立动态事件
- `get_company_standard_draft_events`：标准参研动态事件
- `get_company_ipr_events`：知识产权动态事件
- `get_company_participating_events`：股权变更动态事件
- `get_company_innovation_platform_events`：创新平台动态事件
- `get_company_change_events`：工商变更动态事件
- `get_company_land_purchase_events`：购地动态事件
- `get_company_certification_events`：资质认定动态事件
- `get_company_bid_events`：中标动态事件
- `get_company_rank_events`：榜单收录动态事件
- `get_company_listing_events`：上市动态事件

### 6.3 各Parser推荐调用的MCP接口

**Parser-A（财务）**：MCP接口无直接财务数据接口，财务数据缺失时标注【待补充】或联网检索。

**Parser-B（工商股权）**：
- 企业基本信息缺失：先调用`search_company_id`匹配企业
- 股权结构/股东信息缺失：调用`get_company_shareholder_relations`
- 工商变更信息：调用`get_company_change_events`
- 融资/上市动态：调用`get_company_participating_events`、`get_company_listing_events`

**Parser-C1（宏观业务）**：
- 行业分析缺失：调用`get_industry_chain_graph`、`get_industry_chain_structure_metrics`、`get_industry_tech_hotspots`
- 竞争格局缺失：调用`get_industry_company_ranking`、`company_recall`
- 区域信息缺失：调用`search_region_id`、`get_industry_region_ranking`、`get_industry_region_structure_metrics`
- 可比公司缺失：调用`get_industry_company_ranking`、`get_industry_listed_operation_metrics`

**Parser-C2（技术产品）**：
- 知识产权缺失：调用`get_company_ipr_assets`、`get_company_ipr_events`
- 核心团队/组织架构缺失：MCP无直接接口，联网检索
- 业务数据缺失：调用`get_company_recruit_events`（招聘反映扩张）、`get_company_bid_events`（中标反映业务）
- 资质认证：调用`get_company_certification_events`、`get_company_innovation_platform_events`、`get_company_rank_events`

**Parser-D（项目说明）**：
- 项目相关政策：联网检索为主，MCP辅助产业分析
- 行业影响：调用`get_industry_chain_graph`、`get_industry_tech_hotspots`

## 7. 错误处理

- 文件格式无法解析 → TeamSay(kind='blocked', message='无法解析文件：{文件名}，格式：{格式}')
- 需要用户确认的关键信息 → TeamSay(kind='question', message='需要确认：{具体问题}')
- 发现材料中数据不一致 → 在信息表中标注冲突，附带两个来源的值
- 字数不达标 → 触发联网检索补充内容，仍不达标则在最终输出中标注字数不足

## 8. 反造假三条铁律（所有Writer必须遵守）

### 铁律1：数据来源强制标注
所有表格中的数据必须来自以下来源之一：
- 模块信息表中的数据 → 正常展示
- 财务计算结果.md中的数据 → 正常展示
- 无法从任何来源获取的数据 → 标注【待补充】
不得出现"来源不明"的精确数值。任何精确数值必须能追溯到模块信息表或财务计算结果.md。

### 铁律2：表格完整性检查
每个表格必须确保数据链条完整。如果表格中存在以下情况，则相关字段必须标注【待补充】：
- 中间项缺失但末项有数值（如利润表缺少管理费用但有净利润）
- 比率/百分比缺少分子或分母
- 合计项缺少组成部分
严禁在缺失中间项的情况下自行推算末项数值。严禁用固定比例倒推未知数据。

### 铁律3：禁止自行推算
以下行为严格禁止：
- 禁止用"营收×固定比例"推算费用、利润等数据
- 禁止用历史数据线性外推预测数据（除非材料中已有预测公式）
- 禁止用行业平均值替代企业具体数据
- 禁止在缺失数据时填充"合理估计值"
无数据就标注【待补充】，这是唯一允许的处理方式。

## 9. 数字使用规范（铁律）

所有数据中的数字必须使用阿拉伯数字（0-9），严禁将数字转换为中文汉字。

### 必须使用阿拉伯数字的场景：
- **日期**：2020年4月8日（严禁写为"二零二零年四月八日"）
- **统一社会信用代码/注册号/证件号**：91110108MA01QMKDR1（严禁写为"九一一一零一八MA零一QMKD三一"）
- **地址中的数字**：知春路23号10层1014室（严禁写为"二三号十层一零一四室"）
- **金额/注册资本**：6097.66万元（严禁写为"六千零九十七点六六万元"）
- **百分比/比率**：25.3%、3.5倍（严禁写为"百分之二十五点三""三点五倍"）
- **年龄/人数/数量**：150人、3个、5年（严禁写为"一百五十人""三个""五年"）
- **电话号码/传真/邮编**：全部使用阿拉伯数字
- **财务数据**：所有金额、比率、指标值全部使用阿拉伯数字
- **章节编号**：1.1、1.2、2.1（严禁写为"一点一""二点一"）
- **表格中的数据**：所有表格数据必须使用阿拉伯数字

### 唯一允许使用中文数字的场景：
- 章节标题中的"第X章"：第一章、第二章（使用中文数字"一、二、三..."）
- 惯用语中的数字：如"一把手""一方面"等成语和固定搭配

### 转换规则：
从原始材料中提取数据时，必须保持原始数字格式：
- 如果原始材料是阿拉伯数字，必须原样保留
- 如果原始材料是中文数字（如"贰零贰零年"），必须转换为阿拉伯数字
- 严禁将任何阿拉伯数字主动转换为中文数字
