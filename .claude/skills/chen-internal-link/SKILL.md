---
name: chen-internal-link
description: Chạy trọn luồng "Plan internal links" cho một dự án SEO — đọc sheet kế hoạch, tạo file Google Docs từ URL bài, chèn anchor/internal link đúng quy tắc, tô vàng + ghi chú đỏ, ghi link file và ghi chú về sheet, soát lại; và luồng xử lý góp ý duyệt (đọc comment, sửa thẳng file cũ, phản hồi vào cột phản hồi). Dùng khi Trang nhắc tới chèn internal link, plan internal links, anchor text, tạo file docs từ URL, chạy nốt các bài chưa có file, hoặc sửa theo góp ý người duyệt — cho Techcombank hay dự án mới khác, miễn là Trang đưa đủ tài liệu.
---

# Chèn internal link — luồng dùng lại cho mọi dự án

Mã nguồn và mẫu lệnh: `cong-cu/tao-docs-tu-url/` (README.md = quy trình chi tiết, chen.py/kiemtra.py/... = công cụ),
`cong-cu/tao-docs-tu-url/duyet/` (sửa theo góp ý). Dự án Techcombank là bản mẫu: `plan-internal-links/` (tien-do.csv, bao-cao.md).
Trước khi đụng Google Docs/Sheets: đọc skill `google-workspace`.

## 0. Nhận dự án mới — kiểm đủ tài liệu, thiếu thì hỏi MỘT lần

| Cần | Ví dụ (Techcombank) |
|---|---|
| Link sheet + tên tab | `1KqFQ7…MsM2Lnc`, tab "Plan internal links - Tổng" |
| Bản đồ cột (đọc hàng 1 rồi xác nhận) | B URL · E Ghi chú · I/J anchor + URL tỷ giá · K FILE BLOG · L người duyệt · M phản hồi · P–Y cặp anchor/URL |
| Thư mục Drive chứa file | "Plan internal links - File blog" |
| Quy tắc riêng của dự án | VD "XF Tiết kiệm" thì bỏ anchor tỷ giá |
| Cách lấy bài gốc | Techcombank: `www.` + User-Agent trình duyệt |

Cột của sheet hay bị đổi chỗ → **luôn đọc hàng 1 trước mỗi đợt**, không tin số cột cũ. Ghi dự án mới thành một mục trong
`cong-cu/tao-docs-tu-url/README.md` (sheet, cột, thư mục, quy tắc riêng).

## 1. Quy tắc cứng (mọi dự án)

- Anchor **đúng nguyên văn sheet, phân biệt hoa/thường**. Sheet có bao nhiêu anchor thì chèn đủ bấy nhiêu.
- Không chèn trong 25% đầu thân bài, trong tiêu đề, các bước hướng dẫn, đoạn định nghĩa.
- Chữ chèn/sửa tô vàng; ngay sau là ghi chú đỏ nghiêng **[Nội dung gốc trước khi chèn: …]**; đoạn mới thì **[Đề xuất viết thêm đoạn mới]**.
- Giọng văn tự nhiên theo ngành, **không bịa số liệu**, không thêm thông tin chưa có nguồn. Giữ mọi link cũ của bài.
- Dòng thiếu anchor (chỉ có URL) → **không tự nghĩ anchor**, để trống, báo Trang.
- Sheet: ghi **từng ô một**, chỉ ô trống; ghi đè chỉ khi Trang đồng ý; không bao giờ xoá ô. Trước khi ghi, đối chiếu URL cột B đúng dòng.
- Không in/ghi/commit chìa khóa, token (repo public).

## 2. Luồng A — tạo file cho dòng chưa có file

1. Đọc cột URL + cột FILE (jq/python trên file kết quả đã lưu, đừng in cả cột ra màn hình) → danh sách dòng có URL mà FILE trống.
2. Theo README mục "Plan internal links": tải bài → `prep.py` → `build.py` → `plan.json` → `chen.py` → soát `soat.py`,
   `kiemtra.py`, `linkcu.py`, `cautruc.py` → tải lên Drive (`create_file` text/html, đúng thư mục) → `verify.py`.
3. **Agent tải lên gõ lại nội dung nên có thể sót chữ** → sau khi tải, xuất từng file và so từng chữ với bản gốc
   (`duyet/docdiff.py` + `duyet/docchk.py`), sai thì sửa thẳng trong file. Tải xong lô nào gắn link lô đó vào sheet ngay (Trang muốn thấy dần).
4. Ghi link file vào cột FILE, ghi chú "Đủ x/N anchor…" vào cột Ghi chú (ô trống).
5. Thêm dòng vào `tien-do.csv` (khớp theo URL, không theo số dòng — sheet hay bị sắp xếp lại), thêm mục "Đợt N" vào `bao-cao.md`, commit + push.

## 3. Luồng B — sửa theo góp ý người duyệt

**⛔ Tạm dừng từ 28/10/2026:** Trang báo luồng đang có vấn đề → **không tự vào sửa các dòng người duyệt ghi "cần sửa"**.
Chỉ chạy lại khi Trang bảo rõ ràng. Khi được mở lại:

- Đọc cột duyệt + comment trong file (Drive `read_file_content`, `includeComments: true`).
- Note bắt đầu bằng **"c …"** ("c sửa chút trong bài", "c wording lại…") = **người duyệt đã tự sửa** → không đụng file, không ghi phản hồi.
- Sửa **thẳng file cũ** (Docs `update_doc`, có `requiredRevisionId`, sửa từ vị trí cao xuống thấp). Không tạo file mới, không xoá file.
- Giữ ít nhất 1 ký tự của đoạn có comment, nếu không comment bị tách khỏi chữ.
- Soát mỗi file: `duyet/docchk.py` (anchor/URL/tô vàng) + `duyet/docdiff.py` (chỉ đổi đúng chỗ định đổi). File quá lớn làm sập Drive export → `read_doc` + `duyet/tohtml.py`.
- Phản hồi cột phản hồi bằng tiếng Việt, xưng "Em", gửi người duyệt; chỉ ghi ô trống. Mẫu lệnh: `duyet/PROMPT-*.txt` (thay id sheet/tên cột cho dự án mới).
- Đọc lại cột duyệt ngay trước khi ghi — người duyệt có thể đã đổi trạng thái trong lúc mình làm.

## 4. Tiết kiệm token (Trang yêu cầu 28/10/2026)

- Đọc sheet theo **cột cần dùng**, kết quả lớn thì xử lý bằng jq/python trên file đã lưu; không đọc lại thứ đã có.
- Agent con chỉ khi việc nhiều và song song được (≥ ~15 bài); mỗi agent nhận lệnh từ file mẫu, trả JSON ngắn.
- Không chạy agent soát trùng nếu `docchk`/`kiemtra` đã chạy được tại chỗ.
- Báo cáo cho Trang ngắn, lời thường, đánh số; cuối luôn hỏi 2 câu (lỗi hiển thị? ưng chưa/chỉnh gì?) + nhắc Cmd + R.
