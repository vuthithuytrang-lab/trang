# Cách làm đã chốt với Trang (05/10/2026) — thay cho bản cài trên Windows

Trang thấy bản cài Windows + Service Account quá rắc rối. Chốt lại:

- **Một file sheet gốc duy nhất:** [Ngày publish Techcombank](https://docs.google.com/spreadsheets/d/11YEh1C_oB23FX3AwOupR4P00xaIAMB8jfXY21zCqzgI/edit)
  (ID `11YEh1C_oB23FX3AwOupR4P00xaIAMB8jfXY21zCqzgI`, chủ sở hữu vuthithuytrang@seongon.com). Không tạo file mới mỗi lần.
- Bố cục Trang tự chỉnh: `STT | URL | <dd/mm/yyyy> | Kiểm tra lúc | <dd/mm/yyyy> | Kiểm tra lúc | ...`
  Hàng tiêu đề nền đỏ cam, chữ trắng. Cột C–D = ngày 05/10, E–F = ngày 06/10 (Trang gõ nhầm năm "0205").
- **Mỗi ngày mới thêm 2 cột bên phải:** cột ngày (ghi ngày đang hiển thị của từng URL) + cột "Kiểm tra lúc".
- **Ô nào không phải ngày hôm đó → tô hồng.**
- Agent tự chạy lấy ngày (`lay_ngay.py` trong thư mục này — techcombank vào được từ máy chủ cloud) rồi ghi vào sheet.
  Trang không phải cài gì.

## Đang kẹt

Connector Google Sheets báo `Permission denied` với mọi file của tài khoản seongon
(Drive connector thì tạo/đọc được). Khả năng cao Sheets connector đang đăng nhập tài khoản khác.
Đã nhờ Trang kết nối lại Google Sheets bằng vuthithuytrang@seongon.com rồi mở phiên mới.
(Đã thử share file cho hoaa8k58@gmail.com — không giúp được.)

## Phiên sau làm tiếp

1. Thử `get_values` trên file trên. Được thì: sửa tiêu đề C1/E1 thành 05/10/2026, 06/10/2026.
2. Chạy lấy ngày 35 URL, ghi vào cặp cột của hôm nay (chưa có thì thêm 2 cột), tô hồng ô ≠ hôm nay.
3. Hỏi Trang có muốn lịch tự động 08:00/20:00 (Routine trên cloud) không — lần 20:00 ghi đè cặp cột của ngày đó.
