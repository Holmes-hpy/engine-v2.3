---
name: sbom-generator
description: CycloneDX SBOM生成技能，将结构化组件列表转换为符合CycloneDX 1.5标准的SBOM JSON文件，支持元数据填充、PURL生成、BOM序列号等标准字段。
---

# CycloneDX SBOM生成技能

## 功能

将结构化的组件列表转换为符合 CycloneDX 1.5 规范的标准 SBOM（Software Bill of Materials）JSON 文件。

## 适用场景

当需要将组件清单转换为标准 SBOM 格式，供下游漏洞扫描、合规检查等工具使用时，调用本技能。

## 输入

- **组件列表**：结构化的组件数组（component + version + [可选其他字段]）
- **元数据（可选）**：项目名称、供应商、版本号等信息

## 处理步骤

### 第1步：构建SBOM基础结构

生成 CycloneDX 标准的顶层结构：

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:随机生成的UUID",
  "version": 1,
  "metadata": { ... },
  "components": [ ... ]
}
```

### 第2步：填充metadata

构建元数据节：

| 字段 | 来源 | 默认值 |
|------|------|--------|
| timestamp | 当前时间 | ISO 8601 格式 |
| tools | 生成工具 | 标注 "SBOM Analysis Platform" |
| component（项目本身） | 输入的元数据 | 如未提供则留空 |
| supplier | 供应商信息 | 如未提供则留空 |

### 第3步：生成PURL

为每个组件生成 Package URL（PURL），根据组件名特征猜测技术生态：

| 生态 | 识别特征 | PURL前缀 |
|------|---------|----------|
| Maven | 包含 groupId/artifactId 格式（如 org.apache.logging.log4j/log4j-core） | `pkg:maven/` |
| npm | 常见JS包名（如 react、lodash、vue） | `pkg:npm/` |
| PyPI | 常见Python包名（如 requests、django、flask） | `pkg:pypi/` |
| Go | 包含路径格式（如 github.com/xxx/yyy） | `pkg:golang/` |
| 通用 | 无法识别的 | `pkg:generic/` |

**PURL格式**：`pkg:生态/组件名@版本号`

示例：
- `pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1`
- `pkg:npm/lodash@4.17.21`
- `pkg:pypi/requests@2.31.0`

### 第4步：构建components数组

为每个组件生成标准条目：

```json
{
  "type": "library",
  "name": "log4j-core",
  "version": "2.14.1",
  "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
  "bom-ref": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"
}
```

### 第5步：完整性校验

生成后自检：
1. bomFormat 是否为 "CycloneDX"
2. specVersion 是否为 "1.5"
3. serialNumber 是否为有效的 urn:uuid 格式
4. components 数组长度是否与输入一致
5. 每个组件是否有 name、version、purl、bom-ref

## 输出格式

输出完整的 CycloneDX 1.5 SBOM JSON，同时输出统计摘要：

```json
{
  "status": "success",
  "sbom": { /* 完整的 CycloneDX SBOM JSON */ },
  "stats": {
    "component_count": 48,
    "ecosystem_breakdown": {
      "maven": 32,
      "npm": 12,
      "pypi": 4
    }
  }
}
```

## 注意事项

- 生成的 SBOM 符合 CycloneDX 1.5 规范的最小可用集，不包含依赖关系图（dependencies 字段），因为输入数据通常不包含依赖树
- 生态识别是"启发式"的，基于常见包名和路径格式猜测，准确率约 80-90%。如果有明确的生态信息，建议在调用时传入
- serialNumber 是随机生成的 UUID，用于唯一标识这份 SBOM，方便后续审计追踪
- 如果组件有 groupId（Maven）或 scope（npm）等信息，可在输入时提供，生成的PURL会更准确
