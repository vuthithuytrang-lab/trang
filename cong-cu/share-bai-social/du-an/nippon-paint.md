# Dự án NIPPON PAINT — đăng bài tự động (agent share-bai-social)

> Agent `share-bai-social` đọc file này để biết sheet nào, cột nào, tài khoản nào.
> Không ghi mật khẩu/token vào đây — chúng nằm trong các file `*-accounts.local.json` (đã chặn commit).

## Sheet của dự án

- File: **TTS - Nippon** — https://docs.google.com/spreadsheets/d/1_82x2XUK7KH7ajlPFGZ7d2Llbb70HClY_0xWNzaFDRI/edit?gid=1933816871
- Spreadsheet ID: `1_82x2XUK7KH7ajlPFGZ7d2Llbb70HClY_0xWNzaFDRI`
- Tab: `Share social`
- Sheet-key (tên khai trong `google-sheets-social/sheets-accounts.local.json`): `nippon-paint-share-social`

## Cấu trúc sheet — Layout A (mỗi nền tảng 1 cột)

Đã đọc thử sheet ngày 29/09/2026:

- Dòng 1 = nhãn nhóm gộp ô ("Hàm cố định", "Social doanh nghiệp") — bỏ qua.
- **Dòng 2 = tiêu đề thật** → gọi `parse-sheet-data ... 2`.
- Dòng 3 = link trang chủ từng tài khoản (chữ thường, không gắn hyperlink trên ô tiêu đề).
- Dòng 4 = công thức đếm số link — không phải dữ liệu, không bao giờ ghi vào.
- **Dữ liệu bắt đầu từ dòng 5.**

| Cột | Tiêu đề | Vai trò |
|---|---|---|
| B | Key chính | Từ khóa chính |
| C | Link đăng | URL bài viết gốc |
| D | Ngày thực hiện | Ngày thực hiện (người làm điền, agent không động vào) |
| E | Duyệt share | Ô tích — chỉ đăng dòng có E = TRUE |
| F | Tổng link share | Công thức — không động vào |

Cột nền tảng dự án này dùng: **G, H, I, L, O, U**. Các cột nền tảng khác **không đụng tới**.

## Account key (nền tảng → tài khoản)

Tiêu đề cột G, H, I không gắn hyperlink, nên agent dùng bảng này thay cho việc dò domain.

⚠️ Ô tiêu đề cột L ("X") đang gắn hyperlink **sai** tới `https://x.com/fpt_academy` (sót từ sheet mẫu) — tài khoản đúng là `x.com/nipponpaint_vn` ở dòng 3. Không tin hyperlink ô L; bảng dưới đây là chuẩn.

| Cột | Nền tảng | Skill | Account key | Trạng thái |
|---|---|---|---|---|
| G | Blogger Page | `share-bai-blogger` | `nipponpaint-vietnam.blogspot.com` | ✅ Đã kết nối |
| H | Wordpress | `share-bai-wp` | `nipponpaintvietnam0.wordpress.com` | ⛔ **Blog bị WordPress.com tạm ngưng 30/09/2026** (sau 7 bài trong ~35 phút) — H6–H12 là link chết (410). Chờ Trang kháng nghị |
| I | Google Site | — không có API cho Google Site mới | `sites.google.com/view/nipponpaintvn/homepage-sites` | ⏸ **TẠM DỪNG** (29/09/2026) — xem mục "Việc còn dở — Google Site" |
| L | X | — chưa có skill | `x.com/nipponpaint_vn` | ⏸ Tạm dừng — X bỏ gói miễn phí từ 02/2026 (~0,20 USD/bài có link); Trang chọn Tumblr thay thế (29/09/2026) |
| O | Tumblr | `share-bai-tumblr` | `nipponpaint-vn.tumblr.com` | ⚠️ Nghi bị hạn chế 30/09/2026 — sau 3 bài trong ~10 phút, API báo 401 (code 1017), trang blog báo 429. O6–O8 đã đăng |
| (cột mới) | Threads | `share-bai-threads` (sẽ tự viết) | `threads.com/@nipponpaintvn` | ⏳ Đang kết nối (29/09/2026) — sheet cần thêm cột "Threads" |
| — | Twitch, GETTR | — | `twitch.tv/nipponpaintvn`, `gettr.com/user/e12216658745704448` | ❌ Không tự động được: Twitch không có chức năng đăng bài (Channel Feed bị xóa 2018); GETTR không có API chính thức |
| U | Pinterest | `share-bai-pinterest` (skill tự viết 29/09/2026) | `pinterest.com/nipponpaintvn` | ⏳ App "Nippon Paint Share Social" (App ID 1617333) đang chờ Pinterest duyệt Trial access. Trial = Pin chỉ chủ tài khoản thấy; cần xin Standard access (nộp video) để Pin công khai |

