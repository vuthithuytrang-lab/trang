"""Lấy giá 10 kim loại cho bài TCB "Giá kim loại thế giới" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

Nguồn (Trang chọn): https://www.thitruonghanghoa.com/gia-kim-loai — bảng "Bảng giá Kim loại" (trang dựng sẵn
trên máy chủ, không cần trình duyệt). Mỗi dòng có thẻ data-live-commodity="<id>" với các ô local-price (VNĐ),
diff-arrow (arrow_upward / arrow_downward), diff-pct ("0.10%"). KHÔNG dùng dải chạy chữ đầu trang (số khác bảng).
Khóa mỗi kim loại theo tên tiếng Anh dưới tên (GOLD / XAU USD, SILVER…, IRON ORE, TIN) — không theo vị trí.
Trang không ghi giờ cập nhật (giá chạy theo thời gian thực) → ghi giờ lấy số (giờ VN).
Kim loại nào không đọc được -> null + in "<tên> KHÔNG ĐỌC ĐƯỢC"; cả trang lỗi -> mọi kim loại null.

DỰ PHÒNG MIỄN PHÍ (06/11/2026 – thitruonghanghoa chặn máy GitHub Actions): kim loại nào trang chính không đọc được thì lấy
từ TradingView (scanner.tradingview.com, miễn phí, không cần chìa) đúng mã mà thitruonghanghoa dùng, rồi quy ra VNĐ
theo đúng cách của thitruonghanghoa: giá USD × hệ số đơn vị × tỷ giá USD/VND (FX_IDC:USDVND; đối chiếu open.er-api.com).
  Vàng/Bạc/Bạch kim: TVC:GOLD/SILVER/PLATINUM (USD/ounce) × 1,205653 (ounce/lượng) → VNĐ/lượng
  Đồng: COMEX:HG1! (USD/pound) × 2.204,623 → VNĐ/tấn    Quặng sắt: COMEX:TIO1! (USD/dmtu) → VNĐ/dmtu
  Niken/Chì/Nhôm/Kẽm/Thiếc: LME:NI1!/PB1!/AH1!/ZS1!/SN1! (USD/tấn) → VNĐ/tấn
  % thay đổi = % thay đổi trong ngày TradingView báo. Tỷ giá TradingView khác tỷ giá thitruonghanghoa vài chục đồng
  → số lệch nhẹ (~0,1%) so với trang chính; tao_sua ghi cần duyệt. Thử: KIM_LOAI_DU_PHONG=1 python3 -I lay_gia.py x.json
"""
import datetime, html, json, os, re, subprocess, sys

URL = 'https://www.thitruonghanghoa.com/gia-kim-loai'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
# khóa -> nhận diện bằng tên tiếng Anh in dưới tên kim loại trong bảng nguồn
KIM_LOAI = {
    'vang': r'^GOLD\b', 'bac': r'^SILVER\b', 'dong': r'^COPPER$', 'bach_kim': r'^PLATINUM$', 'niken': r'^NICKEL$',
    'chi': r'^LEAD$', 'nhom': r'^ALUMINU?M$', 'kem': r'^ZINC$', 'quang_sat': r'^IRON ORE', 'thiec': r'^TIN$',
}


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '--retry', '2', '-A', UA, '-w', '\n%{http_code}', url],
                       capture_output=True)
    body = r.stdout.decode('utf-8', 'replace')
    body, _, code = body.rpartition('\n')
    if r.returncode != 0 or code != '200':
        raise RuntimeError(f'HTTP {code} {r.stderr.decode()[:120]}')
    return body


