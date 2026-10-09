# Hướng dẫn share bài Techcombank (TCB) — kết nối site + quy tắc viết

> Tài liệu dùng chung cho **mọi tool / agent share bài** của dự án TCB (Seo Ngon).
> Tổng hợp từ đợt chạy thật ngày 09–11/10/2026 (40 từ khóa × Blogger + WordPress).
> **Không chứa chìa khóa.** Chìa nằm trong file `*-accounts.local.json` trên máy chạy tool, không bao giờ commit.

---

## PHẦN A — Kết nối site

### A1. Danh sách site đang dùng

| Nền tảng | Địa chỉ | Tài khoản sở hữu | Cách xác thực | Chìa hết hạn? |
|---|---|---|---|---|
| Blogger | https://nganhangtechcombankvn.blogspot.com (blog "Techcombank Việt Nam", blog ID `6701158052132617774`) | trangjena3@gmail.com | Google OAuth (Blogger API v3) | **Có — 7 ngày** (app đang ở chế độ Test) |
| WordPress.com | https://techcombankvietnam.wordpress.com (site ID `257871734`) | tài khoản WP của Trang | WordPress.com OAuth, `response_type=code`, scope `global` | Không |
| Mastodon / Pinterest / Wix / Webflow | (tool khác đang chạy) | — | — | — |
| WordPress.com (của mình — cột H ghi `- Hoa`) | https://nganhangtechcombankvn.wordpress.com (tên site "techcombank7", site ID `257873894`) | cần bổ sung | WordPress.com OAuth `response_type=code`, scope `global`, app Client ID `150168` | Không — **đã kết nối 09/10/2026**, thử quyền đăng bài OK |
| Blogger (của mình — cột H ghi `- Hoa`) | https://nganhangtechcombankvietnam.blogspot.com | hoaa8k58@gmail.com (chị Hoa) | Google OAuth, project `share-bai-blogger-511119` trên hoaa8k58 | **CHƯA xong** — đã có chìa, còn bước bấm Cho phép: Google đòi mã trên điện thoại Galaxy của chị Hoa. Hướng đề xuất: chị Hoa mời Gmail của Trang làm Quản trị viên blog |

### A2. Kết nối Blogger (làm 1 lần, ~10 phút)

1. **Tạo project** tại https://console.cloud.google.com/projectcreate (tên `share-bai-blogger`).
2. **Bật Blogger API v3:** https://console.cloud.google.com/apis/library/blogger.googleapis.com → Enable.
3. **Màn hình xin phép:** https://console.cloud.google.com/auth/overview → Get started → External → điền email.
4. **Test users** (BẮT BUỘC, thiếu là lỗi *403 access_denied / "chưa hoàn tất quy trình xác minh"*):
   https://console.cloud.google.com/auth/audience → Add users → **đúng email sở hữu blog** (trangjena3@gmail.com).
5. **Tạo OAuth Client:** https://console.cloud.google.com/auth/clients → Create client → **Desktop app** → Download JSON.
   Người dùng **đính kèm file JSON** vào chat, không dán chữ.
6. **Cấp quyền:** mở link authorize với `scope=https://www.googleapis.com/auth/blogger`,
   `access_type=offline`, `prompt=consent`, `redirect_uri=http://127.0.0.1:8765`.
   - Tool chạy trên máy chủ đám mây → trang `127.0.0.1` báo lỗi "không thể kết nối" là **bình thường**.
     Người dùng copy nguyên địa chỉ trang lỗi (`http://127.0.0.1:8765/?code=...`) gửi lại; tool tự đổi `code` lấy `refresh_token`.
7. Tra blog ID: `GET /blogger/v3/users/self/blogs` (hoặc `blogs/byurl?url=...`).

**Lưu ý Blogger**
- App ở chế độ **Test** → `refresh_token` sống **7 ngày** (`refresh_token_expires_in = 604799`). Nút *Publish app* đang mờ
  (Google đòi trang chủ / chính sách quyền riêng tư có tên miền xác minh) → chấp nhận cấp quyền lại mỗi tuần.
