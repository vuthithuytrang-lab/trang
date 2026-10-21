# Bảng điều khiển cập nhật bài — Google Sheets "Update"

Sheet: https://docs.google.com/spreadsheets/d/1pG0TA0nwiOkF086eAhbukUJ375oZRfuJpQy4bEUiVck/edit (tab đầu tiên, sheetId 0)
Trang tích ô **"Chạy update"** → lần kiểm tra tự động kế tiếp (mỗi giờ, 8h–18h thứ 2–6) sẽ cập nhật bài đó,
dán link file Docs vào cột ngày hôm nay, rồi bỏ tích. Dựng ngày 07/10/2026.

## Cấu trúc sheet (giữ nguyên, đừng đổi)

| Cột | Nội dung |
|---|---|
| A `STT` | số thứ tự |
| B `URL` | link bài Techcombank |
| C `Bài` | tên ngắn (Giá cafe, Lãi suất…) |
| D `Nguồn tham khảo` | link nguồn, cách nhau bằng xuống dòng hoặc dấu phẩy. Để trống được nếu bài có công thức riêng hoặc là bài lãi suất |
| E `Chạy update` | ô tích |
| F trở đi | mỗi cột một ngày (tiêu đề là ngày, hiện `d/m`), **ngày mới nhất ở cột F**; ô = link file Docs đã chạy |

## Thêm bài mới vào bảng — Claude tự điền, Trang không phải gõ

Trang gửi link bài + nguồn + hướng dẫn **trong chat**. Claude làm bài đó lần đầu, Trang duyệt xong thì Claude:
1. Đóng gói thành công thức `../cong-thuc/<ten-ngan>/` (README chốt nguồn + mọi lựa chọn, `cau-hinh.json`, script tự lấy số nếu cần)
   — làm giống `../cong-thuc/gia-ca-phe/`. Ghi thêm 1 dòng vào bảng "Công thức có sẵn" trong `CLAUDE.md`.
2. **Tự thêm 1 dòng vào sheet** (dòng trống đầu tiên có URL rỗng): A = STT tiếp theo, B = URL bài, C = tên ngắn,
   D = `Công thức: <ten-ngan> – nguồn: <tên các nguồn>`, E giữ ô tích = FALSE. Không động vào các dòng khác.
3. Báo Trang: "đã thêm vào bảng, lần sau chỉ cần tích".
Bài làm lần đầu chưa đóng gói thì **chưa** thêm vào bảng.

## Mỗi lần kiểm tra — các bước

⛔ **Cập nhật, không thay đổi nội dung** (Trang dặn 14/10/2026): chỉ đổi số/ngày/tháng; giữ nguyên câu chữ và dạng câu của bài (khoảng vẫn là khoảng, không thêm "(theo …)", không đổi tên riêng). Không cập nhật được đúng dạng → giữ nguyên + ghi cần duyệt.

1. Đọc `A1:Z200` của tab đầu. Dòng nào ô E = TRUE và B có link → cần chạy. **Không có dòng nào → dừng ngay, không làm gì thêm.**
   ⛔ **Chỉ chạy đúng các dòng được tích** (Trang dặn 20/10/2026, để đỡ tốn token): dòng không tích thì không đọc bài, không lấy nguồn,
   không tạo Docs — kể cả khi Trang nhắn chung chung "update giá".
2. Ngày hôm nay `TZ=Asia/Ho_Chi_Minh`. Tìm cột có tiêu đề = hôm nay (tiêu đề là số ngày kiểu Sheets, xem `formattedValue` dạng `d/m`).
   Chưa có → chèn 1 cột tại F (`insertDimension` COLUMNS start 5 end 6, `inheritFromBefore: false`),
   ghi F1 = số ngày Sheets của hôm nay (`numberValue` = số ngày kể từ 30/12/1899) với `numberFormat` `DATE` pattern `d/m`, in đậm, căn giữa.