def doc_bang(s):
    """Các dòng bảng giá (bản máy tính: <tr class="hidden md:table-row">) -> {khóa: {...}}."""
    kq = {}
    for tr in re.findall(r'<tr[^>]*md:table-row[^>]*>(.*?)</tr>', s, re.S):
        ten = re.search(r'<span[^>]*font-bold[^>]*>([^<]+)</span>\s*<span[^>]*block[^>]*>([^<]+)</span>', tr)
        if not ten:
            continue
        ten_vn, ten_en = chu(ten.group(1)), chu(ten.group(2)).upper()
        k = next((k for k, p in KIM_LOAI.items() if re.search(p, ten_en)), None)
        if not k or k in kq:
            continue
        f = {m.group(1): chu(m.group(2)) for m in
             re.finditer(r'data-live-field="([a-z-]+)"[^>]*>(.*?)</span>', tr, re.S)}
        don_vi = re.search(r'data-live-field="local-price"[^>]*>[^<]*</span>\s*<span[^>]*>([^<]+)</span>', tr)
        gia = re.sub(r'\D', '', f.get('local-price', ''))
        pct = re.fullmatch(r'(\d+(?:\.\d+)?)\s*%', f.get('diff-pct', ''))
        mui = f.get('diff-arrow', '')
        if not gia or not pct or mui not in ('arrow_upward', 'arrow_downward', 'remove', ''):
            print(f'{ten_vn} ({ten_en}): dòng nguồn lạ – bỏ qua', file=sys.stderr)
            continue
        p = float(pct.group(1))
        kq[k] = {'ten_nguon': f'{ten_vn} ({ten_en})', 'gia': int(gia), 'don_vi': chu(don_vi.group(1)) if don_vi else '',
                 'thay_doi': -p if mui == 'arrow_downward' else p, 'chieu': mui,
                 'gia_goc': f.get('local-price', ''), 'thay_doi_goc': f.get('diff-pct', '')}
    return kq


TV = {  # khóa: (sàn scanner, mã, hệ số đổi ra đơn vị của bài, đơn vị, tên)
    'vang': ('cfd', 'TVC:GOLD', 37.5 / 31.1034768, 'VNĐ / lượng', 'Vàng (TVC:GOLD, USD/ounce)'),
    'bac': ('cfd', 'TVC:SILVER', 37.5 / 31.1034768, 'VNĐ / lượng', 'Bạc (TVC:SILVER, USD/ounce)'),
    'bach_kim': ('cfd', 'TVC:PLATINUM', 37.5 / 31.1034768, 'VNĐ / lượng', 'Bạch kim (TVC:PLATINUM, USD/ounce)'),
    'dong': ('futures', 'COMEX:HG1!', 1e6 / 453.59237, 'VNĐ / tấn', 'Đồng (COMEX:HG1!, USD/pound)'),
    'niken': ('futures', 'LME:NI1!', 1, 'VNĐ / tấn', 'Niken (LME:NI1!, USD/tấn)'),
    'chi': ('futures', 'LME:PB1!', 1, 'VNĐ / tấn', 'Chì (LME:PB1!, USD/tấn)'),
    'nhom': ('futures', 'LME:AH1!', 1, 'VNĐ / tấn', 'Nhôm (LME:AH1!, USD/tấn)'),
    'kem': ('futures', 'LME:ZS1!', 1, 'VNĐ / tấn', 'Kẽm (LME:ZS1!, USD/tấn)'),
    'quang_sat': ('futures', 'COMEX:TIO1!', 1, 'VNĐ / dmtu', 'Quặng sắt 62% Fe (COMEX:TIO1!, USD/dmtu)'),
    'thiec': ('futures', 'LME:SN1!', 1, 'VNĐ / tấn', 'Thiếc (LME:SN1!, USD/tấn)'),
}


def quet(san, ma):
    r = subprocess.run(['curl', '-sS', '-m', '30', '--retry', '2', '-X', 'POST', f'https://scanner.tradingview.com/{san}/scan',
                        '-H', 'content-type: application/json', '-A', 'vttt-sn-cap-nhat-bai',
                        '-d', json.dumps({'symbols': {'tickers': ma}, 'columns': ['close', 'change', 'last_bar_update_time']})],
                       capture_output=True)
    return {x['s']: x['d'] for x in json.loads(r.stdout or b'{}').get('data', [])}


