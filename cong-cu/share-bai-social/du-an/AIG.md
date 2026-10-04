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

## Cách chọn 5 nền tảng "so le" — CHỜ TRANG CHỐT

- Cần bổ sung: Trang muốn so le theo cách nào (xem ghi chú trong `GHI-CHU.md`).

## Quy tắc viết bài riêng cho AIG

- Cần bổ sung (từ cấm, tên thương hiệu viết đúng nguyên văn, ...).
