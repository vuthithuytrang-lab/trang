"""Đổi ngày "hôm nay" trong bài sang NGÀY HÔM SAU (Trang chốt 21/10/2026: ngày ghi trong bài luôn là ngày hôm sau).

Từ 11/2026 Techcombank ghi ngày ngay trong tiêu đề/đoạn văn ("Giá điều hôm nay 4/11/2026: …") mà công thức cũ
không đổi. Bước này chạy SAU công thức: mọi ngày đủ dạng d/m/yyyy rơi vào hôm nay hoặc 2 ngày trước (giờ VN),
nằm trong chữ (không đụng thuộc tính/đường link, không đụng ô bảng chỉ chứa ngày – đó là dữ liệu bảng giá theo ngày), được đổi thành ngày mai, giữ cách viết (có/không số 0 đầu)
và tô vàng như các chỗ sửa khác.

Dùng: python3 -I doi_ngay_bai.py <bai.html>       (in số chỗ đã đổi)
"""
import datetime as d
import re
import sys

VANG = '<span style="background-color:#ffff00">%s</span>'
NGAY = re.compile(r'(?<![\d/])(\d{1,2})/(\d{1,2})/(\d{4})(?![\d/])')


def hom_nay():
    return (d.datetime.utcnow() + d.timedelta(hours=7)).date()


def doi_chu(chu, to_vang=False, nay=None):
    """Đổi ngày cũ → ngày mai trong một đoạn chữ thường. Trả (chữ mới, số chỗ đổi)."""
    nay = nay or hom_nay()
    mai = nay + d.timedelta(days=1)
    cu = {nay - d.timedelta(days=i) for i in range(3)}
    dem = 0

    def thay(m):
        nonlocal dem
        try:
            x = d.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return m.group(0)
        if x not in cu:
            return m.group(0)
        dem += 1
        ng = ('%02d' if len(m.group(1)) == 2 else '%d') % mai.day
        th = ('%02d' if len(m.group(2)) == 2 else '%d') % mai.month
        s = '%s/%s/%d' % (ng, th, mai.year)
        return VANG % s if to_vang else s

    return NGAY.sub(thay, chu), dem


def doi_html(html, nay=None):
    phan = re.split(r'(<[^>]*>)', html)          # chỉ sửa phần chữ giữa các thẻ
    tong = 0
    trong_vang = False
    o_bang = 0          # ngày trong ô bảng là DỮ LIỆU (bảng giá theo ngày) → không đổi (sửa 06/11/2026)
    for i, p in enumerate(phan):
        if p.startswith('<'):
            if re.match(r'<span[^>]*background-color:#ffff00', p):
                trong_vang = True
            elif p.startswith('</span') and trong_vang:
                trong_vang = False
            elif re.match(r'<t[dh][\s>]', p, re.I):
                o_bang += 1
            elif re.match(r'</t[dh]>', p, re.I):
                o_bang = max(0, o_bang - 1)
            continue
        if o_bang and re.fullmatch(r'\s*\d{1,2}/\d{1,2}/\d{4}\s*', p):
            continue        # ô bảng CHỈ có ngày = dữ liệu bảng giá theo ngày (tiêu đề/sapo nằm trong ô khung vẫn đổi)
        phan[i], n = doi_chu(p, to_vang=not trong_vang, nay=nay)
        tong += n
    return ''.join(phan), tong


if __name__ == '__main__':
    f = sys.argv[1]
    moi, n = doi_html(open(f, encoding='utf-8').read())
    open(f, 'w', encoding='utf-8').write(moi)
    print('đổi ngày trong chữ sang ngày hôm sau: %d chỗ' % n)
