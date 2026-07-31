# 发包测试规范

> **版本**: v2.3.0
> **优先级**: P2（与项目结构规则同级）
> **说明**: 本文件定义版本发布前必须通过的测试检查项。v2.3.0 发包时发现 7 个严重 Bug（目录结构不一致、目录缺失、触发时机冲突、章节编号重复、信心分数不一致、数据过时、脚本未执行），特制定本规范以杜绝同类问题。

---

## 1. 测试维度总览

本次发现的 Bug 根因可归纳为 6 类缺陷，覆盖 5 个测试维度：

| 维度 | 代号 | 防范的 Bug 类型 | v2.3.0 实际案例 |
|------|------|-----------------|-----------------|
| 结构一致性 | STRUCT | 同一事物在不同文件中定义不同 | memory/ 目录在 04-knowledge 和 02-structure 中定义不一致 |
| 实现完整性 | IMPL | 规则定义了但实际未创建/未执行 | bootstrap 只创建 5 个 memory 子目录，规则要求 8 个 |
| 引用正确性 | REF | 不同文件引用同一事物时描述矛盾 | 01-llm-behavior 说"延迟执行"，03-task-execution 说"每轮对话后立即执行" |
| 数据时效性 | DATA | 数值、计数未随变更同步更新 | 专家数量仍是瘦身前的 270/250/290 |
| 流程可执行性 | EXEC | 描述的操作流程实际无法执行 | bootstrap 手动建表而非执行已有 SQL 脚本 |
| 表述一致性 | TERM | 版本号、特性描述未同步更新 | README 写"双层知识沉淀"，实际已是"三层" |

---

## 2. 测试检查清单（必过项）

### 2.1 结构一致性检查（STRUCT）

**检查目标**: 确保所有文件中对同一事物的描述完全一致。

**检查方法**:

```
检查项 S1: memory/ 目录结构一致性
  涉及文件: rules/04-knowledge.md, rules/02-project-structure.md, bootstrap.md, README.md, 项目使用指南.md
  检查内容: 所有文件中的 memory/ 子目录列表是否完全一致（名称、数量、层级）
  期望: 8 个子目录 + _schema.sql，共 9 项，名称完全一致

检查项 S2: 任务文档模板结构一致性
  涉及文件: rules/03-task-execution.md §2.2, bootstrap.md Phase 3, rules/02-project-structure.md §1
  检查内容: _template/ 下的文件列表是否一致
  期望: 至少包含 任务启动清单.md、任务描述.md、交接报告.md

检查项 S3: 规则文件编号一致性
  涉及文件: rules/ 下所有 .md 文件, rules/_registry.yaml, rules.md, README.md
  检查内容: 所有地方引用的规则文件编号（00-05）是否一致
  期望: 编号、文件名、优先级描述完全一致
```

### 2.2 实现完整性检查（IMPL）

**检查目标**: 确保规则/文档中描述的所有目录和文件在 bootstrap 中都有对应的创建命令。

**检查方法**:

```
检查项 I1: bootstrap 目录创建完整性
  方法: 对比 rules/02-project-structure.md 中列出的所有目录，逐一检查 bootstrap.md 中是否有 mkdir 命令
  重点: 中文目录（任务文档/、捡破烂/）和英文目录（memory/、.memory/）都要覆盖

检查项 I2: bootstrap 文件创建完整性
  方法: 对比所有规则文件要求的初始文件，检查 bootstrap 是否都有创建/复制命令
  重点: index/ 下的子文件（knowledge-index.md、session-index.md）容易被遗漏

检查项 I3: memory/ 子目录完整性
  方法: 对比 rules/04-knowledge.md §2.1 和 bootstrap.md Phase 5 的 mkdir 命令
  期望: sessions/ episodes/ facts/ profiles/ principles/ patterns/ decisions/ index/ 共 8 个目录全部创建
```

### 2.3 引用正确性检查（REF）

**检查目标**: 确保不同文件之间的交叉引用描述一致，不存在矛盾。

**检查方法**:

