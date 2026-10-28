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

---

## Luồng "Plan internal links" (từ 19/10/2026) — Bước 1 tạo Docs + Bước 2 chèn link

Câu lệnh gốc: `CAU-LENH-INTERNAL-LINKS.md`. Kết quả từng đợt chạy: thư mục `plan-internal-links/`
(`tien-do.csv`, `bao-cao.md`, `cho-duyet.md`, `ke-hoach-chen-*.json`).

- Thư mục Drive: **Plan internal links - File blog** — https://drive.google.com/drive/folders/1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH
- Sheet: tab "Plan internal links - Tổng" — cột thật: B URL · F/G anchor + URL tỷ giá · H FILE BLOG · I đề xuất tỷ giá ·
  J-K, L-M, N-O, P-Q, R-S = Anchor text N / URL đích N (**từng cặp 2 cột**, không có cột "Nội dung chèn ACN").

Quy trình:
1. Tải bài qua `www.techcombank.com` **kèm User-Agent trình duyệt** (thiếu UA → Akamai trả 403 "Access Denied").
2. `python3 prep.py raw/*.html` — bỏ công cụ quy đổi tiền và thẻ "Tìm hiểu thêm" nằm trong khung bài.
3. `SP=<thư mục>/ python3 build.py` → `out/<id>.html`.
4. Soạn `plan.json` (mỗi bài 1 danh sách thao tác, đánh số đoạn theo `blocks.py`):
   `tygia` (áp nguyên văn cột I) · `phrase` (gắn link vào cụm có sẵn) · `sentence` (viết thêm 1 câu vào đoạn) · `xemthem` (dòng >>> riêng).
5. `python3 -I chen.py <thư mục>/` → `final/<id>.html` (tô vàng chữ mới/đổi, ghi chú đỏ nghiêng ngay sau).
6. `python3 -I soat.py <thư mục>/` — soát % vị trí, đoạn kề có link, bài đã có sẵn link đúng URL đích.
7. Tải `final/<id>.html` lên Drive (`create_file`, `text/html`, `parentId` = thư mục trên) → điền link vào cột H (từng ô).

Giới hạn đã gặp: công cụ Drive không tạo được comment, và `share_file` chỉ chia sẻ theo email
→ quyền "Bất kỳ ai có đường liên kết – Người chỉnh sửa" phải mở ở cấp thư mục bằng tay.

### Quy tắc Trang chốt thêm (19/10/2026, sau khi xem chạy thử)
- **Sheet có bao nhiêu anchor thì chèn đủ bấy nhiêu** (cặp tỷ giá F-G + mọi cặp Anchor/URL đích N có dữ liệu).
  Không để anchor nào chỉ nằm trong `cho-duyet.md`: không có cụm sẵn thì viết thêm câu "xem thêm" hoặc đoạn mới
  (`xemthem` / `doanmoi`), chèn thẳng vào file, ghi chú đỏ **[Đề xuất viết thêm đoạn mới]** đặt TRÊN, cách 1 dòng trống.
- Bài gốc đã có sẵn link đúng URL đích (`dacolink`): giữ link cũ, không chèn trùng, thêm ghi chú đỏ ngay sau đoạn đó.
- Sau khi chèn xong phải chạy lại `soat.py`: bài dài thêm làm % vị trí lùi lại, câu nằm sát mốc 25% có thể lọt vào 25% đầu.
- **Ghi cột E (Ghi chú)** sau mỗi dòng (Trang cho phép 19/10/2026, ô E trống mới ghi): "Đủ x/N anchor. Đã chèn mới (k): anchor (cách chèn); …
  Bài đã có sẵn link đúng URL, giữ nguyên (m): …  Thiếu: … / không." N = cặp tỷ giá F-G + mọi cặp Anchor/URL N có dữ liệu,
  đối chiếu với cột C "Số link chèn".
- Ghi chú đoạn sửa: **[Nội dung gốc trước khi chèn: …]** (đổi từ "[Trước khi chèn: …]" theo Trang 19/10/2026).
  Mọi anchor đều tô vàng, kể cả link có sẵn được giữ nguyên (`dacolink`).
- **Anchor phải đúng NGUYÊN VĂN cụm trong sheet** (chỉ được viết hoa tên riêng). Nếu bài đã có link tới URL đích nhưng gắn trên
  cụm chữ khác (VD "1 Yên bằng khoảng 164.7 đồng" thay vì "1 Yên bằng bao nhiêu tiền Việt") thì dùng `chuyenlink`: bỏ link
  khỏi cụm cũ, gắn vào đúng anchor (cụm có sẵn trong đoạn, hoặc viết thêm 1 câu), tô vàng, ghi chú link cũ đã chuyển.
  `dacolink` chỉ dùng khi chữ của link cũ TRÙNG KHỚP anchor. Kiểm tra cuối: mỗi anchor sheet = chữ của 1 link tới đúng URL.
- Bộ soát bắt buộc trước khi tải lên: `kiemtra.py` (anchor nguyên văn + tô vàng + 25%), `linkcu.py` (không mất link gốc),
  `cautruc.py` (không mất bảng/hàng/gạch đầu dòng/ảnh). Sau khi tải lên: xuất PDF và so chữ (`verify.py`).
- Google Docs biến "NT$; … NT$" thành công thức toán → chen.py tự bọc mỗi dấu $ trong span riêng.

---

## Dự án Okamura — inlink (từ 28/10/2026)

- Sheet: `1xKnPX-uf7av3FpSocVjy9wKJiNeygrsZLVmdcMC7np8`, tab **"Trang tính146"**.
- Cột: D Từ khoá chính (= tên file) · E Landingpage (URL bài) · L/M, N/O, P/Q = 3 cặp anchor/URL · R Tình trạng · **S Fie Blog** (link file).
  H/I (Big Content), J/K (Danh mục) hiện trống.
- Chỉ làm dòng R ≠ "Đã done" và S trống. R = "-" (dòng 9, bàn văn phòng) coi như bỏ qua.
- Thư mục Drive: **Okamura - Inlink - File blog** — https://drive.google.com/drive/folders/1dfPI34Qf5mFI1ALHl5vWU8MUKrqVnwiU
- Site Wix: dựng bằng `BASE=https://www.okamura.com.vn SEL='[data-hook="post-description"]' python3 build.py` (không chạy prep.py);
  build.py tự đổi ảnh mờ của Wix sang ảnh gốc. Bổ sung cho worker: `okamura/BO-SUNG-OKAMURA.md`.
