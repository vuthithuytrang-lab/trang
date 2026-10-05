"""Đọc/ghi Google Sheet theo dõi publish: tab "Danh sách URL" và các tab tuần."""

from datetime import date, timedelta
from pathlib import Path

import gspread

TAB_DANH_SACH = "Danh sách URL"
TEN_THU = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]

# Vị trí cột trong tab tuần (đếm từ 0): A=STT, B=URL, C..I=7 ngày, J=Số ngày, K=Tỷ lệ, L=Ghi chú
COT_URL = 1
COT_NGAY_DAU = 2
COT_SO_NGAY = 9
COT_TY_LE = 10
COT_GHI_CHU = 11
SO_COT = 12

# Màu theo cẩm nang SEONGON
XANH = "#004AEF"
MINT = "#07EF9C"
XANH_NHAT = "#E3ECFE"
DO_NHAT = "#FDE2E2"
XAM_VIEN = "#DCDCDC"


def _mau(hex_):
    hex_ = hex_.lstrip("#")
    return {k: int(hex_[i:i + 2], 16) / 255 for k, i in (("red", 0), ("green", 2), ("blue", 4))}


def _chu_cot(i):
    return chr(ord("A") + i)


def mo_sheet(link: str, file_service_account: str) -> gspread.Spreadsheet:
    gc = gspread.service_account(filename=file_service_account)
    return gc.open_by_url(link)


def _doc(sh, ten_tab, vung="A1:L"):
    kq = sh.values_get(f"'{ten_tab}'!{vung}", params={"valueRenderOption": "UNFORMATTED_VALUE"})
    return kq.get("values", [])


# ---------- Tab "Danh sách URL" ----------

def doc_danh_sach_url(sh, file_mac_dinh: Path) -> list[str]:
    """Đọc URL từ tab Danh sách URL. Chưa có tab thì tạo và điền danh sách mặc định."""
    try:
        sh.worksheet(TAB_DANH_SACH)
    except gspread.WorksheetNotFound:
        # Tab đầu tiên đã có sẵn tiêu đề STT | URL (ví dụ sheet tạo từ file CSV) thì chỉ đổi tên
        dau = sh.get_worksheet(0)
        if dau is not None and [str(o).strip() for o in dau.row_values(1)[:2]] == ["STT", "URL"]:
            dau.update_title(TAB_DANH_SACH)
            return doc_danh_sach_url(sh, file_mac_dinh)
        urls = [d.strip() for d in file_mac_dinh.read_text(encoding="utf-8").splitlines() if d.strip()]
        ws = sh.add_worksheet(TAB_DANH_SACH, rows=max(200, len(urls) + 50), cols=2, index=0)
        sh.values_update(
            f"'{TAB_DANH_SACH}'!A1",
            params={"valueInputOption": "RAW"},
            body={"values": [["STT", "URL"]] + [[i, u] for i, u in enumerate(urls, 1)]},
        )
        sh.batch_update({"requests": [
            {"updateSheetProperties": {"properties": {"sheetId": ws.id, "gridProperties": {"frozenRowCount": 1}},
                                       "fields": "gridProperties.frozenRowCount"}},
            _o_tieu_de(ws.id, 2),
            _do_rong(ws.id, 0, 1, 50), _do_rong(ws.id, 1, 2, 520),
        ]})

    urls, da_co = [], set()
    for hang in _doc(sh, TAB_DANH_SACH, "B2:B"):
        u = str(hang[0]).strip() if hang else ""
        if u.startswith("http") and u not in da_co:
            urls.append(u)
            da_co.add(u)
    return urls


# ---------- Tab tuần ----------

def thu_hai_cua_tuan(ngay: date) -> date:
    return ngay - timedelta(days=ngay.weekday())


def ten_tab_tuan(thu_hai: date) -> str:
    cn = thu_hai + timedelta(days=6)
    return f"Tuần {thu_hai:%d/%m}-{cn:%d/%m}"


def _hang_url(stt, url, so_hang, thu_hai):
    """Một hàng dữ liệu (so_hang đếm từ 1 như trên sheet)."""
    r = so_hang
    return [
        stt, url, *([False] * 7),
        f"=COUNTIF(C{r}:I{r},TRUE)",
        f"=J{r}/MIN(7,MAX(1,TODAY()-DATE({thu_hai.year},{thu_hai.month},{thu_hai.day})+1))",
        "",
    ]


