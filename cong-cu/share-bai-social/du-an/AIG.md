# Dự án AIG (Asia Ingredients Group) — cấu hình cho agent share-bai-social

> Agent `share-bai-social` đọc mục này để biết dùng sheet nào, cột nào, tài khoản nào.
> KHÔNG ghi mật khẩu/token vào đây. Chìa khóa API của AIG nằm riêng trong các file `*-accounts.local.json`
> (đã chặn commit) — không dùng chung với bất kỳ dự án nào khác.

## Sheet của dự án

- Sheet-key (khai trong `google-sheets-social/sheets-accounts.local.json`): `aig-share-social`
- File: "Nội bộ - PLAN | ASIA | SEO | TRANGVTT"
- Spreadsheet ID: `1os17NKJgF6ME4MdYwUoACnAjZAK4MBevxWd0yBJus9E`
- Tab làm việc: `7.2. Share social` (gid 1179164490)
- Tab danh sách tài khoản: `7.1. Social Doanh Nghiệp` (gid 278111889) — chỉ đọc cột D (link profile).
  Tab này có chứa mật khẩu dạng chữ: agent **không đọc, không chép** cột E/F.

## Cấu trúc sheet — Layout B (mỗi nền tảng 1 dòng)

- Dòng 9 = header thật (`Key | Link bài đăng | Duyệt đăng | Social | Link share | Ngày share | PIC | NOTE | ...`);
  dữ liệu bắt đầu từ dòng 10. Dòng 1–7 là ô thống kê, không đụng tới.
- Cột `A` = Key (từ khóa) · `B` = Link bài gốc · `C` = Duyệt đăng (TRUE/FALSE)
- Cột `D` = Social — **agent tự điền** nền tảng đã chọn (ghi link profile, ví dụ `https://asiaingredientsgroup.wordpress.com/`)
- Cột `E` = Link share — **agent điền** link bài sau khi đăng xong
- Cột `F` = Ngày share (agent điền ngày đăng, dạng dd/mm/yyyy)
- Bài cũ (dòng 10–62): 5 dòng/bài + 1 dòng trống. Bài mới: 4 dòng/bài (4 nền tảng) + 1 dòng trống — xem mục "Trang điền sheet thế nào".
- Chỉ xử lý bài có `C = TRUE` và ô `E` còn trống.

## Nền tảng của AIG (từ tab 7.1, cột D)

| Nền tảng | Link profile (ghi vào cột D) | Skill | Account key | Trạng thái |
|---|---|---|---|---|
| Blogger (= blogspot.com, cùng 1 blog) | `https://asiaingredientsgroup.blogspot.com/` | `share-bai-blogger` | `asiaingredientsgroup.blogspot.com` | ✅ Đã kết nối 04/10/2026 (Google Cloud project riêng `aig-share-social`, In production, blog_id 2314208901361543116) |
| WordPress.com | `https://asiaingredientsgroup.wordpress.com/` | `share-bai-wp` | `asiaingredientsgroup.wordpress.com` | ✅ Đã kết nối 04/10/2026 (app "AIG share social", chìa chỉ cấp cho đúng blog này, không hết hạn) |
| Webflow | `https://asiaingredientsgroup.webflow.io/` | `share-bai-webflow` | `asiaingredientsgroup-webflow` | ✅ Đã kết nối 04/10/2026 |
| Wix | `https://nguyenlieuachau.wixsite.com/asia-group` | `share-bai-wix` | `nguyenlieuachau.wixsite.com/asia-group` | ✅ Đã kết nối 04/10/2026 (chìa cần thay — xem BAO-MAT.md) |
| X (Twitter) | `https://x.com/asiagroupvn` | *chưa có skill* | — | Chưa hỗ trợ |

## Ghi chú kỹ thuật từng nền tảng

- **Google Sheet**: sheet-key `aig-share-social`, OAuth client RIÊNG "AIG Sheets" (khác client Blogger) trong project `aig-share-social`. Đã thử đọc OK 04/10/2026; ghi ô chưa thử.

