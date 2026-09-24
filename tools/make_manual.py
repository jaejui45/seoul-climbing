# -*- coding: utf-8 -*-
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manual_content import DOC

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
pdfmetrics.registerFont(UnicodeCIDFont('HYGothic-Medium'))
KR, KRB, MONO = 'HYSMyeongJo-Medium', 'HYGothic-Medium', 'Courier'

ACCENT = colors.HexColor('#e2581a')
INK    = colors.HexColor('#1a1a1e')
MUTED  = colors.HexColor('#6c6c73')

HANGUL = re.compile(r'[가-힣]')

def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('·', ' / ').replace('★', '*'))

S = {
 'title':  ParagraphStyle('title',  fontName=KRB, fontSize=21, leading=27, textColor=INK, spaceAfter=3),
 'sub':    ParagraphStyle('sub',    fontName=KR,  fontSize=9.5, leading=14, textColor=MUTED, spaceAfter=16),
 'h1':     ParagraphStyle('h1',     fontName=KRB, fontSize=14, leading=19, textColor=ACCENT,
                          spaceBefore=17, spaceAfter=7),
 'h2':     ParagraphStyle('h2',     fontName=KRB, fontSize=11, leading=15, textColor=INK,
                          spaceBefore=12, spaceAfter=5),
 'p':      ParagraphStyle('p',      fontName=KR,  fontSize=9.5, leading=15, textColor=INK, spaceAfter=7),
 'bullet': ParagraphStyle('bullet', fontName=KR,  fontSize=9.5, leading=15, textColor=INK,
                          leftIndent=12, bulletIndent=3, spaceAfter=3),
 'url':    ParagraphStyle('url',    fontName=MONO, fontSize=10, leading=15,
                          textColor=colors.HexColor('#1155cc'), spaceAfter=9),
 'cellk':  ParagraphStyle('cellk',  fontName=KRB, fontSize=8.5, leading=12.5, textColor=INK),
 'cellv':  ParagraphStyle('cellv',  fontName=KR,  fontSize=8.5, leading=12.5, textColor=INK),
 'box':    ParagraphStyle('box',    fontName=KR,  fontSize=9, leading=14, textColor=INK),
}

def code_style(line):
    """코드 줄에 한글이 있으면 한글 폰트, 아니면 고정폭 폰트."""
    return ParagraphStyle('c', fontName=(KR if HANGUL.search(line) else MONO),
                          fontSize=8.5, leading=13, textColor=colors.HexColor('#101014'))

def code_block(lines):
    rows = [[Paragraph(esc(l) if l else '&nbsp;', code_style(l))] for l in lines]
    t = Table(rows, colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f4f4f6')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#dcdce2')),
        ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
    ]))
    return [Spacer(1, 3), t, Spacer(1, 9)]

def callout(text, kind):
    label, bg, line = (('참고', '#eef4fb', '#3f7fd0') if kind == 'note'
                       else ('주의', '#fdf2ec', '#e2581a'))
    inner = Paragraph('<b>%s</b>  %s' % (label, esc(text)), S['box'])
    t = Table([[inner]], colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)),
        ('LINEBEFORE', (0, 0), (0, -1), 2.5, colors.HexColor(line)),
        ('LEFTPADDING', (0, 0), (-1, -1), 10), ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    return [Spacer(1, 2), t, Spacer(1, 10)]

def kv_table(rows):
    data = [[Paragraph(esc(k), S['cellk']), Paragraph(esc(v), S['cellv'])] for k, v in rows]
    t = Table(data, colWidths=[52 * mm, 113 * mm])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#e0e0e6')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fafafb')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 2), t, Spacer(1, 10)]

story = []
for kind, body in DOC:
    if kind == 'title':
        story += [Paragraph(esc(body[0]), S['title']), Paragraph(esc(body[1]), S['sub'])]
    elif kind in ('h1', 'h2'):
        story.append(Paragraph(esc(body), S[kind]))
    elif kind == 'p':
        story.append(Paragraph(esc(body), S['p']))
    elif kind == 'url':
        story.append(Paragraph('<link href="%s">%s</link>' % (body, body), S['url']))
    elif kind == 'code':
        story += code_block(body)
    elif kind in ('note', 'warn'):
        story += callout(body, kind)
    elif kind == 'kv':
        story += kv_table(body[1])
    elif kind == 'bullet':
        for b in body:
            story.append(Paragraph(esc(b), S['bullet'], bulletText='•'))
        story.append(Spacer(1, 7))
    elif kind == 'pagebreak':
        story.append(PageBreak())

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(KR, 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(22 * mm, 12 * mm, '서울 클라이밍장 웹 매뉴얼')
    canvas.drawRightString(A4[0] - 22 * mm, 12 * mm, str(doc.page))
    canvas.setStrokeColor(colors.HexColor('#e0e0e6'))
    canvas.line(22 * mm, 16 * mm, A4[0] - 22 * mm, 16 * mm)
    canvas.restoreState()

out = os.path.expanduser('~/Downloads/서울클라이밍_웹_수정배포_매뉴얼.pdf')
SimpleDocTemplate(out, pagesize=A4,
                  leftMargin=22 * mm, rightMargin=22 * mm,
                  topMargin=20 * mm, bottomMargin=22 * mm,
                  title='서울 클라이밍장 웹 — 수정·배포 매뉴얼',
                  author='Claude').build(story, onFirstPage=footer, onLaterPages=footer)
print(out)
