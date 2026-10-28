---
name: theo-doi-publish
description: Cài và chạy bảng theo dõi ngày publish các trang techcombank.com trên Google Sheet — mỗi ngày một cặp cột "dd/mm/yyyy | Kiểm tra lúc", ô chưa cập nhật tự tô hồng, tự kiểm lúc 19:00 hằng ngày và báo kết quả. Dùng skill này khi người dùng nhờ "cài theo dõi publish", "tạo file check publish", "check publish", "update publish", "kiểm tra ngày publish", thêm/bớt link cần theo dõi, đổi giờ kiểm, hoặc dừng/bật lại lịch kiểm — kể cả khi họ không gọi đúng tên skill.
---

# Theo dõi ngày publish (techcombank.com)

Skill này làm lại đúng quy trình team SEO đang chạy: một Google Sheet ghi ngày đang hiển thị
của từng URL, mỗi ngày thêm một cặp cột, ô nào chưa sang ngày mới thì tự tô hồng, và một lịch
tự động kiểm lúc 19:00 mỗi tối.

**Người dùng thường là dân SEO/Marketing, không rành kỹ thuật.** Nói bằng lời thường, không
thuật ngữ (buộc phải dùng thì giải nghĩa trong ngoặc). Tự làm hết phần kỹ thuật, chỉ nhờ họ
những việc chắc chắn mình không làm được (bấm nút kết nối, tạo file trống, chốt quyết định).
Không bịa kết quả: trang nào không đọc được thì ghi "Lỗi"/"Không có ngày" và nói thật.

Các script nằm trong thư mục `scripts/` cạnh file này. Tìm đường dẫn một lần:
```bash
SK=$(dirname "$(find / -path '*theo-doi-publish/scripts/cap_nhat_sheet.py' -not -path '*/proc/*' 2>/dev/null | head -1)")
pip install -q requests beautifulsoup4
```

---

## A. Cài lần đầu — "cài theo dõi publish", "tạo file check publish"

Làm lần lượt, mỗi bước cần người dùng thao tác thì đưa **một bước**, chờ xong mới sang bước sau.

### A1. Kiểm tra kết nối Google Sheets
Tìm công cụ Google Sheets (ToolSearch từ khóa "Google Sheets"). Không có, hoặc gọi thử báo
`Permission denied` → nhờ người dùng: vào https://claude.ai/customize/connectors → **Google Sheets**
→ **Connect**, đăng nhập đúng tài khoản công ty (tài khoản sẽ sở hữu file theo dõi). Xong mới đi tiếp.

### A2. Xin file sheet và danh sách link
Hỏi gọn trong một tin:
1. **File sheet:** nhờ họ mở https://sheets.new (tạo file trống, đặt tên tùy ý, ví dụ "Theo dõi publish TCB")
   rồi dán đường link vào chat. Nếu đã có sẵn file muốn dùng thì dán link file đó — skill sẽ dùng
   **tab đầu tiên**, nên tab đó phải trống hoặc đã đúng bố cục `STT | URL | ...`.
2. **Danh sách URL** cần theo dõi (dán mỗi dòng một link). Không có thì để họ tự điền cột B sau.
3. **Giờ kiểm tự động** — mặc định **19:00** hằng ngày. Chỉ hỏi lại nếu họ nhắc giờ khác.

Lấy `spreadsheetId` từ link (đoạn giữa `/d/` và `/edit`). Gọi `get_spreadsheet` (fields
`sheets.properties.sheetId`, `sheets.properties.title`, `sheets.properties.gridProperties.columnCount`)
→ lấy `sheetId` và tên của tab đầu.

### A3. Định dạng sheet
```bash
python3 "$SK/cai_sheet.py" <sheetId> > cai-dat.json
```
Đưa mảng `requests` trong `cai-dat.json` vào `update_spreadsheet`. Việc này đặt ngôn ngữ Việt Nam + giờ
Việt Nam cho file, cố định hàng tiêu đề + 2 cột đầu, tô màu tiêu đề, cài luật **tô hồng** (ngày nhỏ hơn
ngày ở tiêu đề) và luật **tô xanh** (URL trùng).

⚠️ Mẹo đã gặp: nếu `update_spreadsheet` báo lỗi đọc dữ liệu (JSON), gửi **tách nhỏ** thành vài lần,
mỗi lần 2–5 yêu cầu. Luật tô màu dùng `"format": {"backgroundColor": ...}` (đã đúng sẵn trong script).

### A4. Ghi tiêu đề và danh sách URL
`update_values` vùng `<tab>!A1:B<n+1>`: hàng 1 `["STT","URL"]`, các hàng sau `["1","https://..."]`...
Giữ nguyên link người dùng đưa, không tự sửa, không tự thêm.

### A5. Kiểm lần đầu
Chạy mục **B** với `--ep` để có ngay cột đầu tiên.

