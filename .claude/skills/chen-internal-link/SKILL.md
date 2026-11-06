---
name: chen-internal-link
description: Chạy trọn luồng chèn internal link (inlink) cho dự án SEO từ một Google Sheet kế hoạch — tải bài từ URL, tạo file Google Docs, chèn đủ anchor đúng nguyên văn (tô vàng + ghi chú đỏ nội dung gốc), soát chữ sau khi tải, ghi link file vào sheet; và xử lý góp ý người duyệt (đọc comment, sửa thẳng file cũ, phản hồi bằng comment, đổi cột duyệt thành "đã sửa"). Dùng khi người dùng nhắc tới chèn internal link, inlink, plan internal links, anchor text, tạo file docs từ URL, chạy nốt bài chưa có file, sửa theo góp ý/comment người duyệt — cho Techcombank, Okamura hay dự án mới, miễn là có link sheet.
---

# Chèn internal link (inlink) — Google Sheet → Google Docs

`<SKILL>` = thư mục chứa file này. Công cụ ở `<SKILL>/scripts/`, tài liệu ở `<SKILL>/references/`, lệnh mẫu cho agent con ở `<SKILL>/prompts/`.
Cần kết nối Google Drive + Google Sheets + Google Docs. Trước khi đụng Google: đọc skill `google-workspace` nếu có.
**Trước khi chèn/sửa bất kỳ bài nào: đọc `<SKILL>/references/BAI-HOC-GOP-Y.md`** — lỗi người duyệt đã bắt, phải tránh.

## 0. Nhận dự án — kiểm đủ, thiếu thì hỏi MỘT lần

| Cần | Mẫu đã chạy |
|---|---|
| Link sheet + tên tab | Techcombank `1KqFQ7DIRFM3vwozccCYZrlsRybOAsieAKm_MVsM2Lnc` tab "Plan internal links - Tổng"; Okamura `1xKnPX-uf7av3FpSocVjy9wKJiNeygrsZLVmdcMC7np8` tab "Trang tính146" |
| Bản đồ cột — **luôn đọc hàng 1 mỗi đợt**, cột hay bị đổi chỗ | TCB: B URL · E Ghi chú · G Chèn XF · I/J anchor+URL tỷ giá · K FILE BLOG · L Chị Lộc duyệt · M KT phản hồi · N Demo nội dung chèn · P–Y 5 cặp anchor/URL. Okamura: E URL · L–Q 3 cặp · R Tình trạng · S File blog |
| Thư mục Drive chứa file | TCB `1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH`; Okamura `1dfPI34Qf5mFI1ALHl5vWU8MUKrqVnwiU` (người dùng tự mở quyền "ai có link – chỉnh sửa" ở cấp thư mục; `share_file` chỉ chia theo email) |
| Quy tắc riêng | TCB: ghi chú "XF Tiết kiệm" → bỏ anchor tỷ giá; cột Demo "Trước/Sau khi chèn" → áp nguyên văn. Okamura: bỏ dòng Tình trạng "Đã done"/"-" |
| Cách lấy bài | TCB: `www.` + UA trình duyệt (thiếu UA → 403), `prep.py` bỏ công cụ quy đổi; Okamura (Wix): `BASE=https://www.okamura.com.vn SEL='[data-hook="post-description"]'`, build.py tự đổi ảnh mờ Wix sang ảnh gốc |

Dự án mới: viết 1 file bổ sung như `<SKILL>/references/BO-SUNG-OKAMURA.md` (site, cách dựng, giọng văn, quy tắc riêng).

## 1. Quy tắc cứng

- Anchor **đúng nguyên văn sheet, phân biệt hoa/thường**; sheet có bao nhiêu anchor chèn đủ bấy nhiêu — trừ khi không có chỗ hợp ngữ cảnh
  thì **để thiếu và ghi lý do** (người duyệt chấp nhận bỏ link hơn câu gượng).
- Không chèn trong 25% đầu thân bài, tiêu đề, các bước hướng dẫn, đoạn định nghĩa. Không 2 link ở đoạn kề nhau nếu tránh được.
- Chữ chèn/sửa tô vàng; ngay sau là đoạn ghi chú đỏ nghiêng **[Nội dung gốc trước khi chèn: …]**; đoạn mới thì **[Đề xuất viết thêm đoạn mới]** đặt trên.
- Giọng tự nhiên theo ngành; **không bịa số liệu/tính năng sản phẩm**; giữ mọi link cũ. Dòng chỉ có URL mà thiếu anchor → không tự nghĩ anchor.
- Sheet: ghi **từng ô**, chỉ ô trống, đối chiếu URL đúng dòng trước khi ghi; ghi đè chỉ khi người dùng đồng ý; không xoá ô.
- Không tạo file mới khi được yêu cầu sửa; không xoá file nếu không được bảo.

