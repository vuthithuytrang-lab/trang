# Kiểm tra ngày publish bằng Screaming Frog (Custom Extraction)

Hướng dẫn đã gửi Trang ngày 21/10/2026.

1. Mode → **List**.
2. Configuration → Custom → **Custom Extraction**, thêm 2 dòng:

| Tên | Kiểu | Biểu thức |
|---|---|---|
| Ngay blog | Regex | `article-header-body--date">(\d{4}-\d{2}-\d{2})` |
| Ngay title | Regex | `<title>[^<]*?(\d{1,2}/\d{1,2}/\d{4}|(?<=\()\d{1,2}/\d{1,2}(?=\)))` |

3. Upload → Paste danh sách URL → OK.
4. Xem tab **Custom Extraction**: blog đọc cột `Ngay blog 1` (yyyy-mm-dd), trang khác đọc `Ngay title 1`
   (dd/mm/yyyy; trang tỷ giá chỉ có "dd/mm" trong ngoặc). Lưu cấu hình: File → Configuration → Save As.
