# Agent share-bai-social — đã cài vào repo

Nguồn: https://github.com/nguyenminhnguyet-ops/share-bai-social-agent (tải về ngày 04/10/2026)

## Đã cài ở đâu
- Agent điều phối: `.claude/agents/share-bai-social.md`
- 8 skill: `.claude/skills/` → `google-sheets-social`, `share-bai-wp`, `share-bai-blogger`, `share-bai-ggr`,
  `share-bai-tumblr`, `share-bai-wix`, `share-bai-webflow`, `share-bai-mastodon`
- Danh sách lệnh được phép chạy nền: `.claude/settings.json`
- Hướng dẫn gốc: `README-goc.md` · File mẫu cấu hình dự án: `CLAUDE.md.example`

## Dự án đang chạy
| Dự án | Hồ sơ (sheet, cột, nền tảng, cấu trúc bài) |
|---|---|
| AIG — Asia Ingredients Group | `du-an/AIG.md` |

Thêm dự án mới → tạo file `du-an/<TEN>.md` theo mẫu AIG. **Mỗi dự án tạo chìa API riêng**
(Google Cloud project riêng, OAuth client riêng cho Blogger và cho Sheet, app WordPress riêng, chìa Wix/Webflow riêng) —
không bao giờ dùng chung chìa giữa các dự án.

## Lịch tự chạy
- Routine **"AIG – đăng bài social theo lịch"** (`trig_01XTBV46CbbCK7xXmG1KTwb8`): chạy :05 mỗi giờ, 8:05–20:05 giờ VN,
  mỗi lần đăng đúng 1 mục đến hạn trong `du-an/AIG-lich-dang.json`, theo `HUONG-DAN-LUOT-DANG.md`.
- Lịch đợt 1: 11 bài × 4 nền tảng = 44 lượt, 05/10 14:05 → 09/10 08:05. **✅ XONG 44/44 lúc 09/10/2026 08:10, 0 lỗi.**
  Routine đã **TẮT** (enabled=false) — đợt mới: tạo lịch mới rồi bật lại routine.
- 08/10: lượt 12:05 bị trễ (mất kết nối) → lùi các lượt còn lại 1 giờ, vẫn đúng giãn cách.
- Việc còn hỏi Trang: WordPress có hiện nội dung 2 lần không (giao diện); ảnh trong thân bài Wix có hiện không; Blogger không có ảnh xem trước khi share (giao diện).
- Thêm bài mới → tạo lại lịch (nối tiếp sau lượt cuối), ghi cột F, cập nhật file JSON.

## Còn mở
- [~] **Giữ chìa qua các phiên** — 05/10/2026: thử cất lên Drive bị hệ thống an toàn chặn; Trang chọn để nguyên. Nếu lượt đăng báo thiếu chìa → hướng dẫn Trang kết nối lại (app/client đã có sẵn).: chìa đang nằm trong `*-accounts.local.json` trên máy tạm của phiên làm việc
      → phiên đóng là mất. Cần cất vào cài đặt kín của môi trường (biến môi trường) — chưa làm.
- [x] Thay chìa Wix (xong 04/10/2026). - [ ] Thay chìa Webflow (đã bị dán vào chat) — `BAO-MAT.md` mục 5.
- [ ] X (Twitter): chưa có skill. Chờ Trang quyết làm hay bỏ.
- [x] Bài đầu tiên "trái cây iqf" (dòng 64–67) đã đăng đủ 4 nền tảng 04/10/2026.

⚠️ Repo này public: file `*.local.json` đã được chặn trong `.gitignore`, tuyệt đối không commit token.
