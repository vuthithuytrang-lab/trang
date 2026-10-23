"""Tạo yêu cầu định dạng cho tab theo dõi publish mới (chạy MỘT lần khi cài).

Cách dùng:
  python3 cai_sheet.py <sheet_id> > cai-dat.json
Đưa nguyên mảng "requests" trong cai-dat.json vào update_spreadsheet.

Làm gì:
- Đặt ngôn ngữ vi_VN + giờ Việt Nam cho file (công thức tô hồng dùng dấu ";" theo kiểu Việt Nam).
- Cố định hàng tiêu đề và 2 cột STT | URL, nới rộng cột URL.
- Hàng tiêu đề nền đỏ cam, chữ trắng, căn giữa; cột STT và các cột ngày căn giữa.
- Luật tô hồng: ở cột ngày (C, E, G...), ô có ngày NHỎ HƠN ngày ở tiêu đề → nền hồng (chưa cập nhật).
- Luật tô xanh: URL bị trùng ở cột B → nền xanh lá nhạt.
"""

import json
import sys

DO_CAM = {"red": 0.8784314, "green": 0.4, "blue": 0.4}
TRANG = {"red": 1, "green": 1, "blue": 1}
HONG = {"red": 0.9843137, "green": 0.8, "blue": 0.8745098}
XANH_LA = {"red": 0.7176471, "green": 0.88235295, "blue": 0.8039216}

CONG_THUC_HONG = (
    "=IFERROR(AND(ISODD(COLUMN());LEN($B2)>0;"
    "DATE(RIGHT(TO_TEXT(C2);4);MID(TO_TEXT(C2);4;2);LEFT(TO_TEXT(C2);2))<"
    "DATE(RIGHT(TO_TEXT(C$1);4);MID(TO_TEXT(C$1);4;2);LEFT(TO_TEXT(C$1);2)));FALSE)"
)


def main():
    sid = int(sys.argv[1])
    vung = lambda r0, r1, c0, c1: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                   "startColumnIndex": c0, "endColumnIndex": c1}
    requests = [
        {"updateSpreadsheetProperties": {"properties": {"locale": "vi_VN", "timeZone": "Asia/Ho_Chi_Minh"},
                                         "fields": "locale,timeZone"}},
        {"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {
            "frozenRowCount": 1, "frozenColumnCount": 2, "columnCount": 40}},
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount,gridProperties.columnCount"}},
        {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
                                       "properties": {"pixelSize": 60}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 2},
                                       "properties": {"pixelSize": 430}, "fields": "pixelSize"}},
        {"updateDimensionProperties": {"range": {"sheetId": sid, "dimension": "COLUMNS", "startIndex": 2, "endIndex": 40},
                                       "properties": {"pixelSize": 120}, "fields": "pixelSize"}},
        # Căn giữa cột STT và các cột ngày (cặp đầu C:D; cặp sau được chép định dạng từ C:D)
        {"repeatCell": {"range": vung(1, 1000, 0, 1), "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER"}},
                        "fields": "userEnteredFormat.horizontalAlignment"}},
        {"repeatCell": {"range": vung(1, 1000, 2, 4), "cell": {"userEnteredFormat": {"horizontalAlignment": "CENTER"}},
                        "fields": "userEnteredFormat.horizontalAlignment"}},
        {"repeatCell": {"range": vung(0, 1, 0, 40), "cell": {"userEnteredFormat": {
            "backgroundColorStyle": {"rgbColor": DO_CAM}, "horizontalAlignment": "CENTER",
            "textFormat": {"bold": True, "foregroundColorStyle": {"rgbColor": TRANG}}}},
            "fields": "userEnteredFormat.backgroundColorStyle,userEnteredFormat.horizontalAlignment,userEnteredFormat.textFormat"}},
        {"addConditionalFormatRule": {"index": 0, "rule": {
            "ranges": [vung(1, 1000, 2, 40)],
            "booleanRule": {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": CONG_THUC_HONG}]},
                            "format": {"backgroundColor": HONG}}}}},
        {"addConditionalFormatRule": {"index": 1, "rule": {
            "ranges": [vung(1, 1000, 1, 2)],
            "booleanRule": {"condition": {"type": "CUSTOM_FORMULA", "values": [{"userEnteredValue": "=COUNTIF(B:B;B2)>1"}]},
                            "format": {"backgroundColor": XANH_LA}}}}},
    ]
    json.dump({"requests": requests}, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
