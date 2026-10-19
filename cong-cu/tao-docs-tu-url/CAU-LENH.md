# Câu lệnh tạo file Docs "Tối ưu nhanh" (Trang dùng — dán thẳng vào Claude)

> Chốt 19/10/2026: **tên file chỉ còn từ khóa chính** (bỏ "Loại TU - ID -").

```
Hãy tạo file Google Docs cho các bài trong sheet sau:
https://docs.google.com/spreadsheets/d/1C6cI5gg9jrnn5PjUbwIxWN6ZHCRLEbIydRrCrVfVeHY/edit
Tab: "3. Tối ưu nhanh"

PHẠM VI
- Chỉ làm những dòng có cột N (PIC) = "Trang" VÀ cột I (Link docs) còn trống.
- Không đụng vào dòng của người khác. Dòng chưa có URL thì bỏ qua.

MỖI URL (cột E) TẠO 1 FILE GOOGLE DOCS, NỘI DUNG THEO THỨ TỰ:
1. "URL: <đường dẫn bài>" (có link bấm được)
2. Dòng trống → Title của bài (thẻ title): in đậm, căn giữa
3. Dòng trống → Meta description: chữ màu xám, căn giữa
4. Dòng trống → Toàn bộ nội dung bài viết, giữ nguyên chữ, tiêu đề mục, in đậm/nghiêng,
   gạch đầu dòng, bảng, link, ảnh. Không tóm tắt, không sửa chữ.
   - Chữ căn đều 2 bên.
   - Ảnh và chú thích ảnh căn giữa.
   - Không kẻ khung quanh title/meta, không lặp lại tiêu đề H1.
   - Bỏ phần không thuộc bài: menu, chân trang, nút bấm, "Bài viết liên quan".

ĐẶT TÊN FILE
- Tên file = từ khóa chính ở cột D.
- Nếu cột D trống: lấy từ khóa theo đường dẫn bài, viết lại có dấu cho khớp tiêu đề bài.

SAU KHI TẠO
- Lưu file vào thư mục: https://drive.google.com/drive/folders/1Opbv9Mkgi4szJID_P3RKy-M-pWpI-73k
- Điền link file vào cột I đúng dòng.
- Tự soát vài file: chữ đủ như bài gốc, ảnh và chú thích đã căn giữa.
- Báo lại: đã làm những dòng nào, bài nào lỗi (404, trang sản phẩm, URL trùng),
  từ khóa nào phải tự lấy vì cột D trống.

LƯU Ý KỸ THUẬT
- Tải bài qua "www.techcombank.com" (bản không có www bị chặn).
- Công cụ có sẵn trong kho: cong-cu/tao-docs-tu-url/
```
