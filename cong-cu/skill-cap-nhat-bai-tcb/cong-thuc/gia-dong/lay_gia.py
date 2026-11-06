"""Lấy giá cho bài TCB "Giá đồng hôm nay" -> gia.json (đầu vào của tao_sua.py).

  python3 -I lay_gia.py <file-ra.json>

- phe_lieu (đổi 06/11/2026 – nguồn cũ thumuaphelieugiacao24h.vn không cập nhật từ 04/05/2026):
  bảng phế liệu trên https://hoangngocdiep.vn/bang-gia-phe-lieu-hom-nay-moi-nhat/ (ghi "cập nhật sáng ngày dd/mm/yyyy").
  Lấy 4 dòng theo thứ tự bài: Đồng cáp, Đồng đỏ, Đồng vàng, Đồng dây điện cháy.
- the_gioi (đổi 06/11/2026 – Barchart chặn máy chủ): bài đang ghi mã hợp đồng NHÔM COMEX (ALI…, USD/tấn) → lấy đúng
  các hợp đồng ALI từ TradingView scanner (giữ nội dung bài; vẫn ghi cần duyệt "ALI là nhôm, không phải đồng").
Tải 1 lần như công cụ chung (curl), không giả mạo, không lách chặn. Nguồn lỗi -> null + in "<nguồn> KHÔNG ĐỌC ĐƯỢC".
"""
import html, json, re, subprocess, sys

PL = 'https://hoangngocdiep.vn/bang-gia-phe-lieu-hom-nay-moi-nhat/'
TV = 'https://scanner.tradingview.com/futures/scan'
THU_TU = ['đồng cáp', 'đồng đỏ', 'đồng vàng', 'đồng dây điện cháy']
BC = 'https://www.barchart.com/futures/quotes/HG*0/futures-prices?viewName=main'


def tai(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '2', '-A', 'Mozilla/5.0', '-w', '\n%{http_code}', url],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[:120].strip())
    body, _, code = r.stdout.decode('utf-8', 'replace').rpartition('\n')
    if code != '200':
        raise RuntimeError(f'HTTP {code}')
    return body


def chu(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def so(x):
    d = re.sub(r'\D', '', x)
    return int(d) if d else None


def phe_lieu():
    s = tai(PL)
    m = re.search(r'cập nhật[^.<]{0,40}?(\d{1,2})/(\d{1,2})/(\d{4})', chu(s), re.I)
    cap_nhat = f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}T07:00:00+07:00' if m else '?'
    for t in re.findall(r'<table.*?</table>', s, re.S | re.I):
        if 'đồng cáp' not in chu(t).lower():
            continue
        theo = {}
        for r in re.findall(r'<tr.*?</tr>', t, re.S | re.I):
            c = [chu(x) for x in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S | re.I)]
            if len(c) >= 2:
                m2 = re.fullmatch(r'([\d.,]+)\s*[–—-]\s*([\d.,]+)', c[-1])
                if m2:
                    theo[c[-2].lower()] = {'ten': c[-2], 'thap': so(m2.group(1)), 'cao': so(m2.group(2)), 'chu_goc': f'{c[-2]} | {c[-1]}'}
        dong = [theo[k] for k in THU_TU if k in theo]
        if len(dong) == len(THU_TU):
            return {'dong': dong, 'cap_nhat': cap_nhat, 'nguon': PL}
    raise RuntimeError('không thấy đủ 4 dòng đồng (cáp, đỏ, vàng, dây điện cháy)')


def the_gioi():
    body = json.dumps({'filter': [{'left': 'name', 'operation': 'match', 'right': 'ALI'}, {'left': 'exchange', 'operation': 'equal', 'right': 'COMEX'}],
                       'columns': ['name', 'close', 'change', 'expiration', 'last_bar_update_time'],
                       'sort': {'sortBy': 'expiration', 'sortOrder': 'asc'}, 'range': [0, 300]})
    r = subprocess.run(['curl', '-sS', '-m', '40', '-A', 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0',
                        '-H', 'Content-Type: application/json', '--data', body, TV], capture_output=True)
    data = json.loads(r.stdout.decode('utf-8', 'replace'))['data']
    hd = []
    for it in data:
        ten, gia, pt, han, luc = it['d']
        if re.fullmatch(r'ALI[FGHJKMNQUVXZ]\d{4}', ten or '') and gia is not None and han:
            hd.append({'ma': ten, 'gia': float(gia), 'thay_doi_pt': f'{pt:.2f}%' if pt is not None else None, 'han': han,
                       'dong': f'{ten} close {gia}, change {pt}%'})
    hd.sort(key=lambda x: x['han'])
    if not hd:
        raise RuntimeError('không có hợp đồng ALI')
    return {'goc': 'ALI', 'don_vi': 'USD/tấn', 'nguon': 'https://www.tradingview.com/symbols/COMEX-ALI1!/ (qua scanner.tradingview.com)',
            'cap_nhat': 'TradingView, giá trễ ~10 phút', 'hop_dong': hd}


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'gia.json'
    kq = {'phe_lieu': None, 'the_gioi': None}
    try:
        kq['phe_lieu'] = phe_lieu()
    except Exception as e:
        print('hoangngocdiep.vn KHÔNG ĐỌC ĐƯỢC:', e)
    try:
        kq['the_gioi'] = the_gioi()
    except Exception as e:
        print('tradingview (hợp đồng ALI) KHÔNG ĐỌC ĐƯỢC:', e)
    json.dump(kq, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if kq['phe_lieu']:
        p = kq['phe_lieu']
        print('phế liệu:', '; '.join(d['chu_goc'] for d in p['dong']), '| trang ghi cập nhật', p['cap_nhat'])
    if kq['the_gioi']:
        print('thế giới (ALI):', ', '.join(f"{h['ma']} {h['gia']:,.0f} {h['thay_doi_pt']}" for h in kq['the_gioi']['hop_dong'][:10]))


if __name__ == '__main__':
    main()
