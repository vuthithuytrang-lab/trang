# ⚠️ Bảo mật — chìa khóa đã lộ, cần thu hồi

Repo này là **public**. Không có chìa khóa nào được ghi vào đây, kể cả trong lịch sử commit.

Trong quá trình đọc lại bản chụp session cũ, phát hiện **3 chìa khóa đã bị dán thẳng vào khung chat**
(và giờ nằm trong file PDF ảnh chụp). Tất cả đều phải coi là **đã lộ**.

| # | Loại chìa | Tình trạng | Việc cần làm |
|---|---|---|---|
| 1 | Chìa Agent Boss (bản 1) | Đã bị hệ thống Agent Boss tự khóa vì phát hiện lộ | Không dùng lại |
| 2 | Chìa Agent Boss (bản 2) | Trang gửi lại nhưng **vẫn là chìa cũ** — chưa từng tạo chìa mới | **Phải tạo chìa mới** |
| 3 | Token bot Telegram `ban_tin_marketing_trang_bot` | Đã dán vào chat, vẫn còn hiệu lực | **Thu hồi và cấp lại** |

## Việc 1 — Tạo chìa Agent Boss mới

1. Vào trang **Profile** trên Agent Boss (đường dẫn `/profile`)
2. Tìm mục **"Nối Agent"**
3. Bấm **"Tạo lại chìa khóa"**
4. Hệ thống sinh chìa hoàn toàn mới — vẫn bắt đầu bằng `abs_` nhưng **dãy chữ và số phía sau phải KHÁC** chìa cũ.
   Nếu đuôi vẫn là `...747516` thì nghĩa là chưa tạo mới thành công, bấm lại nút.

## Việc 2 — Thu hồi token bot Telegram

1. Mở Telegram, vào chat với **BotFather**
2. Gõ `/revoke` → chọn bot `ban_tin_marketing_trang_bot`
3. BotFather cấp token mới

## Việc 3 — Cách đưa chìa cho Agent (làm đúng từ giờ)

❌ **KHÔNG** gõ chìa vào khung chat
❌ **KHÔNG** gắn chìa vào URL kiểu `?key=abs_...`
❌ **KHÔNG** commit chìa vào repo

✅ Mở một file văn bản trống, dán chìa vào, lưu tên `chia-agent-boss.txt`
✅ **Đính kèm file đó** vào khung chat (biểu tượng kẹp giấy)
✅ Agent đọc chìa từ file, gửi qua header `Authorization: Bearer <chìa>`, không in ra màn hình

> Lý do (bài học Bài 6): khung chat lưu lại lịch sử, chìa nằm ở đó có thể lộ ra ngoài mà bạn
> không kiểm soát được. Ghi ra file chỉ là để **an toàn hơn** — hệ thống không bắt buộc phải đọc từ file.
