---
name: report_integration
description: "可研报告整合与Word渲染规范"
version: "1.2"
---

# 可研报告整合与Word渲染规范

## 1. 整合流程

### 1.1 读取章节
- 按顺序读取9个Writer的final artifact
- 每个artifact是一个纯文本文件，包含一个章节的完整内容

### 1.2 内容净化（P0级，必须在拼接前完成，必须逐条执行）

净化规则分两类——自动替换（正则匹配）和语义判断：

#### 自动替换规则（必须执行，不可跳过）
1. 正则删除所有 [U] [M] [W] 标记及其所在行（整行删除）
2. 正则删除所有 【待补充】标记所在段落
3. 正则删除所有行首的 # ## ### Markdown标题符号（保留符号后的文字，如"# 第1章 概述"变为"第1章 概述"）
4. 正则删除所有 "本章小结"开头的段落及其后续总结内容（直到空行或下一个标题）
5. 正则删除所有内部路径（/artifacts/、/workspace/、/tmp/）
6. 正则删除所有占位语行（含"待填写""此处由AI生成""详见专项报告""TBD""XXX"的段落）

#### 模糊词汇替换规则（P0级，必须执行）
对以下模糊词汇执行全文正则替换：
- "可能" → "预计"或"将"或删除（根据上下文选择精确表述）
- "大概" → "约"（仅当有近似数据支撑时）或删除
- "或许" → 删除
- "预计"（非财务预测语境时） → "根据数据显示"或删除
- "约为" → 具体数值（如有数据）或删除
- "左右" → 删除
- "估计" → 具体数值或删除
- "应该" → "需要"或删除
- "差不多" → 删除

净化完成后，必须统计残留模糊词数量。如仍有残留，执行第二轮替换。

#### 其他删除规则
- 工具回执和系统输出残留
- 过程性描述（"本章节基于xxx材料撰写""数据来源说明"等）
- 重复的章节标题（合并相邻重复标题）
- 低于50字的空白段落
- "附录：第10章"相关的框架性说明段落（Integrator将自行生成第10章）

### 1.3 内容拼接
- 章节顺序：1→2→3→4→5→6→7→8→9→10
- 不修改任何章节正文内容（除1.2净化外）

### 1.4 质检
- 执行三层质检（P0格式→P1单章→P2结构）
- P0问题直接修复，P1/P2问题标记并报告
- 最多3轮迭代，超限则附带质检报告交付

### 1.5 Word渲染（P0级，必须执行）
- 必须使用python-docx库生成Word文档，禁止直接输出纯文本docx
- Integrator执行下方第8节中的Python代码生成Word文档
- 执行方式：将第8节代码写入临时文件render.py，然后执行 python3 render.py {输入md} {输出docx} {企业名称} {项目名称}
- 输入：拼接净化后的完整纯文本报告
- 输出：可研报告.docx

### 1.6 第10章自动生成（Integrator负责）

第10章"附表、附图和附件"不由Writer撰写，由Integrator在拼接前9章后自动生成。

生成规则：
- 标题格式：第十章 附表、附图和附件
- 正文内容：根据前9章实际包含的表格和数据，整理出附表清单
- 每个附表列出：表编号、表名称、数据来源章节
- 附表至少包括：主要技术经济指标汇总表、财务预测数据汇总表、敏感性分析结果汇总表
- 字数控制在500-800字

## 2. Word文档结构（python-docx渲染规范）

### 2.1 封面页
- 独立一节（section），无页眉页脚
- 居中排版：
  - 第1行：空白（留白约1/3页）
  - 第2行：{企业名称}{项目名称}（黑体 26pt 加粗）
  - 第3行：可行性研究报告（黑体 26pt 加粗）
  - 第4行：空白
  - 第5行：编制单位：{单位名称}（仿宋 15pt）
  - 第6行：编制日期：{YYYY年MM月}（仿宋 15pt）
- 封面后插入分节符

### 2.2 目录页
- 独立一节，页码格式：罗马数字（i, ii, iii...）
- 标题：目  录（黑体 15pt 居中）
- 调用docx添加自动目录（基于文档中使用的标题样式）

### 2.3 正文
- 新一节，页码格式：阿拉伯数字（从1开始）
- 包含第1章到第10章完整内容
- 页眉：{企业名称} — 可行性研究报告（宋体 9pt 居中，单线边框下分隔）
- 页脚：- 第X页 -（居中）

### 2.4 附表、附图和附件
- 属于正文最后一节
- 第10章列出附表清单和附图清单