def lay_tab_tuan(sh, thu_hai: date, urls: list[str]):
    """Trả về tab của tuần; chưa có thì tạo. URL mới thêm giữa tuần được nối vào cuối tab."""
    ten = ten_tab_tuan(thu_hai)
    try:
        ws = sh.worksheet(ten)
    except gspread.WorksheetNotFound:
        return _tao_tab_tuan(sh, ten, thu_hai, urls)

    hang = _doc(sh, ten, "A2:B")
    da_co = {str(h[1]).strip() for h in hang if len(h) > 1}
    moi = [u for u in urls if u not in da_co]
    if moi:
        dau = len(hang) + 2  # hàng trống đầu tiên
        stt = max([h[0] for h in hang if h and isinstance(h[0], (int, float))] or [0])
        if dau + len(moi) > ws.row_count:
            ws.add_rows(dau + len(moi) - ws.row_count + 50)
        sh.values_update(
            f"'{ten}'!A{dau}",
            params={"valueInputOption": "USER_ENTERED"},
            body={"values": [_hang_url(int(stt) + i, u, dau + i - 1, thu_hai) for i, u in enumerate(moi, 1)]},
        )
        sh.batch_update({"requests": _dinh_dang_hang(ws.id, dau - 1, dau - 1 + len(moi))})
    return ws


def _tao_tab_tuan(sh, ten, thu_hai, urls):
    ws = sh.add_worksheet(ten, rows=max(200, len(urls) + 50), cols=SO_COT, index=1)
    ngay_tuan = [thu_hai + timedelta(days=i) for i in range(7)]
    tieu_de = ["STT", "URL", *[f"{t} {n:%d/%m}" for t, n in zip(TEN_THU, ngay_tuan)],
               "Số ngày đã cập nhật", "Tỷ lệ (%)", "Ghi chú"]
    du_lieu = [tieu_de] + [_hang_url(i, u, i + 1, thu_hai) for i, u in enumerate(urls, 1)]
    sh.values_update(f"'{ten}'!A1", params={"valueInputOption": "USER_ENTERED"}, body={"values": du_lieu})

    yeu_cau = [
        {"updateSpreadsheetProperties": {"properties": {"timeZone": "Asia/Ho_Chi_Minh"}, "fields": "timeZone"}},
        {"updateSheetProperties": {
            "properties": {"sheetId": ws.id, "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2}},
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}},
        _o_tieu_de(ws.id, SO_COT),
        {"updateDimensionProperties": {"range": {"sheetId": ws.id, "dimension": "ROWS", "startIndex": 0, "endIndex": 1},
                                       "properties": {"pixelSize": 44}, "fields": "pixelSize"}},
        _do_rong(ws.id, 0, 1, 45), _do_rong(ws.id, 1, 2, 430), _do_rong(ws.id, 2, 9, 82),
        _do_rong(ws.id, 9, 10, 100), _do_rong(ws.id, 10, 11, 80), _do_rong(ws.id, 11, 12, 220),
        *_dinh_dang_hang(ws.id, 1, len(urls) + 1),
    ]
    # Tô cột hôm nay: nền xanh nhạt cho dữ liệu, ô tiêu đề màu mint. Công thức tự đổi theo ngày.
    for i, n in enumerate(ngay_tuan):
        cong_thuc = f"=TODAY()=DATE({n.year},{n.month},{n.day})"
        c = COT_NGAY_DAU + i
        yeu_cau.append(_to_mau_dk(ws.id, 1, None, c, c + 1, cong_thuc, XANH_NHAT))
        yeu_cau.append(_to_mau_dk(ws.id, 0, 1, c, c + 1, cong_thuc, MINT, chu="#151515"))
    # Tô đỏ nhạt hàng có tỷ lệ dưới 100%
    yeu_cau.append(_to_mau_dk(ws.id, 1, None, 0, SO_COT, '=AND($B2<>"",$K2<1)', DO_NHAT))
    sh.batch_update({"requests": yeu_cau})
    return ws


def _o_tieu_de(sheet_id, so_cot):
    return {"repeatCell": {
        "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": so_cot},
        "cell": {"userEnteredFormat": {
            "backgroundColor": _mau(XANH), "horizontalAlignment": "CENTER", "verticalAlignment": "MIDDLE",
            "wrapStrategy": "WRAP", "textFormat": {"bold": True, "foregroundColor": _mau("#FFFFFF")}}},
        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,verticalAlignment,wrapStrategy,textFormat)"}}


def _do_rong(sheet_id, dau, cuoi, px):
    return {"updateDimensionProperties": {
        "range": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": dau, "endIndex": cuoi},
        "properties": {"pixelSize": px}, "fields": "pixelSize"}}


def _dinh_dang_hang(sheet_id, dau, cuoi):
    """Checkbox cho 7 cột ngày, định dạng %, căn giữa — cho các hàng [dau, cuoi) (đếm từ 0)."""
    vung = lambda c1, c2: {"sheetId": sheet_id, "startRowIndex": dau, "endRowIndex": cuoi,
                           "startColumnIndex": c1, "endColumnIndex": c2}
    return [
        {"setDataValidation": {"range": vung(COT_NGAY_DAU, COT_NGAY_DAU + 7),
                               "rule": {"condition": {"type": "BOOLEAN"}, "strict": True}}},
        {"repeatCell": {"range": vung(0, 1), "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER"}},
                        "fields": "userEnteredFormat.horizontalAlignment"}},
        {"repeatCell": {"range": vung(COT_SO_NGAY, COT_TY_LE + 1),
                        "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER",
                                                       "numberFormat": {"type": "NUMBER", "pattern": "0"}}},
                        "fields": "userEnteredFormat(horizontalAlignment,numberFormat)"}},
        {"repeatCell": {"range": vung(COT_TY_LE, COT_TY_LE + 1),
                        "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0%"}}},
                        "fields": "userEnteredFormat.numberFormat"}},
    ]


