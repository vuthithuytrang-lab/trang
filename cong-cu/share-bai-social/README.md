# share-bai-social — Agent đăng bài tự động lên nhiều nền tảng (Claude Code)

Bạn điền **từ khóa + link bài gốc** vào 1 Google Sheet, tích ô "Duyệt share" — agent sẽ tự đọc bài gốc,
**viết lại** (không đạo văn, giữ nguyên ý), **đăng** lên các nền tảng bạn đã kết nối, rồi **ghi link bài đã đăng** ngược lại vào sheet.

## Trong repo này có gì

| Thành phần | Vai trò | Ví von |
|---|---|---|
| `agent: share-bai-social` | Đọc sheet, quyết định dòng nào cần đăng, gọi đúng skill cho từng nền tảng, ghi link về sheet | Người điều phối |
| `skill: google-sheets-social` | Đọc/ghi Google Sheet | Tay đọc/ghi sổ |
| `skill: share-bai-wp` | Đăng lên WordPress.com | Tay đăng #1 |
| `skill: share-bai-blogger` | Đăng lên Blogger | Tay đăng #2 |
| `skill: share-bai-ggr` | Đăng lên Google Groups | Tay đăng #3 |
| `skill: share-bai-tumblr` | Đăng lên Tumblr | Tay đăng #4 |
| `skill: share-bai-wix` | Đăng lên Wix Blog | Tay đăng #5 |
| `skill: share-bai-webflow` | Đăng lên Webflow CMS | Tay đăng #6 |
| `skill: share-bai-mastodon` | Đăng lên Mastodon | Tay đăng #7 |

> **Agent KHÔNG chạy 1 mình được.** Agent chỉ điều phối, việc đăng bài thật nằm ở các skill —
> nên phải cài **cả agent lẫn skill** (repo này đã gói sẵn tất cả).
> Bạn không cần dùng đủ 7 nền tảng: chỉ kết nối nền tảng nào bạn cần, nền tảng chưa kết nối sẽ được báo "Cần setup" và bỏ qua.

## Cài đặt (làm 1 lần)

**Yêu cầu:** đã cài [Claude Code](https://claude.com/claude-code), Node.js, Git (Windows dùng Git Bash).

1. Tải repo về, copy thư mục `.claude` vào **thư mục dự án** bạn dùng với Claude Code
   (nếu dự án đã có `.claude` rồi thì gộp vào, riêng `settings.json` thì chép các dòng `permissions.allow` sang).
   ```
   .claude/agents/share-bai-social.md
   .claude/skills/<8 thư mục skill>/
   .claude/settings.json      ← danh sách lệnh được phép chạy nền, BẮT BUỘC có
   ```
   > Vì sao bắt buộc? Agent chạy ngầm nên không thể hỏi bạn "cho phép chạy lệnh này không?".
   > Lệnh nào chưa được cho phép sẵn trong `settings.json` sẽ bị chặn im lặng.
2. Copy `CLAUDE.md.example` thành `.claude/CLAUDE.md`, sửa theo dự án của bạn (sheet nào, cột nào, tài khoản nào).
3. Kết nối **từng nền tảng** bạn muốn dùng. Mở Claude Code trong dự án, gõ ví dụ:
   `/share-bai-wp` hoặc nói "kết nối WordPress cho tôi" — Claude sẽ dẫn bạn từng bước và tự tạo file
   `<nền tảng>-accounts.local.json` chứa token. Mỗi skill có file mẫu `*.local.example.json` để bạn xem cấu trúc.
4. Kết nối Google Sheet qua skill `google-sheets-social` (đọc `SKILL.md` của nó).

## Cách dùng hằng ngày

Trong Claude Code, nói: **"chạy agent share-bai-social"** (hoặc "đăng các dòng đã tích trên sheet").
Agent sẽ: đọc sheet → tìm dòng đã tích "Duyệt share" mà ô nền tảng còn trống → đăng → ghi link vào sheet → báo cáo
(thành công / cần setup / lỗi).

Có thể chạy thử 1 bài lẻ không qua sheet: `/share-bai-wp [từ khóa], [URL bài gốc]`.

## Sheet cần có dạng nào

Xem `CLAUDE.md.example` — hỗ trợ 2 kiểu: **mỗi nền tảng 1 cột** hoặc **mỗi nền tảng 1 dòng**.

## ⚠ Những điều phải biết để khỏi mất công

- **Bảo mật:** các file `*.local.json` chứa mật khẩu/token thật. Repo này đã chặn sẵn trong `.gitignore` — đừng gỡ, đừng gửi cho người khác.
- **Google OAuth — mỗi skill 1 Client ID riêng.** Dùng chung 1 Client ID cho nhiều skill (Blogger, Groups, Sheets) sẽ làm token của skill cũ bị Google **vô hiệu hoá âm thầm** (giới hạn 50 token/Client ID/tài khoản). Có thể chung 1 Google Cloud project, chỉ cần Client ID khác nhau.
- **Google OAuth — phải bấm "Publish app" (In production)** ở OAuth consent screen. Để "Testing" thì token tự hết hạn sau 7 ngày. Nút Publish bị mờ → điền đủ trang Branding trước.
- **Tumblr:** khi đăng ký app, callback phải là `http://localhost:<cổng>/` (không dùng `127.0.0.1`); 2 ô App Store / Google Play để trống.
- **Wix:** site phải cài sẵn app **Blog** trong Wix Editor, nếu không API báo `Blog instance not found`.
- **Webflow:** gói miễn phí giới hạn số bài CMS; hết hạn mức thì API báo lỗi khi tạo bài mới.
- **Windows:** tiếng Việt có dấu truyền qua curl có thể bị lỗi — xem mục "Quy ước chung" trong `CLAUDE.md.example`.
- **Nội dung:** skill viết lại bài ~900-1100 từ, cấm từ xếp hạng tuyệt đối ("nhất", "số 1", "hàng đầu") khi không có chứng minh. Bạn chịu trách nhiệm về nội dung đăng và tuân thủ quy định của từng nền tảng.
