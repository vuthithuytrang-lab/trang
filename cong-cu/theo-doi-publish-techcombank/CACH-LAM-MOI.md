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

## Tình trạng (05/10/2026 tối)

- Trang đã kết nối lại Google Sheets bằng tài khoản seongon → Agent sửa được sheet.
- File đổi tên thành **Theo dõi publish TCB**. Tab vẫn tên `Untitled` (sheetId `1467189799`).
- Đã đặt múi giờ sheet = Việt Nam, sửa tiêu đề C1/E1 thành 05/10/2026, 06/10/2026 (dạng chữ).
- Đã cài luật tô hồng (định dạng có điều kiện, công thức dùng dấu `;` vì sheet để locale vi_VN):
  `=IFERROR(AND(ISODD(COLUMN());LEN($B2)>0;DATE(RIGHT(TO_TEXT(C2);4);MID(TO_TEXT(C2);4;2);LEFT(TO_TEXT(C2);2))<DATE(RIGHT(TO_TEXT(C$1);4);MID(TO_TEXT(C$1);4;2);LEFT(TO_TEXT(C$1);2)));FALSE)`
  áp cho C2 trở đi → mọi cột ngày (C, E, G...) chỉ tô hồng ô có ngày **nhỏ hơn** ngày tiêu đề
  (Trang chốt 06/10). Ngày bằng/lớn hơn, "Không có ngày", "Lỗi" → không tô.
- `cap_nhat_sheet.py` chuẩn bị dữ liệu ghi: tìm cặp cột của hôm nay (chưa có thì thêm cặp mới,
  chép định dạng từ C:D), lấy ngày toàn bộ URL ở cột B, xuất vùng + giá trị để ghi.
- Lịch tự động 08:00, 13:00 và 19:00 (giờ VN; thêm 13:00 và đổi 20:00 → 19:00 từ 06/10): Routine `trig_01QNyb6Qj58zr6aWAJv8WDD8`, bắn vào phiên `session_01FZgPSenFqeVNPkgaJ1KB2Q`
  (phiên này có connector Google Sheets; kiểu "mỗi lần mở phiên mới" không mang theo connector được nên không dùng).
  Muốn tắt: `update_trigger` enabled=false.

## Kết nối Sheets lỗi lại?

Connector Google Sheets báo `Permission denied` → nhờ Trang vào https://claude.ai/customize/connectors →
tab **Yours** → Google Sheets → Disconnect → Connect bằng vuthithuytrang@seongon.com.
