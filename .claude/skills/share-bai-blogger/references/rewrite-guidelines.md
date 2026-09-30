# Rewrite Guidelines — Bài viết từ nguồn tham khảo

> ⚠️ **BẮT BUỘC đọc thêm `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md`** (checklist nội dung của Trang, 29/09/2026) trước khi viết. Chỗ nào khác với file này → checklist thắng (trừ luật không bịa).

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
   **KHÔNG đặt heading "Kết luận"** (Trang yêu cầu 29/09/2026) — đoạn kết viết liền mạch, không có tiêu đề riêng; nếu cần heading thì dùng câu mang nội dung cụ thể, không dùng các chữ "Kết luận", "Tổng kết", "Lời kết".

## Tiêu đề

- Chứa từ khóa chính, đúng với nội dung, **dưới 63 ký tự**, từ khóa chính ưu tiên đứng đầu (theo checklist).
- Blogger KHÔNG có field slug riêng — URL bài viết tự sinh từ tiêu đề, không cần chuẩn bị slug kebab-case như WordPress.

## Định dạng content

Blogger API nhận HTML thường ở field `content` (không phải Gutenberg block markup — đó là đặc thù riêng của WordPress block editor). Dùng thẻ chuẩn: `<p>` cho đoạn văn, `<h2>`/`<h3>` cho heading phụ, `<ul>`/`<ol>` + `<li>` cho danh sách, `<a href="...">` cho link, `<img src="...">` cho ảnh.

## Self-check trước khi đăng

- [ ] Đếm từ: nằm trong khoảng 900-1100.
- [ ] Không có câu nào giống hệt >1 câu liên tiếp so với bài gốc.
- [ ] Từ khóa chính xuất hiện, có đúng 1 link trỏ về URL nguồn (được thêm tối đa 3 link tới trang sản phẩm/bài liên quan cùng website doanh nghiệp, URL lấy từ trang nguồn — checklist mục 8).
- [ ] Đạt checklist `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md`: TL;DR đầu bài, H2 dạng câu hỏi có từ khóa, FAQ (nếu nguồn đủ thông tin), ≥1 CTA, đoạn 60–80 từ, ≥3 ảnh căn giữa có chú thích in nghiêng <70 ký tự.
- [ ] Thông tin số liệu/sự kiện khớp với bài gốc.
- [ ] Content là HTML hợp lệ (thẻ mở/đóng khớp nhau), không lẫn markdown (`**bold**`, `##heading`).
- [ ] Đủ cấu trúc bài theo checklist mục 10: slug theo từ khóa chính, dòng hashtag (3 từ khóa + hashtag cố định của dự án), "Nguồn tham khảo" (bài gốc + trang sản phẩm), khối "Thông tin liên hệ" và "Follow social" y nguyên hồ sơ dự án.
