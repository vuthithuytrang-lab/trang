# Công thức: cập nhật bài "Giá xăng dầu hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-xang-dau-hom-nay
Chốt với Trang ngày 07/10/2026. Trang chỉ cần tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá xăng dầu"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt — KHÔNG hỏi lại Trang

| Việc | Cách làm cố định |
|---|---|
| Kỳ giá | Thông cáo **"Petrolimex điều chỉnh giá xăng dầu…" mới nhất** trên https://www.petrolimex.com.vn/ndi/thong-cao-bao-chi.html |
| Bảng Petrolimex (6 mặt hàng × Vùng 1/2) | Số lấy từ bảng Petrolimex trên https://topi.vn/gia-xang-dau-hom-nay.html, **bắt buộc đối chiếu với ảnh bảng giá trong thông cáo** (Claude mở ảnh `cap-nhat/tam/plx-gia.jpg` để đọc). Ảnh là gốc: lệch thì sửa `gia.json` theo ảnh |
| Bảng PVOIL | Bảng PVOIL trên topi.vn — pvoil.com.vn chặn máy chủ (Cloudflare), **không cố vượt** |
| Bảng Mipec | https://www.mipec.com.vn/pages/gia-xang-dau-ban-le |
| Topi chưa sang kỳ mới (bảng Petrolimex trên Topi ≠ ảnh thông cáo) | Petrolimex: điền theo ảnh. PVOIL: đặt `"pvoil": null` → giữ số cũ + mục cần duyệt "nhờ Trang chụp màn hình trang PVOIL" |
| Không dùng | webgia.com — hay chậm, có lúc hiện giá trước giờ điều chỉnh |
| Câu hỏi thường gặp 5.1 / 5.3 / 5.4 | Cập nhật số theo Petrolimex; câu 5.1 dùng giá **Vùng 1** |
| Cách viết số | `28,180` (dấu phẩy ngăn nghìn) như bài gốc |
| Lỗi có sẵn trong bài (đánh số 5.1 → 5.3) | Không sửa, chỉ báo lại |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng tên → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-xang-dau
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)   # ngày ghi trong bài: chạy từ 15h trở đi -> ngày hôm sau

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json      # tải bài TCB (lệnh này XÓA cap-nhat/tam/ → chạy trước)
python3 -I $CT/lay_gia.py cap-nhat                                     # giá 3 hệ thống → cap-nhat/gia.json + ảnh thông cáo
```

**Đối chiếu bắt buộc:** mở `cap-nhat/tam/plx-gia.jpg` (công cụ Read xem được ảnh), so từng số Vùng 1/Vùng 2 với bảng
script in ra. Khớp → làm tiếp. Lệch → sửa `cap-nhat/gia.json` theo ảnh, và nếu Topi cũ thì `"pvoil": null` (mục 1).

```bash
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json      # phải ra "khớp hết"
```

Rồi làm Bước 5 – 6 của `SKILL.md`: tạo Google Docs từ `cap-nhat/tam/bai1.min.html`, tải về chạy `soat` (`dòng lệch: 0`),
chạy `bao-cao` (ghi chú: kỳ thông cáo + nguồn từng bảng). Lưu `cau-hinh.json`, `gia.json`, `sua.json`, `bao-cao.md` vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-xang-dau/`, commit + push.
Báo Trang: link file, bảng tóm tắt (kỳ giá, nguồn từng bảng), mục cần duyệt, 2 câu hỏi cuối.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `lay_gia.py` báo lỗi đọc thông cáo Petrolimex | Mở danh sách thông cáo bằng công cụ đọc web, tự lấy bài mới nhất; vẫn không được → báo Trang |
| Topi không có bảng | Petrolimex: đọc từ ảnh thông cáo, tự điền `gia.json` (mẫu: file `gia.json` trong `cap-nhat-bai-tcb/2026-10-07-gia-xang-dau/`). PVOIL: null + nhờ Trang chụp màn hình |
| Mipec null | Giữ bảng Mipec, ghi cần duyệt |
| `tao_sua.py --kiem` báo lệch | Đọc `xem2.txt`, sửa `sua.json` bằng tay, chạy lại `sua` |
| Bài TCB thêm/bớt bảng hoặc đổi tên đề mục 1.1/1.2/1.3 | Script nhận bảng theo đề mục chứa "Petrolimex" / "PVOIL" / "Mipec" — đề mục đổi thì báo Trang |

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Tìm thông cáo Petrolimex mới nhất + tải ảnh bảng giá; lấy số Petrolimex/PVOIL từ Topi, Mipec từ mipec.com.vn → `gia.json` |
| `tao_sua.py` | So 3 bảng + 4 câu hỏi thường gặp với `gia.json` → `sua.json`; `--kiem` soát lại |
