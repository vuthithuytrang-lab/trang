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
5. Đề xuất chủ đề xuyên suốt + outline chi tiết 10 mục.

## Đang chờ Trang

- **Chốt chủ đề xuyên suốt ở mục F** — chưa chốt thì chưa viết bài.
- Ảnh chụp màn hình Google Search Console (8–10 ảnh) — bắt buộc cho bài hướng dẫn thao tác.
- Ảnh chụp trang kết quả Google cho từ khóa.
- Tên + chức danh người đứng tên bài.
- Một ca thật của SEONGON về submit / gỡ lỗi không được index.

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `phan-tich-va-outline-submit-url.html` | Bản đọc được trên máy — giống hệt bản Google Docs |
| `nguon-dung/` | Mã dựng file: `phan_a.py` … `phan_h.py`, `dung.py` |
| `LINK-GOOGLE-DOCS.md` | Link tài liệu trên Drive |

Dựng lại file: `python3 nguon-dung/dung.py`

## Nguồn tài liệu Google đã dùng làm bằng

- Indexing API chỉ dùng cho JobPosting / BroadcastEvent — developers.google.com/search/apis/indexing-api/v3/quickstart
- Cổng ping sitemap đã ngừng (26/6/2023) — developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping
- Chính sách chống spam, mục Link spam — developers.google.com/search/docs/essentials/spam-policies
- Thời gian thu thập dữ liệu, không đảm bảo index, submit lại không nhanh hơn — developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
