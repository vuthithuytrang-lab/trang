# Bài viết tối ưu — thiết kế văn phòng 80m2

| File | Dùng khi nào |
|---|---|
| **`ban-cho-google-docs.html`** | **Xuất sang Google Docs hoặc Word.** Ảnh đã nhúng thẳng vào file — mở bằng trình duyệt, bấm Cmd+A rồi Cmd+C, dán vào Docs là ảnh đi theo. Không còn mã `[caption]` nào. |
| `ma-dan-vao-wordpress.html` | Dán thẳng vào trình soạn thảo WordPress. Giữ mã `[caption]` và đường dẫn ảnh gốc trên website nên ảnh không bị tải lại lần nữa. |
| `ban-doc-duyet.html` | Bản xem đẹp để đọc và duyệt trên máy hoặc điện thoại. Ảnh tải từ website nên cần mạng. |
| `anh-png/` | 48 ảnh trong bài đã đổi từ webp sang PNG, đặt tên theo đúng thứ tự trong bài. Dùng khi cần chèn tay từng ảnh. |
| `danh-sach-link-anh.txt` | Danh sách đường dẫn 48 ảnh gốc trên website, mỗi dòng một link. |

**Vì sao ảnh bị lỗi khi dán sang Docs:** file WordPress dùng mã `[caption]` (chỉ WordPress hiểu) và ảnh
định dạng **webp** (Google Docs không nhận). File `ban-cho-google-docs.html` đã gỡ cả hai —
mã caption đổi thành ảnh kèm dòng chú thích, ảnh đổi sang JPG và nhúng thẳng vào file.

**Còn 7 chỗ chờ dữ liệu thật** — mở file, gõ tìm `CẦN BỔ SUNG`.
