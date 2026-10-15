# Công thức: cập nhật bài "Giá tiêu hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-tieu-hom-nay
Làm lần đầu ngày 15/10/2026 (ghi ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Bảng trong nước (Gia Lai, Đồng Nai, TP. Hồ Chí Minh, Lâm Đồng, Đắk Lắk) | Tạp chí Công Thương, bài hằng ngày "Giá tiêu hôm nay dd/mm" (danh sách: https://tapchicongthuong.vn/hashtag/gia-tieu-hom-nay-24980.htm). Bài này ghi đúng tên tỉnh mới như bài TCB. Nhà Bè Agri (https://nhabeagri.com/gia-nong-san/gia-ho-tieu/) chỉ để đối chiếu — Nhà Bè vẫn dùng tên tỉnh cũ, không có Đồng Nai / TP.HCM |
| Dòng "Tiêu Đen/Trắng Việt Nam (USD/tấn)" trong bảng trong nước + bảng xuất khẩu (Indonesia, Brazil, Malaysia, Việt Nam) | Giá IPC trong cùng bài Tạp chí Công Thương (đoạn "IPC cập nhật giá tiêu mới nhất tính đến ngày …"). Đối chiếu https://banggianongsan.com/ |
| Bảng Ấn Độ (Garbled, Gram/lit, Ungarbled – Rupee/100 kg) | giatieu.com/gia-tieu-the-gioi/ — trang vẽ bằng JavaScript, đọc bằng `doc_trang.js`. Trang **không ghi ngày** của số → luôn ghi `can_duyet` |
| Cột Giá cũ / Giá mới / Thay đổi | Giá mới đang có → Giá cũ; giá nguồn → Giá mới; Thay đổi = mới − cũ |
| Cách ghi Thay đổi | Dòng đ/kg: `+2,500 đ (+1.8%)`, `-1,000 đ (-0.7%)`; bằng 0: `Không đổi`. % tính trên Giá cũ, 1 số lẻ (dưới 0.1% thì 2 số lẻ). Dòng USD/Rupee: `-20 USD (-0.3%)`, `+100 Rupee (+0.1%)` (đặt theo mẫu đ/kg — Trang chưa duyệt) |
| Cách viết số | Bảng trong nước dấu phẩy ngăn nghìn (`138,000`, `5,950`); bảng xuất khẩu và Ấn Độ dấu chấm (`6.827`, `71.400`) — giữ đúng kiểu từng bảng |
| Ngày | Ngày kiểu `9/10/2026` (không số 0) công cụ không tự đổi → `sua_them` trong `gia.json` (tiêu đề + đề mục 1 + mở/kết bài dùng chung 1 mục `tat_ca`, đề mục 1.2 riêng). Câu "giá hồ tiêu trong nước ngày …" = **ngày của giá nguồn** (vd 15/10/2026), không phải ngày ghi bài |
| Tên file Docs | `Giá tiêu hôm nay: Bảng giá cập nhật và các yếu tố ảnh hưởng đến thị trường nông sản – dd/mm/yyyy` |
| Số liệu "9 tháng đầu năm 2026 … 215,733 tấn" | Giữ nguyên trừ khi có nguồn mới về xuất khẩu cả kỳ |

Lỗi có sẵn trong bài (không sửa chữ, chỉ báo): nhãn "Brazil Black - Pepper ASTA 570" đặt gạch nối sai chỗ; "Gram/lit" thiếu dấu.

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-tieu
mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/    # nhớ thay link bài Tạp chí Công Thương của ngày chạy
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)
python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
NODE_PATH=/opt/node22/lib/node_modules node $CT/doc_trang.js https://giatieu.com/gia-tieu-the-gioi/ cap-nhat/an-do.txt 15000
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
# Viết cap-nhat/gia.json theo mẫu /home/user/trang/cap-nhat-bai-tcb/2026-10-16-gia-tieu/gia.json
#   (mỗi dòng: nhan, gia, ngan "," hoặc ".", don_vi đ/USD/Rupee, nguon, thoi_diem; sua_them = các chỗ ngày; can_duyet)
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --ra cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem2.txt
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json      # phải ra "khớp hết"
```

Sau đó Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`).

## 3. Trục trặc

| Hiện tượng | Làm gì |
|---|---|
| `ValueError: ... is not in list` ở `tao_sua.py` | Nhãn dòng trong `gia.json` khác chữ trong bài → chép lại nhãn từ `xem.txt` |
| giatieu.com ra "Không thể giải mã JSON" ở bảng IPC | Bình thường (bảng IPC của trang lỗi); chỉ lấy bảng Ấn Độ |
| `ipcnet.org` | Bị chặn (connection reset) — không thử |
| Tạp chí Công Thương chưa có bài ngày chạy | Dùng bài ngày gần nhất, ghi rõ ngày trong `thoi_diem` + `can_duyet` |