## Quy tắc viết bài riêng cho dự án

- Ghi đúng tên doanh nghiệp: **Nippon Paint** (không viết "Nippon", "Nipon Paint", "NipponPaint"...).
- Lĩnh vực kinh doanh: **Sơn và Sơn phủ**.
- Website chính thức: https://nipponpaint.com.vn/
- Giữ quy tắc chung của skill: không dùng từ xếp hạng tuyệt đối ("nhất", "số 1", "hàng đầu") khi không có chứng minh
  — kể cả khi từ khóa có chữ đó (vd "sơn chống thấm loại nào tốt nhất": giữ nguyên từ khóa, không khẳng định sản phẩm nào "tốt nhất").

## Khối cố định cuối mọi bài share (Trang chốt 30/09/2026)

Dán **y nguyên** theo cấu trúc ở checklist mục 10. (Trang gõ "Nippont Paint" — đã sửa thành **Nippon Paint** theo quy tắc ghi đúng tên doanh nghiệp.)

**Hashtag cố định:** `#sonnoithat #sonngoaithat #nipponpaint`

**Thông tin liên hệ:**

Nippon Paint
Địa chỉ: Số 14, đường 3A, KCN Biên Hòa II, phường Long Hưng, thành phố Đồng Nai
SĐT: (84) 251 383 6579
Email: customer@nipponpaint.com.vn
Website: https://nipponpaint.com.vn/

**Follow social:**

- https://www.facebook.com/NipponPaintVietnam/
- https://www.instagram.com/nipponpaintvietnam/
- https://www.youtube.com/nipponpaintvietnam
- https://www.tiktok.com/@nipponpaintvietnam

## Kết nối API — riêng cho dự án này, KHÔNG dùng chung

Mỗi tài khoản có Client ID / ứng dụng riêng, không lấy lại của dự án khác:

Dự án Google Cloud riêng: tên `nippon-paint-share-social`, Project ID `nodal-rex-510103-e6` (tạo 29/09/2026 bằng tài khoản Google `nipponpaint.seo2026@gmail.com`; dự án cùng tên tạo nhầm bằng email cũ thì bỏ, không dùng).

| Mục | Loại kết nối | Trạng thái |
|---|---|---|
| Google Sheet | OAuth Client ID riêng "Sheet - Nippon Paint" (Desktop app), bật Google Sheets API | ✅ Đã kết nối 29/09/2026 — đọc thử sheet OK |
| Blogger | OAuth Client ID riêng "Blogger - Nippon Paint" (Desktop app), bật Blogger API v3 | ✅ Đã kết nối 29/09/2026 — tra được blog "Nippon Paint Việt Nam", đã lưu blog_id |
| WordPress.com | Ứng dụng riêng "Nippon Paint Share Social" (Client ID 149315) tại developer.wordpress.com/apps | ✅ Đã kết nối 29/09/2026 — có quyền đăng bài + tải ảnh |

OAuth consent screen phải chuyển sang **In production** (để "Testing" thì token hết hạn sau 7 ngày).

## Việc còn dở — Pinterest (cập nhật 29/09/2026)

Đã xong: chuyển tài khoản `nipponpaintvn` sang Business · tạo app "Nippon Paint Share Social" (App ID `1617333`,
use case Pin creation & scheduling, audience Businesses, đọc Pins/Boards: Yes mine,
privacy policy `https://nipponpaint.com.vn/vi/son-nippon-policy`) · skill `share-bai-pinterest` đã viết sẵn.

