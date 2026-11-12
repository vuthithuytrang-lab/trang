# Bàn giao agent share-bai-social — dự án NIPPON PAINT

> Viết ngày 12/11/2026 để Trang **chuyển sang tài khoản Claude khác (hoặc phiên mới) mà không phải dựng lại từ đầu**.
> Phiên Claude mới mở repo này: đọc file này, rồi `du-an/nippon-paint.md`, rồi mới làm.
> Bản dễ đọc cho Trang: `ban-giao-nippon.html` (cùng thư mục).

## 1. Cái gì đã nằm sẵn trong repo (tài khoản mới tự có, không phải làm gì)

| Thứ | Ở đâu |
|---|---|
| Agent điều phối | `.claude/agents/share-bai-social.md` (có quy tắc giãn cách 2 bài/ngày/nền tảng) |
| Skill từng nền tảng + Google Sheet | `.claude/skills/share-bai-*`, `.claude/skills/google-sheets-social` (đã vá: dòng tiêu đề = 2, nhiều ảnh Blogger, OAUTH_STATE Tumblr) |
| Skill Pinterest tự viết | `.claude/skills/share-bai-pinterest/` |
| Danh sách lệnh được phép chạy không hỏi | `.claude/settings.json` |
| Checklist nội dung bắt buộc (bỏ "Kết luận", ≥3 ảnh, cấu trúc bài, hashtag, khối liên hệ) | `cong-cu/share-bai-social/CHECKLIST-NOI-DUNG-SHARE.md` |
| Hồ sơ dự án: sheet, cột, tài khoản, khối liên hệ Nippon, trạng thái, bài học | `cong-cu/share-bai-social/du-an/nippon-paint.md` |
| Gói bài Google Site dòng 5 | `cong-cu/share-bai-social/du-an/nippon-google-site/` |
| Công cụ gói / mở gói chìa | `cong-cu/share-bai-social/goi-chia/goi-chia.js` |

⚠️ **Nhánh git:** toàn bộ phần trên đang nằm ở nhánh `claude/admiring-gauss-4p97bj`. Nhánh mặc định của repo
là `claude/ai-boss-data-replace-hn412r` — phiên mới mở nhánh mặc định sẽ **không thấy** agent/skill.
Phiên mới: `git fetch origin claude/admiring-gauss-4p97bj && git checkout claude/admiring-gauss-4p97bj`
(hoặc gộp nhánh này vào nhánh mặc định nếu Trang đã đồng ý).

## 2. Cái KHÔNG nằm trong repo — chìa kết nối

Chìa (client secret, refresh token, access token) nằm trong các file `.claude/skills/*/*-accounts.local.json`.
Repo public nên các file này **bị chặn commit** (`.gitignore`: `*.local.json`). Chúng chỉ sống trong máy ảo của phiên.

**Sự cố đã gặp:** máy ảo phiên 29/09–02/10 đã bị thu hồi → toàn bộ chìa mất. Ngày 12/11/2026 kiểm tra: không còn file
`*-accounts.local.json` nào. Nhưng **phía nền tảng vẫn còn nguyên** (dự án Google Cloud, Client ID, màn hình đồng ý
đã "In production", ứng dụng WordPress, ứng dụng Pinterest) → kết nối lại chỉ là bước "bấm cho phép", không phải tạo lại.

### Cách giữ chìa từ nay — "gói chìa"

1. Kết nối xong nền tảng nào → chạy
   `node cong-cu/share-bai-social/goi-chia/goi-chia.js dong-goi <scratchpad>/goi-chia-nippon.local.json`
   rồi **gửi file đó cho Trang** (SendUserFile, display `attach`). Trang lưu trên máy cá nhân, **không** gửi ai, **không** đưa lên Drive chia sẻ.
2. Phiên/tài khoản mới: Trang **đính kèm** file gói vào chat → agent chép file vào scratchpad rồi chạy
   `node cong-cu/share-bai-social/goi-chia/goi-chia.js mo-goi <file>` → kiểm tra bằng `kiem-tra` → thử đọc sheet + tra blog.
3. Không bao giờ in nội dung gói ra màn hình, không commit, không dán vào chat. Lệnh `kiem-tra` chỉ in tên tài khoản + loại chìa có mặt.
4. Mỗi lần làm mới chìa (kết nối lại, đổi secret) → đóng gói lại và gửi Trang bản mới, dặn xóa bản cũ.

Refresh token Google sống lâu (app đã In production) nhưng sẽ chết nếu: đổi mật khẩu Google, gỡ quyền ứng dụng,
6 tháng không dùng, hoặc xóa/đổi client secret. Khi đó gói cũ vô dụng → kết nối lại theo mục 4.

## 3. Bảng tài khoản & tài nguyên (không có chìa)

Tài khoản Google dùng cho mọi thứ: `nipponpaint.seo2026@gmail.com`.

