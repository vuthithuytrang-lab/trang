"""Lấy giá cho bài TCB "Giá thép hôm nay" -> gia.json (đầu vào của tao_sua.py). Chỉ dùng thư viện chuẩn + curl.

  python3 -I lay_gia.py <file-ra.json>

- Thép thế giới (Steel HRC FOB China, mã V7, sàn LME) — Barchart:
  https://www.barchart.com/futures/quotes/<mã gần nhất còn hiệu lực>/futures-prices?viewName=main
  Tải 1 lần như trình duyệt thường. Barchart hay trả HTTP 202 rỗng / 403 (trang kiểm tra chống máy) → KHÔNG vượt,
  ghi null, tao_sua.py giữ nguyên bảng + cần duyệt.
  Mã hợp đồng tự tính theo ngày: V7 + chữ tháng (F G H J K M N Q U V X Z) + 2 số năm; hợp đồng tháng M coi như
  hết hạn sau ngày làm việc cuối cùng của tháng M (V7V26 → 30/10/2026).
- Thép trong nước — steelonline.vn: https://steelonline.vn/bang-gia-thep-xay-dung-theo-ngay/dd-mm-yyyy
  Thử từ ngày mai lùi dần 10 ngày, lấy trang ĐẦU TIÊN có bảng giá (trang ngày chưa có số chỉ có khung trống).
  Mỗi thương hiệu lấy bảng đầu tiên (tab đầu) dưới tiêu đề "BẢNG GIÁ THÉP <hãng> NGÀY …":
  thấp nhất – cao nhất của mọi ô VNĐ/kg và mọi ô VNĐ/cây. Lưu kèm chữ gốc của ô thấp nhất/cao nhất để đối chiếu.
Nguồn lỗi → null, in "<nguồn> KHÔNG ĐỌC ĐƯỢC".
"""
import datetime, html, json, re, subprocess, sys

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36'
VN = datetime.timezone(datetime.timedelta(hours=7))
CHU_THANG = 'FGHJKMNQUVXZ'
BARCHART = 'https://www.barchart.com/futures/quotes/{ma}/futures-prices?viewName=main'
STEEL = 'https://steelonline.vn/bang-gia-thep-xay-dung-theo-ngay/{d}'


def tai(url):
    """-> (mã HTTP, nội dung). Một lần tải thường, không giả lập gì thêm."""
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '-A', UA, '-w', '\n%{http_code}', url], capture_output=True)
    if r.returncode != 0:
        return 0, ''
    body, _, code = r.stdout.decode('utf-8', 'replace').rpartition('\n')
    return int(code or 0), body


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def ngay_lam_viec_cuoi(nam, thang):
    d = datetime.date(nam + (thang == 12), thang % 12 + 1, 1) - datetime.timedelta(days=1)
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d


def hop_dong_con_han(hom_nay, so_luong=14):
    out, n, t = [], hom_nay.year, hom_nay.month
    while len(out) < so_luong:
        if ngay_lam_viec_cuoi(n, t) >= hom_nay:
            out.append({'ma': f'V7{CHU_THANG[t - 1]}{n % 100:02d}', 'thang': f'{t}/{n}'})
        t += 1
        if t == 13:
            t, n = 1, n + 1
    return out


def so_thap_phan(s):
    """'481.50s' -> 481.5 ; 'unch' -> 0.0 ; '-1.25' -> -1.25"""
    s = (s or '').strip().rstrip('s')
    if s.lower() == 'unch':
        return 0.0
    return float(s.replace(',', '')) if re.fullmatch(r'[+-]?[\d,]+(\.\d+)?', s) else None


def lay_barchart(hom_nay):
    ds = hop_dong_con_han(hom_nay)
    url = BARCHART.format(ma=ds[0]['ma'])
    code, body = tai(url)
    if code != 200 or len(body) < 2000:
        print(f'barchart KHÔNG ĐỌC ĐƯỢC (HTTP {code}, {len(body)} byte – trang kiểm tra chống máy, không vượt)')
        return None
    # Barchart nhúng dữ liệu báo giá dạng JSON trong trang: {"symbol":"V7X26",…,"lastPrice":"481.50s","priceChange":"-1.50",…,"tradeTime":"10/27/26"}
    # (chưa kiểm chứng được vì máy chủ luôn bị chặn — không khớp đủ trường thì coi như không đọc được)
    hd = []
    for x in ds:
        m = re.search(r'"symbol"\s*:\s*"' + x['ma'] + r'"(.{0,3000}?)\}', html.unescape(body), re.S)
        if not m:
            continue
        f = dict(re.findall(r'"(lastPrice|priceChange|tradeTime)"\s*:\s*"([^"]*)"', m.group(1)))
        gia, td = so_thap_phan(f.get('lastPrice')), so_thap_phan(f.get('priceChange'))
        if gia is None or td is None:
            continue
        hd.append(dict(x, gia=gia, thay_doi=td, phien=f.get('tradeTime', '?'),
                       chu_goc=f'lastPrice "{f.get("lastPrice")}", priceChange "{f.get("priceChange")}"'))
    if not hd:
        print('barchart KHÔNG ĐỌC ĐƯỢC (trang tải được nhưng không thấy số của hợp đồng V7 nào)')
        return None
    return {'nguon': url, 'hop_dong': hd}


