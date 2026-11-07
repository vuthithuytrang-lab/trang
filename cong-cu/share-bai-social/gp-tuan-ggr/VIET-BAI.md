# Viết bài cho Google Group techcombankvietnam (GG Group - Tuấn) — dự án GP

Mỗi dòng trong `plan.json` là 1 bài gốc (`url`) cần thêm 1 bản đăng lên Google Group. Viết 1 bài mới (gửi dạng email HTML, tiêu đề = Subject).

## Đầu ra cho mỗi `row`
- `bai/<row>/ggr.html` — nội dung bài, **mỗi khối 1 dòng** (mỗi `<p>`, `<h2>`, `<h3>`, `<ul>…</ul>`, `<ol>…</ol>` nằm trên 1 dòng; `<li>` có thể nằm trong cùng dòng với `<ul>` hoặc mỗi `<li>` một dòng như mẫu).
- `bai/<row>/meta.json` — `{"kw": "...", "title": "..."}`
  - `kw`: từ khóa chính 2–6 chữ, lấy từ chủ đề bài gốc (tiếng Việt có dấu, chữ thường).
  - `title`: **55–70 ký tự**, chứa nguyên `kw`, không có chữ "checklist".
- Mẫu tham khảo định dạng: `../gp-tuan-wix/bai/309/wix.html (chỉ tham khảo định dạng)` và `meta.json`.

## Quy tắc nội dung (bắt buộc)
1. Tiếng Việt đủ dấu, **900–1100 từ**.
2. Đọc bài gốc thật (WebFetch). Giữ đúng nghĩa và **mọi số liệu**; không thêm số liệu, không suy diễn. **Không đọc được bài gốc thì KHÔNG viết** — ghi row đó vào báo cáo.
3. Diễn đạt lại hoàn toàn, không chép nguyên câu bài gốc.
4. Không dùng từ xếp hạng tuyệt đối: duy nhất, số 1, hàng đầu, tốt nhất, cao nhất, rẻ nhất, lớn nhất, uy tín nhất, nhanh nhất, thấp nhất, hiệu quả nhất.
5. `kw` có ở tiêu đề, đoạn mở đầu và rải 3–5 lần tự nhiên trong bài.
6. **Đúng 1 link**: `<a href="URL bài gốc">kw</a>` ở đoạn mở đầu. Không link nào khác.
7. Không hotline, email, số điện thoại.
8. Không có đoạn/heading "Kết luận", "Tóm lại", "Tổng kết", "Tóm tắt", "Lời kết".
9. Câu cuối bài: `<p>Lưu ý: thông tin trong bài chỉ mang tính tham khảo và có thể thay đổi theo từng thời điểm.</p>`
10. Chỉ dùng thẻ `p, h2, h3, ul, ol, li, strong, a`. Không H1, không markdown, không style.
11. Bài phải **khác rõ rệt** các bản đã share từ cùng bài gốc (link trong `bai_khac_cung_nguon`): khác tiêu đề, đoạn mở, cách sắp xếp ý. Góc viết cho đợt này: **mở bằng một tình huống thực tế của người đọc, rồi đi theo dạng hướng dẫn từng bước / các lưu ý thực hành**, H2 dạng mệnh đề (không đánh số câu hỏi).

## Tự kiểm tra
`cd /home/user/trang/cong-cu/share-bai-social/gp-tuan-ggr && python3 dang_ggr.py check <row>` — phải không còn lỗi nào. Sửa đến khi sạch.
Không chạy lệnh `post` hay `run`, không đăng bài, không sửa `plan.json`, `dang_ggr.py`.

## Đọc bài gốc
- Dùng WebFetch hoặc curl thường (KHÔNG giả User-Agent trình duyệt, không tìm cách vượt chặn).
- Nếu mục trong plan.json có `nguon_local` → đọc nội dung bài gốc từ file đó (Trang đã gửi bản chụp).
- Không đọc được toàn văn bài gốc thì bỏ qua row đó và báo lại. Không bịa.
- Trong `bai_khac_cung_nguon` có cả link Google Group khác (techcombank-bloggroups) và Wix — bài mới phải khác hẳn các bản đó.