- `access_token` sống ~1 giờ → **refresh trước mỗi lần gọi API**.
- **Giới hạn chống spam:** tạo ~19 bài liên tục trong ~15 phút thì API trả **403 "The caller does not have permission"**
  (blog không bị khóa, bài đã tạo vẫn còn). → Mỗi lần tạo bài cách nhau **tối thiểu vài phút**, tốt nhất là tạo đúng giờ đăng.
  Gặp 403 thì **dừng ngay**, thử lại sau vài giờ, không gửi dồn.
- Gặp **429 "Resource has been exhausted"** → cũng là quá nhịp, chờ rồi thử lại.
- Hẹn giờ: tạo bài nháp `POST .../posts/?isDraft=true` rồi `POST .../posts/{id}/publish?publishDate=<RFC3339>`.
  **Phải mã hóa URL cho `publishDate`** (dấu `+` trong `+07:00` thành `%2B`), nếu không sẽ lỗi 400.
- Blogger tự sinh đường dẫn từ tiêu đề và **bỏ chữ "đ"** (vd "điều" → `ieu`). Không sửa được qua API — chấp nhận.
- Không có ảnh đại diện riêng; ảnh phải nhúng trong nội dung (base64), không trỏ thẳng ảnh techcombank.com.

### A3. Kết nối WordPress.com (làm 1 lần, ~3 phút)

1. Tạo app: https://developer.wordpress.com/apps/new/
   - Website URL: `https://techcombankvietnam.wordpress.com` · Redirect URLs: `https://localhost/` · Type: **Web**.
2. Người dùng lưu **Client ID + Client Secret** vào file `.txt` rồi **đính kèm file** (không dán chữ).
3. Cấp quyền: `https://public-api.wordpress.com/oauth2/authorize?client_id=<ID>&redirect_uri=https%3A%2F%2Flocalhost%2F&response_type=code&scope=global`
   → Approve → trang `https://localhost/?code=...` báo lỗi là bình thường → copy địa chỉ gửi lại.
4. Đổi code: `POST https://public-api.wordpress.com/oauth2/token` (grant_type=authorization_code). Token **không hết hạn**.
   Dùng `response_type=code`, KHÔNG dùng `response_type=token` (loại đó hết hạn sau ~14 ngày).

**Lưu ý WordPress**
- Hẹn giờ: `status: "future"` + `date: "<ISO có múi giờ>"`. Múi giờ site: `Asia/Ho_Chi_Minh`.
- Nội dung nên ở dạng khối Gutenberg (`<!-- wp:paragraph -->`…) để mở lại trong trình soạn thảo không bị vỡ.
- Bài hẹn giờ API trả link tạm `?p=<ID>`. Link đẹp = `https://techcombankvietnam.wordpress.com/YYYY/MM/DD/<slug>/`
  (cấu trúc permalink `/%year%/%monthnum%/%day%/%postname%/`, ngày theo giờ đăng). Ghi link đẹp vào sheet.
- Đợt chạy 40 bài liên tiếp (cách nhau ~1–2 giây) **không bị chặn**.

### A4. Bảo mật

- Chìa (client secret, token) **không dán vào chat, không gắn vào URL, không commit**. Người dùng đính kèm file.
- Gửi chìa qua header `Authorization: Bearer ...`, không in ra màn hình.
- Repo `vuthithuytrang-lab/trang` là **public** → mọi file `*.local.json` đã được chặn trong `.gitignore`.

---

## PHẦN B — Đọc & ghi Google Sheet

- Sheet: https://docs.google.com/spreadsheets/d/1UQYdaL67rujn4WBbV2r3QYTvQWuIMhLZCJyU0K8TzVk — tab **"Share social"**.
- Cột: **D** từ khóa · **F** URL bài gốc · **H** nền tảng · **I** link đã share · **J** ngày share. Cột G là số nền tảng (tool khác điền) — không đụng.
- **Dòng gốc** = dòng có cả D và F. Các dòng ngay dưới, D/F trống nhưng có H → cùng bài với dòng gốc.
- Ghi bài mới: điền vào **dòng trống ngay dưới nhóm** của bài đó (không chèn dòng, không ghi đè dòng có sẵn).
  - Cột H ghi theo dạng **`<Tên nền tảng social> - Hoa`**, ví dụ `Blog - Hoa` (từ đợt sau 10/10/2026; đợt 10/10 đã ghi `Blogger - Trang`, `WordPress - Trang` — giữ nguyên các dòng cũ).
  - Cột I: link bài (link đẹp). Cột J: ngày đăng dạng `d/m/yyyy` (vd `10/10/2026`).