def _to_mau_dk(sheet_id, h1, h2, c1, c2, cong_thuc, nen, chu=None):
    vung = {"sheetId": sheet_id, "startRowIndex": h1, "startColumnIndex": c1, "endColumnIndex": c2}
    if h2 is not None:
        vung["endRowIndex"] = h2
    dinh_dang = {"backgroundColor": _mau(nen)}
    if chu:
        dinh_dang["textFormat"] = {"foregroundColor": _mau(chu)}
    return {"addConditionalFormatRule": {"rule": {
        "ranges": [vung],
        "booleanRule": {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": cong_thuc}]},
                        "format": dinh_dang}}}}


# ---------- Ghi kết quả ----------

def doc_tab_tuan(sh, ws) -> list[dict]:
    """Các hàng URL trong tab tuần: số hàng (đếm từ 0), STT, URL, 7 ô checkbox, ghi chú."""
    hang = []
    for i, h in enumerate(_doc(sh, ws.title, "A2:L"), start=1):
        h = list(h) + [""] * (SO_COT - len(h))
        url = str(h[COT_URL]).strip()
        if not url:
            continue
        hang.append({"hang": i, "stt": h[0], "url": url,
                     "ngay": [h[COT_NGAY_DAU + k] is True for k in range(7)],
                     "ghi_chu": str(h[COT_GHI_CHU])})
    return hang


def ghi_ket_qua(sh, ws, hom_nay: date, buoi: str, ket_qua, urls_hien_tai):
    """Tick checkbox cột hôm nay theo kết quả, ghi note vào ô chưa tick.

    Trả về danh sách hàng {stt, url, da_cap_nhat, hien_thi, loi} theo thứ tự trong tab.
    """
    cot = COT_NGAY_DAU + hom_nay.weekday()
    theo_url = {kq.url: kq for kq in ket_qua}
    yeu_cau, tong_hop = [], []
    for h in doc_tab_tuan(sh, ws):
        kq = theo_url.get(h["url"])
        if kq is None:
            if h["url"] not in urls_hien_tai and not h["ghi_chu"]:
                yeu_cau.append(_ghi_o(ws.id, h["hang"], COT_GHI_CHU, {"stringValue": "Đã bỏ khỏi danh sách"}))
            continue
        dung_hom_nay = kq.ngay == hom_nay
        truoc_do = h["ngay"][hom_nay.weekday()]
        # Lần 20:00 ghi đè lần 08:00. Riêng ô đã tick thì giữ tick: trang đã cập nhật hôm nay rồi,
        # buổi tối có lỗi mạng cũng không làm mất kết quả.
        da_cap_nhat = dung_hom_nay or truoc_do
        if dung_hom_nay:
            note = ""
        elif truoc_do:
            note = f"Đã cập nhật (lần kiểm tra trước). Lần {buoi}: {kq.hien_thi}"
        else:
            note = f"{kq.hien_thi} (kiểm tra {buoi})" if kq.loi or kq.ngay is None \
                else f"Ngày đang hiển thị: {kq.hien_thi} (kiểm tra {buoi})"
        yeu_cau.append(_ghi_o(ws.id, h["hang"], cot, {"boolValue": da_cap_nhat}, note))
        tong_hop.append({"stt": h["stt"], "url": h["url"], "da_cap_nhat": da_cap_nhat,
                         "hien_thi": kq.hien_thi, "loi": bool(kq.loi) and not da_cap_nhat})
    if yeu_cau:
        sh.batch_update({"requests": yeu_cau})  # ghi cả lô trong 1 lần gọi API
    return tong_hop


def _ghi_o(sheet_id, hang, cot, gia_tri, note=None):
    o = {"userEnteredValue": gia_tri}
    truong = "userEnteredValue"
    if note is not None:
        o["note"] = note
        truong += ",note"
    return {"updateCells": {"start": {"sheetId": sheet_id, "rowIndex": hang, "columnIndex": cot},
                            "rows": [{"values": [o]}], "fields": truong}}


def link_tab(sh, ws) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sh.id}/edit#gid={ws.id}"
