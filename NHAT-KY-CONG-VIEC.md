# Nhật ký công việc — mở file này TRƯỚC khi làm việc mới

> Trang chốt 28/10/2026: mọi việc làm xong đều ghi lại đây, để lần sau **không phải chạy lại từ đầu**.
> Mỗi dòng: làm gì · kết quả nằm ở đâu · lần sau muốn chạy lại thì làm thế nào.
> Repo đang **public** → chỉ ghi tóm tắt + nơi để kết quả, **không** chép chìa khóa, link webhook, số liệu nội bộ nhạy cảm.

## Việc đang chạy định kỳ

| Việc | Chạy ở đâu | Lần sau làm gì |
|---|---|---|
| Check publish 54 URL Techcombank | Apps Script trong sheet "Theo dõi publish TCB" (`cong-cu/app-check-publish/apps-script.gs`) — tự kiểm ~19:00, báo Lark nhóm "Check publish TCB" | Trang gõ UD/UP trong Lark (khi app Lark được duyệt), bấm "Kiểm tra ngay" trên app, hoặc nhắn Claude "check publish" |
| App xem kết quả | https://claude.ai/artifact/MR7LzabxHN8S1gfQ6PeKGq | Sửa `cong-cu/app-check-publish/index.html` rồi đăng lại cùng file |

## Nhật ký

| Ngày | Việc | Kết quả / nơi lưu | Còn dở |
|---|---|---|---|
| 05–27/10/2026 | Theo dõi ngày publish URL TCB bằng Claude (lịch 08:00/13:00/19:00 → còn 19:00) | Sheet "Theo dõi publish TCB", ghi chú `cong-cu/theo-doi-publish-techcombank/CACH-LAM-MOI.md` | Đã thay bằng Apps Script 28/10 |
| 21/10/2026 | Hướng dẫn check ngày publish bằng Screaming Frog (Custom Extraction) | `cong-cu/theo-doi-publish-techcombank/SCREAMING-FROG.md` | — |
| 23/10/2026 | Skill "theo-doi-publish" cho team khác tự cài | `.claude/skills/theo-doi-publish/`, zip + hướng dẫn: `cong-cu/skill-theo-doi-publish/` | — |
| 28/10/2026 | App Check Publish + chuyển việc kiểm sang Apps Script (không tốn token) + báo Lark ("Done" / tin nhờ chị Tú Anh kèm list URL) | `cong-cu/app-check-publish/` | Chờ admin Lark duyệt app "Check publish TCB" → thêm bot vào nhóm → menu Bước 3 (App ID/Secret) để lệnh UD/UP chạy — XONG 29/10, nhận mọi tin có chữ up/ud/update/publish/check/kiểm tra |
| 28/10/2026 | Quy tắc: sau 13:00 bài phải sang ngày mai mới tính Done (đổi ở `Điều khiển!B6`); trong ngày đã Done thì bỏ lần 19:00 | Apps Script + `cap_nhat_sheet.py` | — |
| 28/10/2026 | Quy tắc: kết quả chỉ gửi về máy Trang + vuthithuytrang@seongon.com | CLAUDE.md | Trang tự xem: chế độ chia sẻ app, repo public, tài khoản Claude dùng chung |
| 29/10/2026 | Đóng gói Check Publish thành trang web công khai (Apps Script → Triển khai → Ứng dụng web): ai có link cũng xem được, nút Kiểm tra ngay giới hạn 5 phút/lần; chặn trang web gọi lén các hàm menu/lịch | `apps-script.gs` (doGet, layDuLieuWeb, kiemTuWeb, laTrigger_) | Trang dán mã mới + Triển khai → gửi link |
| 29/10/2026 | Học cách đóng gói app từ tài liệu bàn giao của đồng nghiệp (chỉ lấy cách làm, không lưu file gốc vì có tên khách) | `cong-cu/cach-dong-goi-app/CACH-DONG-GOI-APP.md` | Chưa áp dụng: trang bàn giao cho app Check Publish |
| trước 15/10/2026 | baotinmanhhai.vn: gợi ý 301 cho 17 URL 404 | — | Trang dừng giữa chừng, chưa làm |
| 15/10/2026 | Sheet "Update": tạo bản 15/10 cho 9 bài | `update1510/` (nháp, không lưu kho) | Trang dừng giữa chừng, đã lỗi thời |
