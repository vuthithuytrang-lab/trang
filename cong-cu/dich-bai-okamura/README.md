# Dịch bài Okamura Việt → Anh (luồng tự động)

**Cách dùng cho Trang:** mở một phiên Claude Code trong repo này, dán link Google Doc bài cần dịch
(hoặc gõ "dịch BV 40"). Claude tự làm hết và gửi lại link.

Kết quả: trong chính file Google Doc đó có thêm tab **"Bản dịch EN"** — trang ngang, bảng 2 cột:
trái là bản Việt (giữ nguyên), phải là bản Anh đã trình bày theo checklist. Tab gốc tiếng Việt không bị đụng tới.

| File | Việc |
|---|---|
| `dump_doc.py` | Đọc bài Việt ra dạng chữ có đánh số từng đoạn |
| `build_requests.py` | Biến bản dịch thành lệnh dựng tab bản dịch trên Google Doc |
| `verify.py` | Soát lại sau khi ghi: chữ, ảnh, link, heading |
| `ban-dich/` | Bản dịch đã làm (mỗi bài 1 file) |

Quy trình chi tiết cho Claude: `.claude/skills/dich-bai-okamura/SKILL.md`.
