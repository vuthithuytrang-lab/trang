# Công thức: cập nhật bài "Vàng 24K là gì? Có phải vàng 9999? Giá mới nhất" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-24k — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 24K"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Dòng trong bài | Lấy giá ở đâu (sản phẩm) |
|---|---|
| SJC – Vàng miếng 999.9 | https://webgia.com/gia-vang/sjc/ — "Vàng SJC 1L, 10L, 1KG" (Hồ Chí Minh). sjc.com.vn chặn máy chủ (Cloudflare) |
| PNJ – Nhẫn trơn 999.9 | https://www.pnj.com.vn/site/gia-vang — "Nhẫn Trơn PNJ 999.9" (khu vực mặc định TP.HCM, đơn vị 1.000đ/chỉ ×1000) |
| DOJI – Vàng miếng 24K | https://banggia.doji.vn/gold-price — "VÀNG MIẾNG SJC" (DOJI không có sản phẩm tên "vàng miếng 24K"; nghìn đ/chỉ ×1000) |
| Bảo Tín Minh Châu – Vàng nhẫn Rồng Thăng Long 999.9 | https://webgia.com/gia-vang/bao-tin-minh-chau/ — "Nhẫn tròn trơn 999.9 (24k)" nhóm VRTL. btmc.vn không vào được từ máy chủ |
| Đối chiếu khi nghi ngờ | giavang.org (đơn vị nghìn đ/lượng = 10 chỉ) |
| Ngày "cập nhật đến ngày d/m/yyyy" (2 chỗ) | Đổi sang hôm nay, viết không số 0 đầu (vd `7/10/2026`) |
| Cách viết số | `14,000,000` VND/chỉ |
| Không dùng | Đoạn chữ "giá vàng sáng nay lúc 8:35" trên topi.vn (cũ, lệch giá trưa/chiều) |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-24k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_vang.js cap-nhat/gia-vang.json   # mở trình duyệt đọc 4 nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-vang.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-vang.json     # phải "khớp hết"
```

Nguồn nào `KHÔNG ĐỌC ĐƯỢC` → dòng đó giữ giá cũ (tao_sua tự ghi cần duyệt) — **khi đó KHÔNG đổi ngày
"cập nhật đến ngày"** (xóa 2 mục ngày khỏi `sua.json`) để bài không ghi ngày mới cho giá cũ; báo Trang chụp màn hình.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-24k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia_vang.js` | Mở 4 trang bằng Chromium, lấy giá mua/bán (VND/chỉ) + giờ cập nhật → `gia-vang.json` |
| `tao_sua.py` | So bảng giá + 2 chỗ ngày trong bài → `sua.json`; `--kiem` soát lại |
