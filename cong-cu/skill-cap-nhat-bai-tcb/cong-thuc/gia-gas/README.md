# Công thức: cập nhật bài "Giá gas hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-gas-hom-nay — đóng gói công thức 28/10/2026 (trước đó Claude làm tay 21/10, 23/10, 29/10).
Trang tích ô trong Sheet "Update" hoặc nhắn *"Update bài giá gas"* — **không hỏi gì thêm**. Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`
và khung chung của `cong-cu/tu-dong/chay.sh` (nhánh `*)`), không cần Claude, không cần cài thêm gì (chỉ Python có sẵn).

## 1. Nguồn (Trang chọn)

| Nguồn | Dùng cho | Đọc chỗ nào |
|---|---|---|
| https://pgas.com.vn/ (Tổng công ty Gas Petrolimex) | **Bảng 1.1** (Hà Nội, Hải Phòng, Đà Nẵng, TP. Hồ Chí Minh, Cần Thơ – bình 12kg, 48kg) + dòng **Petrolimex – Hà Nội** bảng 1.2 | Bảng ngay dưới tiêu đề "GIÁ GAS THÁNG mm/yyyy" |
| https://saigonpetro.com.vn/ban-le-gas | Dòng **Saigon Petro** bảng 1.2 (bình 12kg, 45kg) | Dòng chữ chạy "Giá bán lẻ gas: Chai gas SP loại 45 kg … / loại 12 kg …"; ngày hiệu lực ở ô "Thời gian: Ngày dd.mm.yyyy" (bảng chính của trang vẽ bằng JavaScript nên không đọc) |
| https://pvgaslpg.com.vn/vi/gas-price/ (PV GAS LPG) | 2 dòng **PV GAS** (Hà Nội, TP. Hồ Chí Minh) bảng 1.2 (bình 12kg, 45kg) | Bảng dưới tiêu đề "GIÁ BÁN LẺ GAS THÁNG mm/yyyy", dòng theo tên tỉnh |
| https://gaspetrolimex.vn/ | **Không dùng sửa bài** – trang đại lý, giá khác hẳn trang Tổng công ty (vd 644.112 so với 598.752). Vẫn đọc và ghi vào `gia.json` để đối chiếu | — |

**pvgaslpg.com.vn:** máy chủ của PV GAS gửi thiếu "chứng chỉ trung gian" (giấy tờ bảo mật), nên các công cụ thường báo lỗi
(các lần làm tay trước đều không đọc được). Trình duyệt tự lấy giấy tờ còn thiếu theo địa chỉ ghi ngay trong chứng chỉ của trang;
`lay_gia.py` làm y như vậy (tải từ `http://crt.sectigo.com/SectigoPublicServerAuthenticationCADVR36.crt`) và **vẫn kiểm tra bảo mật đầy đủ**
tới chứng chỉ gốc có sẵn trong máy — không tắt kiểm tra. Lỗi kiểu khác → nguồn = không đọc được → giữ số cũ + cần duyệt.

## 2. Cách sửa (tao_sua.py – không cần mạng, không đoán số)

| Chỗ trong bài | Cách làm |
|---|---|
| Bảng 1.1 "theo khu vực" | Dòng khớp theo **tên tỉnh/thành** (bỏ "TP."), cột khớp theo **số kg** trong tiêu đề cột → giá pgas.com.vn cùng tỉnh, cùng loại bình |
| Bảng 1.2 "theo thương hiệu" | Khớp theo **tên thương hiệu + khu vực**: Petrolimex → pgas.com.vn; Saigon Petro → saigonpetro.com.vn (một giá chung); PV GAS → pvgaslpg.com.vn cùng tỉnh |
| Ô "—" | Giữ nguyên (bài không có giá loại bình đó) |
| Câu "… sau đợt điều chỉnh đầu tháng M" | M = tháng ghi trên nguồn ("GIÁ GAS THÁNG 10/2026", "Ngày 01.10.2026", "GIÁ BÁN LẺ GAS THÁNG 10/2026"). Chỉ đổi khi **đọc được cả 3 nguồn và cả 3 cùng một tháng**; không thì giữ nguyên + cần duyệt. Giá gas đổi đầu mỗi tháng nên tháng trong bài luôn theo tháng của nguồn, không theo ngày chạy |
| Câu "Theo dữ liệu cập nhật gần nhất ngày …" | Công cụ chung đổi sang ngày hôm sau. Nếu **pgas.com.vn lỗi** (bảng 1.1 giữ số cũ) → trả lại ngày gốc của bài + cần duyệt, để bài không ghi ngày mới cho số cũ |
| Câu "tiếp tục duy trì mặt bằng" | Không đổi chữ (quy tắc: chỉ đổi số). Có giá đổi → tự ghi cần duyệt nhờ đọc lại câu |
| Ngày dd/mm/yyyy khác (tiêu đề, sapo, ngày đăng, mục 1) | Công cụ chung tự đổi sang ngày hôm sau |
| Pacific Petro | Bài nhắc tên nhưng không có dòng giá, không có nguồn → chỉ ghi cần duyệt để báo lại (như các lần làm tay) |
| Số giá nằm trong đoạn văn / dòng bảng lạ | Công thức chưa có quy tắc → giữ nguyên + cần duyệt (để không sót giá nào mà không ai biết) |

**Cách viết số:** đúng như số cũ trong ô – dấu phẩy ngăn nghìn, đơn vị đồng/bình, không làm tròn: nguồn `598.752` → bài `598,752`.
Mọi số ghi vào bài lấy thẳng từ trang nguồn đọc trong lần chạy đó (không có số nào phải tính); `ly_do` mỗi chỗ sửa chép nguyên chữ trên nguồn.
Nguồn nào `KHÔNG ĐỌC ĐƯỢC` → mọi dòng của nguồn đó giữ số cũ + cần duyệt.

## 3. Các bước

```bash
cd /home/user/trang && bash cong-cu/tu-dong/chay.sh gia-gas <thư mục ra>     # cách tự động (khung chung, nhánh *)
```

Làm từng bước (giống hệt chay.sh):

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-gas
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # LUÔN ghi ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $CT/lay_gia.py cap-nhat/gia.json                       # đọc 4 trang nguồn
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs từ `bai1.min.html`, `soat`, `bao-cao`). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-gas/`.

## 4. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung |
| `lay_gia.py` | Đọc 4 trang nguồn (Python có sẵn) → `gia.json`: giá đ/bình, tháng/ngày hiệu lực, chữ gốc trên trang, link |
| `tao_sua.py` | Bảng 1.1 + bảng 1.2 + câu "đầu tháng M" (+ ngày dữ liệu khi pgas lỗi) → `sua.json`; `--kiem` soát lại |

Bài đổi câu chữ/bảng khiến công thức không nhận ra một con số giá → công thức tự ghi cần duyệt; vẫn nên đọc lại `xem2.txt` mỗi lần chạy.