```
检查项 R1: 触发时机一致性
  涉及引用: 01-llm-behavior.md §2（延迟执行模式）→ 03-task-execution.md §2.4（执行规范）→ 04-knowledge.md §3.1（实时沉淀）
  检查内容: 三处对"何时执行沉淀"的描述是否一致
  期望: 都明确标注"延迟执行"或"下一轮对话开始前"

检查项 R2: 知识沉淀层次一致性
  涉及引用: 04-knowledge.md §1 → bootstrap.md 元信息 → README.md 特性表 → 项目使用指南.md §5
  检查内容: 所有地方对沉淀层次的描述是否一致
  期望: 都描述为"三层"（实时静默 + 会话标记 + 周度挖掘）

检查项 R3: 版本号一致性
  涉及引用: 所有 .md 文件头部版本声明
  检查内容: 版本号是否统一
  期望: 所有文件版本号一致（如 v2.3.1）
```

### 2.4 数据时效性检查（DATA）

**检查目标**: 确保所有可变的数值数据与实际情况一致。

**检查方法**:

```
检查项 D1: 专家数量一致性
  涉及文件: rules/02-project-structure.md, README.md, 项目使用指南.md, bootstrap.md
  检查内容: 通用专家数、金融专家数、工作流模板数、总计
  验证方法: 实际统计 expert-library/ 下的文件数
  期望: 文档中数量 = 实际文件统计数量

检查项 D2: 规则文件数量一致性
  涉及文件: README.md, 项目使用指南.md, rules/_registry.yaml
  检查内容: 声称的规则文件数量
  验证方法: 实际统计 rules/ 下 .md 文件数
  期望: 文档中数量 = 实际文件数量

检查项 D3: 版本历史表完整性
  涉及文件: README.md §版本历史
  检查内容: 版本历史表是否包含当前版本
  期望: 最新版本行 = 当前版本号
```

### 2.5 流程可执行性检查（EXEC）

**检查目标**: 确保描述的操作流程在实际环境中可以完整执行。

**检查方法**:

```
检查项 E1: bootstrap 全流程可执行
  方法: 在干净目录中执行 bootstrap.md 的全部 Phase
  检查: 每个 Phase 是否都能成功完成
  重点: Phase 5（SQLite 初始化）的 SQL 脚本是否真的会被执行

检查项 E2: SQL 脚本引用正确
  方法: 检查 bootstrap.md Phase 5 中引用的 SQL 脚本路径
  验证: 路径指向的文件是否真实存在
  期望: 所有引用的 SQL 脚本文件都存在且非空

检查项 E3: 模板文件可复制
  方法: 检查 bootstrap.md 中 cp 命令的源路径
  验证: 源路径指向的文件是否真实存在
  期望: 所有模板文件都存在且可读取
```

### 2.6 表述一致性检查（TERM）

**检查目标**: 确保关键术语、特性描述在所有文件中统一。

**检查方法**:

```
检查项 T1: 核心特性描述一致
  涉及: "三层知识沉淀" vs "双层知识沉淀"、"捡破烂"机制描述
  检查: 所有文件对同一特性的描述是否一致
  期望: 同一特性在所有文件中描述一致

检查项 T2: 废弃标记一致
  涉及: 产出物/ 目录、旧规则路径等
  检查: 所有文件对废弃内容的标记是否一致
  期望: 废弃内容统一标注"[已废弃 v2.3.0]"或等效标记

检查项 T3: 中文术语一致
  涉及: "任务文档"、"捡破烂"、"知识沉淀"、"认知闭环"等
  检查: 所有文件中是否使用相同的术语
  期望: 核心术语在所有文件中拼写和含义完全一致
```

---

## 3. 自动化测试脚本

### 3.1 脚本位置

`rules/_test/check-consistency.sh`

### 3.2 脚本内容

