"""Chuẩn bị dữ liệu cập nhật sheet gốc "Theo dõi publish TCB" — dùng cho lịch 08:00 / 20:00.

Bố cục sheet (tab "Untitled"): STT | URL | dd/mm/yyyy | Kiểm tra lúc | dd/mm/yyyy | Kiểm tra lúc | ...
Mỗi ngày một cặp cột. Đã có cặp cột của hôm nay thì ghi đè (lần 20:00 đè lần 08:00),
chưa có thì thêm cặp mới bên phải. Ô không phải ngày hôm đó được sheet tự tô hồng
(luật định dạng có điều kiện đã cài sẵn).

Cách dùng:
  python cap_nhat_sheet.py dau-vao.json > ket-qua.json
dau-vao.json: {"header": [hàng 1 của sheet], "rows": [[STT, URL], ...] (từ hàng 2),
               "column_count": số cột hiện có của tab, "sheet_id": id số của tab, "tab": "Untitled"}
ket-qua.json: {"requests": [...] cho update_spreadsheet (có thể rỗng),
               "range": vùng A1 cho update_values, "values": [...], "tom_tat": "..."}
"""

import json
import sys
from datetime import datetime, timedelta, timezone

import lay_ngay


def ten_cot(i):  # 0 -> A
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def main():
    vao = json.load(open(sys.argv[1], encoding="utf-8"))
    header = [str(o).strip() for o in vao["header"]]
    rows = vao["rows"]  # giữ nguyên thứ tự hàng để ghi đúng chỗ; hàng không có URL thì để trống
    tab, sheet_id = vao.get("tab", "Untitled"), vao["sheet_id"]

    bay_gio = datetime.now(timezone(timedelta(hours=7)))
    hom_nay = bay_gio.strftime("%d/%m/%Y")

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

    da = sum(kq.hien_thi == hom_nay for kq in ket_qua)
    loi = [f"{kq.url} – {kq.hien_thi}" for kq in ket_qua if kq.loi]
    tom_tat = f"Kiểm tra lúc {gio}: đã cập nhật {da}/{len(ket_qua)}, chưa cập nhật {len(ket_qua) - da - len(loi)}, lỗi {len(loi)}"
    if loi:
        tom_tat += "\nLỗi: " + "; ".join(loi)

    json.dump({"requests": requests,
               "range": f"{tab}!{ten_cot(cot)}1:{ten_cot(cot + 1)}{len(rows) + 1}",
               "values": values, "tom_tat": tom_tat}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
