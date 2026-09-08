# Khóa Agent Boss — tiến độ của Trang

Cập nhật tới thời điểm tài khoản cũ bị vô hiệu hóa (08/09/2026).

## Lộ trình 3 chặng (lấy từ hệ thống khóa học, không bịa)

| Chặng | Bài | Nội dung |
|---|---|---|
| **Chặng 1** | 1–5 | *Bạn đang ở đây* — tự tay làm cùng Agent: dựng web, làm việc thật của nghề |
| **Chặng 2** | 6–10 | **Trao quyền cho Agent** — biến "task pop-up" thành việc Agent tự lo |
| **Chặng 3** | 11–15 | **AI Coding Agent** — Agent tự dựng công cụ (landing page, báo cáo, chăm lead…) |
| **Vị thế mới** | — | Trang thành người điều phối dây chuyền, không còn bị việc vặt cuốn đi |

## Mã nộp bài đã lấy được

| Bài | Sản phẩm | Mã nộp | Trạng thái |
|---|---|---|---|
| Bài 1 | Trang HTML "Cố Vấn hay Trợ Lý Kỹ Sư?" — 6 khối, thẻ lật bấm được | `ABS-4GRUY8` | ✅ Đã ưng |
| Bài 2 | Báo cáo "AI Agent và nghề Marketing" — 5 trang, HTML + PDF | `ABS-MYXFG4` | ✅ Đã nộp |
| Bài 3 | Tấm bản đồ cơ hội + ghi chú Bret Taylor | `ABS-JNBM9Z` | ✅ Đã nộp |
| Bài 4 | Truyện tranh "Hai người Marketing — 12 tháng sau" — 8 khung | `ABS-73BFC8` | ✅ Đã nộp |
| Bài 5 | Bot Telegram + bản tin sáng tự động 7h | `ABS-FZBGUY` | ✅ Đã nộp |
| Bài 6 | Bài học bảo mật chìa khóa + cập nhật hồ sơ | *(chưa có)* | ⏸️ **Đang dở** |

> **Lưu ý đã được Agent cũ giải thích rõ**: mỗi bài học chỉ có **ĐÚNG 1 mã nộp**, do hệ thống khóa
> học cấp sẵn, cố định. Agent không tự ghép hay đổi mã được. Bài 3 tuy làm 2 việc (xem video Bret
> Taylor + dựng bản đồ) nhưng vẫn chỉ 1 mã duy nhất — phần xem video là bước chuẩn bị.

## Bài 1 — Cố Vấn hay Trợ Lý Kỹ Sư?

- Gọi `POST /api/agent/connect` lấy hồ sơ → `GET /api/agent/noi-dung-bai-1/marketing-nv` lấy nội dung
- Agent tự viết trang HTML 6 khối, có thẻ lật bấm được
- File: `bai-1-agent-boss.html` (13.9 KB)

## Bài 2 — AI Agent và nghề Marketing

Báo cáo 5 trang dạng tạp chí. Cấu trúc: Bìa → Thế giới đang đổi → Agent làm được gì →
Người cùng nghề đã làm thật → 3 việc bắt đầu tuần này.

- **Phần 1** — 5 phát hiện về nghề Marketing đang đổi (mỗi cái 1 con số + nguồn thật):
  34% đội marketing lớn đã chạy Agent · quảng cáo AI viết tăng nhập +450% ·
  93% doanh nghiệp Việt đã dùng AI · thị trường Agent tăng ×9,3 lần
- **Phần 2** — 6 việc Agent thật sự làm được cho marketing
- **Phần 3** — 5 câu chuyện thật của người cùng nghề (anh Đông, anh Phú, chị Diệu Linh,
  anh Duy Dương, chị Vân Thanh) — lấy trực tiếp từ hệ thống Agent Boss, người thật việc thật
- **Phần 4** — 3 việc bắt đầu ngay tuần này

Nguồn: Deloitte APAC 5/2025, Demand Gen Report, Salesforce, Master of Code, Coupler.io/JPMorgan,
MISA AMIS, Cục Thông tin–Thống kê.

- File: `AI-Agent-va-nghe-Marketing.html` + `.pdf` (~690 KB)

## Bài 3 — Bret Taylor & Tấm bản đồ cơ hội

**Phần A — video Bret Taylor** (CEO Sierra, Chủ tịch HĐQT OpenAI, phỏng vấn CNBC tại Davos,
"Sierra CEO Bret Taylor on the future of AI: We're at the beginning of the curve", 8 phút 12 giây).

Agent **không tải được video** — YouTube chặn IP máy chủ. Đã thử 7 cách: cài `yt-dlp` → đổi 5 kiểu
trình phát (tv/android/ios/safari/mobile) → thử lại kiên nhẫn 5 lần → lắp Node.js → dùng
`youtube-transcript-api` → nhờ 2 trang bên thứ ba → đọc thẳng trang YouTube. **Tất cả đều bị chặn.**

Agent **không bịa bản dịch**. Thay vào đó tìm bài báo/nguồn công khai ghi lại quan điểm của chính
Bret Taylor (CNBC, Stratechery, TechCrunch, Forbes) và soạn file tiếng Việt **có ghi rõ chỗ nào lấy từ đâu**.

- File: `Bret-Taylor-AI-Agent-tieng-Viet.html` (7.8 KB)

**5 lý do dùng Agent SỚM có lợi thế lớn** (đúc kết cho nghề Marketing):

1. Nhân bản cả quy trình, không chỉ từng việc — ai đóng gói sớm chuỗi *lên lịch → viết → đăng →
   báo cáo* cho Agent chạy thì nhân đôi năng suất trước cả team
