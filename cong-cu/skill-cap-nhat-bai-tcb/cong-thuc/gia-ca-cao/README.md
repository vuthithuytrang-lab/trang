# Công thức: cập nhật bài "Giá ca cao hôm nay: Biến động thị trường và góc nhìn cho nhà đầu tư" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-cao — đóng gói 28/10/2026 từ 3 lần làm tay (21/10, 23/10, 29/10/2026).
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá ca cao"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, tự chạy được bằng `cong-cu/tu-dong/chay.sh gia-ca-cao <thư mục>` (khung chung).

## 1. Nguồn

| Phần trong bài | Nguồn | Ghi chú |
|---|---|---|
| Bảng giá trong nước (6 dòng) | https://banggianongsan.com/bang-gia-cacao-hom-nay/ — bảng "Nông sản / Giá cũ / Giá mới / Chênh lệch" | Trang chọn |
| Bảng New York (CCZ26 … CCU28) | **Trang dữ liệu của chính sàn ICE**: https://www.ice.com/products/7/Cocoa-Futures/data | Thay Barchart CCZ26 (Trang chọn) — Barchart chặn máy chủ (403, "The request could not be satisfied") từ 28/10/2026 |
| Bảng London (CAZ26 … CAU28) | **Trang dữ liệu của sàn ICE**: https://www.ice.com/products/37089076/London-Cocoa-Futures/data | Thay Barchart CAZ26, cùng lý do |

- ICE là sàn niêm yết chính các hợp đồng này (Barchart cũng lấy lại số của ICE). Trang ICE mở bình thường bằng trình duyệt;
  khi mở, trang tự tải danh sách hợp đồng (`marketdata/api/productguide/charting/contract-data`) — `lay_gia.js` chỉ ghi lại
  đúng dữ liệu đó. Không vượt tường chặn, không giả danh.
- Số của ICE là **giá khớp gần nhất (LAST), trễ tối thiểu 15 phút**, kèm **% thay đổi so với phiên trước** — không phải giá chốt phiên
  (Barchart lần làm tay dùng giá chốt). Mỗi lần chạy đều có 1 dòng cần duyệt nói rõ giờ khớp của số.
- ICE **không liệt kê CCU28 (9/2028)** và CCN28 (7/2028) thường **chưa có giao dịch** → 2 dòng này giữ nguyên + cần duyệt
  (cập nhật tay nếu cần). Bảng London ICE có đủ 10 hợp đồng.
- Chưa thử được lúc sáng sớm giờ VN (sàn đóng cửa): nếu ICE xoá giá ngày mới (giá = trống) thì các dòng đó tự giữ nguyên + cần duyệt.

## 2. Đã chốt (cách ghép số vào bài)

| Chỗ trong bài | Lấy từ đâu | Cách viết |
|---|---|---|
| Trong nước, cột "Giá hiện tại" | banggianongsan cột **Giá cũ** | `70,000 - 79,000` (nguồn `70.000 – 79.000`) |
| Trong nước, cột "Giá mới dự kiến" | banggianongsan cột **Giá mới** | như trên |
| Trong nước, cột "Thay đổi" | nguồn ghi "Không đổi" → `0 VND/kg`; ghi khác (khoảng "▲ +0 ~ 100", "▲ +1.000"…) → **giữ nguyên + cần duyệt** (bài chỉ có dạng 1 mức) | `0 VND/kg` |
| Khớp dòng trong nước | Theo **tên** (bỏ "(đ/kg)", coi "ca cao" = "cacao"), không theo vị trí | — |
| New York / London, cột "Giá" | ICE `lastPrice` của hợp đồng cùng tháng (CCZ26 ↔ Dec26, H=Mar, K=May, N=Jul, U=Sep, Z=Dec) | `5,843` |
| New York / London, cột "Thay đổi so với phiên trước" | **Tính**: giá − giá / (1 + %thay đổi/100), làm tròn số nguyên (chỉ nhận khi kết quả cách số nguyên ≤ 0,05) — đánh dấu `tinh_toan` | `+42` / `-58` / `0` |
| Khớp dòng thế giới | Theo **mã hợp đồng** + soát cột tháng đáo hạn khớp mã | — |
| Hợp đồng thiếu trên ICE / chưa có giá / giá của ngày cũ hơn các hợp đồng khác | giữ nguyên cả dòng + cần duyệt | — |
| Ngày dd/mm/yyyy trong bài | Bước `dung` của công cụ chung đổi sang **ngày hôm sau** (quy tắc 21/10/2026) | — |
| Tiêu đề "1.2. Bảng giá ca cao thế giới dd/mm/yyyy" | Nếu **cả một sàn** không đọc được → trả về ngày cũ của bài gốc (không ghi ngày mới cho giá cũ) + cần duyệt | — |
| Đoạn văn / FAQ | Bài hiện **không có** giá trong đoạn văn. Nếu sau này bài thêm câu có "… VND/kg", "… USD/tấn", "… GBP/tấn" ngoài bảng → báo cần duyệt | — |

Không dùng: bảng New York / London của banggianongsan (không ghi ngày phiên, chỉ 4/10 hợp đồng, cột Giá cũ New York vô lý +31–38%).

## 3. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-cao
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json      # banggianongsan + 2 trang ICE
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash /home/user/trang/cong-cu/tu-dong/chay.sh gia-ca-cao <thư mục ra>`.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet).

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.js` | Mở banggianongsan + 2 trang ICE bằng Chromium, chép nguyên chữ / số từng ô + giờ cập nhật → `gia.json`; nguồn lỗi → `null` + "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | 3 bảng (+ ngày tiêu đề bảng thế giới khi thiếu nguồn) → `sua.json`; `--kiem` soát lại |