Còn lại, **làm khi Pinterest duyệt Trial access** (có email báo):
1. developers.pinterest.com/apps/1617333/configure → Redirect URIs → thêm `https://localhost/` → Add (lúc chờ duyệt ô này bị khóa).
2. Lấy App secret key (lúc chờ duyệt ghi "Unavailable") → lưu bằng `set-app` (env `sandbox`).
3. Authorize → đổi code → `save-tokens` → `list-boards` chọn board → `set-field board_id`.
4. Đăng Pin thử (sandbox — chỉ chủ tài khoản thấy).
5. Xin **Standard access** (nộp video quay màn hình cảnh app đăng Pin) → được duyệt thì `set-field env prod`.

Không dùng nút "Generate token" trên trang app — token đó chỉ có quyền đọc, không đăng Pin được.

## Google Site — cách làm (bán tự động)

Google Site mới không có API → agent soạn "gói bài" gồm trang xem trước + ảnh, Trang dán vào **trang con mới dưới trang "Tin tức"**
(danh mục lớn của blog — đổi từ trang `blog-1` cũ, 29/09/2026), Xuất bản, gửi link → agent ghi vào cột I. Tài khoản sửa site: `nipponpaint.seo2026@gmail.com`.

| Dòng | Gói bài | Link Google Site |
|---|---|---|
| 5 | `nippon-google-site/dong-5/` (bài 1084 chữ, 4 ảnh, theo checklist) | ⏳ chờ Trang đăng |

> 29/09/2026: đã thử tự động Google Site bằng phiên đăng nhập (cookie) → Google bắt đăng nhập lại, không dùng được; hệ thống an toàn của môi trường cũng chặn cách này. **Không thử lại cách cookie/đăng nhập hộ.** Google Site giữ cách bán tự động.

## Việc còn dở — Google Site (TẠM DỪNG 29/09/2026)

Trang tạm dừng vì muốn tự động 100% mà Google Site không đáp ứng được. Hiện trạng để làm tiếp:

- **Cấu trúc site đã có:** Homepage · Về Nippon Paint · **Tin tức** (danh mục blog, đổi từ `blog-1`; ảnh bìa còn chữ "BLOG 1") ·
  **Tin tức 1** (trang con trống dưới Tin tức — định dùng cho bài dòng 5) · Liên hệ. Sửa bằng `nipponpaint.seo2026@gmail.com`.
- **Gói bài dòng 5 đã soạn xong:** `nippon-google-site/dong-5/bai-google-site-dong-5.html` + `nippon-google-site/anh-dong-5.zip`
  (1084 chữ, 4 ảnh, theo checklist, khác bài Blogger). Ô I5 trên sheet còn trống.
- **Đã loại trừ:** tự động bằng API (không tồn tại) · đăng nhập hộ bằng cookie (Google bắt đăng nhập lại + môi trường chặn) — không thử lại.
- **3 hướng Trang đang cân nhắc:**
  1. Thay bằng **Google Groups** (cột J "GG Group" có sẵn, skill `share-bai-ggr` tự động 100%) — Claude khuyên.
  2. Trang "Tin tức" nhúng danh sách bài Blogger (tự động nhưng không có link riêng từng bài).
  3. Bán tự động: Claude soạn, Trang dán (~5 phút/bài) — đổi tên "Tin tức 1" thành tên bài rồi dán gói dòng 5.

## ⛔ Bài học 30/09/2026 — ĐĂNG GIÃN CÁCH, KHÔNG ĐĂNG DỒN

Chạy 3 nền tảng song song, đăng dồn: WordPress.com **khóa blog** sau 7 bài/~35 phút; Tumblr **hạn chế tài khoản**
sau 3 bài/~10 phút; Blogger đăng 10 bài/~45 phút, tạm thời vẫn sống. Blog mới lập + nhiều bài quảng cáo mang tên thương hiệu
= dễ bị hệ thống chống spam khóa.

**Quy tắc từ nay:** mỗi nền tảng **tối đa 2 bài/ngày**, **cách nhau ít nhất 2 tiếng**; blog mới lập tuần đầu **1 bài/ngày**.
Không bao giờ chạy lại hàng loạt dòng một lúc. Muốn đăng nhiều dòng → xếp lịch rải nhiều ngày.
