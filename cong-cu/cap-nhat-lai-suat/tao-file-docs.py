#!/usr/bin/env python3
"""Dựng file HTML của bài Techcombank (đã cập nhật, tô vàng phần đổi) để tải lên Google Drive thành Google Docs.
Chạy sau lay-so-lieu.py:  python3 tao-file-docs.py dd/mm/yyyy
Đầu ra: tam/bai-viet.html
"""
import re, json, sys, html

HOM_NAY = sys.argv[1]                      # ví dụ 04/10/2026
THANG_NAY = HOM_NAY[3:]                    # ví dụ 10/2026
VANG = 'background-color:#ffff00'
os_dir = 'tam/'
src = open(os_dir + '88bfca.html', encoding='utf-8').read()
res = json.load(open(os_dir + 'result.json'))
doi_ngay = []                              # ghi lại vị trí đổi ngày/tháng cho báo cáo


def to_vang(x):
    return f'<span style="{VANG}">{x}</span>'


def sua_ngay(text, vi_tri):
    """Đổi mọi dd/mm/yyyy khác hôm nay -> hôm nay, và 'tháng mm/yyyy' khác tháng này -> tháng này; chỉ tô phần đổi."""
    def d(m):
        if m.group(0) == HOM_NAY:
            return m.group(0)
        doi_ngay.append(f'{vi_tri}: {m.group(0)} → {HOM_NAY}')
        return to_vang(HOM_NAY)
    text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', d, text)

    def t(m):
        if m.group(2) == THANG_NAY:
            return m.group(0)
        doi_ngay.append(f'{vi_tri}: tháng {m.group(2)} → tháng {THANG_NAY}')
        return m.group(1) + to_vang(THANG_NAY)
    return re.sub(r'(tháng\s*(?:<[^>]+>\s*)*)(\d{2}/\d{4})(?!\d)', t, text)


# ---------- Phần đầu bài: tiêu đề, sapo, ngày đăng ----------
h1 = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', src, re.S).group(1)).strip()
sapo = html.unescape(re.search(r'article-header-body--subTitle">(.*?)</p>', src, re.S).group(1)).strip()
iso = re.search(r'article-header-body--date">(\d{4})-(\d{2})-(\d{2})', src)
ngay_dang = f'{iso.group(3)}/{iso.group(2)}/{iso.group(1)}'

# Docs không nhận nền xám cho đoạn văn khi nhập HTML -> đặt phần đầu bài trong 1 ô bảng nền xám, không viền
O = 'style="font-family:Arial;text-align:center;margin:0;font-size:11pt;font-weight:400;'
head = ('<table style="border-collapse:collapse;width:100%"><tbody><tr>'
        '<td style="background-color:#f5f6f8;border:0pt solid #f5f6f8;padding:4pt">'
        f'<h1 {O}color:#000000;line-height:1.5"><span style="font-weight:400">{sua_ngay(h1, "Tiêu đề")}</span></h1>'
        f'<p {O}color:#8d8175;line-height:1.25">{sua_ngay(sapo, "Sapo")}</p>'
        f'<p {O}color:#a2a2a2;font-style:italic;line-height:1.5">{sua_ngay(ngay_dang, "Ngày đăng")}</p>'
        '</td></tr></tbody></table><p></p>')
head = head.replace(VANG + '"', VANG + ';font-weight:400"')

# ---------- Thân bài: các khối văn bản của bài (bỏ công cụ tính, nút bấm) ----------
khoi = re.findall(r'<div id="text-[0-9a-f]+" class="cmp-text">\s*<html><head></head><body>(.*?)</body></html>', src, re.S)
# chỉ lấy tới hết phần liên hệ cuối bài (sau đó là khối quảng cáo của website)
khoi = khoi[:next(i for i, k in enumerate(khoi) if 'call_center' in k) + 1]
body = '\n'.join(khoi)
body = body.replace('="/content/', '="https://techcombank.com/content/').replace('href="/', 'href="https://techcombank.com/')
body = re.sub(r'\s*\n\s*"', '"', body).replace('style="\t', 'style="')
# figure -> đoạn căn giữa (Docs không hiểu thẻ figure)
body = re.sub(r'<figure[^>]*>\s*(<img[^>]*>)(.*?)</figure>',
              r'<p style="text-align:center">\1</p><p style="text-align:center">\2</p>', body, flags=re.S)
body = re.sub(r'(<img )', r'\1style="width:100%;max-width:451pt" ', body)

