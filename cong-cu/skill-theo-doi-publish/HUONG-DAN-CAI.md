# Cài skill "theo-doi-publish" cho người khác trong team

File cài: `theo-doi-publish.zip` (cùng thư mục này). Bản gốc để sửa: `.claude/skills/theo-doi-publish/`
— sửa xong nhớ đóng gói lại zip.

## Người nhận làm 3 bước (một lần)

1. **Tải skill lên tài khoản Claude:** claude.ai → Cài đặt (Settings) → Tính năng (Capabilities) → Skills
   → Tải lên (Upload) → chọn `theo-doi-publish.zip`. (Tên mục có thể khác chút tùy phiên bản.)
2. **Kết nối Google Sheets:** https://claude.ai/customize/connectors → Google Sheets → Connect bằng tài khoản công ty.
3. **Mở Claude Code bản web** (https://claude.ai/code), gõ: `cài theo dõi publish`
   → Claude sẽ nhờ mở https://sheets.new, dán link file + danh sách URL, rồi tự làm phần còn lại
   (định dạng, kiểm lần đầu, cài lịch 19:00).

Dùng hằng ngày: điền link mới vào cột B · nhắn `check publish` để kiểm ngay · `dừng update publish` để tắt lịch.

Lưu ý: lịch tự động chạy trong phiên Claude Code đã cài nó — đừng xóa/lưu trữ phiên đó.
Skill chỉ đọc đúng kiểu trang techcombank.com (blog đọc ngày dưới tiêu đề, trang khác đọc ngày trong title).
