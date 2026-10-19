---
name: inlink-generator
description: "Gắn inlink (liên kết nội bộ) vào bài viết Google Doc: đọc danh sách anchor text và URL đích từ Google Sheet kế hoạch content, tìm đúng vị trí trong bài (không phải heading, không chèn nhầm cụm ngắn vào trong cụm dài như \"iPhone 18\" vào giữa \"iPhone 18 Pro\"), bôi đậm và gắn link ngay trong Google Doc sau khi người dùng xác nhận, rồi xuất kèm đoạn HTML sẵn dán lên WordPress với link mở tab mới. Dùng khi người dùng nói \"gắn inlink cho bài\", \"chèn anchor text\", \"chèn internal link\", \"gắn link nội bộ vào Google Doc\", \"/inlink-generator\"."
---

# Gắn inlink theo anchor text vào Google Doc

Đọc anchor text + URL đích từ Google Sheet kế hoạch content, tìm đúng vị trí trong bài Google Doc theo ngữ cảnh, ghi bold + hyperlink thẳng vào Doc, và xuất HTML (đã có `target="_blank"`) để dán lên WordPress khi đăng.

## Khi nào dùng

- Có một bài viết dạng Google Doc cần gắn link nội bộ theo kế hoạch anchor trong Google Sheet content.
- Cần đoạn HTML sẵn dán WordPress, link mới mở tab mới.
- Cụm từ hay gặp: "gắn inlink cho bài", "chèn anchor text", "chèn internal link", "/inlink-generator".

## Chuẩn bị

Chạy mọi lệnh trong thư mục chứa skill này.

1. Python 3.10 trở lên. Tạo venv và cài thư viện:
   ```bash
   bash scripts/install.sh
   # hoặc thủ công:
   python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
   ```
2. Quy ước lệnh: `python3 ...` trong skill này nghĩa là chạy bằng Python của venv — macOS/Linux `.venv/bin/python`, Windows `.venv/Scripts/python.exe`.
3. Biến môi trường `INLINK_SHEET_ID` (tuỳ chọn): ID Google Sheet kế hoạch content dùng mặc định (`docs.google.com/spreadsheets/d/{ID}/edit`). Không đặt thì truyền `--sheet-id` mỗi lần chạy `find_anchor_candidates.py`.
4. OAuth Google cần CẢ scope Sheets lẫn Docs, nên lần đầu gần như chắc chắn phải đăng nhập mới. Cần OAuth client của người dùng (không nằm trong gói): tạo OAuth client loại Desktop app trên Google Cloud Console, bật Google Sheets API và Google Docs API, thêm email vào Test users; tải `client_secret.json` và đặt vào thư mục `oauth_clients/` trong thư mục skill (code tự tạo thư mục này). Nếu các skill `maps-audit`, `site-auditor`, `cro-setup`, `seo-analyst` được cài cùng thư mục skills, OAuth client và token của chúng được dùng lại. Mẫu cấu trúc: `assets/client_secret.example.json`.
5. Account đăng nhập cần quyền Editor trên Doc và quyền xem Sheet. Callback OAuth chạy ở `http://localhost:8766`.
6. Thư mục runtime do skill tạo: `credentials/` (token), `oauth_clients/`, `runs/<doc_id>/` (file trung gian từng bài).

## Các bước thực hiện

Nguyên tắc: script chỉ làm việc xác định (đọc Sheet, đọc cấu trúc Doc, tìm occurrence hợp lệ theo word-boundary + độ dài anchor); Claude luôn là người quyết định vị trí nào đúng ngữ cảnh và rải đủ xa nhau. Skill ghi vào tài liệu chung của team nên luôn xác nhận với người dùng trước khi ghi thật.

1. **Kiểm tra cài đặt**:
   ```bash
   if [ -x .venv/bin/python ] || [ -x .venv/Scripts/python.exe ]; then echo READY; else echo NEED_SETUP; fi
   ```
   `NEED_SETUP` → báo "Đang cài môi trường Python (khoảng 30 giây)" rồi chạy `bash scripts/install.sh 2>&1 | tail -10`.

2. **Nhận link Google Doc** của bài (dạng `https://docs.google.com/document/d/...`). Nếu chưa đặt `INLINK_SHEET_ID`, hỏi thêm link Google Sheet kế hoạch content.