2. Kỹ năng giao việc cho Agent cần thời gian tích lũy — "mới ở đầu đường cong", bắt đầu giờ = có
   1–2 năm kinh nghiệm thực chiến khi số đông mới chập chững
3. Phủ đa kênh, đa ngôn ngữ mà không tăng người — chi phí gần như không đổi
4. Giá trị dời sang KẾT QUẢ — Agent lo phần cơ học, người dồn sức cho traffic/lead/doanh số
5. Agent càng hiểu nghề bạn càng mạnh, thành tài sản riêng — brand guide, quy tắc SEO thành
   kho "skill" riêng đối thủ khó copy

**Phần B — Tấm bản đồ cơ hội**: lộ trình 3 chặng từ "đang ở đây" tới vị thế mới, viết riêng theo
mục tiêu tối ưu hiệu suất & dẹp task pop-up.

- File: `Ban-do-co-hoi-Thuy-Trang.html` (10.6 KB)

## Bài 4 — Truyện tranh "Hai người Marketing — 12 tháng sau"

8 khung tranh vẽ tay nét đen. Hai nhân vật phân biệt rõ (Hương tóc rẽ ngôi, Thùy Trang tóc buộc đuôi).

- **Hương** — cùng nghề, cùng núi việc, nhưng gạt AI đi ("chắc chưa cần"), cứ làm tay
- **Thùy Trang** (là Trang) — quyết học dùng Agent, giao dần việc vặt cho máy

4 mốc, khoảng cách doãng dần:

| Mốc | Cảnh |
|---|---|
| Tháng 1 | Chỉ khác một lựa chọn |
| Tháng 3 | Một người 8 giờ tối mới về, một người về lúc 6 giờ |
| Tháng 6 | Sếp hỏi "ai rành AI?", một người im lặng, một người được giao dẫn dắt |
| Tháng 12 | Tin tuyển ghi "ưu tiên biết dùng AI Agent"; Trang thành nòng cốt, Hương mới bắt đầu học |

Giọng viết nhẹ nhàng, **không dìm Hương** — chị ấy không kém, chỉ chọn muộn thôi.

- File: `Hai-nguoi-Marketing-12-thang-sau.html` (15.5 KB)
- **Việc còn dang dở**: Agent cũ đã hứa làm truyện "sống dậy" bằng hoạt hình sau khi Trang gật đầu.
  Trang đã ưng nhưng chưa kịp làm.

## Bài 5 — Bản tin Marketing sáng tự động

Xem chi tiết ở `cong-cu/ban-tin-marketing-sang.md`.

## Bài 6 — Bảo mật chìa khóa (ĐANG DỞ)

Bài học cố tình dạy: dán chìa vào khung chat = chìa lộ. Hệ thống Agent Boss chủ động khóa chìa cũ.

Trạng thái khi dừng:
- ❌ Trang **chưa tạo chìa mới** — mới gửi lại chìa cũ
- ⏸️ 3 trường hồ sơ (chức danh / giới thiệu / việc đã làm) vẫn trống, Agent đang chờ Trang đọc nội dung
- ✅ Trắc nghiệm ôn tập đã trả lời: **1 = C · 2 = B · 3 = A**

## Nộp bài thực tế (ngoài bài tập chương trình)

Việc thật Trang chọn để nộp: **tự tạo một công cụ AI tối ưu Tiêu đề & Meta SEO**, đã test thành
công trên bài thật. Nội dung 2 ô nộp bài đã soạn xong — xem `cong-cu/cong-cu-toi-uu-title-meta-seo.md`.

## Sao lưu Google Drive (ĐANG DỞ)

Trang đã chốt: **(1) sao lưu tất cả file · (2) tần suất "cách khác tùy bạn" · (3) thư mục
"Sao luu Agent Boss"**. Agent chưa kịp dựng lịch tự động thì tài khoản bị tắt.

> ⚠️ Câu 2 Trang chọn "cách khác tùy bạn" — **cần hỏi lại Trang chốt tần suất cụ thể**
> (hằng tuần là khuyến nghị của Agent cũ) trước khi dựng lịch.

## Sản phẩm đã tạo — tình trạng file

Toàn bộ nằm ở nhánh `claude/agent-boss-lesson-1-xdzb5x` thuộc repo của **tài khoản cũ** — không truy
cập được nữa. Tổng ~760 KB.

| Nhóm | File | Dung lượng |
|---|---|---|
| Báo cáo AI Agent & Marketing (Bài 2) | `AI-Agent-va-nghe-Marketing.html` + `.pdf` | ~690 KB |
| Truyện tranh 2 người Marketing (Bài 4) | `Hai-nguoi-Marketing-12-thang-sau.html` | 16 KB |
| Trang bài học 1 | `bai-1-agent-boss.html` | 14 KB |
| Bản đồ cơ hội (Bài 3) | `Ban-do-co-hoi-Thuy-Trang.html` | 11 KB |
| Ghi chú Bret Taylor (Bài 3) | `Bret-Taylor-AI-Agent-tieng-Viet.html` | 8 KB |
| Công cụ tối ưu Title/Meta SEO | `Cong-cu-AI-toi-uu-Title-Meta-SEO.md` | 4 KB |

**Đã khôi phục nguyên vẹn**: công cụ Title/Meta SEO (`cong-cu/`) — vì toàn văn prompt hiện rõ trong
bản chụp. **Chưa khôi phục**: 5 file HTML/PDF — chỉ còn mô tả cấu trúc và nội dung ở trên, đủ để
dựng lại nếu Trang cần.