```bash
#!/bin/bash
# 发包一致性检查脚本 v2.3.0
# 用法: bash rules/_test/check-consistency.sh [TARGET_DIR]
# 默认检查当前目录

set -e

TARGET_DIR="${1:-.}"
ERRORS=0
WARNINGS=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; WARNINGS=$((WARNINGS + 1)); }

echo "============================================"
echo "  项目启动包一致性检查 v2.3.1"
echo "  目标目录: ${TARGET_DIR}"
echo "============================================"
echo ""

# ====== STRUCT: 结构一致性 ======
echo "--- S1: memory/ 目录结构一致性 ---"

# 从 04-knowledge.md 提取 memory 子目录定义
MEM_DIRS=$(grep -oP 'memory/\K[a-z_]+(?=/)' "${TARGET_DIR}/rules/04-knowledge.md" | sort -u | tr '\n' ' ')

# 检查 bootstrap.md 中的 mkdir 命令是否覆盖所有子目录
for dir in $MEM_DIRS; do
    if grep -q "mkdir.*memory/${dir}" "${TARGET_DIR}/bootstrap.md"; then
        pass "memory/${dir}/ 在 bootstrap.md 中有创建命令"
    else
        fail "memory/${dir}/ 在 bootstrap.md 中缺少创建命令"
    fi
done

# 检查 README.md 是否包含所有子目录
for dir in $MEM_DIRS; do
    if grep -q "${dir}/" "${TARGET_DIR}/README.md"; then
        pass "memory/${dir}/ 在 README.md 中存在"
    else
        fail "memory/${dir}/ 在 README.md 中缺失"
    fi
done

# 检查 项目使用指南.md
for dir in $MEM_DIRS; do
    if grep -q "${dir}/" "${TARGET_DIR}/项目使用指南.md"; then
        pass "memory/${dir}/ 在 项目使用指南.md 中存在"
    else
        fail "memory/${dir}/ 在 项目使用指南.md 中缺失"
    fi
done

echo ""
echo "--- S2: _schema.sql 存在性 ---"
for f in "rules/04-knowledge.md" "bootstrap.md" "README.md" "项目使用指南.md"; do
    if grep -q '_schema.sql' "${TARGET_DIR}/${f}"; then
        pass "_schema.sql 在 ${f} 中存在"
    else
        fail "_schema.sql 在 ${f} 中缺失"
    fi
done

echo ""
echo "--- S3: 规则文件编号一致性 ---"
for n in 00 01 02 03 04 05; do
    if [ -f "${TARGET_DIR}/rules/${n}-"*.md ]; then
        pass "rules/${n}-*.md 存在"
    else
        fail "rules/${n}-*.md 缺失"
    fi
done

# ====== REF: 引用正确性 ======
echo ""
echo "--- R1: 触发时机一致性 ---"

# 检查是否都引用了"延迟执行"
for f in "rules/03-task-execution.md" "rules/04-knowledge.md"; do
    if grep -q '延迟执行' "${TARGET_DIR}/${f}"; then
        pass "${f} 引用了延迟执行模式"
    else
        warn "${f} 未引用延迟执行模式"
    fi
done

echo ""
echo "--- R2: 知识沉淀层次一致性 ---"
# 检查是否都描述为"三层"
THREE_LAYER_FILES=0
for f in "rules/04-knowledge.md" "README.md" "项目使用指南.md"; do
    if grep -q '三层' "${TARGET_DIR}/${f}"; then
        THREE_LAYER_FILES=$((THREE_LAYER_FILES + 1))
        pass "${f} 描述为'三层'知识沉淀"
    else
        fail "${f} 未描述为'三层'知识沉淀（可能仍是'双层'）"
    fi
done

echo ""
echo "--- R3: 版本号一致性 ---"
VERSION=$(grep -oP 'v\d+\.\d+\.\d+' "${TARGET_DIR}/bootstrap.md" | head -1)
for f in $(find "${TARGET_DIR}/rules" -name "*.md" -not -name "README.md"); do
    FILE_VER=$(grep -oP 'v\d+\.\d+\.\d+' "$f" | head -1)
    if [ "$FILE_VER" = "$VERSION" ]; then
        pass "$(basename $f) 版本号一致: ${FILE_VER}"
    else
        fail "$(basename $f) 版本号不一致: ${FILE_VER} (期望 ${VERSION})"
    fi
done

# ====== IMPL: 实现完整性 ======
echo ""
echo "--- I1: bootstrap 目录创建完整性 ---"

# 从 02-project-structure 提取所有目录
REQUIRED_DIRS=("任务文档/_template" "任务文档/_archive" "捡破烂/_buffer" "捡破烂/_archive" "捡破烂/_mining-reports" "memory/sessions" "memory/episodes" "memory/facts" "memory/profiles" "memory/principles" "memory/patterns" "memory/decisions" "memory/index" ".memory" "agents" "workflows" "logs")

for dir in "${REQUIRED_DIRS[@]}"; do
    if grep -q "mkdir.*${dir}" "${TARGET_DIR}/bootstrap.md"; then
        pass "bootstrap 包含 mkdir ${dir}"
    else
        fail "bootstrap 缺少 mkdir ${dir}"
    fi
done

echo ""
echo "--- I2: index/ 子文件创建 ---"
for sub in "knowledge-index.md" "session-index.md"; do
    if grep -q "${sub}" "${TARGET_DIR}/bootstrap.md"; then
        pass "bootstrap 包含创建 ${sub}"
    else
        fail "bootstrap 缺少创建 ${sub}"
    fi
done

# ====== EXEC: 流程可执行性 ======
echo ""
echo "--- E2: SQL 脚本引用正确 ---"
SQL_SCRIPTS=$(grep -oP 'cognitive-closure/schema/\d+[^"]+' "${TARGET_DIR}/bootstrap.md" || true)
if [ -z "$SQL_SCRIPTS" ]; then
    fail "bootstrap.md 中未找到 SQL 脚本引用"
else
    for script in $SQL_SCRIPTS; do
        if [ -f "${TARGET_DIR}/${script}" ]; then
            pass "SQL 脚本 ${script} 存在"
        else
            fail "SQL 脚本 ${script} 不存在"
        fi
    done
fi

# ====== DATA: 数据时效性 ======
echo ""
echo "--- D1: 专家数量一致性 ---"
# 实际统计
ACTUAL_AGENCY=$(find "${TARGET_DIR}/expert-library/agency-agents-zh" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
ACTUAL_FIN_AGENTS=$(find "${TARGET_DIR}/expert-library/financial-services" -name "*.md" -path "*/agents/*" 2>/dev/null | wc -l | tr -d ' ')
ACTUAL_WF=$(find "${TARGET_DIR}/expert-library/agency-orchestrator" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

echo "  实际统计: 通用=${ACTUAL_AGENCY}, 金融Agent=${ACTUAL_FIN_AGENTS}, 工作流=${ACTUAL_WF}"

# 检查 README.md 中的数量
README_COUNT=$(grep -oP '\d+(?=位|个)' "${TARGET_DIR}/README.md" | head -3 | tr '\n' ' ')
echo "  README.md 声称: ${README_COUNT}"

echo ""
echo "============================================"
echo "  检查完成: ${ERRORS} 个错误, ${WARNINGS} 个警告"
echo "============================================"

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ 未通过！请修复以上 ${ERRORS} 个错误后再发布。${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 全部通过！可以发布。${NC}"
    exit 0
fi
```