### A6. Cài lịch tự động
Dùng `create_trigger` (công cụ claude-code-remote; tìm bằng ToolSearch "create_trigger"):
- `name`: `Theo dõi publish – 19:00 hằng ngày`
- `cron_expression`: `CRON_TZ=Asia/Ho_Chi_Minh 0 19 * * *` (đổi giờ nếu người dùng chọn giờ khác)
- **Không** đặt `create_new_session_on_fire` — lịch phải bắn vào **chính phiên này**, vì phiên này
  đang có kết nối Google Sheets (phiên mới mở ra không mang theo kết nối).
- `initiation`: `human_request`
- `prompt` (thay các chỗ <...>):
```
[Lịch tự động theo dõi publish] Dùng skill theo-doi-publish, làm mục B (kiểm theo lịch, KHÔNG thêm --ep).
spreadsheetId <ID>, tab "<tên tab>" (sheetId <số>). Không hỏi lại, không tạo file mới.
Xong trả lời người dùng 1–2 dòng: tom_tat, nêu STT các trang chưa cập nhật nếu có.
Sheets báo "Permission denied" → nhờ người dùng kết nối lại Google Sheets (claude.ai/customize/connectors).
```
Nếu không có công cụ `create_trigger` (đang không chạy trên Claude Code bản web), nói thật là
chưa cài được lịch tự động ở đây; người dùng vẫn nhắn "check publish" để kiểm tay được.

### A7. Báo lại
Tóm tắt bằng lời thường, đánh số các việc đã làm; gửi link sheet; dặn:
- Muốn theo dõi thêm link: **điền vào dòng trống tiếp theo ở cột B** — lần kiểm sau tự có.
- Muốn kiểm ngay: nhắn "check publish".
- Muốn dừng: nhắn "dừng update publish".
Rồi hỏi 2 câu: (a) mở sheet có thấy lỗi hiển thị gì không, (b) có ưng không, muốn chỉnh gì.

---

## B. Kiểm và ghi kết quả — "check publish", "update publish", lịch tự động

1. `get_spreadsheet` lấy `columnCount` của tab; `get_values` vùng `<tab>!A1:ZZ` (**toàn bộ** bảng, giữ
   nguyên thứ tự hàng).
2. Ghi `dau-vao.json` (thư mục nháp):
   `{"bang": <giá trị vừa đọc>, "column_count": <số cột>, "sheet_id": <sheetId>, "tab": "<tên tab>"}`
3. Chạy:
   - Người dùng tự nhờ kiểm: `python3 "$SK/cap_nhat_sheet.py" dau-vao.json --ep > ket-qua.json`
   - Lịch tự động: bỏ `--ep`.
   - Người dùng muốn so với một ngày cụ thể: thêm `--ngay dd/mm/yyyy`.
4. `bo_qua` = true → không ghi gì, báo `tom_tat`.
   Ngược lại: `requests` không rỗng → `update_spreadsheet` với đúng `requests` đó trước; rồi `update_values`
   với `range` + `values` (giữ dấu `'` đầu chuỗi để sheet không tự đổi kiểu ngày); rồi `get_values` lại
   vài dòng vừa ghi để chắc đã lên.
5. Báo người dùng: `tom_tat` + STT và link các trang chưa cập nhật / lỗi.
   Trang lỗi mạng: script đã tự thử lại; vẫn lỗi thì thử lại riêng trang đó một lần nữa trước khi báo.

**Quy tắc ngày (giờ Việt Nam):** từ **13:00** trở đi, so với **NGÀY MAI** và ghi vào cặp cột ngày mai
(bài phải chuyển sang ngày hôm sau mới tính Done; chưa chuyển là chậm). Trước 13:00 so với hôm nay.

**Cách đọc ngày:**
- Link có `/thong-tin/blog/`: đọc khung `div.article-header-body--date` dưới tiêu đề bài (dạng ISO).
- Link khác: đọc ngày `dd/mm/yyyy` trong thẻ `<title>`; trang chỉ ghi `(dd/mm)` (như trang tỷ giá) thì lấy năm gần nhất.
- Đọc không ra → "Không có ngày"; không vào được → "Lỗi: <mã>". Không bao giờ tự đoán ngày.

---

## C. Việc khác

| Người dùng nói | Làm |
|---|---|
| Thêm link | Họ tự điền cột B là đủ. Nếu họ dán link vào chat: ghi nối vào dòng trống tiếp theo của cột A–B, rồi hỏi có muốn kiểm ngay không. |
| Đổi giờ kiểm | `update_trigger` đổi `cron_expression` (giữ `CRON_TZ=Asia/Ho_Chi_Minh`). |
| Dừng | `update_trigger` `enabled=false` (tắt, **không xóa**, để bật lại được). |
| Bật lại | `update_trigger` `enabled=true`, rồi chạy mục B với `--ep` cho có số liệu ngay. |
| Tự kiểm bằng Screaming Frog | Xem `SCREAMING-FROG.md` trong thư mục skill. |

Không tìm thấy ID lịch → `list_triggers`, chọn lịch có tên "Theo dõi publish".
