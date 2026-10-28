# Công thức: cập nhật bài "Giá kim loại thế giới: Bảng giá cập nhật và các yếu tố ảnh hưởng" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-kim-loai-the-gioi — làm tay 3 lần (21, 23, 29/10/2026), đóng gói 28/10/2026.
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá kim loại"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, chạy tự động bằng `cong-cu/tu-dong/chay.sh gia-kim-loai <thư mục ra>`
(nhánh chung `*)`). Không cần trình duyệt, không cần Claude lúc chạy.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn (Trang chọn) | https://www.thitruonghanghoa.com/gia-kim-loai — **chỉ** "Bảng giá Kim loại" (trang dựng sẵn, tải bằng `curl`). Không dùng dải chạy chữ đầu trang (số khác bảng) |
| Nhận dòng nguồn | Theo tên tiếng Anh in dưới tên: GOLD, SILVER, COPPER, PLATINUM, NICKEL, LEAD, ALUMINUM, ZINC, IRON ORE, TIN — không theo vị trí |
| Nhận dòng trong bài | Theo tên: Vàng, Bạc, Đồng, Bạch kim, Niken (nguồn ghi "Nickel"), Chì, Nhôm, Kẽm, Quặng sắt 62% Fe, Thiếc. Ô giá / ô thay đổi nhận theo dạng số, không theo cột |
| Ô "Giá (VND/lượng)" | Số VNĐ của nguồn (`local-price`, vd `125.921.056`) viết lại dấu nghìn như bài: `125,921,056`. Không quy đổi đơn vị — nguồn ghi VNĐ/lượng (vàng, bạc, bạch kim), VNĐ/tấn (kim loại cơ bản), VNĐ/dmtu (quặng sắt), bài cũng đang ghi đúng như vậy |
| Ô "Thay đổi (%)" | Chép nguyên chữ số % của nguồn, thêm dấu theo mũi tên: ▲ `0.87%` → `+0.87`, ▼ `0.10%` → `-0.10`; `0.00%` → `0.00` |
| Ngày trong bài (tiêu đề, sapo, ngày đăng, đoạn mở đầu) | Công cụ chung `dung` đổi sang ngày hôm sau. **Thiếu số của bất kỳ kim loại nào → trả lại ngày cũ** (đọc từ bài gốc) + cần duyệt |
| Kim loại nguồn không đọc được | Giữ nguyên 2 ô cũ + cần duyệt |
| Phần chữ | Không có con số giá nào → không đụng. Mốc năm 2025/2026, "giảm 9%" (World Bank) giữ nguyên, ghi cần duyệt |
| Tiêu đề cột "Giá (VND/lượng)" | Giữ nguyên (bài đã có dòng Lưu ý về đơn vị) + cần duyệt |
| Giờ cập nhật | Trang nguồn không ghi giờ (giá chạy theo thời gian thực) → ghi giờ lấy số (giờ VN) vào lý do từng chỗ sửa |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy` |

**Không có số tự nghĩ ra:** mọi số ghi vào bài chép thẳng từ trang nguồn trong lần chạy đó (`gia.json` giữ cả chữ gốc
`gia_goc`, `thay_doi_goc`, `chieu`). Không tính toán, không lấy số lần trước.

## 2. Các bước cho Claude (hoặc để `chay.sh` tự làm)

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-kim-loai
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                                   # đọc bảng nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-kim-loai/`.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Tải trang nguồn (curl, chỉ thư viện chuẩn), đọc 10 dòng bảng → `gia.json` (giá VNĐ, đơn vị, % thay đổi, chữ gốc, giờ lấy). Thiếu dòng nào → `null` + "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | Bảng giá 10 kim loại (+ trả ngày cũ khi thiếu nguồn) → `sua.json`; `--kiem` soát lại |
