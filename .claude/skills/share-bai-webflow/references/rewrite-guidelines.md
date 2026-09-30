# Rewrite Guidelines — Bài viết từ nguồn tham khảo

> ⚠️ **BẮT BUỘC đọc thêm `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md`** (checklist nội dung của Trang, 29/09/2026) trước khi viết. Chỗ nào khác với file này → checklist thắng (trừ luật không bịa).

## Nguyên tắc

- Giữ nguyên NGHĨA và thông tin chính (số liệu, tên riêng, sự kiện) đúng như bài gốc — không bịa thêm, không suy diễn.
- KHÔNG copy nguyên văn câu/đoạn từ bài gốc — diễn đạt lại bằng câu chữ khác, có thể đổi thứ tự ý, gộp/tách ý.
- Độ dài mục tiêu: 900-1100 từ (tiếng Việt).
- Từ khóa chính xuất hiện tự nhiên trong bài: 1 lần ở tiêu đề hoặc đoạn mở đầu, thêm vài lần rải rác trong thân bài (không nhồi nhét).
- Gắn hyperlink vào ĐÚNG 1 lần xuất hiện của từ khóa chính (thường ở đoạn đầu), trỏ về URL nguồn — lồng tự nhiên kiểu "nguồn tham khảo"/"theo bài viết gốc", không lộ liễu kiểu quảng cáo.
- Giọng văn: rõ ràng, mạch lạc, phù hợp bài blog/tin tức phổ thông — không văn phong học thuật khô khan, không sáo rỗng.
- KHÔNG dùng các từ xếp hạng tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"... khi không có tài liệu/số liệu trong bài gốc chứng minh cho khẳng định đó.

## Cấu trúc gợi ý

1. Đoạn mở đầu (~100 từ) — nêu vấn đề/chủ đề, chứa từ khóa chính có gắn link.
2. Thân bài (~700-800 từ) — triển khai các ý chính của bài gốc theo thứ tự logic, thêm heading phụ (H2/H3) nếu bài dài.
3. Đoạn kết (~100-150 từ) — tóm tắt hoặc gợi ý hành động, không lặp lại y nguyên đoạn mở.
   **KHÔNG đặt heading "Kết luận"** (Trang yêu cầu 29/09/2026) — đoạn kết viết liền mạch, không có tiêu đề riêng; nếu cần heading thì dùng câu mang nội dung cụ thể, không dùng các chữ "Kết luận", "Tổng kết", "Lời kết".

## Tiêu đề

Chứa từ khóa chính, đúng với nội dung, **dưới 63 ký tự**, từ khóa chính ưu tiên đứng đầu (theo checklist).

## Định dạng content

Webflow CMS field kiểu Rich Text nhận trực tiếp 1 chuỗi HTML (khác WordPress Gutenberg block) — chỉ dùng tập thẻ HTML cơ bản mà Rich Text field hỗ trợ: `<p>`, `<h2>`, `<h3>`, `<ul>`/`<ol>`/`<li>`, `<strong>`, `<em>`, `<a href="...">`, `<blockquote>`. KHÔNG dùng `<div>`, `<span>`, style inline, hay class — Rich Text field không giữ các thẻ/thuộc tính ngoài tập cơ bản này, có thể bị lược bỏ khi lưu.

Ví dụ khối nội dung:

```html
<p>Đoạn mở đầu chứa <a href="https://nguon.example.com/bai-goc">từ khóa chính</a> đã gắn link.</p>
<h2>Heading phụ</h2>
<p>Đoạn văn tiếp theo...</p>
<ul>
<li>Ý 1</li>
<li>Ý 2</li>
</ul>
```

Ghép toàn bộ thành 1 chuỗi HTML liên tục (không xuống dòng thừa giữa các thẻ block) trước khi ghi ra file để dùng ở bước build payload.

## Self-check trước khi tạo item

- [ ] Đếm từ: nằm trong khoảng 900-1100 (`node scripts/webflow-json.js word-count <file>`).
- [ ] Không có câu nào giống hệt >1 câu liên tiếp so với bài gốc.
- [ ] Từ khóa chính xuất hiện, đúng 1 chỗ được gắn `<a href="...">` trỏ về URL nguồn.
- [ ] Thông tin số liệu/sự kiện khớp với bài gốc.
- [ ] Toàn bộ nội dung là 1 chuỗi HTML hợp lệ, chỉ dùng thẻ cơ bản Rich Text field hỗ trợ.
- [ ] Đủ cấu trúc bài theo checklist mục 10: slug theo từ khóa chính, dòng hashtag (3 từ khóa + hashtag cố định của dự án), "Nguồn tham khảo" (bài gốc + trang sản phẩm), khối "Thông tin liên hệ" và "Follow social" y nguyên hồ sơ dự án.
