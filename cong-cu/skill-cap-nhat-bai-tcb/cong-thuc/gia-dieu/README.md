# Công thức: cập nhật bài "Giá điều hôm nay" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-dieu-hom-nay
Làm lần đầu ngày 15/10/2026 (ghi ngày 16/10/2026). Chạy trên bộ công cụ chung `../../cap-nhat-bai-tcb/`.

## 1. Những gì đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn cả bảng (điều tươi 7 tỉnh, điều nhân W240/W320/W450, điều nhân USD/kg) | https://banggianongsan.com/ mục "Bảng giá điều hôm nay" — cùng cấu trúc Giá cũ/Giá mới/Thay đổi, cùng tên dòng như bài. Đối chiếu https://giacaphehomnay.vn/gia-nong-san/gia-dieu/ (có giờ cập nhật) |
| Đơn vị dòng `10,5 - 12,8` / `8,5 - 10,8` | **USD/kg** (nguồn ghi `10.5 – 12.8 USD/kg`). Bài dùng dấu phẩy thập phân ở 2 dòng này, dấu phẩy ngăn nghìn ở các dòng VND (`25,000 - 30,000`) — giữ đúng kiểu từng ô |
| Khoảng giá | Luôn ghi khoảng `X - Y` như bài, không rút thành 1 mức |
| Cột Giá cũ / Giá mới / Thay đổi | Giá mới đang có → Giá cũ; giá nguồn → Giá mới; Thay đổi: `Không đổi` nếu trùng; đổi thì ghi theo kiểu bài tiêu `+X đ (+p%)` — chưa có mẫu trong bài, ghi `can_duyet` |
| Giá không đổi | Giá điều đứng yên nhiều tuần (trái vụ, tháng 6 – 1). Nguồn trùng bài → giữ nguyên mọi số, chỉ đổi ngày, ghi `can_duyet`. Nguồn cũ hơn bài → giữ số cũ, `can_duyet` |
| Ngày | `Giá điều hôm nay 9/10/2026` (không số 0) công cụ không tự đổi → 1 mục `"lan": "tat_ca"` trong `sua.json` đổi cả tiêu đề, mở bài, đề mục 1, kết bài |
| Tên file Docs | `Giá điều hôm nay: Cập nhật thị trường trong nước, thế giới & các yếu tố tác động – dd/mm/yyyy` |

Lỗi có sẵn trong bài (không sửa chữ, chỉ báo): "Chi phí chế biến và logistic" (thiếu "s").

## 2. Các bước

```bash
SKILL=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cap-nhat-bai-tcb
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-dieu
mkdir -p cap-nhat && cp $CT/cau-hinh.json cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+9 hours" +%d/%m/%Y)
python3 -I $SKILL/scripts/cap_nhat.py lay  cap-nhat/cau-hinh.json      # tải bài + 2 nguồn (thamkhao1 = banggianongsan, thamkhao2 = giacaphehomnay)
python3 -I $SKILL/scripts/cap_nhat.py dung cap-nhat/cau-hinh.json $N
python3 -I $SKILL/scripts/cap_nhat.py xem cap-nhat/cau-hinh.json bai1 > cap-nhat/xem.txt
grep -n -A60 "Bảng giá điều hôm nay" cap-nhat/tam/thamkhao1.txt         # so từng dòng với bảng trong xem.txt
# Viết cap-nhat/sua.json theo mẫu /home/user/trang/cap-nhat-bai-tcb/2026-10-16-gia-dieu/sua.json
python3 -I $SKILL/scripts/cap_nhat.py sua cap-nhat/cau-hinh.json cap-nhat/sua.json
```

Sau đó Bước 5 – 6 của `SKILL.md` (tạo Docs, `soat`, `bao-cao`).

## 3. Trục trặc

| Hiện tượng | Làm gì |
|---|---|
| banggianongsan.com đổi giao diện / không có mục điều | Dùng giacaphehomnay.vn (cùng các dòng, có giờ cập nhật) |
| Hai nguồn lệch nhau | Không chọn, giữ số cũ, ghi `can_duyet` kèm cả hai số |
| nhabeagri.com/gia-nong-san/gia-dieu/ | 404 — không có trang giá điều |