def khong_dau(s):
    import unicodedata
    s = unicodedata.normalize('NFD', s.lower().replace('đ', 'd'))
    return re.sub(r'\s+', ' ', ''.join(c for c in s if unicodedata.category(c) != 'Mn')).strip()


def so_vn(s):
    """'14.920' -> 14920 (steelonline viết dấu chấm hàng nghìn); '-' -> None"""
    return int(s.replace('.', '')) if re.fullmatch(r'\d{1,3}(\.\d{3})+|\d+', s) else None


def doc_steel(body, ngay):
    hang = {}
    tieu_de = list(re.finditer(r'<h[1-6][^>]*>(.*?)</h[1-6]>', body, re.S))
    for i, h in enumerate(tieu_de):
        m = re.match(r'BẢNG GIÁ THÉP (.+?) NGÀY', chu(h.group(1)))
        if not m:
            continue
        het = tieu_de[i + 1].start() if i + 1 < len(tieu_de) else len(body)
        t = re.search(r'<table.*?</table>', body[h.end():het], re.S)      # bảng đầu tiên = tab đầu
        if not t:
            continue
        kg, cay, loai = [], [], []
        for tr in re.findall(r'<tr.*?</tr>', re.sub(r'<thead.*?</thead>', '', t.group(0), flags=re.S), re.S):
            o = [chu(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
            if len(o) < 11:
                continue
            loai.append(o[1])
            kg += [(so_vn(o[k]), o[k]) for k in (4, 5, 7, 9) if so_vn(o[k])]
            cay += [(so_vn(o[k]), o[k]) for k in (6, 8, 10) if so_vn(o[k])]
        if not kg or not cay:
            continue
        ten = m.group(1).strip()
        hang[khong_dau(ten)] = {'ten': ten, 'chung_loai': loai,
                                'kg': [min(kg)[0], max(kg)[0]], 'cay': [min(cay)[0], max(cay)[0]],
                                'chu_goc': f'VNĐ/kg thấp nhất "{min(kg)[1]}", cao nhất "{max(kg)[1]}"; '
                                           f'VNĐ/cây thấp nhất "{min(cay)[1]}", cao nhất "{max(cay)[1]}"'}
    return hang


def lay_steel(hom_nay):
    for lui in range(-1, 10):
        d = (hom_nay - datetime.timedelta(days=lui)).strftime('%d-%m-%Y')
        url = STEEL.format(d=d)
        code, body = tai(url)
        if code != 200:
            continue
        hang = doc_steel(body, d)
        if hang:
            return {'ngay': d, 'nguon': url, 'hang': hang}
    print('steelonline KHÔNG ĐỌC ĐƯỢC (không có trang ngày nào trong 10 ngày gần đây có bảng giá)')
    return None


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    hom_nay = datetime.datetime.now(VN).date()
    kq = {'chay_luc': datetime.datetime.now(VN).strftime('%H:%M %d/%m/%Y'),
          'barchart': lay_barchart(hom_nay), 'steelonline': lay_steel(hom_nay)}
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if kq['barchart']:
        for x in kq['barchart']['hop_dong']:
            print(f'barchart {x["ma"]} {x["thang"]}: {x["gia"]:.2f} {x["thay_doi"]:+.2f} (phiên {x["phien"]})')
    s = kq['steelonline']
    if s:
        print(f'steelonline ngày {s["ngay"]}: {len(s["hang"])} thương hiệu')
        for v in s['hang'].values():
            print(f'  {v["ten"]}: {v["kg"][0]:,} - {v["kg"][1]:,} VND/kg | {v["cay"][0]:,} - {v["cay"][1]:,} VND/cây')
    # Không thoát lỗi khi thiếu nguồn: tao_sua.py giữ số cũ + cần duyệt


if __name__ == '__main__':
    main()
