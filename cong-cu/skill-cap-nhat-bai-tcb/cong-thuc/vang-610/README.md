# Công thức: cập nhật bài "Vàng 610 là vàng gì? Là bao nhiêu K? Giá vàng 610 hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-610-la-vang-gi — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 610"* — **không hỏi gì thêm**.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 610 (14.6K)" (1.000đ/chỉ ×1000), khu vực TP.HCM |
| Tóm tắt đầu bài "Giá vàng 610 (tháng mm/yyyy): Mua vào khoảng … triệu VNĐ/chỉ, bán ra khoảng …" | Tháng này + giữ đúng dạng của bài: 1 mức → giá PNJ; khoảng → thấp nhất – cao nhất (PNJ, SJC 61%). Triệu/chỉ 2 số lẻ, giữ dấu thập phân của bài |
| Mục 3 "Giá mua vào / Giá bán ra: Khoảng … VND/chỉ" | **Giữ dạng "Khoảng X VND/chỉ đến Y VND/chỉ"**: X = thấp nhất, Y = cao nhất của PNJ "Vàng 610 (14.6K)" và SJC "Nữ trang 61%" (webgia.com). Chỉ đọc được 1 nguồn → giữ nguyên dòng, ghi cần duyệt. KHÔNG đổi thành 1 mức, KHÔNG thêm "(theo PNJ)" (Trang dặn 14/10/2026) |
| "tháng mm/yyyy" khác | Tháng này |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)`; trong thư mục Drive chung |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-610
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)   # ngày ghi trong bài: chạy từ 15h trở đi -> ngày hôm sau

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_610.js cap-nhat/gia-610.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-610.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-610.json      # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md`. Lưu kết quả vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-610/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `lay_gia_610.js` | (PNJ + SJC 61% qua webgia) Mở pnj.com.vn bằng Chromium, lấy giá mua/bán vàng 610 → `gia-610.json` |
| `tao_sua.py` | Tóm tắt + mục 3 + tháng → `sua.json`; `--kiem` soát lại |
