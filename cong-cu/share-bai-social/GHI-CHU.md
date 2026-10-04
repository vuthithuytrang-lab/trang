# Agent share-bai-social — đã cài vào repo

Nguồn: https://github.com/nguyenminhnguyet-ops/share-bai-social-agent (tải về ngày 04/10/2026)

## Đã cài ở đâu
- Agent điều phối: `.claude/agents/share-bai-social.md`
- 8 skill: `.claude/skills/` → `google-sheets-social`, `share-bai-wp`, `share-bai-blogger`, `share-bai-ggr`,
  `share-bai-tumblr`, `share-bai-wix`, `share-bai-webflow`, `share-bai-mastodon`
- Danh sách lệnh được phép chạy nền: `.claude/settings.json`
- Hướng dẫn gốc: `README-goc.md` · File mẫu cấu hình dự án: `CLAUDE.md.example`

## Còn thiếu (chưa dùng được ngay)
- [ ] Cấu hình dự án: copy `CLAUDE.md.example` thành `.claude/CLAUDE.md`, điền sheet + cột — **cần Trang cung cấp link Sheet**
- [ ] Kết nối từng nền tảng (tạo file `*-accounts.local.json` chứa token) — chỉ nền tảng nào cần dùng
- [ ] Kết nối Google Sheet (skill `google-sheets-social`)

⚠️ Repo này public: file `*.local.json` đã được chặn trong `.gitignore`, tuyệt đối không commit token.
