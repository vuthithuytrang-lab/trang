# Hướng dẫn 1 lượt đăng (AIG) — dùng cho mỗi lần đến giờ hẹn

Mỗi lượt = **1 dòng trên sheet = 1 bài × 1 nền tảng**. Đọc trước: `du-an/AIG.md` (cấu trúc bài, CHECKLIST, sự cố đã gặp).

## Các bước

1. **Đọc lại dòng trên sheet** (tab `7.2. Share social`). Nếu cột `E` đã có link → lượt này đã xong, dừng.
   Nếu dòng không còn đúng bài/nền tảng như lịch (Trang xóa/chèn dòng) → KHÔNG đăng, báo Trang.
2. **Đọc bài gốc** (cột `B`; key chính = cột `A` của dòng đầu bài). Lấy ảnh `og:image` + 1 ảnh trong bài.
3. **Key phụ**: lấy từ ô Key (sau dấu phẩy) nếu có; không có → chọn 1–2 cụm có thật trong bài gốc.
   Dùng **cùng bộ key phụ cho cả 4 nền tảng của bài đó** — nếu cột `H` dòng đầu bài đã có `Key phụ: ...` thì dùng lại.
4. **Viết bài riêng cho nền tảng này** (khác các nền tảng khác của cùng bài — xem các link đã có ở cột `E` để tránh trùng góc viết):
   - Tiêu đề < 65 ký tự (đếm bằng lệnh), có key chính, đúng insight, thôi thúc click.
   - Mô tả SEO < 165 ký tự, có key chính, trả lời insight + tóm tắt.
   - ~900–1100 từ, key chính + key phụ làm tiêu đề mục H2, **không có mục "Tóm lại/Tóm tắt/Kết luận"**.
   - Đúng 1 link ở key chính về bài gốc. Không "nhất / số 1 / hàng đầu".
   - Cuối bài: dòng hashtag (**Wix viết liền không gạch**) → `Nguồn tham khảo: <link>` → khối liên hệ nguyên văn.
   - **Link Nguồn tham khảo, Website, Fanpage, Youtube phải bấm được.**
   - Ảnh đại diện + 1 ảnh trong bài. Không có ảnh → không đăng.
5. **Đăng bằng skill của nền tảng** (`share-bai-wp` / `share-bai-wix` / `share-bai-blogger` / `share-bai-webflow`), chìa trong
   `.claude/skills/<skill>/*-accounts.local.json`. Slug = key chính không dấu (Blogger: đăng lần đầu với tiêu đề không dấu
   rồi đổi lại tiêu đề thật; Wix: `update-draft-post` đổi `seoSlug`; Webflow: truyền `link <URL gốc>`).
6. **Mở trang thật** (HTTP 200) và soát lại CHECKLIST trên trang thật (link bấm được, hashtag, ảnh, không có "Tóm lại").
7. **Ghi sheet đúng dòng**: `E` link · `F` ngày đăng `dd/mm/yyyy` (thay chữ "Hẹn") · `I` tiêu đề · `J` mô tả ·
   `H` key phụ (dòng đầu bài) hoặc lý do lỗi.
8. Lỗi → để trống `E`, ghi lý do ngắn vào `H`, báo Trang. Không tự đăng lại / xóa bài khi Trang chưa đồng ý.

## Lịch giãn cách

Mỗi lượt cách nhau ≥ 60 phút; mỗi nền tảng ≤ 3 bài/ngày, cách nhau ≥ 3 giờ; chỉ 8:00–21:00 giờ Việt Nam.
Giờ hẹn ghi ở cột `F` dạng `Hẹn 05/10 13:50`.
