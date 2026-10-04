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
- Mỗi bài = 5 dòng liên tiếp (dòng đầu có Key, 4 dòng sau để trống cột A), sau đó 1 dòng trống ngăn cách.
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
2. **Title**: chứa từ khóa chính.
3. **Content**: bài viết lại từ bài gốc, triển khai quanh:
   - từ khóa chính
   - từ khóa phụ 1
   - từ khóa phụ 2
   *(Cần bổ sung: từ khóa phụ lấy từ đâu, và 3 dòng `#keyword` là tiêu đề mục hay hashtag — chờ Trang xác nhận.)*
4. **Dòng hashtag** (nguyên mẫu, thay từ khóa thật, viết không dấu nối gạch):
   `#asiagroup #<key-chinh> #<key-phu-1> #<key-phu-2> #tap-doan-nguyen-lieu-a-chau-aig #asia-ingredients-group`
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