- Không sửa / xóa bất kỳ ô nào khác, đặc biệt cột H do tool khác chèn.
- **Bài và dòng do tool khác đăng/điền: không động vào** — không sửa, không xóa, không đăng lại. Mình là đồng nghiệp đăng song song: chỉ thêm dòng của mình; nền tảng nào trong nhóm đã có link thì không đăng trùng; thấy lỗi bên tool kia thì báo Trang, không tự sửa.
- Bỏ qua dòng tiêu đề nhóm (chỉ có ngày như "10/9"), dòng trống, dòng đã có link ở cột I.
- Lưu ý: từ khoảng dòng 476 có một loạt dòng **trùng lặp, không có STT** (Thẻ tín dụng quốc tế, CIC là gì…) — chưa xử lý, đừng đăng trùng.

---

## PHẦN C — Quy tắc viết bài share TCB

### C1. Đọc bài gốc

- `techcombank.com` **chặn tải trực tiếp** (curl bị reset kết nối). Đọc được qua công cụ đọc web (WebFetch) —
  yêu cầu nó *"liệt kê chi tiết toàn bộ nội dung theo heading, giữ mọi số liệu, tỷ lệ, thời hạn, công thức, căn cứ pháp luật"*.
- Không đọc được → báo lỗi, **bỏ qua dòng đó, tuyệt đối không bịa nội dung**.
- Ảnh trên techcombank.com cũng không tải được → **đăng bài không ảnh**.

### C2. Quy tắc nội dung (bắt buộc)

| # | Quy tắc |
|---|---|
| 1 | Tiếng Việt đủ dấu, **900–1100 từ** mỗi bài. |
| 2 | Giữ đúng nghĩa và **mọi số liệu / căn cứ pháp luật** như bài gốc. Không thêm số liệu, không suy diễn. |
| 3 | **Không chép nguyên câu** của bài gốc — diễn đạt lại hoàn toàn. |
| 4 | **Không dùng từ xếp hạng tuyệt đối**: "nhất", "duy nhất", "số 1", "hàng đầu", "tốt nhất"… trừ khi bài gốc có số liệu chứng minh. (Từ chỉ thời gian/thứ tự như "chậm nhất", "thứ nhất", "mới nhất" thì được.) |
| 5 | Từ khóa chính có ở **tiêu đề**, **đoạn mở đầu**, và rải **3–5 lần** tự nhiên trong bài. |
| 6 | **Đúng 1 link** duy nhất: gắn trên từ khóa chính ở đoạn mở đầu, trỏ về URL bài gốc (cột F). Không link nào khác. |
| 7 | **Không chép hotline / email** của Techcombank vào bài. |
| 8 | Kết bài có câu lưu ý: *thông tin mang tính tham khảo, có thể thay đổi theo thời điểm*. |
| 9 | Tiêu đề **55–70 ký tự**, chứa từ khóa chính. |
| 10 | Chương trình ưu đãi **đã hết hạn** trong bài gốc → bỏ, hoặc ghi rõ "đã kết thúc". Bài gốc gắn nhãn "đã hết hạn" → vẫn viết nhưng ghi chú trong báo cáo. |

### C3. Mỗi nền tảng một bài khác nhau

- Cùng 1 từ khóa, bài cho từng nền tảng phải **khác rõ rệt**: khác tiêu đề, khác đoạn mở, khác cách sắp xếp ý.
  Không có câu nào giống nhau giữa các bài.
- Cách đã dùng: **Blogger** đi theo thứ tự bài gốc · **WordPress** mở bằng một tình huống thực tế / câu hỏi rồi sắp xếp lại ý.

### C4. Định dạng

