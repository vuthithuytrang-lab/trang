# Công thức: cập nhật bài "Vàng 14K giá hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/vang-14k-gia-hom-nay — làm lần đầu 07/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài vàng 14K"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| SJC – Nữ trang 58.3% | https://webgia.com/gia-vang/sjc/ dòng "Nữ trang 58,3%" (sjc.com.vn chặn máy chủ) |
| PNJ – Vàng 585 (14K) | https://www.pnj.com.vn/site/gia-vang dòng "Vàng 585 (14K)" (1.000đ/chỉ) |
| Huy Thanh – Vàng 585 (14K) | https://huythanhjewelry.vn/gia-vang-hom-nay dòng "Giá nguyên liệu 14K" (trang chỉ có dòng 14K này) |
| Đơn vị trong bảng | **triệu VND/lượng** = giá đ/chỉ × 10 ÷ 1.000.000; dấu chấm thập phân, bỏ số 0 cuối (`72.853`, `72.88`, `85`) |
| Khoảng giá tóm tắt (2 đoạn) | Tính trên **SJC + PNJ** như bài gốc: thấp nhất giá mua – cao nhất giá bán; theo chỉ = ÷10, 2 số lẻ; chênh lệch mua–bán từng hãng, 1 số lẻ |
| Đoạn "1.1. Xu hướng giá vàng 14K gần đây" | Không có nguồn lịch sử giá → **giữ nguyên số và ngày gốc** (công cụ chung tự đổi ngày → trả lại ngày gốc, bỏ tô vàng), ghi cần duyệt |
| Mục 2 – ví dụ nhẫn 1.2 chỉ (8,390,000 đ/chỉ…) | Phép tính minh họa → không tự sửa, ghi cần duyệt kèm giá bán PNJ hôm nay |
| Ngày dd/mm/yyyy khác trong bài | Công cụ chung tự đổi sang hôm nay |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/vang-14k
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia_14k.js cap-nhat/gia-14k.json     # mở trình duyệt đọc 3 nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia-14k.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $CT/tao_sua.py --xem - --gia - --bo-to-ngay-xu-huong cap-nhat/tam/bai1.min.html   # bỏ tô vàng ngày gốc đoạn Xu hướng
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia-14k.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Nguồn nào `KHÔNG ĐỌC ĐƯỢC` → dòng đó giữ giá cũ (tự ghi cần duyệt); thiếu SJC hoặc PNJ → khoảng tóm tắt giữ nguyên.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs từ `bai1.min.html`, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-vang-14k/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia_14k.js` | Mở 3 trang bằng Chromium, lấy giá mua/bán 14K (đ/chỉ) + giờ cập nhật → `gia-14k.json` |
| `tao_sua.py` | Bảng giá + khoảng tóm tắt + trả lại ngày đoạn Xu hướng → `sua.json`; `--kiem` soát lại; `--bo-to-ngay-xu-huong` bỏ tô vàng ngày gốc |