def ty_gia():
    """USD/VND: TradingView FX_IDC:USDVND, đối chiếu open.er-api.com (lệch > 1% → không dùng)."""
    tv = er = None
    try:
        tv = quet('forex', ['FX_IDC:USDVND']).get('FX_IDC:USDVND', [None])[0]
    except Exception:
        pass
    try:
        r = subprocess.run(['curl', '-sS', '-m', '20', 'https://open.er-api.com/v6/latest/USD'], capture_output=True)
        er = json.loads(r.stdout)['rates']['VND']
    except Exception:
        pass
    if tv and er and abs(tv - er) / er > 0.01:
        print(f'tỷ giá lệch: TradingView {tv} ≠ open.er-api {er:.0f} – không dùng dự phòng', file=sys.stderr)
        return None, ''
    return (tv, 'FX_IDC:USDVND (TradingView)') if tv else ((er, 'open.er-api.com') if er else (None, ''))


def du_phong(thieu, luc):
    if not thieu:
        return {}
    fx, nguon_fx = ty_gia()
    if not fx:
        print('dự phòng TradingView: không có tỷ giá USD/VND', file=sys.stderr)
        return {}
    d = {}
    for san in ('cfd', 'futures'):
        ma = [TV[k][1] for k in thieu if TV[k][0] == san]
        try:
            d.update(quet(san, ma) if ma else {})
        except Exception as e:
            print('TradingView LỖI', san, str(e)[:100], file=sys.stderr)
    kq = {}
    for k in thieu:
        san, ma, he_so, dv, ten = TV[k]
        v = d.get(ma)
        if not v or not v[0] or v[1] is None or not v[2] or luc.timestamp() - v[2] > 4 * 86400:
            continue                                  # thiếu số hoặc số cũ hơn 4 ngày → coi như không đọc được
        p = round(v[1], 2)
        kq[k] = {'ten_nguon': ten, 'gia': round(v[0] * he_so * fx), 'don_vi': dv, 'thay_doi': p,
                 'chieu': 'arrow_upward' if p > 0 else ('arrow_downward' if p < 0 else 'remove'),
                 'gia_goc': f'{v[0]} USD × {he_so:.6g} × tỷ giá {fx:,.0f} ({nguon_fx})', 'thay_doi_goc': f'{abs(p):.2f}%',
                 'nguon': f'https://www.tradingview.com/symbols/{ma.replace(":", "-")}/',
                 'cap_nhat': 'TradingView cập nhật lúc ' + datetime.datetime.fromtimestamp(v[2], luc.tzinfo).strftime('%Hh%M %d/%m/%Y') + ' giờ VN'}
    return kq


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    luc = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    bang = {}
    if not os.environ.get('KIM_LOAI_DU_PHONG'):
        try:
            bang = doc_bang(tai(URL))
        except Exception as e:
            print('thitruonghanghoa LỖI', str(e)[:150], file=sys.stderr)
    cap_nhat = f'lấy lúc {luc:%Hh%M} giờ VN {luc:%d/%m/%Y} (nguồn cập nhật theo thời gian thực)'
    kq = {'_nguon': URL, '_cap_nhat': cap_nhat}
    for k in KIM_LOAI:
        v = bang.get(k)
        kq[k] = dict(v, nguon=URL, cap_nhat=cap_nhat) if v else None
    dp = du_phong([k for k in KIM_LOAI if not kq[k]], luc)
    if dp:
        print('thitruonghanghoa thiếu', ', '.join(dp), '→ lấy dự phòng TradingView (quy ra VNĐ theo tỷ giá)', file=sys.stderr)
        kq.update(dp)
        kq['_du_phong'] = sorted(dp)
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in KIM_LOAI:
        v = kq[k]
        print(k.ljust(10), f"{v['ten_nguon']} | {v['gia']:,} {v['don_vi']} | {v['thay_doi']:+.2f}% | {cap_nhat}"
              if v else f'{k} KHÔNG ĐỌC ĐƯỢC')
    if any(kq[k] is None for k in KIM_LOAI):
        sys.exit(1)


if __name__ == '__main__':
    main()
