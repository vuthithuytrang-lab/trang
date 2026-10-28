# Công thức: cập nhật bài "Giá cà phê Đắk Lắk hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-ca-phe-dak-lak-hom-nay — đóng gói 28/10/2026 từ 3 lần làm tay
(`cap-nhat-bai-tcb/2026-10-21…`, `…10-23…`, `…10-29-gia-ca-phe-dak-lak/`). Trang tích ô trong Sheet "Update" hoặc nhắn
*"Update bài giá cà phê Đắk Lắk"* — **không hỏi gì thêm**. Chạy được không cần Claude: `bash cong-cu/tu-dong/chay.sh gia-ca-phe-dak-lak <thư mục ra>`
(khung chung `*)` của `chay.sh`). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn Trang chọn | giacaphe.com: [Đắk Lắk](https://giacaphe.com/gia-ca-phe-dak-lak/), [Lâm Đồng](https://giacaphe.com/gia-ca-phe-lam-dong/), [Gia Lai](https://giacaphe.com/gia-ca-phe-gia-lai/), [Đắk Nông](https://giacaphe.com/gia-ca-phe-dak-nong/) |
| Cách đọc giacaphe.com | Số giá trên trang hiển thị bằng CSS (bản tải thường ra ô trống) → mở bằng Chromium, đọc **chữ đang hiển thị** của từng ô (`getComputedStyle`, như lần làm tay). Không vượt chặn, không giả bot |
| Nguồn dự phòng | **Nhà Bè Agri** https://nhabeagri.com/gia-nong-san/gia-ca-phe/ (nguồn của công thức `gia-ca-phe`), bảng "Khu vực \| Giá \| Thay đổi": cùng giá nhân xô 4 tỉnh trong ngày (đối chiếu 28/10/2026: trùng cả 4 tỉnh với giacaphe.com). **Chỉ dùng cho giá mới nhất từng tỉnh** khi giacaphe.com không đọc được (giacaphe.com trả 403 khi chạy từ GitHub Actions). Không dùng cột "Thay đổi" của Nhà Bè (so với 30 ngày trước, không phải phiên trước) và không dùng biểu đồ lịch sử của Nhà Bè (số ngày cũ không khớp giacaphe) |
| Bảng "Ngày \| Giá (VND/kg) \| Thay đổi (VND/kg)" | Bao nhiêu dòng thì lấy bấy nhiêu ngày **mới nhất** trên bảng "Giá cà phê Đắk Lắk theo ngày" của giacaphe.com, đúng ngày / giá / thay đổi như nguồn (nguồn không có ngày nghỉ → ngày có thể không liền nhau). Nhận bảng theo tiêu đề cột, dòng theo ô ngày. giacaphe.com không đọc được → **giữ nguyên cả bảng** + cần duyệt (Nhà Bè không có lịch sử đáng tin) |
| Đoạn "… Đắk Lắk đang được tham khảo ở mức khoảng X VND/kg, tăng khoảng Y VND/kg so với phiên trước" | X = giá Đắk Lắk mới nhất; Y = mức thay đổi giacaphe.com ghi cho ngày đó. Chữ **tăng/giảm** đổi theo dấu của Y (chiều của chính con số, giống công thức vang-14k) + tự ghi cần duyệt. Y = 0 → giữ nguyên câu + cần duyệt. Giá lấy từ Nhà Bè → giữ Y + cần duyệt |
| "Lâm Đồng / Gia Lai / Đắk Nông khoảng X VND/kg" | Giá mới nhất từng tỉnh (giacaphe.com, dự phòng Nhà Bè). Ngày tỉnh khác ngày Đắk Lắk → cần duyệt |
| Câu "giá Đắk Lắk đang ở mức tương đối cao" | Không sửa chữ; tỉnh nào cao hơn hoặc bằng Đắk Lắk → cần duyệt |
| Câu "…kẻ lại y hệt theo hình ảnh bạn cung cấp:" (chữ AI sót trên bài web) | Không sửa, luôn nhắc trong cần duyệt |
| Cách viết số | Giá `89,000`; thay đổi trong bảng `+200` / `-1,300` (số 0 viết `+0` như bài cũ); trong câu `200` (không dấu) |
| Ngày trong bài | Công cụ chung đổi sang ngày hôm sau. Số nguồn là ngày trước đó → cần duyệt ghi rõ ngày của số. **Không đọc được nguồn nào** → ngày "cập nhật trong ngày …" trả về ngày gốc của bài (không nhận số mới) |
| Không bịa số | Mọi số viết vào bài lấy thẳng từ trang nguồn đọc trong lần chạy (`ly_do` ghi nguyên văn dòng nguồn, khóa `chu_nguon` trong `gia.json`). Nguồn lỗi → giữ số cũ + cần duyệt. Số "… VND/kg" nào công thức không nhận ra → cần duyệt để sửa tay |
| Tên file Docs | `<Tiêu đề bài> – dd/mm/yyyy`; trùng → thêm ` (cập nhật HHhMM)` |

## 2. Các bước cho Claude

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-ca-phe-dak-lak
cd <thư mục nháp> && mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)   # ngày ghi trong bài: LUÔN là ngày hôm sau (Trang chốt 21/10/2026)

python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
NODE_PATH=/opt/node22/lib/node_modules node $CT/lay_gia.js cap-nhat/gia.json      # Chromium đọc 4 trang giacaphe.com + Nhà Bè Agri
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua  cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem  cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

`lay_gia.js` in `KHÔNG ĐỌC ĐƯỢC` cho nguồn hỏng (thoát mã 1 nhưng vẫn ghi `gia.json`, các bước sau vẫn chạy).
Rồi Bước 5 – 6 của `SKILL.md` (tạo Docs từ `bai1.min.html`, `soat`, `bao-cao`, chia sẻ quyền sửa theo Sheet). Lưu kết quả vào
`/home/user/trang/cap-nhat-bai-tcb/<yyyy-mm-dd>-gia-ca-phe-dak-lak/`, commit + push.

## 3. File

| File | Làm gì |
|---|---|
| `cau-hinh.json` | Link bài cho công cụ chung (nguồn do `lay_gia.js` tự đọc) |
| `lay_gia.js` | Chromium đọc 4 trang giacaphe.com (giá mới nhất + bảng theo ngày + giờ cập nhật) và bảng Khu vực của Nhà Bè Agri → `gia.json` (`giacaphe.<tỉnh>`, `nha_be.<tỉnh>`, kèm `chu_nguon` = chữ nguyên văn trên nguồn) |
| `tao_sua.py` | Bảng theo ngày + đoạn giá Đắk Lắk + 3 tỉnh lân cận → `sua.json`; tự ghi cần duyệt; `--kiem` soát lại |

Bài đổi câu chữ khiến công thức không nhận ra một con số giá → công thức báo "Có số giá công thức chưa nhận ra"; đọc lại `xem2.txt` mỗi lần chạy.