- Chỉ dùng thẻ: `<p>`, `<h2>`, `<h3>`, `<ul>`, `<ol>`, `<li>`, `<strong>`, `<a>`. Không H1 (tiêu đề nằm riêng), không markdown, không style.
- Blogger: HTML thường. WordPress: bọc thành khối Gutenberg.
- **WordPress — cỡ chữ heading (bắt buộc với mọi bài WP, cả bài đăng ngay lẫn bài hẹn giờ):** theme mặc định làm H2/H3 rất to,
  gói miễn phí không cho sửa giao diện chung của cả trang → đặt cỡ chữ ngay trong từng khối heading. Đây là **ngoại lệ duy nhất** của quy tắc "không style".
  - H2 = **26px**:
    `<!-- wp:heading {"style":{"typography":{"fontSize":"26px"}}} -->`
    `<h2 class="wp-block-heading" style="font-size:26px">…</h2>`
    `<!-- /wp:heading -->`
  - H3 = **21px**:
    `<!-- wp:heading {"level":3,"style":{"typography":{"fontSize":"21px"}}} -->`
    `<h3 class="wp-block-heading" style="font-size:21px">…</h3>`
    `<!-- /wp:heading -->`
  - Blogger không áp dụng (giữ HTML thường).
  - Sau khi đăng: mở bài, chụp ảnh soát cỡ chữ heading + dấu tiếng Việt + bố cục.

### C5. Lỗi hay gặp trong bài gốc TCB (đừng chép theo)

| Bài gốc | Lỗi | Cách xử lý |
|---|---|---|
| cách tính thuế TNDN, thuế TNDN, thuế doanh nghiệp | Công thức ghi "**+** lỗ kết chuyển" (đúng phải là **trừ**) | Viết "trừ đi" hoặc "điều chỉnh theo…", nhắc người đọc đối chiếu văn bản gốc |
| công ty sử dụng tài khoản cá nhân | "Luật Quản lý thuế số 3/2019/QH14" (sai số, đúng là 38/2019/QH14) | Ghi "Luật Quản lý thuế năm 2019" |
| vòng quay vốn | Ví dụ ghi "800/100 = 7,27" | Theo đúng công thức: 800/110 ≈ 7,27 |
| lợi nhuận | Công thức "lợi nhuận một sản phẩm = Lợi nhuận − Giá vốn" sai | Bỏ công thức |
| bảo lãnh ngân hàng là gì | Đơn vị phí "%/tháng" nhưng chia cho 365 | Không ghi đơn vị, nhắc xác nhận với ngân hàng |
| tra cứu nợ thuế vs thủ tục thành lập DN | Mâu thuẫn về lệ phí môn bài (bỏ từ 01/01/2026) | Giữ theo từng bài, ghi "theo bài gốc" |
| điều kiện thành lập DN vs hướng dẫn đăng ký | Nơi xử lý hồ sơ: "Sở Tài chính" vs "Sở KH&ĐT" | Giữ theo từng bài gốc |
| FX Hub (quản lý tài chính DN) | "Hạn mức cao nhất thị trường" không có số liệu | Bỏ khẳng định |

### C6. Tự soát trước khi đăng

- [ ] Đếm từ 900–1100.
- [ ] Đúng 1 link, trỏ đúng URL cột F.
- [ ] Chỉ có thẻ cho phép.
- [ ] Không có từ xếp hạng tuyệt đối, không hotline/email.
- [ ] Số liệu khớp bài gốc.
- [ ] Các bài khác nền tảng của cùng từ khóa không trùng câu.

---

## PHẦN D — Nhịp đăng chống spam

- Mỗi nền tảng **~50 phút / bài** (lệch ngẫu nhiên ±8 phút). Hai nền tảng so le nhau 15–25 phút.
- WordPress: hẹn giờ trước hàng loạt được.
- Blogger: **không tạo hàng loạt** — tạo từng bài cách nhau vài phút trở lên; tốt nhất tạo đúng giờ đăng. Bị 403 → dừng, chờ vài giờ.
- Tài khoản mới: nên ≤ 20–25 bài/ngày/nền tảng.
