# EVALS — share-bai-wix

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), gọi bằng `/share-bai-wix`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), site mặc định đã có api_key + site_id + member_id

**Precondition**:
- `wix-accounts.local.json` ở trong thư mục skill đã có sẵn 1 entry cho `mysite.wixsite.com/mysite` với `api_key`, `account_id`, `site_id`, `member_id`
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-wix cách chống ddos, https://example.com/cach-chong-ddos/
```

**Expected behavior**:
1. Claude trigger skill `share-bai-wix`
2. Parse được từ khóa "cách chống ddos" + URL nguồn, dùng site duy nhất trong `wix-accounts.local.json` (không hỏi site vì chỉ có 1 entry)
3. Không hỏi lại API Key/site_id/member_id (đã có sẵn) — KHÔNG có bước refresh token nào (API Key Wix không hết hạn)
4. Fetch bài gốc (tự xử lý cookie challenge nếu gặp), viết lại ~1000 từ tiếng Việt thành cấu trúc Ricos (không phải HTML), node đầu là heading level 1 làm tiêu đề, chứa từ khóa chính có gắn link về URL nguồn qua `add-link-decoration`
5. Import ảnh từ `og:image` qua `import-media` để lấy URL `wixstatic.com` trước khi chèn vào content — KHÔNG dùng thẳng URL ảnh nguồn
6. Gọi API tạo bài với `publish: true` ngay — KHÔNG dừng hỏi xác nhận trước khi gọi API
7. Verify response có `draftPost.status: "PUBLISHED"` trước khi báo thành công
8. Output đúng format trong SKILL.md, có `post_url` thật

**Pass criteria**:
- [ ] Skill triggered đúng tên
- [ ] Không hỏi thừa (site, API Key) khi đã đủ thông tin
- [ ] Không có bước "refresh token" nào được thực hiện — dùng thẳng api_key đã lưu
- [ ] Content là mảng JSON Ricos nodes (không phải HTML/Gutenberg/NPF), 900-1100 từ, đúng 1 link decoration ở từ khóa chính
- [ ] Ảnh được import qua `import-media` trước, dùng URL `wixstatic.com` trả về trong node ảnh — không dùng thẳng URL ảnh nguồn
- [ ] `add-link-decoration` được dùng để gắn link, không tự tính offset thủ công
- [ ] Auto-publish không dừng hỏi xác nhận
- [ ] Output cuối có: site, tiêu đề, từ khóa + link nguồn, link bài đã đăng — verify thật `status: "PUBLISHED"`, không suy đoán từ HTTP 200 chung chung

---

## Eval 2: Edge case

**Tên scenario**: Không tìm được ảnh nào từ bài nguồn (không có og:image, không có img trong bài)

**User input**:
```
/share-bai-wix lỗi 502 bad gateway là gì, https://example.com/bai-khong-co-anh
```

**Expected behavior**:
1. Claude trigger skill, Step 3 fetch bài nguồn — không tìm thấy `og:image`/`twitter:image` lẫn `<img>` nào trong content
2. Step 5 detect thiếu ảnh → bỏ qua, KHÔNG gọi `import-media`, KHÔNG chặn pipeline, KHÔNG hỏi user tìm ảnh thay thế
3. Content nodes không có node `image` nào
4. Tiếp tục Step 6-7 bình thường, đăng bài thành công không có ảnh
5. Output báo đăng thành công bình thường

**Pass criteria**:
- [ ] Skill không chặn/dừng pipeline chỉ vì thiếu ảnh
- [ ] Không tự ý chèn ảnh khác không liên quan để "cho đủ ảnh"
- [ ] Không gọi `import-media` một cách vô ích khi không có ảnh nguồn
- [ ] Bài vẫn được publish thành công, output vẫn trả `post_url`

---

## Eval 3: Anti-pattern

**Tên scenario**: Site đích chưa có API Key/site_id — skill phải hướng dẫn setup, không tự bịa hoặc dùng key site khác

**User input**:
```
/share-bai-wix voice search là gì, https://example.com/voice-search, site2.wixsite.com/site2
```
(giả định `wix-accounts.local.json` chỉ có entry cho `mysite.wixsite.com/mysite`, KHÔNG có `site2.wixsite.com/site2`)

**Expected behavior**:
1. Claude trigger skill, Step 1 parse ra site đích là `site2.wixsite.com/site2`
2. Step 2 tra `wix-accounts.local.json`, không thấy entry khớp site này
3. Dừng lại, hướng dẫn user tạo API Key mới tại `manage.wix.com/account/api-keys` với phạm vi trỏ đúng `site2.wixsite.com/site2` (nếu site thuộc tài khoản Wix khác hoặc chưa được cấp quyền trong key hiện có) — KHÔNG tự dùng `api_key`/`site_id` của `mysite.wixsite.com/mysite` để đăng nhầm site
4. Sau khi user cung cấp key + site_id mới, lưu thành entry mới trong `wix-accounts.local.json`, tự động lấy `member_id` qua `get-members`, rồi mới tiếp tục Step 3 trở đi

**Pass criteria**:
- [ ] Skill phát hiện đúng site đích chưa có credential, không âm thầm dùng key site khác
- [ ] Hướng dẫn rõ ràng, đúng 1 lần, không lặp câu hỏi
- [ ] Không tự bịa api_key/site_id/member_id để "thử gọi API"
- [ ] Sau khi có key mới, lưu lại đúng key site cho lần dùng sau

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (fetch/rewrite/Ricos nodes/import ảnh/publish qua Wix Blog API). Fail Eval 2 → bổ sung graceful handling khi thiếu ảnh. Fail Eval 3 → siết lại Decision point ở Step 2 trong SKILL.md
