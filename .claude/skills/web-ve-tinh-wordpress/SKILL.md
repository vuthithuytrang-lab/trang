---
name: web-ve-tinh-wordpress
description: Thiết kế lại trang WordPress.com vệ tinh (site phụ làm SEO trỏ về website chính thức của một thương hiệu) — xuất 2 mã HTML hoàn chỉnh cho Trang chủ và Trang Tin tức, dán vào là chạy. Dùng khi Trang gửi link *.wordpress.com kèm website chính thức, hoặc nói "tạo trang chủ / trang tin tức / header / footer như AIG, VIB", "thiết kế lại web vệ tinh", "làm giống ASIA vừa làm", kể cả khi không gọi tên skill.
---

# Web vệ tinh WordPress.com — quy trình chuẩn

Đã làm thành công: **AIG** (`khach-hang/aig/`) và **VIB** (`khach-hang/vib/`).
Lần mới: **copy `khach-hang/vib/tao-ma-html.py`** sang `khach-hang/<ten-thuong-hieu>/`, thay nội dung, chạy lại.

## Kết quả Trang mong muốn (đừng hỏi lại những điều này)

1. **2 mã hoàn chỉnh, DÁN THẲNG VÀO CHAT** trong khung ```html để Trang bấm copy — không chỉ gửi file.
   - **Mã 1 – Trang chủ**: tự đủ đầu trang + nội dung + chân trang.
   - **Mã 2 – Trang Tin tức**: tự đủ đầu trang + dải tiêu đề + lưới bài viết + chân trang.
   - **Kèm 3 dòng mã mẫu "Pages"** (bên dưới) — bắt buộc, nếu không đầu trang/chân trang cũ của theme sẽ hiện chồng lên.
2. **Mỗi mã chỉ dán 1 lần.** Trang ghét phải dán đi dán lại — gộp hết vào một khung.
3. **Màu CHỈ lấy từ logo** (đo pixel bằng PIL, không đoán). Màu chính cho nền/tiêu đề, màu phụ chấm phá cho nút.
4. **Logo dùng đúng file gốc** (ảnh đại diện có sẵn trên site WP hoặc file logo trên web chính thức). Không vẽ lại. Logo trên nền tối → kê nền trắng/viền trắng.
5. **Nội dung lấy từ website chính thức hoặc mã Trang gửi — không bịa.** Địa chỉ, điện thoại, email, con số phải là số thật. Câu tiêu đề phụ tự thêm thì liệt kê ra để Trang duyệt.
6. **Đầu trang (header)**: logo + tên thương hiệu · menu (Giới thiệu, Sản phẩm/Giải pháp…, **Tin tức**, Liên hệ) · nút **"Website chính thức"** trỏ về web chính.
7. **Chân trang (footer) đầy đủ 3–4 cột**: giới thiệu ngắn + logo, link nhanh, liên hệ thật, dòng bản quyền. Không để chữ mẫu kiểu "123 Example Street".
8. **Trang Tin tức**: tên trang "Tin tức" → đường dẫn `/tin-tuc/`. Lưới **4 bài mỗi hàng × 5 hàng = 20 bài/trang**, có phân trang; mỗi bài: ảnh đại diện, ngày, tiêu đề, tóm tắt, "Đọc tiếp →".
9. **Không để chữ rớt dòng lẻ loi**: nối 2 chữ cuối tiêu đề bằng `&nbsp;` (vd `chọn&nbsp;AIG`); ô số liệu dùng nhãn ngắn (vd "Chứng nhận" thay vì "ISO · HACCP · FSSC").
10. **Nhiều link trỏ về website chính thức** (mục đích SEO của Trang).
11. Nói trước những thứ **không tắt được ở gói Free**: dải quảng cáo xanh "Create your own website…" và dòng "Blog at WordPress.com".

## Luật kỹ thuật WordPress.com gói Free (đã kiểm chứng)

- Không có `<style>`, `<script>`, không Custom CSS → **chỉ dùng style inline**.
- Màu viết **hex** (độ trong dùng hex 8 số `#005BAA14`), **không dùng `rgba()`** (bị lọc).
- Responsive bằng `display:flex;flex-wrap:wrap` + `flex:1 1 240px` — không có media query. `clamp()` cho cỡ chữ.
- Đầu trang/chân trang dùng `<div>` (không `<header>/<nav>/<footer>` — theme chèn CSS lạ).
- Bọc tất cả trong group full-width, `blockGap:0`:
  `<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->`