---

## 4. 发布前检查流程

### 4.1 流程总览

```
代码修改完成
    │
    ▼
┌─────────────────────┐
│ Step 1: 手动目视检查 │  ← 对照 §2 检查清单逐项确认
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Step 2: 自动化脚本   │  ← 运行 check-consistency.sh
└────────┬────────────┘
         │
    ┌────┴────┐
    │ 通过？   │
    └────┬────┘
    失败 │     通过
    ▼         ▼
  修复     ┌─────────────────────┐
           │ Step 3: 干净环境测试 │  ← 在新目录执行 bootstrap
           └────────┬────────────┘
                    │
               ┌────┴────┐
               │ 通过？   │
               └────┬────┘
               失败 │     通过
               ▼         ▼
             修复    ┌─────────────────────┐
                     │ Step 4: 打 Tag 发布  │
                     └─────────────────────┘
```

### 4.2 Step 1: 手动目视检查（5 分钟）

按优先级逐项确认：

| 序号 | 检查项 | 怎么查 |
|:---:|--------|--------|
| 1 | 版本号是否统一 | `grep -r "v[0-9]" rules/ README.md bootstrap.md 项目使用指南.md` |
| 2 | "三层"还是"双层" | `grep -r "层.*沉淀\|层.*知识" README.md 项目使用指南.md` |
| 3 | 专家数量是否最新 | 手动统计 expert-library/ 下文件数，对比文档 |
| 4 | 触发时机是否对齐 | 搜"延迟执行"，确认 01/03/04 三个文件都引用了 |
| 5 | 废弃标记是否一致 | 搜"已废弃"，确认格式统一 |
| 6 | 版本历史表是否更新 | 检查 README.md 版本历史表包含当前版本 |

### 4.3 Step 2: 自动化脚本（1 分钟）

```bash
cd {启动包目录}
bash rules/_test/check-consistency.sh .
```

必须 0 错误通过。警告可接受，但需记录原因。

### 4.4 Step 3: 干净环境测试（5 分钟）

