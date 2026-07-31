---
name: SEO知识库
version: 2.0.0
category: D-知识库类
description: >-
  提供SEO优化知识查询，覆盖技术SEO、关键词研究、页面SEO优化、外链建设四大领域。
  做什么：按查询类型输出对应SEO知识，包含检查清单、最佳实践、工具推荐和分阶段实施路线图。
  适用于什么场景：网站SEO优化、内容策略制定、SEO技术审计、新站SEO规划、SEO团队培训。
  支持哪些参数：查询类型（technical/keyword/onpage/offpage/all）、网站类型（ecommerce/content/saas）、网站阶段（new/established/mature）、当前排名问题描述（可选）、目标关键词（可选）。
---

# SEO知识库

## 一、输入要求

| 参数名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| query_type | string | 查询类型，可选值：technical（技术SEO）、keyword（关键词研究）、onpage（页面SEO优化）、offpage（外链建设）、all（全部） | 是 |
| site_type | string | 网站类型，可选值：ecommerce（电商）、content（内容站）、saas（SaaS） | 是 |
| site_stage | string | 网站阶段，可选值：new（新站，<6个月）、established（已建立，6-24个月）、mature（成熟站，>24个月） | 否 |
| target_keywords | string | 目标关键词，逗号分隔，用于关键词研究和页面优化建议 | 否 |
| competitor_url | string | 竞品网站URL，用于内容缺口分析 | 否 |
| current_ranking | string | 当前排名问题描述，如：核心词排名第2页、长尾词无排名、流量下降等 | 否 |
| cms | string | 使用的CMS/技术栈，可选值：WordPress、Shopify、Webflow、Custom（自建）、Other | 否 |

## 二、执行逻辑

### 步骤1：识别查询类型并路由到对应知识模块

根据 `query_type` 参数，确定输出范围：

| 查询类型 | 覆盖模块 | 输出重点 |
|----------|----------|----------|
| technical | 技术SEO | 抓取索引、网站速度、Core Web Vitals、结构化数据、移动端优化、HTTPS安全 |
| keyword | 关键词研究 | 主题集群、支柱页面、支撑内容、内容缺口、搜索意图映射 |
| onpage | 页面SEO | Meta标签、内容结构、Schema标记、图片优化、内部链接 |
| offpage | 外链建设 | 数字公关、内容驱动外链、策略性外联、链接审计 |
| all | 全部模块 | 综合SEO审计报告 |

### 步骤2：输出对应知识模块

#### 2.1 技术SEO（Technical SEO）

**2.1.1 抓取与索引（Crawlability & Indexability）**

| 检查项 | 说明 | 工具/方法 | 优先级 |
|--------|------|----------|--------|
| robots.txt | 检查是否误屏蔽重要页面 | Google Search Console > robots.txt测试工具 | 高 |
| XML Sitemap | 确保sitemap包含所有重要页面，已提交至GSC | Google Search Console > Sitemaps | 高 |
| 孤立页面 | 检查是否有页面无任何内部链接指向 | Screaming Frog / Sitebulb | 中 |
| 重复内容 | 检查canonical标签是否正确设置 | Screaming Frog > Canonicals | 中 |
| 404页面 | 检查死链数量和影响 | Google Search Console > Coverage | 中 |
| 分页处理 | 检查分页是否使用正确的rel="prev/next"或规范处理 | 手动检查+抓取工具 | 低 |
| JavaScript渲染 | 确保JS渲染的内容能被Google抓取 | Google Search Console > URL Inspection > 渲染截图 | 高（SPA站点） |

