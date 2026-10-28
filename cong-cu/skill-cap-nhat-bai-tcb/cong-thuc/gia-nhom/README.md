# Công thức: cập nhật bài "Giá nhôm hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-nhom — đóng gói 28/10/2026 từ 3 lần cập nhật tay (21/10, 23/10, 29/10/2026).
Trang tích ô dòng "giá nhôm" trong Sheet "Update" hoặc nhắn *"Update bài giá nhôm"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, chạy tự động được bằng `cong-cu/tu-dong/chay.sh gia-nhom <thư mục>` (nhánh chung `*)`).

## 1. Nguồn (Trang chọn trong Sheet "Update")

| Phần trong bài | Nguồn | Lấy gì |
|---|---|---|
| Bảng "Giá nhôm thế giới" (Hợp đồng · Giá (USD/tấn) · Thay đổi) | https://www.tradingview.com/symbols/COMEX-ALI1!/contracts/ (mở bằng Chromium) | Từng hợp đồng ALI…: cột Price, Chg %, ngày đáo hạn, giờ "As of … GMT", dấu "D" (giá trễ) |
| Bảng "Giá nhôm trong nước" (Loại nhôm · Giá tham khảo (VND/kg)) | https://www.phelieuquangphong.com/bang-gia-thu-mua-phe-lieu/ | Các dòng nhôm trong bảng thu mua (đ/kg) + "Cập nhật ngày …" |

Không dùng số nào khác: mọi số ghi vào bài là chữ trên nguồn ở lần chạy đó, chỉ đổi cách viết. `gia.json` giữ nguyên chữ gốc của nguồn,
`ly_do` của từng chỗ sửa chép lại chữ gốc đó (vd `Price "3,212.50", Chg % "−0.87%"`).

## 2. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Khớp dòng bảng thế giới | Theo **mã hợp đồng** (ALIV2026…), không theo thứ tự |
| Giá thế giới | Bài ghi số nguyên → **bỏ phần lẻ, không làm tròn** (3,285.25 → 3,285), như bản đã đăng từ 23/10. Ô cũ có số lẻ thì giữ đúng số chữ số lẻ |
| % thay đổi | Chép nguyên từ nguồn, dấu trừ "−" của TradingView → "-" (vd `-0.87%`, `+1.96%`) |
| Hợp đồng đáo hạn | Mã trong bài không còn trên nguồn → **cuộn bảng**: các dòng lấy đúng N hợp đồng đầu tiên trên nguồn (theo ngày đáo hạn), ghi cần duyệt. Ký tự tháng mới chưa có trong dòng "Ký tự V, X, Z…" → giữ câu đó + cần duyệt |
| Khớp dòng bảng trong nước | Theo **tên loại nhôm** (giống hệt tên trên bảng Quang Phong, bỏ chữ "Giá " đầu khi so) |
| Giá trong nước | `67.000 - 90.000 đ/kg` → `67,000 - 90,000` (dấu nghìn như ô cũ) |
| Ngày dd/mm/yyyy | Lệnh `dung` đổi mọi ngày sang **ngày hôm sau**. Nguồn thế giới hỏng → tiêu đề "Giá nhôm thế giới ngày …" và câu "tại thời điểm ngày …" trả về ngày cũ; nguồn trong nước hỏng → "Giá nhôm trong nước ngày …" trả về ngày cũ; hỏng cả hai → mọi ngày trong bài trả về ngày cũ |
| Số khác trong bài (85% bauxite, 60% sản lượng Trung Quốc, 45 triệu tấn/năm, thuế Section 232 50%, năm 2026) | Không phải giá, 2 nguồn không nói tới → giữ nguyên (3 lần làm tay đều giữ) |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy` |

Cần duyệt chỉ hiện khi có chuyện thật: nguồn không đọc được, cuộn mã hợp đồng, dòng trong bài không có trên nguồn,
bảng Quang Phong ghi ngày cũ hơn 10 ngày, bài đổi trình bày (không thấy bảng).

## 3. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-nhom
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json      # mở Chromium đọc 2 nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash /home/user/trang/cong-cu/tu-dong/chay.sh gia-nhom <thư mục ra>`.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-nhom/`, commit + push.

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.js` | Mở 2 trang bằng Chromium → `gia.json` (chữ gốc của nguồn + giờ cập nhật). Nguồn hỏng → `null`, in "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | 2 bảng (+ trả ngày khi nguồn hỏng) → `sua.json`; `--kiem` soát lại. Không dùng mạng |
