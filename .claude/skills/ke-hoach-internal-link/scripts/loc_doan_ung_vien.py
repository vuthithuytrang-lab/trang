"""Lọc sẵn 4 đoạn ứng viên tốt nhất trong bài nguồn cho từng link, rồi chia lô cho người đọc.

Cách dùng:
    python3 loc_doan_ung_vien.py links.tsv thu-muc-bai/ thu-muc-lo/ [so_lo] [ten_thuong_hieu]

ten_thuong_hieu (tuỳ chọn): tên thương hiệu của website, ví dụ "techcombank", để không tính là từ khoá chủ đề.

links.tsv: mỗi dòng "hàng<TAB>trang đích<TAB>anchor<TAB>bài nguồn" (hàng = số hàng trong tab tạm
trên Google Sheet, để người đọc ghi kết quả đúng chỗ). Các dòng cùng bài nguồn phải nằm liền nhau.
thu-muc-bai/: nơi tai_bai.py đã lưu bài (cả bài nguồn lẫn trang đích, để lấy tiêu đề trang đích).
Kết quả: thu-muc-lo/in00.txt, in01.txt… — mỗi lô liên tục theo số hàng, không cắt đôi một bài.
"""
import json
import os
import re
import sys

STOP = {"là", "gì", "và", "của", "có", "cho", "các", "những", "được", "một", "khi", "với", "tại", "trong",
        "bao", "nhiêu", "nào", "thế", "như", "này", "để", "không", "ở", "đâu", "cách", "bằng", "mới", "nhất",
        "ngân", "hàng"}
LUAT = re.compile(r"(luật|nghị định|thông tư|điều \d+|khoản \d+|quyết định số|bộ luật|văn bản hợp nhất"
                  r"|nđ-cp|tt-btc|qh1\d)", re.I)
BO_QUA = ("bạn đọc lưu ý", "lưu ý:", "(*)", "email:", "trung tâm dịch vụ", "hệ thống chi nhánh", ">>>",
          "xem thêm", "đăng ký ngay", "thông tin được cập nhật", "thông tin cập nhật")


def toks(s):
    return re.findall(r"[0-9a-zà-ỹđ]+", s.lower())


def slug(u):
    return u.rstrip("/").split("/")[-1]


def doc_bai(thu_muc, u):
    """Trả về (tiêu đề, danh sách (mục, loại, đoạn), dàn ý). Bỏ sapo, bảng, khối quảng cáo, bài liên quan."""
    f = os.path.join(thu_muc, slug(u) + ".json")
    if not os.path.exists(f):
        return None
    title, muc, sapo, out, dan_y = "", "(Mở bài)", False, [], []
    for t, x in json.load(open(f, encoding="utf-8"))["blocks"]:
        if t == "h1" and not title:
            title = x
            continue
        if not title:
            continue
        if t in ("h2", "h3", "h4"):
            if "bài viết liên quan" in x.lower():
                break
            muc = x
            if t == "h2":
                dan_y.append(x)
            continue
        if t == "td":
            continue
        if not sapo and t == "p":
            sapo = True
            continue
        if x.lower().strip().startswith(BO_QUA) or len(x) < 45:
            continue
        out.append((muc, t, x))
    return title, out, dan_y


def cat(x, keys, n=300):
    if len(x) <= n:
        return x
    xl, best, bi = x.lower(), -1, 0
    for i in range(0, len(x) - n + 1, 40):
        sc = sum(1 for k in keys if k in xl[i:i + n])
        if sc > best:
            best, bi = sc, i
    return ("…" if bi else "") + x[bi:bi + n] + "…"


def main():
    tsv, thu_muc, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    so_lo = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    if len(sys.argv) > 5:
        STOP.update(toks(sys.argv[5]))
    rows = [l.rstrip("\n").split("\t") for l in open(tsv, encoding="utf-8") if l.strip()]
    tieu_de = {}
    nhom = {}
    for hang, dich, anchor, nguon in rows:
        nhom.setdefault(nguon, []).append((int(hang), dich, anchor))
        if dich not in tieu_de:
            b = doc_bai(thu_muc, dich)
            tieu_de[dich] = b[0] if b else slug(dich).replace("-", " ")
    khoi, thieu = [], []
    for nguon, ds in nhom.items():
        b = doc_bai(thu_muc, nguon)
        if not b:
            thieu.append(nguon)
            continue
        title, doan, dan_y = b
        L = [f"\n=== BÀI NGUỒN: {nguon}\nTiêu đề: {title}\nDàn ý: " + " | ".join(dan_y)[:600]]
        for hang, dich, anchor in ds:
            keys = [w for w in toks(anchor) if w not in STOP]
            tk = set(w for w in toks(tieu_de[dich]) if w not in STOP)
            diem = []
            for j, (muc, t, x) in enumerate(doan):
                xl, xt = x.lower(), set(toks(x))
                s = (3 * (anchor.lower() in xl) + 2 * sum(w in xt for w in keys) / max(1, len(keys))
                     + sum(w in xt for w in tk) / max(1, len(tk)) - (1.5 if LUAT.search(x) else 0)
                     + (0.2 if t == "p" else 0))
                diem.append((s, j))
            diem.sort(reverse=True)
            L.append(f"\n-- DÒNG {hang} | anchor: «{anchor}» | trang đích: {dich} ({tieu_de[dich]})")
            for _, j in diem[:4]:
                muc, t, x = doan[j]
                loai = "gạch đầu dòng" if t == "li" else "đoạn"
                luat = ", CÓ LUẬT" if LUAT.search(x) else ""
                L.append(f"   [{j}] mục «{muc[:90]}» ({loai}{luat}): {cat(x, keys + list(tk))}")
        khoi.append((ds[0][0], ds[-1][0], len(ds), "\n".join(L)))
    os.makedirs(out_dir, exist_ok=True)
    tong = sum(k[2] for k in khoi)
    lo, dem, k_lo = [[]], 0, 0
    for k in khoi:
        lo[-1].append(k)
        dem += k[2]
        if dem >= tong / so_lo * len(lo) and len(lo) < so_lo:
            lo.append([])
    for i, ds in enumerate(x for x in lo if x):
        open(os.path.join(out_dir, f"in{i:02d}.txt"), "w", encoding="utf-8").write("\n".join(k[3] for k in ds))
        print(f"in{i:02d}.txt: hàng {ds[0][0]}–{ds[-1][1]}, {sum(k[2] for k in ds)} link")
    if thieu:
        print("Chưa tải được bài (cần tải lại hoặc báo Trang):", *thieu, sep="\n  ")


if __name__ == "__main__":
    main()
