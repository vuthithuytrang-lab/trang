# Công thức: cập nhật bài "Vàng 16K giá hôm nay: Bảng giá chi tiết cập nhật" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-vang-16k-hom-nay — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 16K"* — **không hỏi gì thêm**.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| SJC – Vàng 680 (16.3K) | https://webgia.com/gia-vang/sjc/ dòng "Nữ trang 68%" (sjc.com.vn chặn máy chủ) |
| Mi Hồng – Vàng 680 (16.3K) | https://www.mihong.vn/gia-vang-trong-nuoc dòng "680" (ô giá kèm phần tăng/giảm → lấy số đầu) |
| PNJ – Vàng 680 (16,3K) | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 680 (16.3K)" (1.000đ/chỉ ×1000) |
| Đơn vị bảng | **triệu VND/lượng** = đ/chỉ × 10 ÷ 1.000.000; dấu chấm thập phân, bỏ số 0 cuối (`86.58`, `83.5`) |
| Khoảng giá tóm tắt (2 chỗ) | Cả 3 hãng: thấp nhất giá mua – cao nhất giá bán, triệu/lượng **1 số lẻ**; theo chỉ ÷10, **2 số lẻ** |
| Ngày dd/mm/yyyy | Công cụ chung tự đổi sang hôm nay |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)`; đặt trong thư mục Drive chung |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-16k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_16k.js cap-nhat/gia-16k.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-16k.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-16k.json      # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md`. Lưu kết quả vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-16k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `lay_gia_16k.js` | Mở 3 trang bằng Chromium, lấy giá mua/bán vàng 680 (đ/chỉ) → `gia-16k.json` |
| `tao_sua.py` | Bảng giá + 2 chỗ khoảng tóm tắt → `sua.json`; `--kiem` soát lại |
