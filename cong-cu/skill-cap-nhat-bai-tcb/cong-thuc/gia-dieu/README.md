# Công thức: cập nhật bài "Giá điều hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-dieu-hom-nay — đóng gói 28/10/2026 (trước đó Claude làm tay 21/10, 23/10, 29/10/2026).
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá điều"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, không cần Claude (chạy bằng `cong-cu/tu-dong/chay.sh gia-dieu`).

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn (Trang chọn) | https://banggianongsan.com/bang-gia-hat-dieu/ — trang HTML thường, đọc bằng `curl` (không cần trình duyệt). Bảng "Nông sản (đơn vị tính) \| Giá cũ \| Giá mới \| Thay đổi", 12 dòng |
| Giờ cập nhật của nguồn | `dateModified` (giờ VN) trong trang, vd `08:42 28/10/2026`; dự phòng: dòng "Đăng bởi … hh:mm dd/mm/yyyy" |
| Bảng trong bài | Cùng 12 dòng, cùng 4 cột với nguồn → **chép đúng từng ô của nguồn**: Giá cũ ← Giá cũ nguồn, Giá mới ← Giá mới nguồn, Thay đổi ← Thay đổi nguồn |
| Ghép dòng | Theo **tên** (không theo thứ tự): bỏ dấu cách thừa, "vnđ" = "VND", không phân biệt hoa thường. Dự phòng: tên bỏ phần trong ngoặc + cùng loại tiền (VND/USD) |
| Cách viết số | Như ô cũ của bài: VND dấu phẩy ngăn nghìn `25,000 - 30,000`; USD dấu phẩy thập phân `10,5 - 12,8`; nối " - ". Chữ số lấy **đúng như nguồn**, không làm tròn (nguồn `10.75` → `10,75`) |
| Cột Thay đổi | "Không đổi" → chép. Khác (vd "Tăng 1.000") → vẫn chép, đổi cách viết số theo bài (`Tăng 1,000`) + **cần duyệt** để đọc lại |
| Nguồn ghi khác dạng (vd 1 mức thay vì khoảng) | Giữ nguyên ô cũ + cần duyệt |
| Dòng trong bài không có ở nguồn / nguồn có dòng mới | Giữ nguyên / không tự thêm dòng — cả hai đều ghi cần duyệt |
| Ngày (tiêu đề, sapo, ngày đăng, mục 1, đoạn kết — 6 chỗ) | Lệnh `dung` tự đổi sang **ngày hôm sau** |
| Nguồn không đọc được | Giữ nguyên **toàn bộ bảng** + trả **mọi ngày** về ngày gốc của bài (đọc từ `tam/bai1.html`) + cần duyệt |
| Nguồn cũ hơn 2 ngày | Vẫn chép bảng (là số mới nhất có) + cần duyệt |
| Số tiền ngoài bảng | Bài hiện **không có** giá nào trong đoạn văn / FAQ. Nếu sau này bài thêm (dòng chữ có "… VND", "… USD") → cần duyệt "chưa có quy tắc" |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy` |

Không có số nào tự nghĩ ra: mọi số ghi vào bài đều chép từ bảng nguồn đọc trong đúng lần chạy đó (không có phép tính nào).

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-dieu
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # ngày ghi trong bài: LUÔN là ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                                   # đọc bảng banggianongsan.com
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash /home/user/trang/cong-cu/tu-dong/chay.sh gia-dieu <thư mục ra>` (khung chung `*)` của chay.sh).
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-dieu/`.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Tải trang banggianongsan.com, đọc 12 dòng (giá cũ, giá mới — giữ nguyên chữ số nguồn, chữ cột Thay đổi) + giờ cập nhật → `gia.json`. Hỏng → `null`, in "KHÔNG ĐỌC ĐƯỢC" |
| `tao_sua.py` | Bảng giá (ghép theo tên) → `sua.json`; nguồn hỏng → trả ngày gốc; `--kiem` soát lại |
