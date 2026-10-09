# Rewrite Guidelines — Bài viết từ nguồn tham khảo

## Nguyên tắc

- Giữ nguyên NGHĨA và thông tin chính (số liệu, tên riêng, sự kiện) đúng như bài gốc — không bịa thêm, không suy diễn.
- KHÔNG copy nguyên văn câu/đoạn từ bài gốc — diễn đạt lại bằng câu chữ khác, có thể đổi thứ tự ý, gộp/tách ý.
- Độ dài mục tiêu: 900-1100 từ (tiếng Việt).
- Từ khóa chính xuất hiện tự nhiên trong bài: 1 lần ở tiêu đề hoặc đoạn mở đầu, thêm vài lần rải rác trong thân bài (không nhồi nhét).
- Gắn hyperlink vào ĐÚNG 1 lần xuất hiện của từ khóa chính (thường ở đoạn đầu), trỏ về URL nguồn — lồng tự nhiên kiểu "nguồn tham khảo"/"theo bài viết gốc", không lộ liễu kiểu quảng cáo.
- Giọng văn: rõ ràng, mạch lạc, phù hợp bài blog/tin tức phổ thông — không văn phong học thuật khô khan, không sáo rỗng.

## Cấu trúc gợi ý

1. Đoạn mở đầu (~100 từ) — nêu vấn đề/chủ đề, chứa từ khóa chính có gắn link.
2. Thân bài (~700-800 từ) — triển khai các ý chính của bài gốc theo thứ tự logic, thêm heading phụ (H2/H3) nếu bài dài.
3. Đoạn kết (~100-150 từ) — tóm tắt hoặc gợi ý hành động, không lặp lại y nguyên đoạn mở.

## Tiêu đề

- Chứa từ khóa chính, đúng với nội dung, khoảng 60-70 ký tự.
- Blogger KHÔNG có field slug riêng — URL bài viết tự sinh từ tiêu đề, không cần chuẩn bị slug kebab-case như WordPress.

## Định dạng content

Blogger API nhận HTML thường ở field `content` (không phải Gutenberg block markup — đó là đặc thù riêng của WordPress block editor). Dùng thẻ chuẩn: `<p>` cho đoạn văn, `<h2>`/`<h3>` cho heading phụ, `<ul>`/`<ol>` + `<li>` cho danh sách, `<a href="...">` cho link, `<img src="...">` cho ảnh.

## Self-check trước khi đăng

- [ ] Đếm từ: nằm trong khoảng 900-1100.
- [ ] Không có câu nào giống hệt >1 câu liên tiếp so với bài gốc.
- [ ] Từ khóa chính xuất hiện, có đúng 1 link trỏ về URL nguồn.
- [ ] Thông tin số liệu/sự kiện khớp với bài gốc.
- [ ] Content là HTML hợp lệ (thẻ mở/đóng khớp nhau), không lẫn markdown (`**bold**`, `##heading`).