**robots.txt最佳实践**：
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /cart/
Disallow: /checkout/
Disallow: /*?*  # 阻止带参数的URL（需根据实际情况调整）

Sitemap: https://www.example.com/sitemap.xml
```

**2.1.2 Core Web Vitals（核心网页指标）**

| 指标 | 优秀 | 需改进 | 差 | 测量工具 |
|------|------|--------|-----|----------|
| LCP（最大内容绘制） | ≤2.5秒 | ≤4.0秒 | >4.0秒 | PageSpeed Insights / Lighthouse |
| INP（交互到下次绘制） | ≤200ms | ≤500ms | >500ms | PageSpeed Insights / CrUX |
| CLS（累积布局偏移） | ≤0.1 | ≤0.25 | >0.25 | PageSpeed Insights / Lighthouse |

**Core Web Vitals优化清单**：

```
LCP优化：
  □ 使用CDN加速静态资源
  □ 图片转WebP/AVIF格式，使用响应式图片
  □ 关键CSS内联，非关键CSS延迟加载
  □ 服务器响应时间（TTFB）< 800ms
  □ 预加载LCP资源：<link rel="preload" as="image" href="hero.webp">

INP优化：
  □ 拆分长任务（Long Tasks > 50ms）
  □ 使用Web Worker处理密集计算
  □ 防抖/节流高频事件（scroll, resize）
  □ 延迟加载非关键JS：<script defer>

CLS优化：
  □ 所有图片/视频/广告位设置明确的width和height
  □ 动态注入内容使用占位符预留空间
  □ Web字体使用font-display: swap，避免FOIT
  □ 避免在已有内容上方插入新内容（除非用户交互触发）
```

**2.1.3 结构化数据（Structured Data）**

按 `site_type` 推荐Schema标记：

| 网站类型 | 必须标记 | 推荐标记 | 格式 |
|----------|----------|----------|------|
| 电商 | Product, Offer, AggregateRating | BreadcrumbList, Organization, Review | JSON-LD |
| 内容站 | Article, BreadcrumbList, Organization | FAQ, HowTo, Author | JSON-LD |
| SaaS | Organization, SoftwareApplication | FAQ, BreadcrumbList, WebSite | JSON-LD |

**电商Product Schema示例**：
```json
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "name": "产品名称",
  "image": "https://example.com/product.jpg",
  "description": "产品描述",
  "sku": "SKU-001",
  "brand": {
    "@type": "Brand",
    "name": "品牌名"
  },
  "offers": {
    "@type": "Offer",
    "url": "https://example.com/product",
    "priceCurrency": "CNY",
    "price": "299.00",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "128"
  }
}
```

**2.1.4 移动端优化（Mobile Optimization）**

| 检查项 | 标准 | 工具 |
|--------|------|------|
| 移动友好测试 | Google Mobile-Friendly Test 通过 | Google Mobile-Friendly Test |
| 响应式设计 | 所有页面在320px-1920px宽度下正常显示 | 浏览器开发者工具 |
| 触摸目标 | 按钮/链接最小48×48px，间距≥8px | 手动检查 |
| 字体大小 | 正文≥16px，不需要缩放即可阅读 | 手动检查 |
| 弹窗 | 无侵入式插页广告（Intrusive Interstitials） | Google Search Console |
| 移动页速 | 3G网络下LCP≤3秒 | PageSpeed Insights（移动端） |

**2.1.5 技术SEO分阶段实施路线图**

根据 `site_stage` 输出优先级：

```
新站（<6个月）：
  第1周：配置robots.txt + 提交XML Sitemap到GSC
  第2周：配置HTTPS + 设置301重定向（如有旧站）
  第3周：安装结构化数据 + 配置canonical标签
  第4周：配置CDN + 图片优化

已建立站（6-24个月）：
  第1周：Core Web Vitals审计 + 修复LCP
  第2周：修复抓取错误（GSC Coverage报告）
  第3周：修复INP + CLS
  第4周：移动端体验优化 + 结构化数据增强

成熟站（>24个月）：
  按月：监控Core Web Vitals趋势
  按季：全面技术审计 + 页面速度优化
  按年：技术栈升级评估 + 国际化SEO（如适用）
```

#### 2.2 关键词研究（Keyword Research）

**2.2.1 主题集群模型（Topic Cluster Model）**

```
主题集群结构：

【支柱页面（Pillar Page）】
  核心主题的权威长文（3000-5000字）
  覆盖该主题的所有核心子话题

├── 【支撑内容1（Cluster Content）】
│   针对一个具体子话题的深度文章（1500-2500字）
│   链接回支柱页面
│
├── 【支撑内容2（Cluster Content）】
│   针对另一个具体子话题的深度文章
│   链接回支柱页面
│
└── 【支撑内容N（Cluster Content）】
    更多子话题文章
    链接回支柱页面

内部链接策略：
  支柱页面 ← 所有支撑内容都链接回支柱页面
  支撑内容 ← 支柱页面链接到所有支撑内容
  支撑内容 ↔ 相关支撑内容之间互相链接
```

**按网站类型定制的主题集群示例**：

电商站（以"跑鞋"为例）：
```
【支柱页面】跑鞋选购终极指南（2026版）
  ├── 支撑内容：扁平足跑鞋推荐（10款实测）
  ├── 支撑内容：马拉松训练用什么跑鞋（按配速分类）
  ├── 支撑内容：跑鞋寿命多久？5个更换信号
  ├── 支撑内容：碳板跑鞋 vs 普通跑鞋（实测对比）
  └── 支撑内容：宽脚掌跑鞋品牌推荐（含尺码对照表）
```

内容站（以"时间管理"为例）：
```
【支柱页面】时间管理：从入门到精通的完整指南
  ├── 支撑内容：番茄工作法实测（30天记录）
  ├── 支撑内容：GTD方法详解（含Notion模板）
  ├── 支撑内容：时间管理App横评（2026年10款）
  ├── 支撑内容：ADHD人群的时间管理策略
  └── 支撑内容：管理者的时间管理（带团队如何不加班）
```

SaaS站（以"项目管理工具"为例）：
```
【支柱页面】项目管理工具选购指南（2026年对比）
  ├── 支撑内容：敏捷开发 vs 瀑布开发（选工具前必读）
  ├── 支撑内容：小团队项目管理工具推荐（10人以下）
  ├── 支撑内容：远程团队如何用项目管理工具提升协作
  ├── 支撑内容：项目管理工具ROI计算（量化省钱公式）
  └── 支撑内容：Jira替代品测评（2026年5款）
```

**2.2.2 搜索意图映射（Search Intent Mapping）**

| 意图类型 | 典型查询词 | 最佳内容形式 | 页面类型 |
|----------|-----------|-------------|---------|
| 信息型 | "是什么"、"怎么"、"教程"、"指南" | 深度文章、视频教程、信息图 | 博客文章/知识库 |
| 导航型 | 品牌名、产品名 | 首页/产品页 + 站内搜索 | 首页/落地页 |
| 商业型 | "最好"、"推荐"、"对比"、"评测" | 对比表格、评测文章、买家指南 | 对比页/列表页 |
| 交易型 | "购买"、"价格"、"优惠"、"注册" | 产品页 + 优惠信息 + CTA | 产品页/定价页 |

**关键词卡片模板**：

```
关键词：[关键词]
搜索量：[月搜索量]
搜索意图：[信息型/导航型/商业型/交易型]
难度：[低/中/高]
当前排名：[排名/未收录]
优先级别：[P0/P1/P2/P3]

推荐内容形式：[文章/视频/对比页/产品页]
推荐标题：[标题建议]
推荐内容大纲：
  1. [大纲要点1]
  2. [大纲要点2]
  3. [大纲要点3]
竞品表现：[竞品URL] 排名第[X]位，内容形式为[文章/视频/...]
内容缺口：[我们缺少而竞品有的内容]
```

**2.2.3 内容缺口分析（Content Gap Analysis）**

如果提供了 `competitor_url`，执行内容缺口分析：

```
步骤1：收集竞品已排名关键词
步骤2：收集我方已排名关键词
步骤3：计算缺口 = 竞品关键词 - 我方关键词
步骤4：按搜索量/难度/相关性排序
步骤5：输出Top 10内容缺口清单
```

#### 2.3 页面SEO优化（On-Page SEO）

**2.3.1 页面SEO检查清单**

```
【Meta标签】
□ Title标签：40-60字符，包含主关键词靠前，每个页面唯一
□ Meta Description：120-155字符，包含关键词+C TA，吸引点击
□ H1标签：每个页面仅1个H1，包含主关键词
□ Open Graph标签：og:title, og:description, og:image, og:url
□ Twitter Card标签：twitter:card, twitter:title, twitter:description

【URL结构】
□ URL简短（<75字符），包含关键词
□ 使用连字符（-）分隔单词，不使用下划线
□ 避免URL参数（如?utm_source=...），使用canonical处理
□ 目录层级不超过3层

【内容结构】
□ 首段200字内出现主关键词
□ H2/H3层级清晰，包含相关关键词变体
□ 段落长度≤3-4句，增加可读性
□ 使用列表（ul/ol）和表格提升可读性
□ 内容长度满足搜索意图（信息型1500+字，交易型500+字）
□ 关键词密度自然（1-2%），避免堆砌

【图片优化】
□ 文件名使用描述性关键词（如：red-running-shoes-review.jpg）
□ Alt属性描述图片内容，包含关键词
□ 使用WebP/AVIF格式
□ 使用响应式图片（srcset + sizes）
□ 图片懒加载（loading="lazy"）
□ 图片尺寸不超过实际显示尺寸的2倍

【内部链接】
□ 每个重要页面至少有3个内部链接指向
□ 锚文本多样化（不完全匹配关键词）
□ 新内容发布后48小时内添加内部链接
□ 最重要的页面从首页链接

【Schema标记】
□ 根据页面类型添加对应的Schema
□ 使用JSON-LD格式（推荐）
□ 通过Google Rich Results Test验证
□ 监控GSC中的"增强功能"报告
```

**2.3.2 按网站类型定制的页面优化建议**

电商站：
```
产品页优化重点：
  - 产品标题：品牌 + 产品名 + 核心属性 + 型号
  - 产品描述：原创描述（非厂商提供），包含使用场景
  - 用户评价：鼓励UGC评论，标记AggregateRating Schema
  - FAQ：产品页底部添加FAQ区块，标记FAQ Schema
  - 结构化数据：Product + Offer + AggregateRating + BreadcrumbList
  - 变体处理：使用canonical指向主产品URL
```

SaaS站：
```
产品页优化重点：
  - 功能页：每个核心功能一个独立页面，长尾关键词覆盖
  - 解决方案页：按行业/角色/场景创建解决方案页
  - 对比页：产品名 vs 竞品名，捕获商业型搜索
  - 集成页：列出所有集成，页面标题"产品名 + 集成"
  - 案例/客户故事：使用真实数据，标记Review Schema
  - 定价页：明确价格，Schema标记，FAQ区块
```

#### 2.4 外链建设（Link Building）

**2.4.1 外链建设策略矩阵**

| 策略 | 难度 | 效果 | 适用阶段 | 投入产出比 |
|------|------|------|----------|-----------|
| 数字公关（Digital PR） | 高 | 高 | 所有阶段 | 高（长期） |
| 内容驱动外链（Linkable Assets） | 中 | 高 | 已建立/成熟 | 中高 |
| 策略性外联（Strategic Outreach） | 中 | 中 | 已建立/成熟 | 中 |
| 资源页面外链（Resource Page） | 低 | 中 | 新站/已建立 | 中 |
| 失效链接建设（Broken Link） | 低 | 中低 | 新站 | 中低 |
| 客座博客（Guest Posting） | 低 | 中低 | 所有阶段 | 中低 |
| HARO/记者求助 | 中 | 中高 | 所有阶段 | 高 |
| 行业目录/列表 | 低 | 低 | 新站 | 低 |

**2.4.2 外链质量评估标准**

```
高质量外链特征：
  ✓ 域名权威（DR/DA）≥ 40
  ✓ 行业相关性高
  ✓ 自然编辑放置（非赞助/付费标记）
  ✓ 流量可观（Ahrefs/Semrush月流量>1000）
  ✓ 链接页面有真实流量
  ✓ 锚文本自然多样

低质量外链特征（需拒绝/disavow）：
  ✗ 来自PBN（Private Blog Network）
  ✗ 来自链接农场/目录
  ✗ 来自完全不相关网站
  ✗ 来自被惩罚的网站
  ✗ 过度优化的锚文本（精确匹配关键词占比过高）
  ✗ Footer/侧边栏全站链接
  ✗ 付费链接（未标记nofollow/sponsored）
```

**2.4.3 按网站类型定制的链接建设策略**

```
电商站外链策略：
  1. 产品评测合作：向博主/评测网站寄送产品获取评测链接
  2. 数字公关：发布行业数据报告（如"2026年XX品类消费趋势"）
  3. 资源页面：创建工具型内容（如"尺码计算器"、"材质对比表"）
  4. 用户UGC：鼓励用户分享开箱/使用体验

内容站外链策略：
  1. 数据驱动内容：原创研究、调查数据、统计集合页
  2. 专家综述（Expert Roundup）：邀请行业专家贡献观点
  3. HARO/记者求助：成为媒体引用来源
  4. 内容更新外联：告知引用了过时数据的网站更新为你的内容

SaaS外链策略：
  1. 免费工具：创建免费SEO工具/计算器吸引自然链接
  2. 行业报告：发布年度行业报告（如"2026年XX行业软件使用报告"）
  3. 集成合作：与互补产品共建集成页面，互相链接
  4. 案例研究：被客户案例中的企业反向链接
```

### 步骤3：根据网站阶段和实施紧迫度排序

根据 `site_stage` 和 `current_ranking` 调整优先级：

```
新站（<6个月）：
  优先级：技术SEO > 关键词研究 > 页面SEO > 外链建设
  理由：先确保网站可被搜索引擎正确抓取和索引

已建立站（6-24个月）：
  优先级：关键词研究 > 页面SEO > 外链建设 > 技术SEO
  理由：技术基础已具备，重点转向内容策略和权威建设

成熟站（>24个月）：
  优先级：外链建设 > 页面SEO优化 > 技术SEO微调 > 关键词研究
  理由：已有大量内容，重点提升权威度和优化现有页面
```

## 三、输出格式

### 输出结构

```markdown
# SEO知识库查询结果

## 1. 查询概览
- 查询类型：[technical/keyword/onpage/offpage/all]
- 网站类型：[ecommerce/content/saas]
- 网站阶段：[new/established/mature]

## 2. [模块名称] 知识输出

### 2.X 核心概念
### 2.X 检查清单
### 2.X 最佳实践
### 2.X 工具推荐
### 2.X 行业定制建议

## 3. 分阶段实施路线图

## 4. 工具推荐总览

## 5. 常见误区提醒

## 附录
### A. 术语表
### B. 参考资源
```

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 2.0.0 | 2026-07-29 | 初始版本，覆盖技术SEO、关键词研究、页面SEO优化、外链建设四大领域 |