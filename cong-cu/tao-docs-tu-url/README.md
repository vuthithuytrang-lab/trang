# Tạo file Google Docs "Tối ưu nhanh" từ URL bài Techcombank

Mỗi URL → 1 file Google Docs chứa URL, Title, Meta và toàn bộ bài viết; link điền vào cột I.

## Sheet & tab chính thức (từ 16/10/2026)

- Sheet: https://docs.google.com/spreadsheets/d/1C6cI5gg9jrnn5PjUbwIxWN6ZHCRLEbIydRrCrVfVeHY/edit
- Tab: **`3. Tối ưu nhanh`** (sheetId 853841798)
- Cột: A STT · B ID · C Topic · D Từ khóa chính · E URL bài đăng · F Loại TU · I Link docs · J Tình trạng · N PIC
- **Chỉ làm dòng có PIC (cột N) = "Trang" VÀ cột I còn trống.** Không đụng dòng của người khác.
- **Chỉ chạy khi Trang báo** đã đẩy dòng mới vào — không tự chạy.
- Thư mục Drive chứa file: https://drive.google.com/drive/folders/1Opbv9Mkgi4szJID_P3RKy-M-pWpI-73k
  Trang mở quyền "ai có link cũng sửa" ở cấp thư mục → file mới tạo xong phải chuyển vào đây
  (Drive `update_file` với `parentId = 1Opbv9Mkgi4szJID_P3RKy-M-pWpI-73k`).

## Quy tắc đặt tên file

`F - B - Từ khóa` → ví dụ `Tối ưu nhanh - WebTUN785 - Giấy phép kinh doanh`.
Nếu cột D trống: lấy từ khóa từ đường dẫn bài (slug) rồi khớp lại chữ có dấu trong H1/title (script tự làm).

## Mẫu trình bày Trang đã duyệt

1. `URL: <link>`
2. dòng trống → **Title** in đậm, căn giữa
3. dòng trống → Meta description chữ xám, căn giữa
4. dòng trống → toàn bộ thân bài, **căn đều 2 bên**
5. **Ảnh và chú thích ảnh căn giữa** (yêu cầu 15/10/2026)

Không kẻ khung quanh title/meta, không lặp lại H1.

## Quy trình (agent tự làm, Trang không cần thao tác)

1. Đọc tab trên, lọc dòng PIC = Trang và cột I trống.
2. Ghi `urls.txt` (mỗi dòng: `ID URL`), tải trang qua **`www.techcombank.com`**
   (tên miền không có `www` bị tường lửa chặn; có `www` thì vào được) vào `raw/ID.html`.
3. `SP=<thư mục chứa urls.txt> python3 build.py` → `out/ID.html` + `out/index.json` (từ khóa, loại trang).
4. Tải từng file lên Drive: `create_file`, `contentMimeType: text/html` → Google tự chuyển thành Docs.
   Nhiều file thì chia cho vài agent con chạy song song (mỗi agent ~6 file).
5. Chuyển file vào thư mục Drive ở trên, điền link vào cột I đúng dòng.
6. Soát: xuất PDF vài bài (`download_file_content`, `application/pdf`), so độ dài chữ với bản gốc, nhìn ảnh bố cục.

## Lưu ý đã gặp (15–16/10/2026)

- Trang sản phẩm (không phải blog) không có khung `.article-text` → script lấy chữ theo tiêu đề/đoạn, bỏ nút bấm.
- Bài đã bị gỡ (404, "Không tìm thấy trang") → để trống cột I và báo Trang.
- Hai dòng trùng URL vẫn tạo 2 file theo 2 ID, nhưng báo cho Trang biết.
- Không mở được quyền "ai có link cũng sửa" qua công cụ (`share_file` chỉ nhận email) → dùng thư mục chung.
- Chưa có kết nối Google Docs → không sửa được file đã tạo; muốn sửa phải bật kết nối hoặc tạo lại file.
