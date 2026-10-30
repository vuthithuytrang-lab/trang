# Ép index Google Search Console — bản Windows

Bộ công cụ tự bấm "Request indexing" trong GSC cho cả danh sách link. Nó chỉ ép link nào
Google **chưa đọc lại sau giờ publish**, và ép tới khi thành công.

## Cách dùng (chỉ cần bấm đúp chuột)

1. Bấm đúp **`1-MO-CHROME-GSC.bat`**. Một cửa sổ Chrome riêng sẽ mở ra.
   - Lần đầu: đăng nhập tài khoản Google có quyền GSC, rồi mở trang **Overview** của website.
   - Những lần sau Chrome tự nhớ đăng nhập.
2. Dán danh sách link vào **`danh-sach-url.txt`**, mỗi dòng 1 link, rồi lưu file.
3. Bấm đúp **`2-CHAY-EP-INDEX.bat`**, gõ giờ publish theo dạng `2026-10-30 21:00`, rồi Enter.
4. Để máy chạy, **không đóng cửa sổ Chrome GSC**. Xong việc sẽ có file **`ket-qua.tsv`**.
   Gửi file này vào khung chat để Claude tích vào bảng theo dõi.

## Kết quả trong ket-qua.tsv

| Chữ | Nghĩa |
|---|---|
| `DA-DOC` | Google đã đọc sau giờ publish, không cần ép |
| `OK` | Đã ép thành công (đã thấy hộp thoại "Indexing requested" mới) |
| `SKIP` | Link không thuộc website đang mở trong GSC |

## Cần biết

- Mỗi ngày Google chỉ cho ép khoảng 10 link cho một website. Hết lượt thì công cụ tự chờ 30 phút,
  kiểm tra lại xem Google đã tự đọc chưa, rồi ép tiếp. Lượt ép được cấp lại khoảng 14–15h chiều giờ Việt Nam.
- Nếu Google hiện ô "Tôi không phải robot", công cụ sẽ dừng. Bạn tự bấm ô đó, rồi chạy lại file 2.
- Thư mục `mac/` là bản gốc cho máy Mac (dùng AppleScript), máy Windows không cần đến.

## Cách hoạt động (cho người kỹ thuật)

File 1 mở Chrome với `--remote-debugging-port=9222` và hồ sơ riêng `%LOCALAPPDATA%\GSC-Chrome`
(Chrome 136+ không cho bật cổng điều khiển trên hồ sơ mặc định). Script `ep-index.ps1` dùng
PowerShell có sẵn trên Windows, nối vào tab GSC qua DevTools Protocol, và chạy đúng phần JS
của skill gốc (`mac/request.sh`, `mac/inspect.sh`).