## 3. 样式表（python-docx渲染必须严格遵循）

### 3.1 标题样式
| 样式名称 | 字体 | 字号 | 加粗 | 颜色 | 段前段后 |
|---------|------|------|------|------|---------|
| 文档标题(封面) | 黑体 | 26pt | 是 | 黑色 | 段前0 段后0 |
| 章标题(Heading1) | 黑体 | 15pt | 是 | 黑色 | 段前24pt 段后12pt |
| 节标题(Heading2) | 楷体 | 15pt | 是 | 黑色 | 段前18pt 段后6pt |
| 子节标题(Heading3) | 仿宋 | 15pt | 否 | 黑色 | 段前12pt 段后6pt |

### 3.2 正文样式
| 样式名称 | 字体 | 字号 | 行距 | 首行缩进 | 对齐 |
|---------|------|------|------|---------|------|
| 正文(Body) | 仿宋 | 15pt | 固定值28.95pt(约1.5倍) | 480twips | 两端对齐 |

### 3.3 表格样式
- 表头行：黑体 12pt 加粗，居中，底色RGB(217,217,217)
- 表体行：仿宋 12pt，居中
- 边框：单线边框(RGB(0,0,0))，线宽0.5pt
- 列对齐规则：文本列左对齐，数字列右对齐
- 表格上方必须有标题行（仿宋 12pt 加粗，居中）

### 3.4 页面设置
| 参数 | 值 |
|------|-----|
| 纸张 | A4 (210mm x 297mm) |
| 上边距 | 37mm |
| 下边距 | 35mm |
| 左边距 | 28mm |
| 右边距 | 26mm |

### 3.5 字体回退方案
macOS环境：华文楷体 → 华文仿宋 → STHeiti → PingFang SC
如方正字体不可用，按以下优先级回退：
- 方正小标宋简体 → 华文楷体(STKaiti) → 黑体(系统)
- 方正黑体 → 华文黑体(STHeiti) → 黑体(系统)
- 方正楷体 → 华文楷体(STKaiti) → 楷体(系统)
- 仿宋_GB2312 → 华文仿宋(STFangsong) → 仿宋(系统)

## 4. 纯文本表格转Word表格规则

Writer输出的纯文本表格使用|分隔列，渲染脚本解析规则：
1. 按行分割文本，识别|分隔的列
2. 第一行为表头，后续行为数据行
3. 第一行与第二行之间有|---|---|分隔行的，跳过该行
4. 转换为python-docx的Table对象
5. 应用表格样式（表头灰色底色、居中对齐、边框）
6. 自动调整列宽（根据内容长度按比例分配）

## 5. 章节标题识别规则（渲染脚本用）

渲染脚本需要识别纯文本中的章节标题并应用对应样式：

| 模式 | 样式 | 示例 |
|------|------|------|
| /^第[一二三四五六七八九十\d]+章/ | Heading 1 | 第一章 概述 或 第1章 概述 |
| /^\d+\.\d+\s/ | Heading 2 | 1.1 项目概况 |
| /^\d+\.\d+\.\d+\s/ | Heading 3 | 4.1.1 工艺流程 |

## 6. 交付文件

整合完成后输出两个文件：
1. 完整可研报告.md — 纯文本格式的完整报告（经净化处理）
2. 可研报告.docx — Word格式的正式报告（经python-docx渲染，含完整格式）

## 7. 质检报告模板

| 检查项 | 结果 | 备注 |
|--------|------|------|
| 来源标记清除 | 通过/未通过 | 残留[U][M][W]数量 |
| 模糊词汇清除 | 通过/未通过 | 残留数量 |
| 二级标题完整性 | N/43 | 缺失列表 |
| 总字数 | N字 | 目标28,500字 |
| 表格数量 | N个 | 含空表格数 |
| 财务指标完整性 | N/8 | 缺失列表 |
| 数字一致性 | 通过/未通过 | 不一致项 |
| Word格式 | 通过/未通过 | 字体/字号/行距/缩进 |
| 迭代次数 | N/3 | |

## 8. Word渲染脚本（内嵌代码）

Integrator必须将以下完整Python代码写入临时文件render.py，然后执行：
python3 render.py 输入报告.md 输出报告.docx 企业名称 项目名称

