# Quy tắc suy ra anchor từ Sheet và chọn vị trí đặt link

Đọc file này ở bước 4 (suy ra danh sách anchor → URL từ Sheet) và bước 7 (chọn vị trí đặt link, xử lý anchor không tìm thấy) trong SKILL.md.

## 1. Suy ra anchor → URL từ Sheet kế hoạch content

Đọc `header_hint_rows` + `window_rows` của match đã chọn (output `scripts/find_anchor_candidates.py`) để suy ra danh sách `[{anchor_text, target_url}]` cho đúng dòng bài này. Sheet kế hoạch content có ít nhất 3 kiểu trình bày đã gặp — không giả định trước kiểu nào:

1. Cột HEADER chính là URL đích (vd header `https://example.com/iphone-18-pro-256gb.html`), giá trị cell dưới header đó ở đúng dòng bài = anchor text cần dùng cho URL đó.
2. Có dòng "legend" phía trên bảng dạng `Anchor: https://...` — mọi cột `Anchor N` trong bảng đó đều trỏ về URL trong legend.
3. Có sẵn cặp cột `Anchor N` / `URL N` liền kề, đọc trực tiếp.

Bỏ qua các cột rõ ràng thuộc quy trình audit khác, không phải nguồn để gắn link (vd cột "Anchor text 1..4" lặp lại + "Kết quả check inlink" nếu xuất hiện cùng lúc với cột header-là-URL ở trên — đó là dữ liệu của một audit thủ công riêng, không phải input cho skill này).

Luôn trình bảng mapping suy ra được cho người dùng xác nhận trước khi đụng tới Doc (không chỉ khi không chắc — Sheet đủ rối để sai âm thầm là rủi ro thật). Nếu 1 `anchor_text` map tới 2 `target_url` khác nhau, hoặc cấu trúc thực sự mơ hồ, hỏi thẳng người dùng thay vì tự đoán.

Định dạng file lưu: `assets/anchor_candidates.example.json`.

## 2. Chọn vị trí đặt link (Claude quyết định)

Với mỗi anchor trong `match_results.json`:

### `already_present: true`
Giữ nguyên, không làm gì thêm (đã có link đúng trong bài).

### `not_found: true`
Hai lựa chọn, **luôn hỏi người dùng chọn cái nào** (không tự quyết):

1. Bỏ qua anchor đó (an toàn nhất, mặc định).
2. Viết 1 đoạn văn MỚI, ngắn (**tối thiểu 2 câu**, không phải câu nhồi từ khoá vô nghĩa), tự nhiên nhắc tới đúng anchor text, rồi gắn link vào anchor trong CHÍNH đoạn mới đó bằng `scripts/insert_context_paragraph.py`.
   - Script này **luôn tự bôi vàng toàn bộ đoạn mới chèn** (mặc định, không cần cờ) — vì đây là nội dung mới, biên tập viên cần thấy ngay để soát trước khi đăng. Khác `apply_links.py`, nơi bôi vàng chỉ tuỳ chọn qua `--highlight-paragraphs` vì đó là định dạng lại chữ có sẵn.
   - Mỗi lần gọi chỉ xử lý **1 anchor** (`--candidates` là file JSON chứa đúng anchor đó).
   - Nhiều anchor not_found cùng lúc: **chèn ở nhiều vị trí khác nhau, cách xa nhau trong bài** (vd khoảng 25% / 50% / 75% chiều dài bài), KHÔNG dồn nhiều đoạn mới liền kề — vẫn phải theo rule "rải rác, không quá gần nhau" dù là nội dung mới hay có sẵn.
   - Sau mỗi lần chèn phải **chạy lại `scripts/fetch_doc_structure.py`** trước khi tính vị trí chèn tiếp theo (index dịch chuyển sau insertText) — tìm lại đoạn đích bằng cách khớp nội dung text, không dùng lại index cũ; lấy `revision_id` mới cho `--expected-revision`.
   - Luôn cho người dùng xem trước câu dự kiến viết + vị trí chèn, xác nhận rồi mới chạy thật. `--dry-run` không thay được bước này — người dùng phải đọc chính nội dung câu chữ trước khi ghi.
   - Điểm chèn (`--insert-index`) là `start_index` của một đoạn văn NORMAL_TEXT hiện có gần chủ đề nhất. Script tự ép đoạn mới về NORMAL_TEXT (`updateParagraphStyle`), nên chèn ngay trước một heading vẫn an toàn.

   Lệnh mẫu:
   ```bash
   python3 scripts/insert_context_paragraph.py --doc-id "<link_doc>" \
     --insert-index START_INDEX --text "Đoạn văn mới ít nhất 2 câu có chứa anchor." \
     --candidates runs/<doc_id>/insert_candidate.json \
     --expected-revision "<revision_id>" --dry-run
   ```

### Có nhiều `occurrences`
- Đọc `context_before` / `context_after` từng occurrence, chọn cái mà câu/đoạn xung quanh **thực sự đang nói về đúng thực thể đó** (không chọn occurrence nằm trong câu chỉ lướt qua hoặc so sánh với thứ khác).
- Vừa chọn cho anchor này vừa nhìn lại các anchor đã chọn trước — ưu tiên đoạn văn khác nhau, tránh 2 link rơi vào cùng một đoạn hoặc 2 đoạn liên tiếp trừ khi không còn lựa chọn nào khác. Cờ `paragraph_has_existing_link` cũng là gợi ý nên tránh đoạn đó.

### Ghi placements
Copy nguyên occurrence đã chọn (giữ đủ `paragraph_index`, `text_start`, `text_end`, `start_index`, `end_index`, `matched_text`) vào `runs/<doc_id>/placements.json`, thêm `anchor_text` + `target_url`. Định dạng: `assets/placements.example.json`.

### Bảng preview trình người dùng trước khi ghi

| Anchor | URL đích | Trích đoạn quanh vị trí đặt | Trạng thái |
|---|---|---|---|
| ... | ... | "...{context_before}**[anchor]**{context_after}..." | Đặt / Bỏ qua + lý do |