| Nền tảng | Tài nguyên cố định | File chìa | Trạng thái 12/11/2026 |
|---|---|---|---|
| Google Sheet | Dự án GCP `nippon-paint-share-social` (ID `nodal-rex-510103-e6`), OAuth Desktop client **"Sheet - Nippon Paint"** `462260259198-dq51hs2gmn1rkrdrs276v7q04lbavqnd.apps.googleusercontent.com`, Sheets API bật. Sheet `1_82x2XUK7KH7ajlPFGZ7d2Llbb70HClY_0xWNzaFDRI`, tab `Share social`, sheet-key `nippon-paint-share-social` | `google-sheets-social/sheets-accounts.local.json` | 🔑 Mất chìa — cần kết nối lại |
| Blogger | Cùng dự án GCP, client **"Blogger - Nippon Paint"** `462260259198-8qvobsflaa3mt9snd6pm9bvtafsc6tgt.apps.googleusercontent.com`, Blogger API v3 bật. Blog `https://nipponpaint-vietnam.blogspot.com`, blog_id `6614444719230130830`, account key `nipponpaint-vietnam.blogspot.com` | `share-bai-blogger/blogger-accounts.local.json` | 🔑 Mất chìa — cần kết nối lại. Đã đăng 21 bài (dòng 5–25) |
| WordPress.com | App "Nippon Paint Share Social", Client ID `149315`, redirect `https://localhost/`. Site `nipponpaintvietnam0.wordpress.com` | `share-bai-wp/wp-accounts.local.json` | ⛔ Site bị tạm ngưng 30/09, đã khiếu nại — chờ mail. Mở lại rồi mới kết nối |
| Tumblr | App "Nippon Paint Share Social". Blog `nipponpaint-vn.tumblr.com` | `share-bai-tumblr/tumblr-accounts.local.json` | ⛔ Tài khoản bị hủy 30/09 — bỏ |
| Pinterest | App "Nippon Paint Share Social", App ID `1617333`, tài khoản `pinterest.com/nipponpaintvn` (Business) | `share-bai-pinterest/pinterest-accounts.local.json` | ⏳ Chờ duyệt Trial — các bước tiếp ở `du-an/nippon-paint.md` |
| Google Site | `sites.google.com/view/nipponpaintvn/homepage-sites` | — (không có API) | ⏸ Tạm dừng |
| X | `x.com/nipponpaint_vn` | — | ⏸ Tạm dừng (trả phí) |
| Threads | `threads.com/@nipponpaintvn` | — | ⏳ Chờ Trang mượn tài khoản Facebook |

Client ID không phải chìa bí mật (nó hiện công khai trong mọi đường link cho phép) nên được ghi ở đây.
**Client secret thì không** — xem mục 4.

## 4. Kết nối lại khi không có gói chìa (~10 phút cho Sheet + Blogger)

Làm theo SKILL.md của từng skill (`set-client` → mở link cho phép → đổi code → `save-tokens`). Những điểm đã học:

1. **Client secret:** Google Cloud không cho xem lại secret cũ. Trang vào
   console.cloud.google.com → chọn dự án `nippon-paint-share-social` → APIs & Services → Credentials → bấm tên client
   → **Add secret** → tải file JSON → **đính kèm vào chat** (không chụp màn hình, không dán chữ). Sau khi lưu xong, xóa secret cũ trên trang đó.
2. **Đổi code trong máy ảo:** máy ảo không mở được trình duyệt của Trang. Cách đã chạy được: dựng link cho phép
   (redirect `http://127.0.0.1:<port>`) → Trang mở link, bấm Cho phép → trình duyệt báo "không truy cập được" → Trang
   **copy cả địa chỉ trên thanh trình duyệt** gửi lại → agent chạy oauth-server của skill rồi `curl` lại đúng địa chỉ đó vào 127.0.0.1.
3. Dặn Trang chọn đúng tài khoản `nipponpaint.seo2026@gmail.com` trên màn hình chọn tài khoản; gặp "Google chưa xác minh ứng dụng" → Nâng cao → Tiếp tục.
4. Màn hình đồng ý **đã In production — không bấm "Back to testing"** (Testing làm token chết sau 7 ngày).
5. Kiểm tra: đọc sheet (`parse-sheet-data ... 2`), tra blog theo URL → so blog_id với bảng trên.
6. Xong → **đóng gói chìa và gửi Trang ngay** (mục 2).

WordPress (khi site mở lại): Client secret xem được tại developer.wordpress.com/apps → app 149315 (BAO-MAT.md khuyên Reset Key trước).
Kiểu cho phép "code" với redirect `https://localhost/` — Trang copy địa chỉ lỗi gửi lại, agent đổi code.

## 5. Quy tắc vận hành không được quên

- **Tối đa 2 bài/ngày/nền tảng, cách nhau ≥2 tiếng.** Đăng dồn 30/09 đã làm chết WordPress + Tumblr. Ngoại lệ chỉ khi Trang duyệt rõ ràng, ghi vào hồ sơ dự án, và ghi luôn vào brief gửi agent con.
- Chỉ đăng dòng có ô E (Duyệt share) = TRUE, ghi link vào đúng cột của nền tảng, không đụng cột D/F/dòng 1–4.
- Nội dung: theo checklist; không bịa thông tin; ≥3 ảnh thật; không "Kết luận"; không "nhất/số 1/hàng đầu"; ghi đúng "Nippon Paint".
- Chìa: không in, không gắn URL, không commit, chỉ nhận qua file đính kèm.

## 6. Việc đang treo

1. WordPress: chờ mail trả lời khiếu nại (về `nipponpaint.seo2026@gmail.com`).
2. Pinterest: chờ duyệt Trial (App 1617333).
3. Threads: chờ Trang mượn tài khoản Facebook đồng nghiệp.
4. Google Site: Trang chưa chọn 1 trong 3 hướng (khuyên Google Groups).
5. Hỏi Trang: dọn link chết O6–O8 (Tumblr) và H6–H12 (nếu WordPress không mở lại)?
6. Báo bên Nippon: nút "THAM KHẢO SẢN PHẨM" trên vài bài web gốc trỏ sang `stg-web.npp.kyanon.dev` (địa chỉ thử nghiệm).
