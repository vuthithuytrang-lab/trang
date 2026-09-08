# Bật lịch bản tin tự động 7h sáng — còn 1 bước

## Tình trạng

| Việc | Trạng thái |
|---|---|
| Bot Telegram `@ban_tin_marketing_bot` | ✅ Đang chạy |
| Trang đã bấm START, lấy được chat id | ✅ Xong |
| Bản tin mẫu (giọng vui, 4 mảng quan tâm) | ✅ Đã gửi thành công |
| Lịch tự động 7h sáng hằng ngày | ✅ Đã tạo — `trig_0193PQKZuz27brzWJibGu2eN` |
| File chìa `cong-cu/telegram.env` | ⏸️ **Chưa đưa lên kho** — chờ kho chuyển sang riêng tư |

## Vì sao còn kẹt

Lịch tự động chạy trong một phiên làm việc mới toanh mỗi sáng. Phiên đó tải kho về rồi
đọc chìa bot từ file `cong-cu/telegram.env`. Nghĩa là file chìa **phải nằm trong kho**.

Nhưng kho `vuthithuytrang-lab/trang` đang để **công khai** — cất chìa vào đó thì ai
trên Internet cũng đọc được và điều khiển được bot.

Nên hiện file chìa chỉ nằm trên máy, và đã được `.gitignore` chặn không cho commit nhầm.

## Việc Trang cần làm — 1 phút

1. Mở https://github.com/vuthithuytrang-lab/trang/settings
2. Kéo xuống cuối trang, mục **Danger Zone**
3. Bấm **Change repository visibility** → chọn **Make private**
4. Gõ tên kho để xác nhận

Xong báo Agent một câu, Agent sẽ đưa file chìa lên kho và lịch chạy được ngay sáng hôm sau.

## Muốn đổi gì về bản tin

Nội dung bản tin do lịch tự soạn mỗi sáng theo khuôn đã đặt sẵn. Muốn đổi giờ chạy,
đổi giọng văn, thêm/bớt mảng quan tâm — chỉ cần nói, Agent sửa phần cấu hình lịch.

## Muốn tắt bot

Vào BotFather trên Telegram, gõ `/revoke` → chọn bot. Chìa cũ hết hiệu lực ngay lập tức.