- **Blogger**: Blogger tự tạo slug từ tiêu đề lúc đăng LẦN ĐẦU và bỏ mất chữ "đ" (vd "đông" → "ong").
  Để slug đúng từ khóa: đăng lần đầu với tiêu đề KHÔNG DẤU = từ khóa chính (vd `trai cay iqf` → `/trai-cay-iqf.html`),
  rồi cập nhật lại tiêu đề tiếng Việt thật (link giữ nguyên). Lệnh tải ảnh `download-image` cần truyền đủ tham số cookie (để chuỗi rỗng).
- **Wix**: site AIG `site_id` 43c11825-0837-44a0-b7ea-7c8800737638, tác giả `asiaseoproject6`.
- **Webflow**: collection **Blogs** (slug `blog`). Cả 5 field đều BẮT BUỘC: `name`, `slug`, `content` (RichText),
  `thumbnail` (ảnh — bài không có ảnh sẽ bị Webflow từ chối), `link` (điền URL bài gốc —
  truyền `link <URL gốc>` vào cuối lệnh `build-item-payload`). Link bài dạng `asiaingredientsgroup.webflow.io/blog/<slug>`.

## Trang điền sheet thế nào (đã thống nhất 04/10/2026)

Trang chỉ điền **1 dòng cho mỗi bài**, ở dòng trống đầu tiên dưới bài cuối cùng:
- `A` = Key, `B` = link bài gốc, tích ô `C` (Duyệt đăng).
- Chừa **5 dòng trống** bên dưới trước khi điền bài tiếp theo (4 dòng cho agent + 1 dòng ngăn cách).

Agent làm phần còn lại cho mỗi dòng có `A` + `B` + `C = TRUE` mà `D` còn trống:
1. Chọn nền tảng (hiện 4: Blogger, WordPress, Webflow, Wix — X chưa hỗ trợ), xoay thứ tự giữa các bài
   (bài sau bắt đầu từ nền tảng kế tiếp bài trước) để không lần nào cũng đăng cùng một thứ tự.
2. Ghi nền tảng thứ 1 vào `D` của chính dòng đó; nền tảng 2–4 vào `D` của 3 dòng ngay dưới,
   đồng thời chép link bài gốc vào `B` của 3 dòng đó (cột `A` để trống, đúng mẫu các bài cũ).
   Nếu 3 dòng bên dưới không trống → KHÔNG ghi đè, báo lại cho Trang.
3. Đăng xong nền tảng nào → ghi link vào `E` và ngày vào `F` của đúng dòng đó.
4. Dòng nào lỗi → để trống `E`, ghi lý do ngắn vào `H` (NOTE).

Các bài cũ (đã có `E`) agent bỏ qua, dù ô `C` tích hay không.

## Cách "so le" — CHỜ TRANG CHỐT

- Tạm thời: đủ 4 nền tảng mỗi bài, xoay thứ tự như trên. Chờ Trang chốt có giãn thời gian giữa các nền tảng không.

## Cấu trúc bài đăng AIG — áp dụng cho MỌI bài, mọi nền tảng (Trang gửi 04/10/2026)

1. **Slug**: tối ưu theo từ khóa chính (không dấu, nối gạch ngang, vd `cong-ty-cung-cap-huong-lieu`).
2. **Tiêu đề SEO (Title)** — Trang dặn 04/10/2026:
   - **Dưới 65 ký tự** (đếm cả dấu cách) — đếm thật trước khi đăng.
   - Chứa từ khóa chính; **đúng insight** người đọc (nỗi lo / mong muốn thật của doanh nghiệp mua nguyên liệu).
   - Có yếu tố **kích thích, thôi thúc click** (lợi ích cụ thể, câu hỏi, con số có thật trong bài) — không giật tít sai sự thật.
   - Ghi tiêu đề đã dùng vào cột `I` (Title bài share) của đúng dòng nền tảng đó.
