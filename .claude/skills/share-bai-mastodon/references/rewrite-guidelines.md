# Rewrite Guidelines — Toot Mastodon từ nguồn tham khảo

Khác `share-bai-wp`/`share-bai-blogger`/`share-bai-ggr`/`share-bai-tumblr`/`share-bai-wix` (viết lại thành 1 bài ~1000 từ), skill này chỉ viết **1 status (toot) ngắn** — không áp dụng rule độ dài 900-1100 từ. Gần với `share-bai-instagram` về tinh thần "caption ngắn", nhưng khác 2 điểm quan trọng: Mastodon **cho phép link clickable** (tự động linkify + tạo preview card), và giới hạn ký tự chặt hơn nhiều (500, không phải 2200).

## Nguyên tắc

- Giữ nguyên NGHĨA và thông tin chính (số liệu, tên riêng, sự kiện) đúng như bài gốc — không bịa thêm, không suy diễn.
- TUYỆT ĐỐI KHÔNG dùng các từ mang nghĩa xếp hạng/so sánh tuyệt đối như "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất", "lớn nhất"... khi bài gốc không có tài liệu/số liệu chứng minh cho khẳng định đó. Nếu bài gốc tự dùng các từ này mà không kèm nguồn chứng minh, phải diễn đạt lại trung lập hơn (vd: "một trong những trường được đánh giá cao" thay vì "trường tốt nhất").
- KHÔNG copy nguyên văn câu/đoạn dài từ bài gốc — cô đọng thành 1-2 câu bằng chữ riêng.
- Giọng văn: ngắn gọn, vào thẳng ý chính ngay câu đầu — Mastodon không cắt "…more" như Instagram nhưng người đọc lướt timeline rất nhanh, câu đầu yếu là mất người đọc.

## Độ dài & cấu trúc

- Giới hạn cứng: **500 ký tự** (đo theo cách Mastodon tính, xem dưới) — vượt quá bị API từ chối (HTTP 422).
- **Link luôn được tính đúng 23 ký tự bất kể độ dài thật** (đây là hành vi thật của Mastodon — `characters_reserved_per_url` trong cấu hình instance, tương tự cách Twitter rút gọn t.co link). Vì vậy ngân sách chữ thực tế cho phần nội dung + hashtag là khoảng 500 − 23 = **~477 ký tự** khi toot có đúng 1 link.
- Đếm ký tự BẮT BUỘC qua `node scripts/mastodon-json.js char-count <file>` — KHÔNG tự đếm bằng mắt hay `.length` thô (không phản ánh đúng cách Mastodon tính link).
- Mục tiêu thực tế: **200-350 ký tự nội dung** (chưa tính link) — đủ truyền tải ý chính, không cố nhồi cho đầy 500.
- Link nguồn đặt ở CUỐI toot, dòng riêng, dạng URL trần (KHÔNG bọc Markdown `[text](url)` hay HTML `<a>` — Mastodon không parse, sẽ hiển thị nguyên ký tự thừa). Mastodon tự động biến URL trần thành link clickable + tự tạo preview card (ảnh/tiêu đề trang nguồn) — không cần làm gì thêm.
- Từ khóa chính xuất hiện tự nhiên trong câu đầu hoặc câu thứ hai — không nhồi nhét, không lặp lại nhiều lần trong 1 toot ngắn.
- Hashtag: tối đa 2-4, chỉ dùng nếu có từ/cụm liên quan chuyển thành hashtag tự nhiên được (ASCII hoặc không dấu, viết liền không khoảng trắng); KHÔNG ép từ khóa tiếng Việt có dấu thành hashtag nếu đọc gượng gạo. Đặt cuối toot, sau dòng link hoặc ngay trước dòng link đều được — không bắt buộc phải có hashtag.

## Cấu trúc gợi ý

1. **Câu mở (1 câu, chứa từ khóa chính)** — nêu thẳng vấn đề/thông tin đáng chú ý nhất.
2. **1 câu bổ sung (tuỳ chọn)** — thêm 1 ý/số liệu nổi bật từ bài gốc, chỉ thêm nếu còn ngân sách ký tự.
3. **Dòng link** — URL nguồn trần, dòng riêng.
4. **Hashtag (tuỳ chọn)** — 2-4 hashtag liên quan trực tiếp, cuối toot.

## Self-check trước khi đăng

- [ ] `node scripts/mastodon-json.js char-count <file>` trả về ≤500.
- [ ] Từ khóa chính xuất hiện tự nhiên trong 1-2 câu đầu.
- [ ] Có ĐÚNG 1 URL trần trong toot (URL nguồn) — không có Markdown/HTML link nào.
- [ ] Không câu nào copy nguyên văn >1 câu so với bài gốc.
- [ ] Không có từ xếp hạng tuyệt đối ("nhất", "duy nhất", "số 1", "hàng đầu"...) mà không có tài liệu/số liệu chứng minh.
- [ ] Hashtag (nếu có) ≤4, liên quan trực tiếp chủ đề, không có khoảng trắng trong từng hashtag.
