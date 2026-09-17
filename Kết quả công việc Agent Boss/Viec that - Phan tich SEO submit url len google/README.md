# Từ khóa: cách submit url lên google

Trang chưa có bài. Đây là bài viết mới.

## Đã làm (16/09/2026)

1. Thu thập 7 URL đối thủ Trang đưa. **Mở đọc được 6/7.**
   Bài brandsvietnam.com bị tường lửa Cloudflare chặn (lỗi 403) — đã thử 6 cách, không vào được.
   **Không đoán nội dung bài đó.**
2. Phân tích search intent **từng đối thủ một** (yêu cầu riêng của Trang): mỗi bài chấm
   dàn ý · intent thật sự phục vụ · khớp từ khóa không · mạnh · yếu · nỗi đau đã gỡ và chưa gỡ.
   Mọi nhận xét đều có câu trích từ chính bài đó.
3. Đối chiếu với **tài liệu chính thức của Google** — tìm ra 4 điểm đối thủ dạy sai hoặc dạy thứ đã chết.
4. Bảng khoảng trống 15 dòng → 6 khoảng trống vàng.
5. Đề xuất outline chi tiết 10 mục.
6. Dựng **file outline content theo đúng mẫu của Trang** (chốt 16/09/2026):
   tiêu đề → sapo → các mục đánh số, mỗi mục có nội dung định hướng + link tham khảo +
   dòng `Yêu cầu:` nói rõ cách trình bày.
   **Không dùng mục "chủ đề xuyên suốt"** — cái đó chỉ dành cho nhóm bài nội thất (deco).

7. **Dựng lại bản 2 (17/09/2026)** sau góp ý của Trang: bản 1 đi xa search intent.
   Bỏ 2 mục lạc đề, thêm 2 mục đúng intent ("kiểm tra đã index chưa" 4/6 bài có,
   "mẹo index nhanh hơn" 5/6 bài có), từ 10 mục xuống 9 mục, độ dài giảm còn 1.800–2.200 chữ.
   Bài học ghi ở `LINK-GOOGLE-DOCS.md`.

## Đang chờ Trang

- **Ảnh chụp màn hình Google Search Console (8–10 ảnh, giao diện tiếng Việt)** — bắt buộc,
  bài hướng dẫn thao tác thiếu ảnh là hỏng.
- Tên + chức danh người đứng tên bài.
- Một ca thật của SEONGON về submit / gỡ lỗi không được index.
- Bài đăng ở đâu, có bài nào để trỏ link nội bộ không.

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `outline-content-submit-url-ban2.html` | **File outline content bản 2** — bản chính để viết bài |
| `outline-content-submit-url.html` | Bản 1 — giữ để đối chiếu, đã bị thay |
| `phan-tich-va-outline-submit-url.html` | Bản phân tích 7 đối thủ — tài liệu nền, để tra cứu bằng chứng |
| `nguon-dung/` | Mã dựng file: `phan_a.py` … `phan_h.py`, `dung.py` |
| `LINK-GOOGLE-DOCS.md` | Link tài liệu trên Drive |

Dựng lại bản phân tích: `python3 nguon-dung/dung.py`

## Nguồn tài liệu Google đã dùng làm bằng

- Indexing API chỉ dùng cho JobPosting / BroadcastEvent — developers.google.com/search/apis/indexing-api/v3/quickstart
- Cổng ping sitemap đã ngừng (26/6/2023) — developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping
- Chính sách chống spam, mục Link spam — developers.google.com/search/docs/essentials/spam-policies
- Thời gian thu thập dữ liệu, không đảm bảo index, submit lại không nhanh hơn — developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
