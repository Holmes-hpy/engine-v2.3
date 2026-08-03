---
name: vuln-scanner
description: 多工具漏洞扫描技能，基于SBOM组件清单，模拟Snyk、Trivy、OSV等多工具并行漏洞扫描，采集原始漏洞数据（CVE编号、CVSS评分、描述、影响版本、修复版本），支持单工具失败容错。
---

# 多工具漏洞扫描技能

## 功能

基于 SBOM 组件清单，模拟多工具并行漏洞扫描，采集原始漏洞数据。

> **说明**：本技能为知识驱动的模拟扫描，基于公开的 CVE 知识库和组件历史漏洞模式进行匹配。真实生产环境应接入 Snyk、Trivy、OSV 等真实扫描工具 API。

## 适用场景

当需要对组件清单进行漏洞扫描，获取原始漏洞数据供下游分析时，调用本技能。

## 输入

- **SBOM数据**：CycloneDX 格式的 SBOM 或组件列表
- **扫描工具列表（可选）**：指定使用哪些工具，默认 Snyk + Trivy + OSV

## 扫描策略

### 工具分工

| 工具 | 擅长生态 | 特点 |
|------|---------|------|
| Snyk | 全生态（Maven/npm/PyPI/Go等） | 覆盖面广，漏洞库更新快 |
| Trivy | 容器、OS包、Maven/npm/PyPI | 开源免费，速度快 |
| OSV | 开源生态（Google维护） | 数据准确，与Git提交关联 |
| Grype | 容器、OS包 | 开源，与Trivy能力重叠 |

### 扫描方式

1. **生态识别**：根据 PURL 或组件名判断技术生态
2. **工具分配**：为每个组件分配 2-3 个适合的扫描工具
3. **并行扫描**：各工具同时开始扫描（模拟并行）
4. **结果采集**：收集每个工具的扫描结果
5. **容错处理**：单个工具失败不影响整体，记录失败原因

### 漏洞匹配规则

基于知识库进行漏洞匹配，匹配优先级：

1. **精确匹配**：组件名 + 版本号完全命中已知 CVE
2. **版本区间匹配**：组件名匹配，且版本号落在受影响版本区间内
3. **同源匹配**：同一组件的不同版本，参考相邻版本的漏洞情况推断
4. **模式匹配**：同类组件常见漏洞模式（如所有 log4j 版本都关注 JNDI 注入）

## 处理步骤

### 第1步：生态识别与工具分配

遍历组件列表，为每个组件判断生态并分配扫描工具。

### 第2步：执行扫描（模拟）

对每个组件，使用分配的工具进行漏洞匹配：

1. 查知识库中该组件的历史 CVE 列表
2. 判断当前版本是否落在受影响版本范围内
3. 提取漏洞详情：CVE编号、CVSS评分、描述、影响版本、修复版本
4. 每个工具独立输出结果（故意保留差异，模拟真实情况）

### 第3步：结果整理

按组件维度整理原始扫描结果，不去重（去重交给下游漏洞分析专家）。

### 第4步：异常处理

模拟 1-2 个工具的部分失败场景，增加真实感：
- 某个工具连接超时
- 某个组件在某个工具中查不到
- 某个工具返回的数据格式有小差异

## 输出格式

```json
{
  "status": "success",
  "scan_id": "scan-随机ID",
  "scan_timestamp": "2026-08-03T10:00:00Z",
  "tools_used": ["Snyk", "Trivy", "OSV"],
  "component_count": 48,
  "scan_results": [
    {
      "component": "log4j-core",
      "version": "2.14.1",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
      "vulnerabilities": [
        {
          "cve_id": "CVE-2021-44228",
          "source": "Snyk",
          "cvss_score": 10.0,
          "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
          "severity": "critical",
          "description": "Apache Log4j2 JNDI features do not protect against attacker controlled LDAP and other JNDI related endpoints.",
          "affected_versions": ">=2.0-beta9 <=2.14.1",
          "fixed_version": "2.15.0",
          "disclosure_date": "2021-12-10"
        }
      ]
    }
  ],
  "scan_errors": [
    {
      "tool": "Grype",
      "component": "all",
      "reason": "服务连接超时，重试3次失败，已跳过"
    }
  ],
  "summary": {
    "total_findings_raw": 70,
    "by_tool": {
      "Snyk": 28,
      "Trivy": 23,
      "OSV": 19
    }
  }
}
```

## 注意事项

- 本技能为**模拟扫描**，数据基于公开知识库，不保证与真实扫描工具100%一致
- 故意保留了多工具结果的差异（如CVSS评分略有不同、描述措辞不同），以模拟真实场景，供下游去重合并
- 扫描速度是"即时"的，但在演示中应模拟扫描过程的时间感（如显示进度条）
- 真实生产环境中，应替换为 Snyk API、Trivy 命令行、OSV API 等真实数据源
- Grype 和 Trivy 能力高度重叠，Demo 中可以故意让 Grype 失败，展示容错能力
