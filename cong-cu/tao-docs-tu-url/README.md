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

`F - B - Từ khóa` → ví dụ `Tối ưu nhanh - WebTUN785 - Giấy phép kinh doanh`. **Giữ nguyên cách này cho luồng "Tối ưu nhanh".**

> ⚠️ Yêu cầu ngày 19/10/2026 (tên file chỉ còn từ khóa chính, sheet "Plan internal links") là **luồng KHÁC**,
> không áp dụng cho luồng này. Câu lệnh của luồng đó: `CAU-LENH-INTERNAL-LINKS.md`.
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

## ✅ ĐÃ XONG 01/11/2026 — 7 bài Business_Lending (giữ lại làm mẫu tham khảo)

Sheet riêng của Trang: https://docs.google.com/spreadsheets/d/1GVPQPqSN7lAe-BItxtB9BD8_Qx3c_jBhXreVbCLUCYg/edit
(tab "Trang tính1": URL cột C, link Docs điền cột D, tên file = từ khóa chính cột E).
Đã tạo 7 Docs trên Drive vuthithuytrang@seongon.com và gắn link cột D (khớp theo URL, vì Trang có xoá/chèn dòng trong lúc chạy — số dòng dưới đây là lúc đọc, sau đó lệch lên 1), vào thư mục chung
(Trang đã mở công khai "ai có link cũng sửa" cho thư mục ngày 01/11):

| Dòng | URL | Tên file |
|---|---|---|
| 62 | /thong-tin/blog/nen-vay-tin-chap-o-dau | cần vay vốn ngân hàng |
| 63 | /thong-tin/blog/kinh-nghiem-chuyen-doi-tu-ho-kinh-doanh-len-doanh-nghiep | hồ sơ vay doanh nghiệp chuyển đổi từ hộ kinh doanh |
| 64 | /thong-tin/blog/cac-hinh-thuc-vay-von-ngan-hang | vay doanh nghiệp nhỏ |
| 68 | /thong-tin/blog/lai-suat-the-tin-dung | số ngày miễn lãi thẻ tín dụng doanh nghiệp |
| 69 | /thong-tin/blog/thu-tuc-vay-von-kinh-doanh-nho | vay tiền bằng giấy phép kinh doanh |
| 71 | /thong-tin/blog/vay-von-doanh-nghiep-khong-the-chap | thủ tục vay doanh nghiệp mới không cần tài sản đảm bảo |
| 72 | /thong-tin/blog/vay-tin-chap-toi-da-duoc-bao-nhieu | hạn mức cho vay doanh nghiệp sme |

⚠️ Trước khi tạo: kiểm tra Drive đang kết nối đúng tài khoản Trang (`search_files owner='me'` → owner phải là
vuthithuytrang@seongon.com). Ngày 01/11 connector từng bị nối nhầm tuanmai2k4@gmail.com — KHÔNG tạo file ở đó.

## Trang nguồn khác Techcombank (01/11/2026)
- `build.py` đọc được thêm **asiagroup-vn.com** (WordPress): khung bài `section.main_content_post div.col.large-8`,
  bỏ mục lục ez-toc + khối "Thẻ / Chia sẻ", ảnh lazy (`data-lazy-src`), chú thích `figcaption` → đoạn nghiêng căn giữa.
- **Ảnh webp không hiện trong Google Docs** → script tự đổi link ảnh webp sang `https://wsrv.nl/?url=...&output=jpg`.
  Đã thử: bản không đổi → 0 ảnh; bản đổi → đủ ảnh.
- Trang nguồn mới khác: kiểm tra khung bài bằng H2 đầu tiên rồi thêm selector vào `article()`.
