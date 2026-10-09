# EVALS — share-bai-mastodon

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), gọi bằng `/share-bai-mastodon`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), tài khoản mặc định đã có access_token hợp lệ

**Precondition**:
- `mastodon-accounts.local.json` đã có sẵn entry cho `tenban@mastodon.social` với `access_token` hợp lệ, `instance_url: "https://mastodon.social"`
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-mastodon học bổng du học Nhật Bản, https://example.com/hoc-bong-du-hoc-nhat-ban
```

**Expected behavior**:
1. Claude trigger skill `share-bai-mastodon`
2. Parse được từ khóa "học bổng du học Nhật Bản" + URL nguồn, dùng tài khoản duy nhất trong `mastodon-accounts.local.json` (không hỏi tài khoản vì chỉ có 1 entry)
3. Verify token qua `verify-token`, không hỏi lại setup vì đã có token hợp lệ
4. Fetch bài gốc, viết 1 toot ngắn (1-2 câu + link nguồn trần cuối toot), KHÔNG viết bài dài ~1000 từ
5. Tải + upload ảnh từ `og:image`, lấy `media_id`
6. `char-count` trả về ≤500, đăng status với `media_ids` chứa ảnh đã upload — KHÔNG dừng hỏi xác nhận trước khi đăng
7. Verify response có `id`/`url`, không có `error`, trước khi báo thành công
8. Output đúng format trong SKILL.md, có link toot thật

**Pass criteria**:
- [ ] Skill triggered đúng tên
- [ ] Không hỏi thừa (tài khoản, setup token) khi đã đủ thông tin
- [ ] Nội dung là 1 toot ngắn (không phải bài dài kiểu WordPress/Tumblr)
- [ ] Đếm ký tự qua `mastodon-json.js char-count`, không tự đếm tay
- [ ] Link nguồn là URL trần, không bọc Markdown/HTML
- [ ] Ảnh được upload qua `upload-media` (multipart bytes thật, không dùng thẳng URL ngoài)
- [ ] Auto-publish không dừng hỏi xác nhận
- [ ] Output cuối có: tài khoản, nội dung toot, từ khóa + link nguồn, link toot đã đăng — verify thật có `url`/không `error`, không suy đoán từ HTTP 200 chung chung

---

## Eval 2: Edge case

**Tên scenario**: Không tìm được ảnh nào từ bài nguồn (không có og:image, không có img trong bài)

**User input**:
```
/share-bai-mastodon lỗi 504 gateway timeout là gì, https://example.com/bai-khong-co-anh
```

**Expected behavior**:
1. Claude trigger skill, Step 3 fetch bài nguồn — không tìm thấy `og:image`/`twitter:image` lẫn `<img>` nào trong content
2. Step 5 detect thiếu ảnh → bỏ qua, KHÔNG chặn pipeline, KHÔNG hỏi user tìm ảnh thay thế
3. `build-status-payload` không có tham số media_id nào, payload không có field `media_ids`
4. Tiếp tục Step 6-7 bình thường, đăng toot thành công không có ảnh
5. Output báo đăng thành công bình thường

**Pass criteria**:
- [ ] Skill không chặn/dừng pipeline chỉ vì thiếu ảnh
- [ ] Không tự ý chèn ảnh khác không liên quan để "cho đủ ảnh"
- [ ] Toot vẫn được đăng thành công, output vẫn trả link toot thật

---

## Eval 3: Anti-pattern

**Tên scenario**: Nội dung soạn ra vượt 500 ký tự (kể cả sau khi tính link = 23 ký tự) — skill phải tự cắt ngắn qua đúng flow, không tự đếm tay hoặc đăng bừa rồi để API lỗi 422

**User input**:
```
/share-bai-mastodon quy trình xin visa du học, https://example.com/quy-trinh-xin-visa-du-hoc-chi-tiet-tat-ca-cac-buoc
```
(giả định Claude ban đầu viết 1 đoạn tóm tắt dài ~600 ký tự thô trước khi tự check)

**Expected behavior**:
1. Claude trigger skill, viết toot nháp ở Step 4
2. Chạy `node scripts/mastodon-json.js char-count <file>` — KHÔNG tự đếm bằng mắt hoặc đoán
3. Kết quả vượt 500 → quay lại cắt ngắn nội dung (giữ câu mở chứa từ khóa + dòng link), KHÔNG giữ nguyên bản dài rồi cứ gọi `create-status` để "xem API có báo lỗi không"
4. Đếm lại sau khi cắt, xác nhận ≤500 rồi mới tiếp tục Step 5-6
5. Nếu vẫn lỡ đăng gặp lỗi 422 ở Step 6 → cắt ngắn thêm, gọi lại đúng 1 lần theo Recovery, không lặp vô hạn

**Pass criteria**:
- [ ] Skill dùng `char-count` để verify trước khi đăng, không tự đếm tay/đoán
- [ ] Phát hiện vượt giới hạn TRƯỚC khi gọi `create-status`, không dựa vào API trả lỗi để biết
- [ ] Cắt ngắn hợp lý (giữ từ khóa + link), không cắt cụt mất nghĩa hoặc mất link
- [ ] Không lặp lại gọi API nhiều lần vô tội vạ khi gặp lỗi 422

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`)
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (fetch/rewrite/upload media/đăng status qua Mastodon API). Fail Eval 2 → bổ sung graceful handling khi thiếu ảnh. Fail Eval 3 → siết lại self-check char-count ở Step 4 trong SKILL.md
