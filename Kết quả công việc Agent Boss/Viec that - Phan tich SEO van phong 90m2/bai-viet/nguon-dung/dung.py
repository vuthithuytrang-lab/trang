# -*- coding: utf-8 -*-
import sys, os, re, html as H
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from noidung_a import A
from noidung_b import B
from noidung_c import C
from noidung_d import D
from noidung_e import E
BLOCKS = A+B+C+D+E

SCR = '/tmp/claude-0/-home-user-trang/b01499db-3e47-587b-84ec-f73e3ff320ac/scratchpad'
IMGDIR = SCR+'/img70'
OUT = SCR+'/bai90'
JPG = OUT+'/anh_jpg'
os.makedirs(JPG, exist_ok=True)

from PIL import Image

def prep(key):
    """webp/png -> jpg ~1000px, tra ve duong dan"""
    dst = os.path.join(JPG, key+'.jpg')
    if os.path.exists(dst): return dst
    src = os.path.join(IMGDIR, key+'.webp')
    if not os.path.exists(src): src = os.path.join(SCR, key+'.png')
    im = Image.open(src).convert('RGB')
    if im.width > 940:
        im = im.resize((940, round(im.height*940/im.width)), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=72, optimize=True)
    return dst

# ============ dem chu ============
def plain(t): return re.sub(r'\*\*(.+?)\*\*', r'\1', t)
words = 0
imgs = []
for b in BLOCKS:
    k = b[0]
    if k in ('h1','h2','h3','h4','p','sapo','lead','note','meta'):
        words += len(plain(b[1]).split())
    elif k == 'ul':
        for it in b[1]: words += len(plain(it).split())
    elif k == 'table':
        for r in b[2]:
            for c in r: words += len(plain(c).split())
    elif k in ('img','sodo'):
        imgs.append(b[1])
    elif k == 'box_tacgia':
        words += len(b[1].split())+len(b[2].split())
print('So chu (uoc):', words, '| So anh:', len(imgs))
dup = [x for x in set(imgs) if imgs.count(x)>1]
print('Anh bi lap:', dup if dup else 'khong')

# ============ WORD ============
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()
st = doc.styles['Normal']
st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'),'Times New Roman')
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2)

def runs(p, text, base_bold=False, size=12, color=None, italic=False):
    for i, seg in enumerate(re.split(r'\*\*(.+?)\*\*', text)):
        if not seg: continue
        r = p.add_run(seg)
        r.bold = base_bold or (i % 2 == 1)
        r.italic = italic
        r.font.size = Pt(size)
        r.font.name = 'Times New Roman'
        if color: r.font.color.rgb = RGBColor(*color)
    return p

def shade(cell, hexv):
    el = OxmlElement('w:shd'); el.set(qn('w:val'),'clear'); el.set(qn('w:fill'),hexv)
    cell._tc.get_or_add_tcPr().append(el)

for b in BLOCKS:
    k = b[0]
    if k == 'h1':
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(6)
        runs(p, b[1], True, 20, (0x1F,0x2A,0x44))
    elif k == 'meta':
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(14)
        runs(p, b[1], False, 10.5, (0x6B,0x72,0x80), italic=True)
    elif k == 'sapo':
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        runs(p, b[1], False, 12.5)
    elif k == 'h2':
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(20); p.paragraph_format.space_after = Pt(8)
        runs(p, b[1], True, 16, (0x0B,0x3D,0x91))
    elif k == 'h3':
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
        runs(p, b[1], True, 13.5, (0x1F,0x2A,0x44))
    elif k == 'h4':
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4)
        runs(p, b[1], True, 12.5, (0x0B,0x3D,0x91))
    elif k == 'lead':
        p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
        runs(p, b[1], True, 12, (0x0D,0x6E,0x4F))
    elif k == 'p':
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        runs(p, b[1], False, 12)
    elif k == 'note':
        p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.left_indent = Cm(0.5)
        runs(p, b[1], False, 10.5, (0x5B,0x64,0x78), italic=True)
    elif k == 'ul':
        for it in b[1]:
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(4)
            runs(p, it, False, 12)
    elif k == 'table':
        hd, rows = b[1], b[2]
        t = doc.add_table(rows=1, cols=len(hd)); t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(hd):
            c = t.rows[0].cells[i]; c.text = ''
            runs(c.paragraphs[0], h, True, 10.5, (0xFF,0xFF,0xFF))
            shade(c, '0B3D91')
        for ri, r in enumerate(rows):
            cells = t.add_row().cells
            for i, v in enumerate(r):
                cells[i].text = ''
                runs(cells[i].paragraphs[0], v, False, 10.5)
                if ri % 2 == 1: shade(cells[i], 'F2F5FA')
        doc.add_paragraph().paragraph_format.space_after = Pt(6)
    elif k in ('img','sodo'):
        path = prep(b[1])
        doc.add_picture(path, width=Cm(15.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(12)
        runs(p, b[2], False, 10, (0x5B,0x64,0x78), italic=True)
    elif k == 'box_tacgia':
        t = doc.add_table(rows=1, cols=1); t.style = 'Table Grid'
        c = t.rows[0].cells[0]; shade(c, 'F2F5FA'); c.text = ''
        runs(c.paragraphs[0], b[1], True, 11.5, (0x0B,0x3D,0x91))
        runs(c.add_paragraph(), b[2], False, 10.5, (0x33,0x3A,0x48))
        doc.add_paragraph()

docx_path = OUT + '/bai-viet-thiet-ke-van-phong-90m2.docx'
doc.save(docx_path)
print('DOCX:', docx_path, round(os.path.getsize(docx_path)/1048576, 2), 'MB')
