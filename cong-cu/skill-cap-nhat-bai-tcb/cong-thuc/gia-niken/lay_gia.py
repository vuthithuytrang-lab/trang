#!/usr/bin/env python3
"""Lấy giá Niken LME hằng ngày cho bài TCB "Giá Niken hôm nay" (curl thường, không vượt chặn, không tắt kiểm tra TLS).

Dùng: python3 -I lay_gia.py <file-ra.json>        (thường là cap-nhat/gia.json)

Nguồn chính : Westmetall, bảng LME Nickel hằng ngày (giá chính thức LME, USD/tấn) – cột "LME Nickel 3-month".
Nguồn đối chiếu: TradingView scanner (hợp đồng LME Nickel gần nhất, chỉ có giá mới nhất) – chỉ để soát độ lệch, KHÔNG ghi vào bài.
Nguồn lỗi → in "<nguồn> KHÔNG ĐỌC ĐƯỢC …" và ghi null; vẫn luôn ghi file ra.
"""
import datetime as dt
import html
import json
import re
import subprocess
import sys

CHUOI = 'LME Nickel 3-month'
DUNG_SAI = 3.0                # % lệch tối đa giữa 2 nguồn (TradingView là giá đang chạy, Westmetall là giá chốt phiên)
COT = 2                       # cột trong bảng Westmetall: 0 ngày, 1 Cash-Settlement, 2 3-month, 3 stock
WM = 'https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Ni_cash'
TV = 'https://scanner.tradingview.com/futures/scan'
THANG = {m: i for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                     'September', 'October', 'November', 'December'], 1)}


def curl(url, post=None):
    cmd = ['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}']
    if post:
        cmd += ['-X', 'POST', '-H', 'content-type: application/json', '-d', post]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        raise RuntimeError('curl lỗi ' + (r.stderr.strip()[:100] or str(r.returncode)))
    body, _, ma = r.stdout.rpartition('\n')
    if ma != '200':
        raise RuntimeError('HTTP ' + ma)
    return body


def so(s):
    return float(s.replace(',', ''))


def doc_nam(nam):
    """các dòng (ngày, giá 3M) của 1 năm trên Westmetall, mới nhất trước"""
    h = curl(WM + (f'&year={nam}' if nam != dt.date.today().year else ''))
    kq = []
    for tr in re.findall(r'<tr>(.*?)</tr>', h, re.S):
        td = [html.unescape(re.sub(r'<[^>]+>', '', x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
        m = re.fullmatch(r'(\d{1,2})\. (\w+) (\d{4})', td[0]) if td else None
        if not m or len(td) < 4 or m.group(2) not in THANG:
            continue
        try:
            g = so(td[COT])
        except ValueError:
            continue                                       # ô trống / "-" (ngày chưa có giá)
        d = dt.date(int(m.group(3)), THANG[m.group(2)], int(m.group(1)))
        kq.append((d, g, f'{td[0]} | Cash {td[1]} | 3-month {td[2]}'))
    kq.sort(key=lambda x: x[0], reverse=True)
    return kq


def doc_westmetall():
    rows = doc_nam(dt.date.today().year)
    if len(rows) < 8:                                      # đầu năm: lấy thêm năm trước để đủ 6+ phiên
        rows += doc_nam(dt.date.today().year - 1)
    seen, ls = set(), []
    for d, g, c in rows:
        if d not in seen:
            seen.add(d)
            ls.append((d, g, c))
    ls.sort(key=lambda x: x[0], reverse=True)
    if len(ls) < 6:
        raise RuntimeError(f'chỉ thấy {len(ls)} phiên (cần ít nhất 6)')
    out = []
    for i, (d, g, c) in enumerate(ls[:10]):
        if i + 1 >= len(ls):
            break
        t = round(g - ls[i + 1][1], 2)
        out.append({'ngay': d.strftime('%d/%m/%Y'), 'gia': g, 'thay_doi': t,
                    'chu_nguon': f'{c} (phiên trước {ls[i + 1][0].strftime("%d/%m/%Y")}: {ls[i + 1][1]:,.2f})'})
    return {'ten': 'Westmetall', 'nguon': WM, 'chuoi': CHUOI, 'don_vi': 'USD/tấn',
            'ngay_du_lieu': [x['ngay'] for x in out], 'lich_su': out}


def doc_tradingview():
    body = json.dumps({'filter': [{'left': 'exchange', 'operation': 'equal', 'right': 'LME'},
                                  {'left': 'name', 'operation': 'match', 'right': 'NI'},
                                  {'left': 'description', 'operation': 'match', 'right': 'Nickel Futures'}],
                       'columns': ['name', 'description', 'close', 'change_abs', 'expiration'],
                       'sort': {'sortBy': 'expiration', 'sortOrder': 'asc'}, 'range': [0, 3]})
    d = json.loads(curl(TV, body))['data']
    if not d:
        raise RuntimeError('không có hợp đồng')
    n, mo_ta, close, chg, hh = d[0]['d']
    return {'ten': 'TradingView', 'nguon': TV, 'hop_dong': n, 'mo_ta': mo_ta, 'gia': round(close, 2),
            'thay_doi': round(chg, 2), 'gia_phien_truoc': round(close - chg, 2), 'het_han': str(hh),
            'ngay_doc': dt.datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}


def main():
    ra = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    kq = {'westmetall': None, 'tradingview': None, 'doi_chieu': None}

    def ghi():
        json.dump(kq, open(ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ghi()
    for k, ten, f in (('westmetall', 'Westmetall', doc_westmetall), ('tradingview', 'TradingView', doc_tradingview)):
        try:
            kq[k] = f()
        except Exception as e:
            kq[k] = None
            print(f'{ten} KHÔNG ĐỌC ĐƯỢC ({str(e)[:120]})')
        ghi()
    w, t = kq['westmetall'], kq['tradingview']
    if w:
        x = w['lich_su'][0]
        print(f'Westmetall {CHUOI}: {len(w["lich_su"])} phiên, mới nhất {x["ngay"]} {x["gia"]:,.2f} ({x["thay_doi"]:+,.2f}) | ngày {", ".join(w["ngay_du_lieu"][:6])}')
    if t:
        print(f'TradingView {t["hop_dong"]}: {t["gia"]:,.2f} ({t["thay_doi"]:+,.2f}), phiên trước {t["gia_phien_truoc"]:,.2f} | {t["ngay_doc"]}')
    if w and t:
        l = w['lich_su'][0]['gia']
        p = abs(l - t['gia']) / l * 100
        kq['doi_chieu'] = {'westmetall': l, 'tradingview': t['gia'], 'lech_phan_tram': round(p, 2), 'khop': p <= DUNG_SAI}
        ghi()
        print(f'Đối chiếu: Westmetall mới nhất {l:,.2f} vs TradingView hiện tại {t["gia"]:,.2f} → lệch {p:.2f}%'
              + ('' if p <= DUNG_SAI else f' (QUÁ {DUNG_SAI}%)'))
    sys.exit(0 if w else 1)


if __name__ == '__main__':
    main()
