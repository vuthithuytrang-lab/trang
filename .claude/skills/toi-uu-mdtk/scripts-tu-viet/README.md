# Bộ script tự viết (thay cho scripts/ trong file nén chưa nhận được)

Quy trình chèn thẳng vào Google Docs có sẵn:
1. `read_doc` → lưu JSON → `dump.py raw.json` (xem đoạn + vị trí) → `count.py raw.json <vị trí dòng Title> kw...` (đếm).
2. Viết `spec.json` (`{"keywords":[...],"edits":[{"para":<startIndex>,"old":"...","new":"..."}]}`).
3. `build.py raw.json spec.json req.json` → gửi `update_doc` với `requests` + `requiredRevisionId`.
4. `read_doc` lại → `hl.py` (xem chỗ tô vàng), `nl.py` (gỡ tô vàng sót ở dấu xuống dòng), `count.py`.

Bài chưa có Docs: `make_html.py <url> out.html` → `create_file` (text/html) trong thư mục chung, rồi làm như trên.
`BRIEF-tro-ly.md`: lời dặn khi giao trợ lý soạn nháp song song.