- Phần HTML đặt trong `<!-- wp:html -->`. Lưới bài dùng block `wp:query` (`inherit:false`, `perPage:20`, `post-template` grid `columnCount:4`) — xem `khach-hang/vib/HTML-TRANG-TIN-TUC.txt`.

### 3 dòng mã mẫu "Pages" (bỏ đầu/chân trang cũ của theme)

```html
<!-- wp:group {"tagName":"main","style":{"spacing":{"blockGap":"0","margin":{"top":"0"}}},"layout":{"type":"default"}} -->
<main class="wp-block-group" style="margin-top:0"><!-- wp:post-content {"layout":{"type":"constrained"}} /--></main>
<!-- /wp:group -->
```

## Các bước làm

1. **Kiểm tra site WP trước** (curl, không hỏi Trang):
   - `body class` có `home blog` → trang chủ là **mẫu Blog Home** → Mã 1 dán vào mẫu đó.
   - `body class` có `home page page-id-N` → trang chủ là **một Page** → Mã 1 dán vào nội dung trang, và mẫu Pages phải được thay bằng 3 dòng.
   - `/tin-tuc/` có tồn tại chưa; lấy danh sách ảnh `wp-content/uploads` để dùng lại.
2. **Lấy nội dung + logo** từ website chính thức (nếu bị chặn bot → dùng mã/ảnh Trang gửi và ảnh đã có trên site WP; báo rõ).
3. **Đo màu logo** bằng PIL.
4. Viết `tao-ma-html.py` → xuất `HTML-TRANG-CHU.txt`, `HTML-TRANG-TIN-TUC.txt`, `xem-truoc-trang-chu.html`.
5. **Tự soát**: tải ảnh về máy, thay link ảnh thành file nội bộ, chụp bằng Playwright ở **1366px và 390px**, kiểm `scrollWidth` = chiều rộng (không tràn ngang), đọc lại ảnh chụp: dấu tiếng Việt, rớt dòng, layout.
6. Commit + push vào `khach-hang/<ten>/`.
7. **Trả lời Trang** (xưng "bạn xinh đẹp"):
   - Tóm tắt đã làm gì (đánh số, lời thường).
   - Dán **Mã 1**, **Mã 2**, **3 dòng mẫu Pages** — mỗi mã kèm chỗ dán + **link mở thẳng trình sửa**:
     - Mẫu trang chủ: `https://<site>/wp-admin/site-editor.php?postType=wp_template&postId=pub%2Fassembler%2F%2Fhome&canvas=edit`
     - Mẫu Pages: `…postId=pub%2Fassembler%2F%2Fpage&canvas=edit`
     - (theme khác `assembler` → đổi `pub%2F<theme>`; lấy tên theme từ body class `wp-theme-pub<theme>`)
   - Cách dán: ⋮ → Code editor → Ctrl+A → Delete → dán → Save. Trang Tin tức: Pages → Add Page → tên "Tin tức" → Code editor → dán → Publish.
   - Hỏi 2 câu: có lỗi hiển thị không · có ưng không.

## Lỗi đã gặp — đừng lặp lại

| Lỗi | Nguyên nhân | Cách tránh |
|---|---|---|
| Đầu trang "About · Get Started" + chân trang "123 Example Street" hiện chồng | Trang con dùng mẫu Pages có template-part header/footer | Luôn đưa 3 dòng mẫu Pages ngay từ đầu |
| Link "Tin tức" ra 404 | Trang tên "Blog" có slug `blog`, Trang không tìm được chỗ đổi slug | Bảo Trang **tạo trang mới tên "Tin tức"** (tự ra `/tin-tuc/`), bỏ trang cũ vào thùng rác |
| Trang dán nhầm chỗ | Hướng dẫn tìm menu (Patterns/Template Parts) quá khó | Luôn đưa **link mở thẳng** trình sửa |
| Trong trình soạn thảo thấy "Chưa có bài viết…", số trang 1 2 3…7, bài "Hello World!" | Hình minh họa của editor + bài mẫu WP | Giải thích trước; nhắc xoá bài "Hello World!" và đặt ảnh đại diện cho mỗi bài |
