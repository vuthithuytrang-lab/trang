# Công thức: cập nhật bài "Giá cà phê Đắk Lắk hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-phe-dak-lak-hom-nay
Viết lần đầu ngày 15/10/2026 (chạy cho ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

Trang chỉ cần nhắn *"Update bài giá cà phê Đắk Lắk"* (hoặc dán link). **Không hỏi gì thêm** — các lựa chọn đã chốt ở mục 1.

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng "Ngày \| Giá (VND/kg) \| Thay đổi (VND/kg)" (5 dòng) | Nhà Bè Agri trang Đắk Lắk https://nhabeagri.com/gia-nong-san/gia-ca-phe-dak-lak/ — bảng lịch sử giá theo ngày; lấy **5 ngày mới nhất** của nguồn, mới nhất ở trên, đổi cả ô ngày theo đúng ngày của nguồn |
| Ô ngày trong bảng | Là ngày của số liệu, **không** đổi thành ngày ghi bài. Nguồn chưa có giá ngày ghi bài (chạy chiều hôm trước) → dòng đầu là ngày gần nhất nguồn có, ghi `can_duyet` |
| Đoạn "…tại Đắk Lắk đang được tham khảo ở mức khoảng **X** VND/kg, tăng khoảng **Y** VND/kg so với phiên trước" | Lấy dòng mới nhất của bảng lịch sử. Giá giảm → đổi "tăng" thành "giảm" và ghi `can_duyet`; không đổi → chỉ đổi giá, giữ phần tăng/giảm, ghi `can_duyet` |
| 3 dòng "Lâm Đồng / Gia Lai / Đắk Nông khoảng X VND/kg" | Nhà Bè Agri trang chính https://nhabeagri.com/gia-nong-san/gia-ca-phe/ (bảng 5 vùng, cùng nguồn với bài "Giá cà phê hôm nay") |
| Cách viết số | Giá `93,300` (dấu phẩy nghìn); thay đổi `+100`, `-2,400`; **không đổi ghi `+0`** (đúng kiểu bài) |
| Câu "giá Đắk Lắk đang ở mức tương đối cao" | Giữ nguyên chữ; nếu có vùng lân cận giá cao hơn Đắk Lắk → `can_duyet` |
| Lỗi có sẵn trong bài | Câu nháp "Dưới đây là bảng thông tin được trích xuất và kẻ lại y hệt theo hình ảnh bạn cung cấp:" — không sửa, chỉ báo `can_duyet` |
| Ngày trong câu chữ (tiêu đề mục, sapo, ngày đăng) | Công cụ chung tự đổi sang ngày ghi bài |
| Tên file Docs | `Giá cà phê Đắk Lắk hôm nay: Biến động thị trường và góc nhìn cho nhà đầu tư – dd/mm/yyyy`; trùng tên → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-phe-dak-lak
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json      # bài + thamkhao1 (trang chính) + thamkhao2 (trang Đắk Lắk)
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --nha-be cap-nhat/tam/thamkhao1.goc \
        --dak-lak cap-nhat/tam/thamkhao2.goc --ra cap-nhat/sua.json --gia cap-nhat/gia.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --nha-be cap-nhat/tam/thamkhao1.goc \
        --dak-lak cap-nhat/tam/thamkhao2.goc                            # phải ra "khớp hết"
```

Sau đó làm **Bước 5 – 6 của `SKILL.md`** (tạo Docs từ `cap-nhat/tam/bai1.min.html`, `soat` phải `dòng lệch: 0`, `bao-cao`
kèm `--ghi-chu` ghi nguồn + giờ cập nhật của 2 trang Nhà Bè Agri). Lưu `cau-hinh.json`, `sua.json`, `gia.json`, `bao-cao.md`
vào `/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-ca-phe-dak-lak/`.

## 3. Khi có trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `Không đọc được bảng lịch sử giá…` | Nhà Bè Agri đổi giao diện trang Đắk Lắk (bảng `table.gia-ca-phe`, ô `<td>dd/mm/yyyy</td><td>93.300đ</td><td class="price-up">+100đ</td>`) → đọc `thamkhao2.txt` bằng mắt, tự ghi `sua.json`, sửa hàm `doc_lich_su` |
| `Không đọc được bảng giá các vùng…` | Như công thức `gia-ca-phe` — sửa hàm `doc_nha_be` |
| `Không thấy bảng Ngày \| Giá \| Thay đổi` / `Không thấy câu "ở mức khoảng…"` | Techcombank đổi bài → dừng, đọc `xem.txt`, báo lại |
| `--kiem` báo ô lệch | Đọc `xem2.txt`, sửa `sua.json` bằng tay rồi chạy lại `sua` |

## 4. File trong thư mục

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài + 2 trang Nhà Bè Agri (trang chính, trang Đắk Lắk) |
| `tao_sua.py` | So bảng 5 ngày, đoạn giá hôm nay, 3 dòng vùng lân cận với nguồn → viết `sua.json` + `gia.json`; `--kiem` để soát lại |