2b. **Mô tả SEO (Meta description)**:
   - **Dưới 165 ký tự**, khoảng 2–3 dòng.
   - **Trả lời được insight** (mong muốn thầm kín của người đọc) + **tóm tắt** nội dung bài.
   - **Chứa từ khóa chính** (và từ khóa phụ nếu vừa).
   - Ghi vào cột `J` (Mô tả bài share) của đúng dòng; đặt làm mô tả/đoạn trích của bài ở nền tảng nào hỗ trợ
     (WordPress: `excerpt`; Wix: `excerpt`/SEO description; Blogger: không có qua API → chỉ ghi sheet; Webflow: chỉ có nếu collection có field mô tả).
3. **Content**: bài viết lại từ bài gốc, triển khai quanh:
   - từ khóa chính
   - từ khóa phụ 1
   - từ khóa phụ 2
   **Từ khóa phụ là TÙY CHỌN** — chỉ dùng khi Trang ghi trong ô Key (cột A), cách nhau bằng dấu phẩy:
   `bã sắn, từ khóa phụ 1, từ khóa phụ 2` → từ đầu tiên là key chính. Ô Key chỉ có 1 cụm → bài chỉ có key chính.
   Ô Key KHÔNG có key phụ → agent **tự chọn 1–2 key phụ** từ chính nội dung bài gốc (Trang cho phép 04/10/2026):
   cụm từ thật sự xuất hiện trong bài gốc, liên quan trực tiếp key chính, không bịa thông tin mới.
   Ghi key phụ đã chọn vào cột `H` (NOTE) của dòng đầu bài, dạng `Key phụ: a, b`, để Trang soát lại.
   *(Cần bổ sung: 3 dòng `#keyword` trong Content là tiêu đề mục hay hashtag — chờ Trang xác nhận; tạm làm tiêu đề mục H2.)*
4. **Dòng hashtag** (thay từ khóa thật, viết không dấu, nối gạch ngang; bỏ hashtag key phụ nếu không có):
   `#asiagroup #<key-chinh> [#<key-phu-1> #<key-phu-2>] #tap-doan-nguyen-lieu-a-chau-aig #asia-ingredients-group`
   Ví dụ Trang đưa — key "bã sắn", không có key phụ:
   `#asiagroup #ba-san #tap-doan-nguyen-lieu-a-chau-aig #asia-ingredients-group`
3b. **KHÔNG dùng mục "Tóm lại" / "Tóm tắt" / "Kết luận"** làm tiêu đề mục trong bài (Trang dặn 04/10/2026).
   Đoạn chốt cuối bài vẫn viết bình thường nhưng không đặt tiêu đề kiểu đó — có thể để không tiêu đề,
   hoặc dùng tiêu đề mang nội dung (vd "AIG đồng hành cùng doanh nghiệp thế nào?").
4b. **Ảnh — BẮT BUỘC mọi bài, mọi nền tảng** (Trang dặn 04/10/2026): dùng ảnh đại diện của bài gốc (thẻ `og:image`),
   làm ảnh đại diện bài + chèn 1 ảnh trong thân bài. Không lấy được ảnh → KHÔNG đăng, ghi lý do vào cột `H`.
5. **Nguồn tham khảo**: `Nguồn tham khảo: <link bài gốc ở cột B>`
6. **Khối liên hệ — chép NGUYÊN VĂN, không sửa chữ nào:**

```
Thông tin liên hệ:
Asia Ingredients Group
Địa chỉ: Tòa nhà AIG – Lô TH-1B Đường số 7 Khu Thương mại Nam Khu Chế Xuất Tân Thuận, Phường Tân Thuận, TP HCM, Việt Nam
SĐT: +84 28 5411 1557
Email: contact@asiagroup-vn.com
Website: https://asiagroup-vn.com/

Follow social:
Fanpage: https://www.facebook.com/tapdoanaig
Youtube: https://www.youtube.com/@AIG2001
```

Quy tắc chung của skill vẫn giữ: viết lại không chép nguyên câu, ~1000 từ, gắn link bài gốc vào 1 lần xuất hiện
từ khóa chính, không dùng "nhất / số 1 / hàng đầu" khi không có chứng minh.
