"""Tạo sua.json cho bài Giá tiêu: đọc xem.txt (bảng hiện tại) + gia.json (giá mới), dịch cột Giá mới -> Giá cũ, tính Thay đổi."""
import json, re, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument('--xem'); ap.add_argument('--gia'); ap.add_argument('--ra'); ap.add_argument('--kiem', action='store_true')
a = ap.parse_args()
L = [re.sub(r'^\s*\d+\.\s', '', l.rstrip('\n')) for l in open(a.xem, encoding='utf-8')]
G = json.load(open(a.gia, encoding='utf-8'))

def doc_hang(nhan):
    i = L.index(nhan)
    return [L[i + k].lstrip('| ').strip() for k in (1, 2, 3)]

def so(s, ngan):  # "136,500" / "6.828" -> int
    return int(s.replace(ngan, ''))

def viet(n, ngan):
    return f'{n:,}'.replace(',', ngan)

def thay_doi(cu, moi, ngan, dv):
    d = moi - cu
    if d == 0: return 'Không đổi'
    p = d / cu * 100
    ps = f'{abs(p):.1f}' if round(abs(p), 1) >= 0.1 else f'{abs(p):.2f}'
    dau = '+' if d > 0 else '-'
    return f'{dau}{viet(abs(d), ngan)} {dv} ({dau}{ps}%)'

sua, loi = [], []
for h in G['hang']:
    nhan, ngan, dv, N = h['nhan'], h['ngan'], h['don_vi'], h['gia']
    cu, moi, td = doc_hang(nhan)
    if a.kiem:
        ok = [cu, moi, td] == [h['ky_vong_cu'], viet(N, ngan), h['ky_vong_td']]
        if not ok: loi.append(f'{nhan}: {cu} | {moi} | {td}  (mong: {h["ky_vong_cu"]} | {viet(N, ngan)} | {h["ky_vong_td"]})')
        continue
    Nv = viet(N, ngan); td_moi = thay_doi(so(moi, ngan), N, ngan, dv)
    h['ky_vong_cu'], h['ky_vong_td'] = moi, td_moi
    ly = f'{nhan}: giá mới {Nv} ({h["nguon_ten"]}, {h["thoi_diem"]}); Giá mới cũ {moi} chuyển sang Giá cũ; Thay đổi = {Nv} - {moi}'
    c_cu, c_moi, c_td = cu, moi, td
    if Nv != c_moi:   # 1) Giá mới
        sua.append({'ngu_canh': f'{nhan} {c_cu} {c_moi} {c_td}', 'tim': c_moi, 'thay': Nv, 'lan': 2 if c_cu == c_moi else 1,
                    'giu_nguyen_so': True, 'nguon': h['nguon'], 'ly_do': ly}); c_moi = Nv
    if td_moi != c_td:  # 2) Thay đổi
        sua.append({'ngu_canh': f'{nhan} {c_cu} {c_moi} {c_td}', 'tim': c_td, 'thay': td_moi, 'giu_nguyen_so': True,
                    'nguon': h['nguon'], 'ly_do': ly + ' (tính ra, % so với giá cũ, 1 số lẻ)'}); c_td = td_moi
    if moi != c_cu:   # 3) Giá cũ
        sua.append({'ngu_canh': f'{nhan} {c_cu} {c_moi} {c_td}', 'tim': c_cu, 'thay': moi, 'lan': 1, 'giu_nguyen_so': True,
                    'nguon': 'bài Techcombank (cột Giá mới trước khi cập nhật)', 'ly_do': 'Giá mới của kỳ trước chuyển sang cột Giá cũ'})
if a.kiem:
    print('\n'.join(loi) if loi else 'khớp hết'); sys.exit(1 if loi else 0)
out = {'bai1': {'sua': G.get('sua_them', []) + sua, 'can_duyet': G.get('can_duyet', [])}}
json.dump(out, open(a.ra, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(G, open(a.gia, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'{len(sua)} chỗ sửa bảng + {len(G.get("sua_them", []))} chỗ khác -> {a.ra}')
