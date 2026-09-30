# EVALS — share-bai-blogger

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), vì `disable-model-invocation: true` nên phải gọi bằng `/share-bai-blogger`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), blog mặc định đã có refresh_token + blog_id

**Precondition**:
- `blogger-accounts.local.json` ở trong thư mục skill đã có sẵn 1 entry cho `myblog.blogspot.com` với `client_id`, `client_secret`, `refresh_token`, `blog_id`
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-blogger cách chống ddos, https://example.com/cach-chong-ddos/
```

**Expected behavior**:
1. Claude trigger skill `share-bai-blogger`
2. Parse được từ khóa "cách chống ddos" + URL nguồn, dùng blog duy nhất trong `blogger-accounts.local.json` (không hỏi blog vì chỉ có 1 entry)
3. Không hỏi lại OAuth client/refresh_token (đã có sẵn) — chỉ tự động refresh access_token qua `bash scripts/blogger-http.sh refresh-token`, không cần user tương tác
4. Fetch bài gốc (tự xử lý cookie challenge nếu gặp), viết lại ~1000 từ tiếng Việt dạng HTML thường (không phải Gutenberg block), chứa từ khóa chính có gắn link về URL nguồn
5. Chèn `<img>` từ `og:image` vào content, gọi API tạo post với publish ngay — KHÔNG dừng hỏi xác nhận trước khi gọi API
6. Verify response trả `status: "LIVE"` trước khi báo thành công
7. Output đúng format trong SKILL.md, có link bài đã đăng thật

**Pass criteria**:
- [ ] Skill triggered đúng tên
- [ ] Không hỏi thừa (blog, OAuth client) khi đã đủ thông tin
- [ ] Access_token được refresh tự động, không dùng access_token cũ hoặc bịa token
- [ ] Bài viết 900-1100 từ, đúng 1 link ở từ khóa chính trỏ về URL nguồn, content là HTML thường (không có comment `<!-- wp:... -->`)
- [ ] Auto-publish không dừng hỏi xác nhận
- [ ] Output cuối có: blog, tiêu đề, từ khóa + link nguồn, link bài đã đăng — link đó thật sự có `status: "LIVE"` (không phải suy đoán từ HTTP 200 chung chung)

---

## Eval 2: Edge case

**Tên scenario**: Không tìm được ảnh nào từ bài nguồn (không có og:image, không có img trong bài)

**User input**:
```
/share-bai-blogger lỗi 502 bad gateway là gì, https://example.com/bai-khong-co-anh
```

**Expected behavior**:
1. Claude trigger skill, Step 3 fetch bài nguồn — không tìm thấy `og:image`/`twitter:image` lẫn `<img>` nào trong content
2. Step 5 detect thiếu ảnh → bỏ qua, KHÔNG chặn pipeline, KHÔNG hỏi user tìm ảnh thay thế
3. Step 6 bỏ qua việc chèn `<img>`, content không có ảnh
4. Tiếp tục Step 7-8 bình thường, đăng bài thành công không có ảnh
5. Output báo đăng thành công bình thường

**Pass criteria**:
- [ ] Skill không chặn/dừng pipeline chỉ vì thiếu ảnh
- [ ] Không tự ý chèn ảnh khác không liên quan để "cho đủ ảnh"
- [ ] Content HTML không có thẻ `<img>` mồ côi (src rỗng hoặc trỏ file local không truy cập công khai được)
- [ ] Bài vẫn được publish thành công, output vẫn trả link bài đã đăng

---

## Eval 3: Anti-pattern

**Tên scenario**: Blog đích chưa có OAuth client/refresh_token — skill phải hướng dẫn setup, không tự bịa hoặc dùng token blog khác

**User input**:
```
/share-bai-blogger voice search là gì, https://example.com/voice-search, blog2.blogspot.com
```
(giả định `blogger-accounts.local.json` chỉ có entry cho `myblog.blogspot.com`, KHÔNG có `blog2.blogspot.com`)

**Expected behavior**:
1. Claude trigger skill, Step 1 parse ra blog đích là `blog2.blogspot.com`
2. Step 2 tra `blogger-accounts.local.json`, không thấy entry khớp blog này
3. Dừng lại, hướng dẫn user tạo OAuth client (nếu blog thuộc Google account khác) hoặc chạy `google-oauth-server.js` để lấy refresh_token riêng cho `blog2.blogspot.com` — KHÔNG tự dùng refresh_token của `myblog.blogspot.com` để đăng nhầm blog
4. Sau khi user hoàn tất OAuth cho blog mới, lưu thành entry mới trong `blogger-accounts.local.json` rồi mới tiếp tục Step 3 trở đi

**Pass criteria**:
- [ ] Skill phát hiện đúng blog đích chưa có credential, không âm thầm dùng token blog khác
- [ ] Hướng dẫn rõ ràng, đúng 1 lần, không lặp câu hỏi
- [ ] Không tự bịa refresh_token/blog_id để "thử gọi API"
- [ ] Sau khi có token mới, lưu lại đúng key blog cho lần dùng sau

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (fetch/rewrite/publish qua Blogger API). Fail Eval 2 → bổ sung graceful handling khi thiếu ảnh. Fail Eval 3 → siết lại Decision point ở Step 2 trong SKILL.md
