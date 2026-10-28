# Công thức: cập nhật bài "Giá tiêu hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-tieu-hom-nay — làm tay 3 lần (22, 23, 29/10/2026), đóng gói công thức 28/10/2026.
Trang tích ô trong Sheet "Update" (dòng tiêu) hoặc nhắn *"Update bài giá tiêu"* — **không hỏi gì thêm**.
Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`, chạy tự động được bằng `cong-cu/tu-dong/chay.sh gia-tieu <thư mục ra>` (khung chung).
Không dùng AI lúc chạy: mọi con số ghi vào bài lấy **thẳng từ trang nguồn tải trong lần chạy đó** — không đoán, không mang số từ lần trước.

## 1. Nguồn (Trang chọn) và vai trò

| Nguồn | Dùng để | Ghi chú |
|---|---|---|
| https://banggianongsan.com/bang-gia-tieu/ | **Lấy số** cho cả 3 bảng của bài | Có đúng tên dòng như bài (bài TCB chép bảng của trang này). Giờ đăng ở dòng tác giả (vd `08:32 28/10/2026`) |
| https://giatieu.com/gia-tieu-hom-nay/ | **Đối chiếu** giá trong nước (không lấy số) | Tên vùng khác: Gia Lai, Đắk Lắk, Đắk Nông (= Lâm Đồng), Bình Phước (= Đồng Nai), Bà Rịa - Vũng Tàu (= TP. Hồ Chí Minh) — tỉnh cũ sáp nhập 2025 |
| https://giatieu.com/gia-tieu-truc-tuyen/ | **Đối chiếu** bảng thế giới + Ấn Độ | Bảng thế giới thường trống "Hệ thống đang bận" (trang trả về như vậy cả khi mở bằng Chromium) |

Cả 3 trang là trang tĩnh → `lay_gia.py` (Python + curl, không cần trình duyệt).

## 2. Đã chốt (theo các lần làm tay)

| Chỗ trong bài | Cách làm cố định |
|---|---|
| Bảng "1.1. Bảng giá hồ tiêu trong nước" (5 vùng + 3 dòng tiêu đen/trắng Việt Nam) | Khớp **theo tên dòng** với bảng "Nông sản (tên + đơn vị tính)" của banggianongsan. Ghi Giá cũ, Giá mới, Thay đổi đúng như nguồn |
| Bảng "Giá hồ tiêu tại các thị trường xuất khẩu" (8 dòng) | Khớp theo tên với bảng "Thị trường xuất khẩu" của banggianongsan. Đối chiếu Giá mới với bảng đầu trang của chính nguồn (Tiêu Đen Indonesia…): lệch → giữ dòng + cần duyệt (lỗi tự mâu thuẫn 21–22/10) |
| Bảng "Giá hồ tiêu nội địa Ấn Độ" (Garbled, Gram/lit, Ungarbled) | **Theo banggianongsan** — đúng như lần làm tay mới nhất (29/10, và 22, 23/10). giatieu.com thường lệch 100 Rupee → vẫn ghi theo banggianongsan, tự ghi cần duyệt kèm số của giatieu để người chọn nguồn |
| Cách viết số | Số nguyên của nguồn, viết theo **dấu nghìn của ô cũ cùng chỗ**: `137,000` (phẩy), `5.950` / `6.850` (chấm), `8,450` (phẩy) |
| Ô "Thay đổi" | Chữ của nguồn bỏ biểu tượng (▼ ▲ ➖) và phần trong ngoặc (`(-0,7%)`, `(0)`): `Không đổi`, `-1,000 đ`, `+1,500 đ` (dấu nghìn phẩy như bài). Số trong ô phải đúng bằng Giá mới − Giá cũ của nguồn, không thì giữ dòng + cần duyệt |
| Ô Thay đổi dạng bài chưa có (vd bảng xuất khẩu "Giảm (100)", hay "USD" ở dòng tiêu VN) | **Giữ nguyên cả dòng** + cần duyệt (ghi nguyên dòng của nguồn để người ghi tay) — bài chưa có mẫu cho dạng này |
| Đối chiếu giá trong nước với giatieu.com (cùng ngày) | Giá mới lệch → giữ cả dòng + cần duyệt (như 23/10). Giá mới khớp, chỉ Thay đổi lệch → vẫn ghi theo banggianongsan + cần duyệt (như 29/10). Khác ngày → không đối chiếu, ghi chú |
| Ngày | Công cụ chung đổi mọi `dd/mm/yyyy` sang **ngày hôm sau**; công thức bắt thêm ngày 1 chữ số/tách chữ đậm ở "hôm nay …", "trong nước ngày …", "tiêu thế giới …", dòng ngày đăng |
| banggianongsan không đọc được | Mọi bảng giữ nguyên; câu "cập nhật giá hồ tiêu trong nước ngày …" và tiêu đề "Bảng giá tiêu thế giới …" **trả về ngày gốc** (không nhận là số mới). Ngày ở tiêu đề / sapo / kết bài vẫn đổi theo quy tắc |
| Mục 3 "9 tháng đầu năm 2026, Việt Nam xuất khẩu 215,733 tấn…" | 3 nguồn không có → giữ nguyên, luôn ghi cần duyệt |
| Dòng có trong bài mà nguồn không có | Giữ nguyên + cần duyệt |

## 3. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-tieu
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                       # 3 nguồn → gia.json (nguồn lỗi = null)
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Hoặc gọn: `bash /home/user/trang/cong-cu/tu-dong/chay.sh gia-tieu <thư mục ra>`.
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-tieu/`.

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung (nguồn do `lay_gia.py` tự tải) |
| `lay_gia.py` | Tải 3 trang, đọc bảng → `gia.json`: `banggianongsan` {cap_nhat, trong_nuoc, xuat_khau, an_do}, `giatieu_hom_nay` {ngay, vung}, `giatieu_truc_tuyen` {the_gioi, an_do} |
| `tao_sua.py` | 3 bảng + ngày → `sua.json` (mỗi chỗ sửa ghi nguyên dòng của nguồn trong `ly_do`); `--kiem` soát lại |

Đã thử 28/10/2026: dựng lại bài như trước lần làm tay 29/10 (số cũ 137,500 / 6.769 / 9.268…) → công thức ra **đúng y** bản bài sau lần làm tay
(15 chỗ đổi, cùng 5 nhóm cần duyệt).
