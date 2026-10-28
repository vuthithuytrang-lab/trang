# Công thức: cập nhật bài "Cập nhật giá dầu thế giới hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-dau-the-gioi — đóng gói 28/10/2026 từ 3 lần làm tay
(`cap-nhat-bai-tcb/2026-10-21-…`, `2026-10-23-…`, `2026-10-29-gia-dau-the-gioi/`).
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá dầu thế giới"* — **không hỏi gì thêm**.
Chạy được không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-dau-the-gioi <thư mục ra>` (nhánh chung `*)` của `chay.sh`).

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn (Trang chọn) | Brent = https://vn.tradingview.com/symbols/UKOIL/ ; WTI = https://vn.tradingview.com/symbols/USOIL/ (TVC, USD/thùng) |
| Đọc nguồn | TradingView vẽ số bằng JavaScript → mở bằng Chromium (`lay_gia.js`), đọc ô `.js-symbol-last` (giá), `.js-symbol-change-direction` (thay đổi), `.js-symbol-change-pt` (%), kèm "Tính đến …", "Thị trường mở/đóng cửa", "Đóng cửa ngày hôm trước" để soát |
| Bảng "Loại dầu \| Giá (USD/thùng) \| Thay đổi so với phiên trước" | Dòng nhận theo tên ("Brent"/"WTI"), ô nhận theo dạng: ô chỉ có 1 con số = giá; ô `+1.70 USD (+1.55%)` = thay đổi. Không dựa vào thứ tự cột |
| Cách viết số | Giữ đúng kiểu ô cũ: dấu `.` thập phân, 2 số lẻ (`111.43`), dấu `+`/`-` trước số, `+1.70 USD (+1.55%)`. Lấy **nguyên chữ số TradingView hiển thị**; chỉ khi TradingView hiện khác số chữ số lẻ mới làm tròn → đánh dấu `tinh_toan` (vào mục cần duyệt) |
| Câu văn có "Brent/WTI … X USD/thùng" | Hiện bài không có. Nếu sau này có: đổi giá khi câu chỉ nhắc 1 loại dầu và không phải mức tăng/giảm; còn lại giữ nguyên + cần duyệt |
| Ngày | `dung` của bộ công cụ chung tự đổi mọi ngày sang **ngày hôm sau**. Thiếu nguồn nào → đưa mọi ngày về ngày gốc của bài (không ghi ngày mới cho giá cũ) + cần duyệt |
| Cần duyệt cố định | (1) giá trong phiên, thị trường đang mở nên còn đổi (ghi giờ lấy); (2) sapo nhắc "diễn biến 5 ngày gần đây" nhưng bài không có bảng 5 ngày — giữ nguyên câu chữ (giống 3 lần làm tay) |
| Nguồn hỏng | Giữ giá cũ của dòng đó + cần duyệt "không đọc được TradingView"; không bao giờ tự điền số |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy` (bỏ `ten_file` → script lấy tiêu đề) |

Không có số nào khác trong bài (FAQ/ví dụ tính không nhắc giá dầu) — `tao_sua.py` vẫn dò mọi "… USD/thùng" trong câu văn để
không sót khi bài đổi.

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-dau-the-gioi
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # ngày ghi trong bài: LUÔN là ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json      # mở trình duyệt đọc 2 trang TradingView
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-dau-the-gioi/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.js` | Mở 2 trang TradingView bằng Chromium → `gia.json` (giá, thay đổi, %, đóng cửa hôm trước, giờ, trạng thái thị trường, chữ gốc). Trang nào hỏng → `null` + in "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | Bảng giá + câu văn có giá + xử lý ngày khi thiếu nguồn → `sua.json`; `--kiem` soát lại |