3. **Kiểm tra credential (Sheets + Docs)**:
   ```bash
   python3 -c "
   from scripts.auth import find_credential
   found = find_credential()
   print('OK:', found[0]) if found else print('MISSING')
   "
   ```
   `MISSING` (thường gặp lần đầu) → hỏi người dùng có đăng nhập Google không, đồng ý thì:
   ```bash
   python3 -c "
   from scripts.auth import auto_oauth
   import json; print(json.dumps(auto_oauth('default'), ensure_ascii=False))
   "
   ```
   Không tìm thấy OAuth client → hướng dẫn đặt `client_secret.json` vào `oauth_clients/`. Môi trường không mở được trình duyệt → dùng cặp `generate_auth_url('default')` / `complete_auth('default', redirect_url)` trong `scripts/auth.py`.

4. **Tìm dòng của bài trong Sheet**:
   ```bash
   python3 scripts/find_anchor_candidates.py --doc-url "<link_doc>" [--sheet-id SHEET_ID] 2>&1
   ```
   - 0 match → hỏi người dùng: chỉ đúng tên tab để dump cả tab (`--full-tab "<tên tab>"`), hoặc tự nhập danh sách anchor + URL ngay trong chat.
   - 1 match → tiếp tục.
   - Nhiều match (bài được nhắc ở nhiều tab) → hỏi tab nào đúng, hoặc dùng cả nếu hợp lý (đọc `header_hint_rows` để phân biệt tab kế hoạch chính với tab chỉ nhắc lại link).

5. **Suy ra anchor → URL và xác nhận**: đọc `header_hint_rows` + `window_rows` theo 3 kiểu trình bày Sheet trong `references/placement-rules.md` (mục 1). Luôn trình bảng mapping cho người dùng xác nhận; anchor map tới 2 URL hoặc cấu trúc mơ hồ thì hỏi thẳng. Lưu danh sách đã xác nhận vào `runs/<doc_id>/anchor_candidates.json` (định dạng `assets/anchor_candidates.example.json`).

6. **Lấy cấu trúc Doc**:
   ```bash
   python3 scripts/fetch_doc_structure.py --doc-id "<link_doc>" --out runs/<doc_id>/doc_structure.json
   ```
   Ghi nhớ `revision_id`. `has_pending_suggestions: true` → cảnh báo: Doc còn suggestion chưa xử lý, index ghi theo bản đã chốt (suggestion coi như bị từ chối) — hỏi người dùng muốn xử lý suggestion trước hay ghi thẳng.

7. **Chạy matcher**:
   ```bash
   python3 scripts/match_anchors.py --doc-structure runs/<doc_id>/doc_structure.json \
     --candidates runs/<doc_id>/anchor_candidates.json --out runs/<doc_id>/match_results.json
   ```
   Đọc `warnings` (vd 1 anchor trỏ 2 URL khác nhau) và báo người dùng trước khi chọn vị trí.

8. **Chọn vị trí đặt link** theo `references/placement-rules.md` (mục 2): `already_present` giữ nguyên; `not_found` luôn hỏi người dùng bỏ qua hay viết đoạn mới (ít nhất 2 câu) qua `scripts/insert_context_paragraph.py`; nhiều occurrence thì chọn câu thực sự nói về đúng thực thể, rải link ở các đoạn khác nhau. Ghi `runs/<doc_id>/placements.json` (định dạng `assets/placements.example.json`), trình bảng preview và **chờ người dùng xác nhận**.

9. **Ghi vào Doc** — chạy thử trước:
   ```bash
   python3 scripts/apply_links.py --doc-id "<link_doc>" --placements runs/<doc_id>/placements.json \
     --expected-revision "<revision_id từ bước 6>" --dry-run
   ```
   Xem `requests` hợp lý rồi bỏ `--dry-run` chạy thật (thêm `--highlight-paragraphs` nếu người dùng muốn bôi vàng đoạn có link để dễ soát). Gặp `doc_changed_since_fetch` → có người vừa sửa Doc, quay lại bước 6.

10. **Xuất HTML sẵn dán WordPress**:
    ```bash
    python3 scripts/export_html.py --doc-structure runs/<doc_id>/doc_structure.json \
      --placements runs/<doc_id>/placements.json
    ```
    Dán giá trị `html` vào một code block cho người dùng copy.

11. **Tóm tắt** theo mẫu ở mục Đầu ra mong muốn. Nếu Sheet có cột kiểu "Bài sau inlink" trỏ tới các Doc khác cũng nên link chéo, gợi ý người dùng chạy skill tiếp cho từng Doc đó (không tự chạy dây chuyền).

## Đầu ra mong muốn

