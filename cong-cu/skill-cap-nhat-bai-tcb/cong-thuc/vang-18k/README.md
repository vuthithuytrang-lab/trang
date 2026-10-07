# Công thức: cập nhật bài "Vàng 18K là gì? Đặc điểm, cách phân biệt và giá mới nhất" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-18k — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 18K"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| PNJ | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 750 (18K)" (1.000đ/chỉ ×1000), khu vực mặc định TP.HCM |
| SJC (Nữ trang 75%) | https://webgia.com/gia-vang/sjc/ dòng "Nữ trang 75%" (sjc.com.vn chặn máy chủ) |
| DOJI | https://banggia.doji.vn/gold-price dòng "GIÁ NGUYÊN LIỆU 18K" — **chỉ có giá mua**; ô bán giữ "(Liên hệ để cập nhật giá)". Trang DOJI có lúc chậm hiện bảng → script tự chờ + tải lại |
| Ô giá | `9,623,000 VND/chỉ` |
| Câu "mua vào cao nhất … bán ra thấp nhất …" | Tính từ bảng: giá mua lớn nhất, giá bán nhỏ nhất; triệu VND/chỉ 3 số lẻ (`9.879`) |
| FAQ "Vàng 18K bao nhiêu một chỉ?" | = giá bán thấp nhất |
| Ngày "cập nhật đến ngày d/m/yyyy" (2 chỗ) | Đổi sang hôm nay (`7/10/2026`) — thiếu nguồn nào thì KHÔNG đổi ngày |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-18k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_18k.js cap-nhat/gia-18k.json      # mở trình duyệt đọc 3 nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-18k.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-18k.json      # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-18k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia_18k.js` | Mở 3 trang bằng Chromium, lấy giá mua/bán 18K (đ/chỉ) + giờ cập nhật → `gia-18k.json` |
| `tao_sua.py` | Bảng giá + câu tổng kết + FAQ + 2 chỗ ngày → `sua.json`; `--kiem` soát lại |