## 2. Luồng A — tạo file cho dòng có URL mà cột FILE trống

1. Đọc cột URL + FILE (kết quả lớn: lọc bằng python trên file đã lưu). Lập `rows.json`: `row, B, F, G, I, pairs[[anchor,url]], kw`.
2. Chia lô ~7 bài; mỗi lô 1 thư mục `D`: `cp <SKILL>/scripts/* D/`, `cp <SKILL>/references/example-plan.json D/`, tạo `raw-goc/ raw/ tgt/ out/ final/` + `rows.json`.
   Giao agent con theo `<SKILL>/prompts/worker.txt` (đọc `references/HUONG-DAN-WORKER.md`, file bổ sung dự án, BAI-HOC).
   Lõi: `fetch.sh` → (`prep.py`) → `SP=D/ python3 -I D/build.py` → `map.py` → viết `plan.json` + `targets.json` → `chen.py` →
   `soat.py`, `kiemtra.py`, `linkcu.py` (phải im), `cautruc.py` (phải im).
3. Tải lên: `prompts/upload.txt` (Drive `create_file`, `text/html`, đúng `parentId`). **Agent tải lên gõ lại nội dung nên có thể sót chữ** →
   bắt buộc `prompts/verify.txt`: xuất từng file HTML, `docdiff.py` so từng chữ + `docchk.py` (anchor/URL/vàng), sai thì sửa thẳng bằng `update_doc`.
4. **Tải xong lô nào ghi link lô đó vào sheet ngay** (`prompts/sheet.txt`) — người dùng muốn thấy dần. Ghi chú "Đủ x/N anchor…" vào cột Ghi chú nếu có.
5. Lưu tiến độ + báo cáo đợt (khớp theo URL, không theo số dòng).

## 3. Luồng B — sửa theo góp ý người duyệt (làm 1 bài mẫu cho người dùng duyệt trước khi chạy hàng loạt)

1. Quét comment còn mở: `prompts/scan-gop-y.txt` (Drive `read_file_content` includeComments). Nhiều dòng "cần sửa" cũ đã sửa rồi, chỉ thiếu phản hồi.
2. Note ở ô duyệt bắt đầu bằng **"c …"** ("c sửa chút trong bài", "c wording lại…") = người duyệt đã tự sửa → không đụng.
3. Sửa thẳng file cũ: `prompts/fix-gop-y.txt` — `read_doc` → `update_doc` một lô có `requiredRevisionId`, sửa từ vị trí cao xuống thấp, tính offset UTF-16
   bằng python (`runs.py`, `docs_index.py find`); đoạn trả về phải đúng nguyên văn ghi chú đỏ. Soát lại sau khi sửa.
4. Phản hồi: `insertComment` {range, content} gắn vào câu đã sửa, viết thẳng **"Em đã …"**, không trích lại góp ý.
   **Không trả lời được thẳng dưới luồng comment** (insertCommentReply/replyToComment/insertPost không có); `deleteComment` dùng được.
   Dòng đã sửa trước đó chỉ cần comment: `prompts/reply.txt`.
5. Đổi ô duyệt thành **"đã sửa"** sau khi sửa + comment (đọc lại ô ngay trước khi ghi). Bỏ link → nói rõ "còn x/N anchor".
6. Ghi mỗi nhận xét mới vào `references/gop-y-chi-loc.csv` + cập nhật `BAI-HOC-GOP-Y.md` (nhóm lỗi A–H).

## 4. Lỗi môi trường đã gặp

- File Docs quá lớn làm Drive export lỗi → `read_doc` + `tohtml.py` để soát.
- Một số Docs lưu tiếng Việt dạng tổ hợp (decomposed) → offset lệch 1; luôn `find` trên bản đọc mới.
- Xoá trọn câu có comment → comment bị tách khỏi chữ; giữ ≥1 ký tự nếu muốn comment còn gắn.
- Sheet hay bị sắp xếp lại → khớp theo URL, đọc lại hàng 1 trước khi ghi.
- Lịch tự chạy tạo từ phiên không có kết nối Google sẽ không đọc được Docs/Sheets.

## 5. Tiết kiệm token, báo cáo

- Chỉ đọc cột/đoạn cần; agent con chỉ khi ≥ ~15 bài; agent trả JSON ngắn; không chạy agent soát trùng nếu script soát tại chỗ được.
- Báo cáo người dùng ngắn, lời thường, đánh số; cuối hỏi: có lỗi hiển thị không, có ưng không/muốn chỉnh gì.
