# EVALS — share-bai-wp

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), vì `disable-model-invocation: true` nên phải gọi bằng `/share-bai-wp`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), site mặc định đã có access token còn hạn

**Precondition**:
- `wp-accounts.local.json` (trong thư mục skill này) đã có sẵn 1 entry cho `myblog.wordpress.com` với `client_id`, `client_secret`, `access_token` còn hạn
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-wp cách chống ddos, https://example.com/cach-chong-ddos/
```

**Expected behavior**:
1. Claude trigger skill `share-bai-wp`
2. Parse được từ khóa "cách chống ddos" + URL nguồn, dùng site duy nhất trong `wp-accounts.local.json` (không hỏi site vì chỉ có 1 entry)
3. Không hỏi lại OAuth app/token (đã có sẵn, còn hạn)
4. Fetch bài gốc (tự xử lý cookie challenge nếu gặp), viết lại ~1000 từ tiếng Việt dạng Gutenberg block markup, chứa từ khóa chính có gắn link về URL nguồn
5. Upload ảnh từ `og:image`, gọi API tạo post với `status: publish` luôn — KHÔNG dừng hỏi xác nhận trước khi gọi API publish
6. Verify response trả `status: "publish"` trước khi báo thành công
7. Output đúng format trong SKILL.md, có link bài đã đăng thật

**Pass criteria**:
- [ ] Skill triggered đúng tên
- [ ] Không hỏi thừa (site, OAuth) khi đã đủ thông tin
- [ ] Bài viết 900-1100 từ, đúng 1 link ở từ khóa chính trỏ về URL nguồn, content là Gutenberg block markup
- [ ] Auto-publish không dừng hỏi xác nhận
- [ ] Output cuối có: site, tiêu đề, từ khóa + link nguồn, link bài đã đăng — và link đó thật sự publish thành công (không phải suy đoán từ HTTP 200 chung chung)

---

## Eval 2: Edge case

**Tên scenario**: Access token đã lưu bị revoke (API trả 401 dù trong `wp-accounts.local.json` có sẵn `access_token`)

**User input**:
```
/share-bai-wp lỗi 502 bad gateway là gì, https://example.com/bai-ve-502
```
(giả định `wp-accounts.local.json` có entry cho site mặc định với `access_token` sẵn có, nhưng token đã bị user revoke thủ công phía WordPress.com nên gọi API trả 401)

**Expected behavior**:
1. Claude trigger skill, Step 2 thấy có `access_token` sẵn nên KHÔNG hỏi lại, dùng luôn (đúng vì loại token này mặc định không hết hạn, không có cơ chế đoán trước khi nào bị revoke)
2. Khi gọi API thực tế (Step 6/7) nhận response 401 → dừng lại, hướng dẫn user lấy lại access token theo `references/wordpress-rest-api-steps.md` (mở lại link `response_type=code`, đổi code lấy token qua `/oauth2/token`) — KHÔNG tự bịa token mới, KHÔNG báo lỗi chung chung không rõ nguyên nhân
3. Sau khi user cung cấp code mới, đổi lấy access token, lưu đè vào `wp-accounts.local.json`, rồi mới tiếp tục pipeline từ bước đang dang dở

**Pass criteria**:
- [ ] Skill không hỏi thừa khi đã có token sẵn (vì token dạng authorization-code grant không tự hết hạn theo thời gian)
- [ ] Khi gặp 401 thật, nhận diện đúng đây là vấn đề token bị revoke, không nhầm với lỗi khác (vd lỗi nội dung, lỗi ảnh)
- [ ] Hướng dẫn lấy lại token đúng luồng `response_type=code` (không quay lại dùng `response_type=token` đã bị coi là legacy)
- [ ] Sau khi có token mới, tiếp tục pipeline bình thường, không phải chạy lại từ đầu (không viết lại bài lần 2)

---

## Eval 3: Anti-pattern

**Tên scenario**: Site đích chưa từng tạo OAuth app — skill phải hướng dẫn setup, không tự bịa hoặc dùng token site khác

**User input**:
```
/share-bai-wp voice search là gì, https://example.com/voice-search, mysite2.wordpress.com
```
(giả định `wp-accounts.local.json` chỉ có entry cho `myblog.wordpress.com`, KHÔNG có `mysite2.wordpress.com`)

**Expected behavior**:
1. Claude trigger skill, Step 1 parse ra site đích là `mysite2.wordpress.com`
2. Step 2 tra `wp-accounts.local.json`, không thấy entry khớp domain này
3. Dừng lại, hướng dẫn user tạo OAuth app tại `developer.wordpress.com/apps/new/` cho đúng `mysite2.wordpress.com` — KHÔNG tự dùng access token của `myblog.wordpress.com` để đăng nhầm site
4. Sau khi user cung cấp Client ID/Secret rồi hoàn tất OAuth, lưu thành entry mới trong `wp-accounts.local.json` rồi mới tiếp tục Step 3 trở đi

**Pass criteria**:
- [ ] Skill phát hiện đúng site đích chưa có app/token, không âm thầm dùng token site khác
- [ ] Hướng dẫn setup rõ ràng, đúng 1 lần, không lặp lại
- [ ] Không tự bịa Client ID/Secret/token để "thử gọi API"
- [ ] Sau khi có token mới, lưu lại đúng key domain `mysite2.wordpress.com` cho lần dùng sau

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (fetch/rewrite/publish qua REST API). Fail Eval 2 → siết lại xử lý lỗi 401 ở Step 6/7. Fail Eval 3 → siết lại Decision point ở Step 2 trong SKILL.md