# ---------- Sửa số trong 2 bảng lãi suất ----------
KY = ['1', '3', '6', '12', '18', '24', '36']
sua = {}
for c in res['changes'] + res['caseA']:
    sua[(c[0], c[1], c[2])] = (c[3], c[4])

bang = list(re.finditer(r'<table.*?</table>', body, re.S))
bang_ls = [m for m in bang if 'tháng</b>' in m.group(0)]
assert len(bang_ls) == 2, 'không thấy đủ 2 bảng lãi suất'
moi = body
for ten_bang, m in zip(['Tại quầy', 'Online'], bang_ls):
    tb = m.group(0)

    def sua_dong(rm):
        row = rm.group(0)
        cells = re.findall(r'<td>.*?</td>', row, re.S)
        ten = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', cells[0]))).strip()
        ten = ten.replace(' (', '(').replace('(', ' (')
        out = row
        for i, k in enumerate(KY):
            key = (ten_bang, ten, k)
            if key not in sua:
                continue
            cu, moi_so = sua[key]
            cell = cells[i + 1]
            cell2, n = re.subn(r'>(\s*)' + re.escape(cu) + r'(\s*)<', lambda x: '>' + x.group(1) + to_vang(moi_so) + x.group(2) + '<', cell, count=1)
            assert n == 1, f'không thay được {key}'
            out = out.replace(cell, cell2, 1)
            del sua[key]
        return out
    tb2 = re.sub(r'<tr>.*?</tr>', sua_dong, tb, flags=re.S)
    moi = moi.replace(tb, tb2, 1)
assert not sua, f'còn ô chưa thay: {sua}'
body = moi

# kẻ bảng giống file mẫu: viền xám nhạt, cột tên ngân hàng 92.5pt, cột kỳ hạn 51.3pt
TD = 'border:1pt solid #dedede'
def ke_bang(m):
    tb = m.group(0)
    if 'tháng</b>' not in tb:
        return tb.replace('<td>', f'<td style="{TD};padding:4pt">')
    # độ rộng cột chỉ cần ghi ở dòng tiêu đề, Docs lấy theo dòng đầu
    dau, con_lai = tb.split('</tr>', 1)
    i = [0]
    def o(_):
        i[0] += 1
        return f'<td style="{TD};width:{92.5 if i[0] == 1 else 51.3}pt">'
    dau = re.sub(r'<td>', o, dau)
    return dau + '</tr>' + con_lai.replace('<td>', f'<td style="{TD}">')
body = re.sub(r'<table.*?</table>', ke_bang, body, flags=re.S)
body = re.sub(r'<table[^>]*>', '<table style="border-collapse:collapse">', body)

# ngày/tháng trong đoạn văn (ngoài bảng)
phan = re.split(r'(<table.*?</table>)', body, flags=re.S)
body = ''.join(p if p.startswith('<table') else sua_ngay(p, 'Đoạn văn') for p in phan)

doc = ('<html><head><meta charset="utf-8"></head>'
       '<body style="font-family:Arial;font-size:11pt">' + head + body + '</body></html>')
open(os_dir + 'bai-viet.html', 'w', encoding='utf-8').write(doc)
# bản gọn để tải lên Drive (bỏ xuống dòng thừa, thuộc tính không cần cho Docs)
g = re.sub(r'\s*\n\s*', ' ', doc).replace('&#61;', '=')
g = re.sub(r'(</(?:p|td|tr|li|ul|table|h1|h2|tbody)>) +(<)', r'\1\2', g)
g = re.sub(r'(<(?:tr|td|tbody|ul|table)[^>]*>) +(<)', r'\1\2', g)
g = re.sub(r' (?:class|id|rel|target)="[^"]*"', '', g).replace('style="text-align: center;"', 'align="center"')
g = re.sub(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', lambda m: '#%02x%02x%02x' % tuple(int(x) for x in m.groups()), g)
g = re.sub(r'style="([^"]*)"', lambda m: 'style="' + re.sub(r'\s*([:;])\s*', r'\1', m.group(1)).rstrip(';') + '"', g)
g = g.replace('border:1pt solid #dedede', 'border:1px solid #ddd')
open(os_dir + 'bai-viet.min.html', 'w', encoding='utf-8').write(g)
json.dump(doi_ngay, open(os_dir + 'doi-ngay.json', 'w'), ensure_ascii=False)
print('Đã dựng tam/bai-viet.html', len(doc), 'ký tự')
print('Đổi ngày/tháng:', doi_ngay or 'không có')
print('Ô tô vàng:', len(res['changes']) + len(res['caseA']))
