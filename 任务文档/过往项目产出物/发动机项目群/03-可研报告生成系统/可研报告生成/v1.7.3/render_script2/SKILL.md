---
name: render_script2
description: 可研报告Word渲染脚本。Leader在步骤12加载此SKILL后，将正文中的Python代码写入临时文件并执行。
---

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
    set_font(pt.add_run('（目录将在打开文档时自动生成）'), '仿宋', Pt(12))
    r5 = pt.add_run(); r5._element.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))
    doc.add_page_break(); add_hdr(ns, f'{cn} — 可行性研究报告'); add_pgn(ns)
    for b in blocks:
        if b['type'] in ('heading1', 'heading2', 'heading3'): add_para(doc, b['text'], b['type'])
        elif b['type'] == 'table': add_tbl(doc, b.get('title'), b.get('rows', []))
        elif b['type'] == 'paragraph':
            t = b['text'].strip()
            if t: add_para(doc, t, 'body')
    # 设置Word打开时自动更新所有域（包括目录）
    from lxml import etree
    ns_w = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    settings = doc.settings.element
    uf = settings.find(f'{{{ns_w}}}updateFields')
    if uf is None:
        uf = etree.SubElement(settings, f'{{{ns_w}}}updateFields')
        uf.set(f'{{{ns_w}}}val', 'true')
    doc.save(out_f); print(f'报告已生成: {out_f}')

if __name__ == '__main__':
    if len(sys.argv) < 3: print('用法: python render.py 输入.md 输出.docx [企业名称] [项目名称]'); sys.exit(1)
    render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '企业名称', sys.argv[4] if len(sys.argv) > 4 else '项目名称')
```
