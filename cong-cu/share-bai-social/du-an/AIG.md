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
| Blogger (= blogspot.com, cùng 1 blog) | `https://asiaingredientsgroup.blogspot.com/` | `share-bai-blogger` | `asiaingredientsgroup.blogspot.com` | Cần setup |
| WordPress.com | `https://asiaingredientsgroup.wordpress.com/` | `share-bai-wp` | `asiaingredientsgroup.wordpress.com` | Cần setup |
| Webflow | `https://asiaingredientsgroup.webflow.io/` | `share-bai-webflow` | `asiaingredientsgroup-webflow` | Cần setup |
| Wix | `https://nguyenlieuachau.wixsite.com/asia-group` | `share-bai-wix` | `nguyenlieuachau.wixsite.com/asia-group` | Cần setup |
| X (Twitter) | `https://x.com/asiagroupvn` | *chưa có skill* | — | Chưa hỗ trợ |

## Cách chọn 5 nền tảng "so le" — CHỜ TRANG CHỐT

- Cần bổ sung: Trang muốn so le theo cách nào (xem ghi chú trong `GHI-CHU.md`).

## Quy tắc viết bài riêng cho AIG

- Cần bổ sung (từ cấm, tên thương hiệu viết đúng nguyên văn, ...).
