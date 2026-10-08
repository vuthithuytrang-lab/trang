# Công thức: cập nhật bài "Vàng 10K là gì? Bao nhiêu tiền 1 chỉ? Có nên mua không" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-10k — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 10K"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Giá mua vào / Giá bán ra (VND/chỉ) | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 416 (10K)" (1.000đ/chỉ ×1000), khu vực mặc định TP.HCM |
| Cách viết | `4,896,000 VND/chỉ` |
| Ngày "cập nhật đến ngày d/m/yyyy" | Đổi sang hôm nay (`7/10/2026`); không đọc được PNJ thì giữ nguyên cả giá lẫn ngày |
| Lệch có sẵn trong bài (58.4% / 58.3%) | Không sửa, chỉ báo lại |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-10k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)   # ngày ghi trong bài: chạy từ 15h trở đi -> ngày hôm sau

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_10k.js cap-nhat/gia-10k.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-10k.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-10k.json      # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-10k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia_10k.js` | Mở pnj.com.vn bằng Chromium, lấy giá mua/bán vàng 10K → `gia-10k.json` |
| `tao_sua.py` | 2 dòng giá + ngày → `sua.json`; `--kiem` soát lại |