```
GẮN INLINK HOÀN TẤT
  Đã đặt:        N anchor
  Bỏ qua:        M anchor (lý do: ...)
  Đã có sẵn:     K anchor

Google Doc: <doc_url>
HTML sẵn dán WordPress: (code block ở trên)
```

- Trong Google Doc: anchor được bôi đậm + gắn link tại đúng vị trí đã xác nhận; đoạn mới chèn (nếu có) được bôi vàng.
- Code block HTML: link mới dạng `<a href="..." target="_blank" rel="noopener"><strong>anchor</strong></a>`, link/bold có sẵn giữ nguyên.

## Lưu ý

- Không bao giờ ghi vào Doc khi người dùng chưa xác nhận bảng mapping (bước 5) và bảng preview vị trí (bước 8). Nội dung đoạn mới phải được người dùng đọc trước khi chèn.
- Không đặt link trong heading; anchor dài được xử lý trước để cụm ngắn không chiếm chỗ bên trong cụm dài.
- Index Docs API tính theo UTF-16, không phải độ dài chuỗi Python; sau mỗi lần chèn đoạn mới phải lấy lại cấu trúc Doc.
- Giới hạn v1: chỉ quét đoạn văn cấp body — nội dung trong bảng chưa được quét; `export_html.py` không xuất ảnh, bảng, footnote.
- Không script nào tự gọi LLM API.
- Xử lý lỗi thường gặp:

| Lỗi | Cách xử lý |
|---|---|
| `MISSING` credential | Lần đầu chạy — chưa token nào đủ scope Docs. Chạy `auto_oauth` (bước 3). |
| Docs API `SERVICE_DISABLED` / `accessNotConfigured` | Bật Google Docs API trong GCP project của OAuth client. |
| 403 khi đọc Doc | Doc chưa chia sẻ quyền Editor cho account đã đăng nhập. |
| 404 khi đọc Doc | Sai link/ID, hoặc account không có quyền thấy Doc. |
| `doc_changed_since_fetch` | Doc bị sửa giữa lúc lấy cấu trúc và lúc ghi — chạy lại từ bước 6. |
| Chưa có Sheet kế hoạch content | Đặt `INLINK_SHEET_ID` hoặc truyền `--sheet-id`. |
| 0 match trong Sheet | Doc chưa được liệt kê, hoặc Sheet dùng link bài đã đăng thay vì link Doc — hỏi tab hoặc nhập tay. |
| Nhiều anchor `not_found` | Bài chưa đề cập thực thể đó — hỏi người dùng bỏ qua hay viết đoạn mới. |

## Tài nguyên đi kèm

- `references/placement-rules.md` — 3 kiểu trình bày anchor trong Sheet, quy tắc chọn vị trí, xử lý anchor không tìm thấy, chèn đoạn mới (đọc ở bước 5 và 8).
- `scripts/find_anchor_candidates.py` — quét mọi tab của Sheet tìm dòng tham chiếu tới Doc (giá trị và hyperlink), hoặc dump cả 1 tab.
- `scripts/fetch_doc_structure.py` — lấy cấu trúc đoạn văn của Doc (index UTF-16, style, link có sẵn, revision_id, suggestion chưa xử lý).
- `scripts/match_anchors.py` — tìm occurrence hợp lệ của từng anchor (bỏ heading, không chồng lấn, word-boundary).
- `scripts/apply_links.py` — ghi bold + link vào Doc qua batchUpdate, khoá theo revision, có `--dry-run`.
- `scripts/insert_context_paragraph.py` — chèn 1 đoạn văn mới chứa anchor, gắn link và bôi vàng đoạn mới.
- `scripts/export_html.py` — xuất HTML sẵn dán WordPress, link mới mở tab mới.
- `scripts/common.py` — tiện ích dùng chung (tách doc ID, index UTF-16, dàn phẳng Doc, đọc `INLINK_SHEET_ID`).
- `scripts/auth.py` — tìm credential đủ scope Sheets + Docs, tìm OAuth client, đăng nhập tự mở trình duyệt hoặc 2 pha.
- `scripts/install.sh` — tạo `.venv`, cài thư viện, tạo thư mục runtime.
- `scripts/requirements.txt` — thư viện Python cần cài.
- `assets/client_secret.example.json` — mẫu cấu trúc file OAuth client đặt vào `oauth_clients/` (giá trị giả).
- `assets/anchor_candidates.example.json` — mẫu danh sách anchor → URL đã xác nhận.
- `assets/placements.example.json` — mẫu placement đã chọn để ghi vào Doc.