```python
import re, os, sys
from docx import Document
from docx.shared import Pt, Cm, Twips, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

PAGE_WIDTH = Cm(21.0)
PAGE_HEIGHT = Cm(29.7)
MARGIN_TOP = Cm(3.7)
MARGIN_BOTTOM = Cm(3.5)
MARGIN_LEFT = Cm(2.8)
MARGIN_RIGHT = Cm(2.6)

STYLES = {
    'heading1': {'font_name': '黑体', 'font_size': Pt(15), 'bold': True, 'space_before': Pt(24), 'space_after': Pt(12), 'alignment': WD_ALIGN_PARAGRAPH.LEFT},
    'heading2': {'font_name': '楷体', 'font_size': Pt(15), 'bold': True, 'space_before': Pt(18), 'space_after': Pt(6), 'alignment': WD_ALIGN_PARAGRAPH.LEFT},
    'heading3': {'font_name': '仿宋', 'font_size': Pt(15), 'bold': False, 'space_before': Pt(12), 'space_after': Pt(6), 'alignment': WD_ALIGN_PARAGRAPH.LEFT},
    'body': {'font_name': '仿宋', 'font_size': Pt(15), 'bold': False, 'space_before': Pt(0), 'space_after': Pt(0), 'alignment': WD_ALIGN_PARAGRAPH.JUSTIFY, 'first_line_indent': Twips(480), 'line_spacing': Pt(28.95)},
    'table_title': {'font_name': '仿宋', 'font_size': Pt(12), 'bold': True, 'space_before': Pt(6), 'space_after': Pt(3), 'alignment': WD_ALIGN_PARAGRAPH.CENTER},
    'table_header': {'font_name': '黑体', 'font_size': Pt(12), 'bold': True, 'alignment': WD_ALIGN_PARAGRAPH.CENTER},
    'table_cell': {'font_name': '仿宋', 'font_size': Pt(12), 'bold': False, 'alignment': WD_ALIGN_PARAGRAPH.CENTER},
}

CHAPTER_RE = re.compile(r'^(第[一二三四五六七八九十\d]+章)\s+(.+)$')
SECTION_RE = re.compile(r'^(\d+\.\d+)\s+(.+)$')
SUBSECTION_RE = re.compile(r'^(\d+\.\d+\.\d+)\s+(.+)$')
TABLE_SEP_RE = re.compile(r'^\|[-:\s|]+\|$')
TABLE_ROW_RE = re.compile(r'^\|(.+)\|$')
EMPTY_RE = re.compile(r'^\s*$')

def parse_blocks(text):
    lines = text.split('\n')
    blocks = []
    cur_table = []
    cur_title = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if EMPTY_RE.match(line):
            if cur_table:
                blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table})
                cur_table, cur_title = [], None
            i += 1; continue
        m = CHAPTER_RE.match(line)
        if m:
            if cur_table: blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table}); cur_table, cur_title = [], None
            blocks.append({'type': 'heading1', 'text': f'{m.group(1)} {m.group(2)}'}); i += 1; continue
        m = SECTION_RE.match(line)
        if m:
            if cur_table: blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table}); cur_table, cur_title = [], None
            blocks.append({'type': 'heading2', 'text': f'{m.group(1)} {m.group(2)}'}); i += 1; continue
        m = SUBSECTION_RE.match(line)
        if m:
            if cur_table: blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table}); cur_table, cur_title = [], None
            blocks.append({'type': 'heading3', 'text': f'{m.group(1)} {m.group(2)}'}); i += 1; continue
        if TABLE_ROW_RE.match(line):
            if not cur_table and blocks and blocks[-1]['type'] == 'paragraph' and len(blocks[-1]['text']) < 50:
                cur_title = blocks[-1]['text']; blocks.pop()
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if not TABLE_SEP_RE.match(line): cur_table.append(cells)
            i += 1; continue
        if cur_table: blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table}); cur_table, cur_title = [], None
        blocks.append({'type': 'paragraph', 'text': line}); i += 1
    if cur_table: blocks.append({'type': 'table', 'title': cur_title, 'rows': cur_table})
    return blocks

def set_font(run, font_name, font_size, bold=False):
    run.font.name = font_name; run.font.size = font_size; run.font.bold = bold
    r = run._element
    rPr = r.find(qn('w:rPr'))
    if rPr is None: rPr = parse_xml(f'<w:rPr {nsdecls("w")}></w:rPr>'); r.insert(0, rPr)
    rf = rPr.find(qn('w:rFonts'))
    if rf is None: rf = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{font_name}"/>'); rPr.insert(0, rf)
    else: rf.set(qn('w:eastAsia'), font_name)

def add_para(doc, text, sn='body'):
    s = STYLES[sn]; p = doc.add_paragraph(); p.alignment = s.get('alignment', WD_ALIGN_PARAGRAPH.JUSTIFY)
    pf = p.paragraph_format; pf.space_before = s.get('space_before', Pt(0)); pf.space_after = s.get('space_after', Pt(0))
    if sn == 'body': pf.first_line_indent = s.get('first_line_indent', Twips(480))
    if 'line_spacing' in s: pf.line_spacing = s['line_spacing']
    set_font(p.add_run(text), s['font_name'], s['font_size'], s.get('bold', False))
    return p

def add_tbl(doc, title, rows):
    if not rows: return
    if title: add_para(doc, title, 'table_title')
    nc = max(len(r) for r in rows)
    t = doc.add_table(rows=len(rows), cols=nc); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = 'Table Grid'
    for i, rd in enumerate(rows):
        for j in range(nc):
            c = t.cell(i, j); c.text = rd[j] if j < len(rd) else ''
            for pg in c.paragraphs:
                pg.alignment = STYLES['table_cell']['alignment']
                for rn in pg.runs: set_font(rn, STYLES['table_header']['font_name'] if i == 0 else STYLES['table_cell']['font_name'], STYLES['table_header']['font_size'] if i == 0 else STYLES['table_cell']['font_size'], STYLES['table_header'].get('bold', False) if i == 0 else STYLES['table_cell'].get('bold', False))
            if i == 0:
                sh = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9D9D9"/>')
                c._tc.get_or_add_tcPr().append(sh)
    doc.add_paragraph()

def set_margins(sec):
    sec.top_margin = MARGIN_TOP; sec.bottom_margin = MARGIN_BOTTOM; sec.left_margin = MARGIN_LEFT; sec.right_margin = MARGIN_RIGHT; sec.page_width = PAGE_WIDTH; sec.page_height = PAGE_HEIGHT

def add_hdr(sec, txt):
    h = sec.header; h.is_linked_to_previous = False; p = h.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(p.add_run(txt), '宋体', Pt(9))

def add_pgn(sec):
    f = sec.footer; f.is_linked_to_previous = False; p = f.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for xml, typ in [(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>', 'begin'), (f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>', None), (f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>', 'end')]:
        r = p.add_run(); r._element.append(parse_xml(xml))

def render(md_f, out_f, cn='企业名称', pn='项目名称'):
    with open(md_f, 'r', encoding='utf-8') as f: blocks = parse_blocks(f.read())
    doc = Document(); s0 = doc.sections[0]; set_margins(s0)
    for _ in range(6): add_para(doc, '', 'body')
    for txt in [cn, pn, '可行性研究报告']:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(p.add_run(txt), '黑体', Pt(26), True)
    for _ in range(4): add_para(doc, '', 'body')
    p4 = doc.add_paragraph(); p4.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(p4.add_run('编制日期：2026年7月'), '仿宋', Pt(15))
    ns = doc.add_section(); set_margins(ns)
    pd = doc.add_paragraph(); pd.alignment = WD_ALIGN_PARAGRAPH.CENTER; set_font(pd.add_run('目  录'), '黑体', Pt(15), True)
    pt = doc.add_paragraph()
    for xml in [f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>', f'<w:instrText {nsdecls("w")} xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>', f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>']:
        r = pt.add_run(); r._element.append(parse_xml(xml))
    set_font(pt.add_run('（请在Word中右键更新域以生成目录）'), '仿宋', Pt(12))
    r5 = pt.add_run(); r5._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))
    doc.add_page_break(); add_hdr(ns, f'{cn} — 可行性研究报告'); add_pgn(ns)
    for b in blocks:
        if b['type'] in ('heading1', 'heading2', 'heading3'): add_para(doc, b['text'], b['type'])
        elif b['type'] == 'table': add_tbl(doc, b.get('title'), b.get('rows', []))
        elif b['type'] == 'paragraph':
            t = b['text'].strip()
            if t: add_para(doc, t, 'body')
    doc.save(out_f); print(f'报告已生成: {out_f}')

if __name__ == '__main__':
    if len(sys.argv) < 3: print('用法: python render.py 输入.md 输出.docx [企业名称] [项目名称]'); sys.exit(1)
    render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '企业名称', sys.argv[4] if len(sys.argv) > 4 else '项目名称')
```

Integrator执行步骤：
1. 将上述代码写入临时文件 /tmp/render_feasibility.py
2. 执行命令：python3 /tmp/render_feasibility.py 完整可研报告.md 可研报告.docx {企业名称} {项目名称}
3. 确认输出文件生成成功
4. 交付可研报告.docx给用户
