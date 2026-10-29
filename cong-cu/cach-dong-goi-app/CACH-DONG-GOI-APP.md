# Cách đóng gói một việc thành "app" — học từ dự án "Thư ký công việc" (29/10/2026)

> Nguồn: tài liệu bàn giao một đồng nghiệp ở SEONGON gửi Trang ngày 29/10/2026 (dự án trang quản lý công việc).
> Chỉ chép lại **cách làm**, không chép tên khách hàng / số liệu / link của dự án đó (repo này public).

## 1. Khuôn mẫu họ dùng

| Phần | Họ làm thế nào | Vì sao hay |
|---|---|---|
| **Một file duy nhất** | Toàn bộ app = 1 file HTML (HTML + CSS + JavaScript thuần), không máy chủ, không cơ sở dữ liệu, không thư viện ngoài (trừ font) | Dễ sửa, dễ chuyển chỗ, không có gì để "sập" |
| **Dữ liệu** | Lưu trong trình duyệt của từng người (localStorage), có nút **Sao lưu / Khôi phục** ra file | Không tốn tiền máy chủ; mỗi người một bảng riêng |
| **Đưa lên web** | Kho GitHub → **Netlify tự đăng** mỗi lần đẩy code (khoảng 20 giây) → link cố định `ten-app.netlify.app` | Miễn phí, link mở được trên mọi máy, không cần đăng nhập |
| **Mở nhanh** | Lối tắt trên Desktop trỏ tới link web | Dùng như phần mềm cài trên máy |
| **Phiên bản** | Dòng chú thích số phiên bản trong file (vd `2026-09-19d`), tăng mỗi lần sửa | Mở trang là biết đang chạy bản nào |
| **Dữ liệu ngoài** | Nhập số liệu bằng cách **tải file .csv** từ Google Sheets rồi chọn file trên trang (không "công bố file lên web" vì lộ dữ liệu khách) | Không lộ dữ liệu, không cần quyền đặc biệt |
| **Bàn giao** | Một trang HTML "Tài liệu bàn giao" có nút **📋 Copy toàn bộ để dán cho AI khác** | AI/người mới đọc là làm tiếp được, không phải hỏi lại từ đầu |

## 2. Tài liệu bàn giao của họ có 10 mục — dùng làm khung chuẩn

1. Cách dùng tài liệu (đọc hết trước khi làm)
2. Người dùng: tên, cách xưng hô, trình độ kỹ thuật, cách giao việc
3. Sản phẩm là gì, nằm ở đâu (file gốc, link web, kho code, lối tắt)
4. **Các quyết định người dùng ĐÃ CHỐT — đừng làm ngược lại** (đánh số, mỗi dòng 1 quyết định)
5. Tính năng hiện có
6. Cấu trúc dữ liệu
7. Quy trình sửa và đưa lên web (từng bước, có bước kiểm tra rò rỉ dữ liệu trước khi đẩy lên)
8. Bẫy kỹ thuật đã gặp trên máy đó
9. Việc còn dở / đã đề xuất nhưng chưa làm
10. Lời khuyên cho AI tiếp nhận

## 3. Thói quen làm việc đáng học

- **Hỏi trước, làm sau:** 2–4 câu trắc nghiệm có sẵn phương án "Nên chọn", rồi làm một mạch.
- **Tự kiểm thử rồi mới báo xong** (chạy trình duyệt ẩn, chụp màn hình).
- **Kiểm tra rò rỉ trước mỗi lần đẩy lên kho public:** tìm tên khách hàng / link sheet trong file, phải bằng 0.
- **Báo thật** cái gì chưa thử được, nhờ người dùng thử giúp.
- Nói rõ **sau khi sửa người dùng cần làm gì** (thường chỉ F5) và **dữ liệu cũ có mất không**.

## 4. So với cách mình đang làm cho Trang

| | Cách đồng nghiệp | Cách app Check Publish của Trang |
|---|---|---|
| Nơi chạy | Netlify (web công khai) | Artifact trên claude.ai |
| Việc nặng (mở link, gửi tin) | Không có — chỉ hiển thị | **Apps Script** trong Google Sheet (miễn phí, chạy cả khi tắt máy) |
| Dữ liệu | Trình duyệt từng người | Google Sheet (dùng chung, không mất) |
| Báo tin | Thông báo góc màn hình | Lark |
| Bàn giao | Trang HTML + nút copy | `NHAT-KY-CONG-VIEC.md`, `CACH-LAM-MOI.md` (chưa có trang bàn giao gom một chỗ) |

## 5. Khi Trang muốn "đóng gói thành app" một việc mới — làm theo thứ tự

1. Hỏi Trang 2–4 câu trắc nghiệm: dùng cho ai, dữ liệu để đâu (trình duyệt / Google Sheet), cần tự chạy khi tắt máy không, báo tin về đâu (chỉ máy Trang / vuthithuytrang@seongon.com / nhóm Lark riêng — xem CLAUDE.md).
2. Phần hiển thị: **1 file HTML tự viết**, màu + logo theo cẩm nang SEONGON.
3. Phần tự chạy / gửi tin: **Apps Script trong Google Sheet** (miễn phí, không tốn token Claude).
4. Đưa lên: Artifact claude.ai (nhanh, riêng tư) — hoặc Netlify nếu cần link mở không cần đăng nhập Claude
   (kho phải **private** hoặc file không chứa dữ liệu khách).
5. Tự kiểm thử + chụp màn hình; kiểm tra rò rỉ dữ liệu trước khi lưu kho.
6. Viết **trang bàn giao 10 mục** (khung ở mục 2) có nút "Copy cho AI khác"; ghi 1 dòng vào `NHAT-KY-CONG-VIEC.md`.
