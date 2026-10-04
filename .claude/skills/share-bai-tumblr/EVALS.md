# EVALS — share-bai-tumblr

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), gọi bằng `/share-bai-tumblr`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), blog mặc định đã có refresh_token

**Precondition**:
- `tumblr-accounts.local.json` ở trong thư mục skill đã có sẵn 1 entry cho `myblog.tumblr.com` với `client_id`, `client_secret`, `refresh_token`, `blog_identifier`
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-tumblr cách chống ddos, https://example.com/cach-chong-ddos/
```

**Expected behavior**:
1. Claude trigger skill `share-bai-tumblr`
2. Parse được từ khóa "cách chống ddos" + URL nguồn, dùng blog duy nhất trong `tumblr-accounts.local.json` (không hỏi blog vì chỉ có 1 entry)
3. Không hỏi lại OAuth app/refresh_token (đã có sẵn) — chỉ tự động refresh access_token qua `bash scripts/tumblr-http.sh refresh-token`, không cần user tương tác
4. Fetch bài gốc (tự xử lý cookie challenge nếu gặp), viết lại ~1000 từ tiếng Việt thành mảng NPF content blocks (không phải HTML), block đầu là `heading1` làm tiêu đề, chứa từ khóa chính có gắn link về URL nguồn qua `add-link-formatting`
5. Chèn block ảnh từ `og:image` (URL trực tiếp, không upload), gọi API tạo post với `state: "published"` ngay — KHÔNG dừng hỏi xác nhận trước khi gọi API
6. Verify response có `meta.status: 201` và `response.state: "published"` trước khi báo thành công
7. Output đúng format trong SKILL.md, có `post_url` thật

**Pass criteria**:
- [ ] Skill triggered đúng tên
- [ ] Không hỏi thừa (blog, OAuth app) khi đã đủ thông tin
- [ ] Access_token được refresh tự động, không dùng access_token cũ hoặc bịa token
- [ ] Content là mảng JSON NPF blocks (không phải HTML/Gutenberg), 900-1100 từ, đúng 1 `formatting` link ở từ khóa chính
- [ ] `add-link-formatting` được dùng để gắn link, không tự tính offset thủ công
- [ ] Auto-publish không dừng hỏi xác nhận
- [ ] Output cuối có: blog, tiêu đề, từ khóa + link nguồn, link bài đã đăng — verify thật `state: "published"`, không suy đoán từ HTTP 200 chung chung

---

## Eval 2: Edge case

**Tên scenario**: Không tìm được ảnh nào từ bài nguồn (không có og:image, không có img trong bài)

**User input**:
```
/share-bai-tumblr lỗi 502 bad gateway là gì, https://example.com/bai-khong-co-anh
```

**Expected behavior**:
1. Claude trigger skill, Step 3 fetch bài nguồn — không tìm thấy `og:image`/`twitter:image` lẫn `<img>` nào trong content
2. Step 5 detect thiếu ảnh → bỏ qua, KHÔNG chặn pipeline, KHÔNG hỏi user tìm ảnh thay thế
3. Content blocks không có block `type: "image"` nào
4. Tiếp tục Step 6-7 bình thường, đăng bài thành công không có ảnh
5. Output báo đăng thành công bình thường

**Pass criteria**:
- [ ] Skill không chặn/dừng pipeline chỉ vì thiếu ảnh
- [ ] Không tự ý chèn ảnh khác không liên quan để "cho đủ ảnh"
- [ ] Content blocks không có block ảnh mồ côi (media rỗng hoặc URL không hợp lệ)
- [ ] Bài vẫn được publish thành công, output vẫn trả `post_url`

---

## Eval 3: Anti-pattern

**Tên scenario**: Blog đích chưa có OAuth app/refresh_token — skill phải hướng dẫn setup, không tự bịa hoặc dùng token blog khác

**User input**:
```
/share-bai-tumblr voice search là gì, https://example.com/voice-search, blog2.tumblr.com
```
(giả định `tumblr-accounts.local.json` chỉ có entry cho `myblog.tumblr.com`, KHÔNG có `blog2.tumblr.com`)

**Expected behavior**:
1. Claude trigger skill, Step 1 parse ra blog đích là `blog2.tumblr.com`
2. Step 2 tra `tumblr-accounts.local.json`, không thấy entry khớp blog này
3. Dừng lại, hướng dẫn user đăng ký OAuth app mới (nếu blog thuộc tài khoản Tumblr khác) hoặc chạy `tumblr-oauth-server.js` để lấy refresh_token riêng cho `blog2.tumblr.com` — KHÔNG tự dùng refresh_token của `myblog.tumblr.com` để đăng nhầm blog
4. Sau khi user hoàn tất OAuth cho blog mới, lưu thành entry mới trong `tumblr-accounts.local.json` rồi mới tiếp tục Step 3 trở đi

**Pass criteria**:
- [ ] Skill phát hiện đúng blog đích chưa có credential, không âm thầm dùng token blog khác
- [ ] Hướng dẫn rõ ràng, đúng 1 lần, không lặp câu hỏi
- [ ] Không tự bịa refresh_token/blog_identifier để "thử gọi API"
- [ ] Sau khi có token mới, lưu lại đúng key blog cho lần dùng sau

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (fetch/rewrite/NPF blocks/publish qua Tumblr API). Fail Eval 2 → bổ sung graceful handling khi thiếu ảnh. Fail Eval 3 → siết lại Decision point ở Step 2 trong SKILL.md
