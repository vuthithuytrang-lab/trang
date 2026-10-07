"""Chuẩn bị dữ liệu cập nhật sheet gốc "Theo dõi publish TCB" — dùng cho lịch 08:00 / 13:00 / 19:00.

Bố cục sheet (tab "Untitled"): STT | URL | dd/mm/yyyy | Kiểm tra lúc | dd/mm/yyyy | Kiểm tra lúc | ...
Mỗi ngày một cặp cột. Đã có cặp cột của ngày cần kiểm thì ghi đè (lần sau đè lần trước),
chưa có thì thêm cặp mới bên phải. Ô có ngày nhỏ hơn ngày ở tiêu đề được sheet tự tô hồng
(luật định dạng có điều kiện đã cài sẵn).

Từ 18:00 trở đi (lần kiểm 19:00), ngày cần kiểm là NGÀY MAI: nội dung phải chuyển sang ngày hôm sau
từ tối, chưa chuyển là chậm (Trang chốt 06/10/2026). Kết quả ghi vào cặp cột của ngày mai.

Lần kiểm buổi trưa (11:00–17:59) được BỎ QUA nếu lần kiểm gần nhất trong ngày đã thấy toàn bộ URL
cập nhật đúng ngày (Trang chốt 07/10/2026). Muốn kiểm bất kể, thêm --ep (Trang nhờ kiểm tay).

Cách dùng:
  python cap_nhat_sheet.py dau-vao.json > ket-qua.json
  python cap_nhat_sheet.py dau-vao.json --ep > ket-qua.json   (kiểm tay, không bỏ qua)
dau-vao.json: {"bang": [toàn bộ giá trị tab từ A1, mỗi hàng 1 mảng],
               "column_count": số cột hiện có của tab, "sheet_id": id số của tab, "tab": "Untitled"}
              (kiểu cũ vẫn dùng được: "header": [hàng 1], "rows": [[STT, URL], ...] từ hàng 2)
ket-qua.json: {"bo_qua": true/false, "requests": [...] cho update_spreadsheet (có thể rỗng),
               "range": vùng A1 cho update_values, "values": [...], "tom_tat": "..."}
              bo_qua = true → KHÔNG ghi gì vào sheet, chỉ báo tom_tat.
"""

import json
import sys
from datetime import datetime, timedelta, timezone

import lay_ngay

GIO_CHUYEN_NGAY = 18  # từ giờ này, trang phải hiện ngày mai mới tính là đã cập nhật
GIO_TRUA = (11, 18)  # khung giờ của lần kiểm 13:00 — được bỏ qua nếu buổi sáng đã đủ


def _doc_ngay(chu):
    try:
        return datetime.strptime(str(chu).strip().lstrip("'"), "%d/%m/%Y").date()
    except ValueError:
        return None


def ten_cot(i):  # 0 -> A
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    vao = json.load(open(sys.argv[1], encoding="utf-8"))
    ep = "--ep" in sys.argv[2:]
    bang = vao.get("bang")
    if bang is not None:
        header = [str(o).strip() for o in (bang[0] if bang else [])]
        rows = [list(h[:2]) for h in bang[1:]]
    else:
        header = [str(o).strip() for o in vao["header"]]
        rows = vao["rows"]  # giữ nguyên thứ tự hàng để ghi đúng chỗ; hàng không có URL thì để trống
    tab, sheet_id = vao.get("tab", "Untitled"), vao["sheet_id"]

    bay_gio = datetime.now(timezone(timedelta(hours=7)))
    ngay_kiem = bay_gio.date() + timedelta(days=1 if bay_gio.hour >= GIO_CHUYEN_NGAY else 0)
    hom_nay = ngay_kiem.strftime("%d/%m/%Y")  # ngày cần kiểm (tên biến giữ nguyên cho gọn)

    # Lần kiểm trưa: buổi sáng đã đủ hết thì bỏ qua
    if (not ep and bang is not None and GIO_TRUA[0] <= bay_gio.hour < GIO_TRUA[1]
            and hom_nay in header[2:]):
        c = header.index(hom_nay, 2)
        co_url = [h for h in bang[1:] if len(h) > 1 and str(h[1]).strip().startswith("http")]
        ngay = [_doc_ngay(h[c]) if len(h) > c else None for h in co_url]
        if co_url and all(n is not None and n >= ngay_kiem for n in ngay):
            gio_cu = next((str(h[c + 1]) for h in co_url if len(h) > c + 1 and h[c + 1]), "?")
            json.dump({"bo_qua": True, "requests": [], "range": None, "values": [],
                       "tom_tat": f"Bỏ qua lần kiểm {bay_gio:%H:%M}: lần kiểm trước ({gio_cu}) đã thấy "
                                  f"đủ {len(co_url)}/{len(co_url)} URL cập nhật ngày {hom_nay}."},
                      sys.stdout, ensure_ascii=False)
            return

    # Tìm cặp cột của hôm nay; chưa có thì lấy cặp trống đầu tiên bên phải
    if hom_nay in header[2:]:
        cot = header.index(hom_nay, 2)
    else:
        while header and not header[-1]:
            header.pop()
        cot = max(2, len(header))
        cot += cot % 2  # cột ngày luôn ở C, E, G... (chỉ số chẵn)

    requests = []
    if cot + 2 > vao["column_count"]:
        requests.append({"appendDimension": {"sheetId": sheet_id, "dimension": "COLUMNS",
                                             "length": cot + 2 - vao["column_count"] + 10}})
    if cot != 2:  # chép định dạng cặp cột đầu (C:D) sang cặp mới cho đồng bộ
        requests.append({"copyPaste": {
            "source": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": len(rows) + 1,
                       "startColumnIndex": 2, "endColumnIndex": 4},
            "destination": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": len(rows) + 1,
                            "startColumnIndex": cot, "endColumnIndex": cot + 2},
            "pasteType": "PASTE_FORMAT"}})

    urls = [str(r[1]).strip() if len(r) > 1 else "" for r in rows]
    ket_qua = lay_ngay.lay_nhieu([u for u in urls if u.startswith("http")])
    theo_url = dict(zip([u for u in urls if u.startswith("http")], ket_qua))
    gio = bay_gio.strftime("%H:%M %d/%m/%Y")
    # Dấu ' ở đầu giữ nguyên dạng chữ, để Sheets không tự đổi thành kiểu ngày
    values = [["'" + hom_nay, "Kiểm tra lúc"]]
    for u in urls:
        kq = theo_url.get(u)
        values.append(["'" + kq.hien_thi, "'" + gio] if kq else ["", ""])

    da = sum(kq.ngay is not None and kq.ngay >= ngay_kiem for kq in ket_qua)
    loi = [f"{kq.url} – {kq.hien_thi}" for kq in ket_qua if kq.loi]
    tom_tat = f"Kiểm tra lúc {gio} (so với ngày {hom_nay}): đã cập nhật {da}/{len(ket_qua)}, chưa cập nhật {len(ket_qua) - da - len(loi)}, lỗi {len(loi)}"
    if loi:
        tom_tat += "\nLỗi: " + "; ".join(loi)

    json.dump({"bo_qua": False, "requests": requests,
               "range": f"{tab}!{ten_cot(cot)}1:{ten_cot(cot + 1)}{len(rows) + 1}",
               "values": values, "tom_tat": tom_tat}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