3. Với từng dòng cần chạy, chọn cách làm:
   - URL là bài giá cà phê (`gia-ca-phe-hom-nay`) → `../cong-thuc/gia-ca-phe/README.md`.
   - URL là bài giá xăng dầu (`gia-xang-dau-hom-nay`) → `../cong-thuc/gia-xang-dau/README.md`.
   - URL là bài vàng 24K (`vang-24k`) → `../cong-thuc/vang-24k/README.md`.
   - URL là bài vàng 14K (`vang-14k-gia-hom-nay`) → `../cong-thuc/vang-14k/README.md`.
   - URL là bài vàng 18K (`vang-18k`) → `../cong-thuc/vang-18k/README.md`.
   - URL là bài vàng 10K (`vang-10k`) → `../cong-thuc/vang-10k/README.md`.
   - URL là bài 1 chỉ vàng (`1-chi-vang-bao-nhieu-tien`) → `../cong-thuc/1-chi-vang/README.md`.
   - URL là bài vàng 16K (`gia-vang-16k-hom-nay`) → `../cong-thuc/vang-16k/README.md`.
   - URL là bài vàng 610 (`vang-610-la-vang-gi`) → `../cong-thuc/vang-610/README.md`.
   - URL là bài lãi suất `lai-suat-tiet-kiem` (Bài 1) hoặc `cach-tinh-lai-suat-tien-gui-tiet-kiem` (Bài 2) → công cụ lãi suất
     `/home/user/trang/cong-cu/cap-nhat-lai-suat/` (đọc `QUY-TRINH.md`, mục "Cách chạy"; `cap-nhat.py lay` → `dung <ngày>` dựng cả 2 bài).
     Chỉ tạo Docs cho bài có dòng được tích; `bao-cao` lưu ở `cong-cu/cap-nhat-lai-suat/bao-cao/`. Dòng 10–11 trong sheet (thêm 16/10/2026).
   - Dòng 12–22 (thêm 20/10/2026): giá nhôm, lúa gạo, kim loại thế giới, ca cao, điều, đồng, thép, cà phê Đắk Lắk,
     cà phê sàn Luân Đôn (luôn lấy 5 hợp đồng hiển thị đầu tiên), gas, dầu thế giới, tiêu (dòng 23, thêm 21/10/2026) — **chưa có công thức** → quy trình chung `../cap-nhat-bai-tcb/SKILL.md`, nguồn ở cột D. Chạy ổn lần đầu thì đóng gói thành công thức.
   - URL khớp một công thức khác trong `../cong-thuc/` → làm theo công thức đó.
   - Còn lại → quy trình chung `../cap-nhat-bai-tcb/SKILL.md`, nguồn tham khảo lấy ở cột D;
     bài có bảng lãi suất tiết kiệm mà cột D trống → dùng nguồn mặc định VnExpress + Topi như SKILL.md.
   - Cột D trống, không có công thức, không phải bài lãi suất → **không đoán nguồn**: ghi vào ô ngày
     `⚠️ Thiếu nguồn tham khảo – điền cột D rồi tích lại`, bỏ tích, chuyển dòng sau.
   **Ngày ghi trong bài (Trang chốt 21/10/2026, thay quy tắc 15h cũ):** **luôn ghi ngày hôm sau**, không cần biết chạy lúc mấy giờ
   (vd chạy 9h ngày 8/10 → mọi ngày trong bài, tên file Docs, báo cáo đều ghi 9/10). Các công thức đã tự làm việc này
   (`N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)`). Cột ngày trong Sheet vẫn là **ngày chạy** (hôm nay).
   **Không hỏi Trang gì** — chạy theo lịch, không ai trả lời. Mọi lựa chọn mặc định ghi vào báo cáo.
4. Tạo Google Docs đúng như SKILL.md, **`parentId` = `1FXvxKb6TvSsbMeK6I3utnLvRZ4Y_vXxI`** (thư mục "Cập nhật bài Techcombank (Claude)") (Bước 5: `search_files` trùng tên → thêm ` (cập nhật HHhMM)` vào tên, `create_file` text/html,
   tải về chạy `soat` phải ra `dòng lệch: 0`; lệch → trash file vừa tạo, tạo lại).
4b. **Chia sẻ quyền sửa:** đọc tab `Hướng dẫn` ô `B11:B20` (mỗi ô một email) → `share_file` role `writer` cho từng email
   với file Docs vừa tạo. Danh sách email chỉ nằm trong Sheet (repo công khai — KHÔNG chép email vào repo).
5. Ghi vào ô (dòng đó × cột hôm nay) bằng `updateCells`: `userEnteredValue.stringValue` = tên file,
   `textFormatRuns` = `[{"startIndex":0,"format":{"link":{"uri":"<link Docs>"}}}]`
   (fields `userEnteredValue,textFormatRuns`). Ô đã có link của lần chạy trước cùng ngày → ghi đè bằng link mới.
   Lỗi không tạo được file → ghi `⚠️ Lỗi: <lý do ngắn>` thay cho link.
6. Bỏ tích: E của dòng đó = FALSE (`update_values`, giữ nguyên ô tích). **Luôn bỏ tích**, kể cả khi lỗi, để không chạy lặp mỗi giờ.
7. Lưu kết quả vào repo `cap-nhat-bai-tcb/<yyyy-mm-dd>-<tên ngắn>/` (cau-hinh.json, sua.json, bao-cao.md…), commit + push
   lên nhánh `claude/vibrant-keller-rk0i98` (luồng giá vàng đã gộp vào đây ngày 14/10/2026).

Đọc lại sheet sau khi ghi để chắc ô link và ô tích đúng.

## Giới hạn cần nói thật với Trang

- Không bắt được "ngay lúc tích": chạy theo lịch mỗi giờ (8h–18h, thứ 2–6). Muốn chạy ngay → nhắn Claude "chạy bảng update".
- Bài chạy sau 15h: giá thế giới trong bài giá cà phê là giá đang giao dịch (không có "s"), xem công thức giá cà phê.
