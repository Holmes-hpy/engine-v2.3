---
name: vex-assessor
description: VEX可达性评估技能，基于漏洞分析结果和目标系统运行上下文，逐漏洞进行可达性分析，分配标准VEX状态（not_affected/affected/fixed/under_investigation），并为每个判定提供可审计的技术推理依据。
---

# VEX可达性评估技能

## 功能

基于漏洞分析结果和目标系统的运行上下文，逐漏洞进行可达性分析，分配标准 VEX 状态，并为每个判定提供可审计的技术推理依据。

> **VEX**（Vulnerability Exploitability eXchange，漏洞可利用性交换）是一种标准化的断言格式，用于说明特定组件的特定漏洞在实际产品环境中是否可被利用。核心价值是"降噪"——区分"理论上有漏洞"和"实际上受影响"。

> **说明**：本技能基于组件使用模式和常见部署架构进行模拟评估。真实生产环境应结合代码调用链分析、运行时配置审计等手段进行精确判定。

## 适用场景

当需要区分漏洞的"理论存在"和"实际受影响"，减少虚假告警，生成 VEX 文档时，调用本技能。

## 输入

- **漏洞分析结果**：分级后的漏洞列表
- **系统上下文**：目标系统的部署环境、组件使用方式、运行配置等信息

## VEX标准状态

| 状态 | 含义 | 使用场景 |
|------|------|---------|
| **affected** | 受影响 | 漏洞在当前环境中确实可被利用 |
| **not_affected** | 不受影响 | 虽然组件有漏洞，但在当前使用方式下不可达/不可利用 |
| **fixed** | 已修复 | 漏洞已通过补丁或升级修复 |
| **under_investigation** | 调查中 | 暂时无法确定，需进一步分析或人工确认 |

## 评估维度

### 维度1：部署范围

| 场景 | 判定倾向 | 典型理由 |
|------|---------|---------|
| 生产环境部署 | → affected | 直接暴露在运行时 |
| 仅测试/开发环境 | → not_affected | 不进入生产环境 |
| 已卸载/未使用 | → not_affected | 组件不存在 |

### 维度2：依赖Scope

| Scope | 判定倾向 | 典型理由 |
|-------|---------|---------|
| compile/runtime | → affected | 打包进生产运行时 |
| test/provided | → not_affected | 不进入生产包 |
| optional | → 视情况 | 看是否实际启用 |

**常见的 test scope 组件**：
- junit、testng 等测试框架
- mockito、powermock 等 mock 工具
- h2、hsqldb 等内存数据库（仅用于测试）

### 维度3：漏洞触发条件

| 触发条件 | 判定倾向 | 典型理由 |
|---------|---------|---------|
| 需要特定配置开启 | → 看配置 | 配置开了才受影响 |
| 需要特定输入格式 | → 看业务 | 业务是否接受这种输入 |
| 需要特定权限 | → 看权限模型 | 低权限用户能否触发 |
| 网络可达 | → 看部署 | 攻击面是否暴露 |

### 维度4：缓解措施

| 缓解措施 | 判定倾向 | 典型理由 |
|---------|---------|---------|
| 已打补丁 | → fixed | 漏洞已修复 |
| 有WAF/防护规则 | → 降级 | 有防护但不彻底 |
| 配置了安全开关 | → not_affected | 危险功能已禁用 |

## 处理步骤

### 第1步：加载系统上下文

收集目标系统的上下文信息：
- 部署环境（生产/测试/开发）
- 组件的依赖 scope
- 关键配置项（安全开关、功能开关）
- 网络部署架构（是否暴露公网）
- 业务使用方式（组件被怎么用）

### 第2步：逐漏洞可达性分析

对每个漏洞，从四个维度进行分析：

1. **部署维度**：组件是否在生产环境运行？
2. **Scope维度**：依赖类型是否为运行时？
3. **触发维度**：漏洞触发条件在当前环境下是否满足？
4. **缓解维度**：是否已有防护措施？

### 第3步：分配VEX状态

根据分析结果分配 VEX 状态：

| 判定结论 | VEX状态 |
|---------|---------|
| 确定受影响，且无有效缓解 | affected |
| 确定不受影响，有明确技术依据 | not_affected |
| 已确认修复（版本已升级或已打补丁） | fixed |
| 信息不足，无法确定 | under_investigation |

### 第4步：撰写判定依据

为每个 VEX 断言撰写清晰、可审计的技术依据：

**not_affected 的依据必须包含**：
- 为什么这个漏洞在当前环境下不可达
- 具体的技术原因（如 scope=test、功能未启用、配置已禁用等）
- 置信度评估（高/中/低）

**affected 的依据必须包含**：
- 漏洞为什么可达
- 触发条件是否满足
- 置信度评估

### 第5步：标记待人工审核项

以下情况必须标记为 `under_investigation`，转人工处理：
- 调用链复杂，无法静态判断是否可达
- 配置信息不完整，缺少关键参数
- 漏洞原理复杂，需要专业知识判断
- 多个因素交织，难以简单判定

## 输出格式

```json
{
  "status": "success",
  "assessment_id": "vex-随机ID",
  "context_summary": "核心交易系统，生产环境K8s部署，公网可达",
  "vex_assertions": [
    {
      "cve_id": "CVE-2021-44228",
      "component": "log4j-core",
      "version": "2.14.1",
      "vex_status": "affected",
      "justification": "该组件以compile scope打包进入生产镜像，部署于公网可达的Web服务中，直接处理用户输入的日志消息，JNDI查找功能默认启用（log4j 2.14.1默认值），满足漏洞利用条件。",
      "analysis_confidence": 0.95,
      "assessment_dimensions": {
        "deployment": "production",
        "scope": "compile",
        "trigger_condition": "satisfied",
        "mitigation": "none"
      }
    },
    {
      "cve_id": "CVE-2020-12345",
      "component": "junit",
      "version": "4.12",
      "vex_status": "not_affected",
      "justification": "该组件scope=test，仅用于单元测试阶段，不打包进入生产运行时镜像，生产环境中不存在该组件，因此不受影响。",
      "analysis_confidence": 0.98,
      "assessment_dimensions": {
        "deployment": "test_only",
        "scope": "test",
        "trigger_condition": "not_applicable",
        "mitigation": "not_applicable"
      }
    }
  ],
  "pending_review": [
    {
      "cve_id": "CVE-2022-5678",
      "component": "commons-collections",
      "version": "3.2.1",
      "reason": "反序列化漏洞，需确认应用是否接受不可信的序列化数据输入，调用链分析不充分"
    }
  ],
  "summary": {
    "total_assessed": 23,
    "affected": 15,
    "not_affected": 5,
    "fixed": 0,
    "under_investigation": 3
  }
}
```

## 注意事项

- **not_affected 必须慎之又慎**——漏掉一个真实受影响的漏洞，后果可能很严重。拿不准的就标 under_investigation，宁可多查，不能漏判
- VEX 判定是**针对特定环境**的——同一个漏洞在A系统是 not_affected，在B系统可能是 affected，因为使用方式不同
- VEX 状态是**动态变化**的——配置变了、部署变了、新的利用方式出来了，VEX 状态都可能变
- 本技能的评估是**基于模式的快速初筛**，高风险漏洞的 not_affected 判定必须人工复核
- 置信度（confidence）是评估结果可靠程度的指标，< 0.7 的建议人工复核
- 常见的"肯定不受影响"场景：test scope 依赖、构建时插件、文档生成工具、已弃用未使用的组件
