"""Lấy giá bạch kim thế giới (USD/oz) cho bài TCB "Giá bạch kim".

Nguồn chính : Yahoo Finance, mã PL=F = hợp đồng tương lai bạch kim tháng gần nhất trên NYMEX (CME Group) – bài TCB cũng nhắc NYMEX.
              API biểu đồ công khai query1/query2.finance.yahoo.com/v8/finance/chart/PL=F (đọc bằng curl thường, không vượt chặn).
Đối chiếu   : TradingView scanner (POST) – NYMEX:PL1! (cùng loại, phải trùng) và TVC:PLATINUM (giá giao ngay, chỉ để tham khảo).
Chạy        : python3 -I lay_gia.py <file-ra.json>      (ví dụ cap-nhat/gia.json)
Lỗi nguồn   : in "Yahoo Finance PL=F KHÔNG ĐỌC ĐƯỢC …", ghi null vào file, thoát mã 1.
"""
import datetime, json, subprocess, sys, time

OUT = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
MA = 'PL=F'
HOSTS = ['query1', 'query2']
TEN = 'Yahoo Finance PL=F'


def curl(url, du_lieu=None):
    cmd = ['curl', '-sS', '-m', '30', '-A', 'gia-bach-kim-lay-gia/1.0']
    if du_lieu is not None:
        cmd += ['-X', 'POST', '-H', 'content-type: application/json', '-d', json.dumps(du_lieu)]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=45)
    if r.returncode != 0:
        raise RuntimeError('curl: ' + (r.stderr.strip().splitlines() or ['lỗi'])[-1][:100])
    return r.stdout


def doc_yahoo():
    loi = '?'
    for lan in range(3):
        for h in HOSTS:
            url = f'https://{h}.finance.yahoo.com/v8/finance/chart/{MA}?range=1mo&interval=1d'
            try:
                raw = curl(url)
                if not raw.lstrip().startswith('{'):
                    raise RuntimeError('nguồn trả về: ' + raw.strip()[:40])   # vd "Too Many Requests" (429) → chờ rồi thử lại, không đổi cách gọi
                d = json.loads(raw)
                r = d['chart']['result'][0]
                off = r['meta'].get('gmtoffset', 0)
                dong = [(datetime.datetime.utcfromtimestamp(t + off).strftime('%d/%m/%Y'), c)
                        for t, c in zip(r['timestamp'], r['indicators']['quote'][0]['close']) if c is not None]
                if len(dong) < 7:
                    raise RuntimeError(f'chỉ có {len(dong)} phiên')
                ls = []
                for i in range(len(dong) - 1, 0, -1):        # mới nhất trước
                    g, truoc = round(dong[i][1], 2), round(dong[i - 1][1], 2)
                    td = round(g - truoc, 2)
                    ls.append({'ngay': dong[i][0], 'gia': g, 'thay_doi': td,
                               'chu_nguon': f'{dong[i][0]} | close {g:.2f} | phiên trước {dong[i - 1][0]} close {truoc:.2f} | đổi {td:+.2f}'})
                ls = ls[:10]
                mt = r['meta'].get('regularMarketTime')
                return {'nguon': f'https://finance.yahoo.com/quote/{MA}/history/', 'api': url, 'ma': MA,
                        'loai': 'hợp đồng tương lai bạch kim tháng gần nhất, NYMEX (USD/oz); phiên mới nhất có thể là giá đang giao dịch',
                        'san': r['meta'].get('exchangeName'), 'ngay': ls[0]['ngay'], 'gia': ls[0]['gia'], 'thay_doi': ls[0]['thay_doi'],
                        'gia_hien_tai': r['meta'].get('regularMarketPrice'),
                        'cap_nhat': (datetime.datetime.utcfromtimestamp(mt).strftime('%Y-%m-%d %H:%M UTC') if mt else None),
                        'lich_su': ls}
            except Exception as e:
                loi = f'{h}: {str(e)[:100]}'
        time.sleep(10 * (lan + 1))
    raise RuntimeError(loi)


def doc_tradingview():
    """Chỉ để đối chiếu giá mới nhất – lỗi thì bỏ qua."""
    kq = {}
    for ten, san, tk in (('futures_pl1', 'futures', 'NYMEX:PL1!'), ('giao_ngay', 'cfd', 'TVC:PLATINUM')):
        try:
            d = json.loads(curl(f'https://scanner.tradingview.com/{san}/scan',
                                {'symbols': {'tickers': [tk]}, 'columns': ['close', 'change_abs']}))
            c, ca = d['data'][0]['d']
            kq[ten] = {'ma': tk, 'gia': round(c, 2), 'thay_doi': round(ca, 2), 'nguon': f'https://scanner.tradingview.com/{san}/scan'}
        except Exception as e:
            kq[ten] = None
            print(f'TradingView {tk} (đối chiếu) KHÔNG ĐỌC ĐƯỢC: {str(e)[:100]}', file=sys.stderr)
    return kq


def ghi(v):
    json.dump(v, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


try:
    kq = doc_yahoo()
except Exception as e:
    ghi(None)
    print(f'{TEN} KHÔNG ĐỌC ĐƯỢC ({e}) – giữ nguyên số cũ, cần duyệt')
    sys.exit(1)
kq['doi_chieu'] = doc_tradingview()
ghi(kq)
print(f'{TEN} ({kq["loai"].split(",")[0]}): {kq["ngay"]} {kq["gia"]:,.2f} ({kq["thay_doi"]:+,.2f}) | {len(kq["lich_su"])} phiên | cập nhật {kq["cap_nhat"]}')
for k, v in kq['doi_chieu'].items():
    print(f'  đối chiếu TradingView {v["ma"]}: {v["gia"]:,.2f} ({v["thay_doi"]:+,.2f})' if v else f'  đối chiếu TradingView {k}: không đọc được')
