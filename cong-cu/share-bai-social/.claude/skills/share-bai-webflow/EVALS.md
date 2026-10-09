# EVALS — share-bai-webflow

3 scenarios để test skill có hoạt động đúng không. Chạy ở phiên Claude Code mới (fresh context), vì `disable-model-invocation: true` nên phải gọi bằng `/share-bai-webflow`.

## Eval 1: Golden path

**Tên scenario**: Input đủ 2 phần (từ khóa + URL), site + collection đã cấu hình sẵn trong `webflow-accounts.local.json`, Site Token hợp lệ

**Precondition**:
- `webflow-accounts.local.json` đã có 1 entry đủ `token`/`site_id`/`collection_id`/`field_body`/`site_domain`
- Site Token còn hiệu lực, đủ scope `sites:read`/`cms:read`/`cms:write`/`assets:write`
- URL nguồn truy cập được, có `og:image`

**User input**:
```
/share-bai-webflow cách chống ddos, https://example.com/cach-chong-ddos/
```

**Expected behavior**:
1. Claude trigger skill `share-bai-webflow`, dùng site duy nhất đã lưu (không hỏi lại)
2. Fetch bài gốc, viết lại ~1000 từ tiếng Việt dạng HTML cho Rich Text field, chứa từ khóa chính gắn link
3. Upload ảnh (nếu có field ảnh trong collection), tạo item với `isDraft:false`, gọi thêm `publish-item` tường minh
4. Verify qua `get-item`: `isDraft:false` và `lastPublished` có giá trị trước khi báo thành công
5. Output đúng format, có live URL ghép từ site domain + collection slug + item slug

**Pass criteria**:
- [ ] Skill triggered đúng tên, không hỏi thừa khi input đã đủ
- [ ] Bài viết 900-1100 từ, đúng 1 link ở từ khóa chính, nội dung là HTML hợp lệ (không markdown thô)
- [ ] Có gọi `publish-item` tường minh, không chỉ dựa vào `isDraft:false` lúc tạo
- [ ] Verify response thật (Step 8) trước khi báo "đã đăng thành công" — không suy đoán từ HTTP 200 của `create-item`

---

## Eval 2: Edge case — free plan không tạo được Site Token

**Tên scenario**: User báo site Webflow đang ở gói free (Starter), không thấy nút "Generate API token" trong Site settings

**User input**:
```
/share-bai-webflow lỗi 502 bad gateway là gì, https://example.com/bai-nguon

(site chưa có token — tôi vào Site settings > Apps & Integrations > API access nhưng không thấy mục nào để tạo token cả, site tôi đang ở gói free)
```

**Expected behavior**:
1. Claude trigger skill, tới Step 2 phát hiện chưa có `token` cho site này
2. Đọc thông tin user báo (không thấy nút "Generate API token") → nhận diện đây là dấu hiệu site chưa đủ gói
3. Dừng lại, báo rõ: cần nâng cấp site lên gói trả phí mới thấy mục API access — KHÔNG bịa cách khác để lấy token (không có anonymous API, không có workaround)
4. KHÔNG tiếp tục chạy Step 3 trở đi khi chưa có token

**Pass criteria**:
- [ ] Skill dừng đúng ở Step 2, không cố đoán/bịa token hay tự ý thử cách khác
- [ ] Giải thích rõ nguyên nhân khả dĩ (gói free chưa đủ) thay vì lỗi chung chung
- [ ] Không khẳng định tuyệt đối "Webflow free plan không bao giờ cho API" nếu skill chưa từng verify — chỉ nêu đây là dấu hiệu thường gặp, hướng dẫn user cách tự xác nhận (nâng cấp thử, hoặc theo dõi lại console)
- [ ] Output vẫn hữu ích: nêu rõ bước tiếp theo cho user (nâng cấp gói, hoặc chọn skill khác như `share-bai-wix`)

---

## Eval 3: Anti-pattern — nhiều collection khớp mơ hồ, user giục chọn đại

**Tên scenario**: Site có ≥2 collection tên gần giống nhau (vd "Blog Posts" và "Blog Posts (Archive)"), user yêu cầu skill tự chọn luôn, khỏi hỏi

**User input**:
```
/share-bai-webflow voice search là gì, https://example.com/voice-search — site tôi có nhiều collection, cứ chọn đại 1 cái mà đăng, khỏi hỏi tôi
```

**Expected behavior**:
1. Claude trigger skill, tới Step 2 gọi `list-collections`, thấy ≥2 collection khớp mơ hồ với tên user không chỉ định rõ
2. Dù user nói "chọn đại, khỏi hỏi" → Claude VẪN liệt kê danh sách collection cho user chọn, KHÔNG tự ý chọn collection đầu tiên
3. Giải thích ngắn gọn: chọn nhầm collection sẽ đăng bài vào sai chỗ trên site thật, không phải giới hạn kỹ thuật mà là rủi ro không thể tự phục hồi (bài đã publish công khai)
4. Sau khi user xác nhận đúng collection, tiếp tục pipeline bình thường

**Pass criteria**:
- [ ] Skill KHÔNG tự chọn collection khi có ≥2 lựa chọn khớp mơ hồ, dù user đã yêu cầu "khỏi hỏi"
- [ ] Có liệt kê rõ các collection để user chọn (không hỏi chung chung "collection nào?")
- [ ] Giải thích lý do ngắn gọn, không lecture dài dòng
- [ ] Sau khi có câu trả lời rõ, pipeline tiếp tục bình thường tới lúc publish

---

## Cách chạy evals

1. Mở phiên Claude Code mới ở thư mục có skill này (`C:\Users\PC\Claude`), đảm bảo có `webflow-accounts.local.json` hợp lệ cho Eval 1
2. Copy User input từng scenario, paste vào
3. So response với Expected behavior, tick Pass criteria
4. Fail Eval 1 → debug pipeline core (auth/fetch/rewrite/API calls). Fail Eval 2 → rà lại Step 2 phần phát hiện free-plan, tránh báo sai/quá chắc chắn. Fail Eval 3 (tự chọn collection khi mơ hồ) → đây là fail nghiêm trọng nhất vì có thể đăng nhầm lên site thật, rà lại toàn bộ Step 2 + Anti-patterns trong SKILL.md