```bash
# 创建临时目录
TMP_DIR=$(mktemp -d)
echo "测试目录: ${TMP_DIR}"

# 模拟：把 bootstrap.md 扔给 AI，让它初始化
# 手动验证关键步骤：
# 1. TARGET_DIR 确认逻辑正确
# 2. Phase 1-8 全部执行成功
# 3. memory/ 下 8 个子目录全部创建
# 4. SQLite 数据库可连接
# 5. 规则文件全部复制到位

# 最后清理
rm -rf "${TMP_DIR}"
```

### 4.5 Step 4: 打 Tag 发布

```bash
git add -A
git commit -m "release: vX.Y.Z - {简要说说明}"
git tag -a "vX.Y.Z" -m "vX.Y.Z"
git push origin main --tags
```

---

## 5. 版本发布检查清单（速查卡）

每次发包前，打印/复制此清单，逐项打勾：

```
□ 1. 版本号统一检查
    □ grep 确认所有文件版本号一致
    □ README.md 版本历史表已更新

□ 2. 结构一致性
    □ memory/ 目录结构在 5 个文件中一致
    □ index/ 子文件（knowledge-index.md, session-index.md）在所有文件中存在
    □ _schema.sql 在所有 memory 目录描述中存在

□ 3. 规则文件完整性
    □ 00-05 共 6 个 .md 文件全部存在
    □ _registry.yaml 存在
    □ rules.md 入口文件存在

□ 4. 数值一致性
    □ 专家数量与实际文件统计一致
    □ 规则文件数量与实际一致
    □ "三层"沉淀描述一致（非"双层"）

□ 5. 引用一致性
    □ "延迟执行"模式在 01/03/04 三个文件中都正确引用
    □ 废弃标记格式统一

□ 6. 流程可执行性
    □ bootstrap 包含所有目录的 mkdir 命令
    □ SQL 脚本引用路径正确
    □ 模板文件路径正确

□ 7. 自动化脚本
    □ check-consistency.sh 执行通过（0 错误）
    □ 警告已记录原因

□ 8. 干净环境测试
    □ 新目录中 bootstrap 全流程可执行
    □ 所有目录和文件创建正确

□ 9. Git 操作
    □ git commit 已提交
    □ git tag 已打
    □ git push 已推送
```

---

## 6. Bug 根因分析与预防

### 6.1 v2.3.0 Bug 根因分析

| Bug | 根因 | 为什么没发现 |
|-----|------|-------------|
| memory/ 目录结构不一致 | 多处手写目录结构，无单一真相来源 | 人工目视检查，人眼疲劳 |
| 缺失 3 个 memory 子目录 | bootstrap 是手动写的，不是从规则生成的 | 无自动化对比检查 |
| 触发时机冲突 | 先写了"延迟执行"，后补了"每轮后执行"，未同步 | 缺少交叉引用验证 |
| 章节编号重复 | 手动编辑时插入新章节，未检查现有编号 | 无编号唯一性检查 |
| 信心分数不一致 | 两套度量体系并存，未统一清理 | 无度量体系一致性检查 |
| 专家数量过时 | 瘦身操作后只更新了部分文件 | 无数据时效性检查 |
| 脚本未执行 | bootstrap 写了"手动"建表，实际有现成脚本 | 无流程可执行性验证 |

### 6.2 核心原则

> **"单一真相来源"原则**: 任何信息只应在一处定义，其他地方通过引用获取。如果必须多处存在，则必须有自动化检查确保一致性。

> **"修改即验证"原则**: 每次修改涉及多文件的内容（如目录结构、版本号、计数），修改后必须立即运行一致性检查脚本。

> **"干净环境验证"原则**: 每次发布前必须在全新目录中执行一次完整 bootstrap，模拟用户真实使用场景。

---

## 7. 规则文件索引更新

本文件（07-testing.md）加入规则体系后，需要更新以下文件：

- [ ] `rules/_registry.yaml` — 添加 07-testing.md 条目
- [ ] `rules.md` — 添加读取顺序
- [ ] `README.md` — 规则体系表更新为 7+1
- [ ] `bootstrap.md` — 规则复制列表增加 07-testing.md
- [ ] `项目使用指南.md` — 规则优先级表更新

---

*本规范诞生于 v2.3.0 的惨痛教训。记住：测试不是可选项，是发布前的最后一道防线。*