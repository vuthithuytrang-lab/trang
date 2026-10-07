# Bảng lãi suất tiết kiệm – cấu hình `nguon` và quy tắc tự động

Áp dụng cho bảng trong bài TCB có cột đầu "Ngân hàng", có dòng Techcombank và các cột kỳ hạn (1, 3, 6, 9, 12, 13, 18, 24, 36 tháng).
Script tự nhận bảng **tại quầy** / **online** theo chữ ngay phía trên bảng; cột nào ghi rõ "tại quầy / phòng giao dịch" hay
"online / trực tuyến" ở tiêu đề cột thì theo cột (bảng so sánh 2 kênh).

## Khai nguồn

```json
"nguon": [
  {"url": "https://vnexpress.net/chu-de/lai-suat-ngan-hang-3210", "ky_han": ["1", "3", "6", "9", "12"]},
  {"url": "https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html", "ky_han": ["18", "24", "36"]},
  {"tep": "cap-nhat/nhap-tay.json", "ky_han": ["18", "24", "36"]}
],
"ten_ghep": {"Tên trong bài": ["Tên trên nguồn"]}
```

- `ky_han`: kỳ hạn nguồn đó **phụ trách**. Bỏ trống = mọi kỳ hạn nguồn có. Nhiều nguồn cùng phụ trách → nguồn đứng trước ưu tiên,
  thiếu số mới lấy nguồn sau.
- **VnExpress**: đọc qua API riêng (trang vẽ bảng bằng JavaScript); tab Tại quầy ↔ bảng tại quầy, tab Online ↔ bảng online.
  Chỉ bảng Tại quầy có ngày "cập nhật đến"; bảng Online không ghi ngày.
- **Trang web khác** (Topi, …): đọc thẳng bảng HTML — dòng đầu là kỳ hạn, cột đầu là tên ngân hàng, chữ phía trên bảng có
  "tại quầy" hoặc "online".
- **Nguồn nhập tay** (`tep`): nguồn script không đọc được (PDF biểu lãi suất, trang chính thức ngân hàng, ảnh…) — bạn tự đọc rồi ghi số
  **đúng như nguồn** theo mẫu `nguon-nhap-tay-mau.json`. Ô nguồn không có thì `null`. Không đọc được thì không điền.
- **Tên ngân hàng**: script tự ghép (bỏ dấu, bỏ chữ "Bank", đọc cả phần trong ngoặc, kèm danh sách ghép sẵn: MBBank = MB = MB Bank,
  OceanBank = MBV, CBBank = VCBNeo, Kienlongbank = Kiên Long, BacABank = Bắc Á, …). Ghép thêm qua `ten_ghep` khi **chắc chắn**.

## Quy tắc (script làm sẵn)

- Dòng Techcombank không bao giờ sửa. Không thêm/xóa/đổi thứ tự ngân hàng.
- Số bằng giá trị (2.10 = 2,1) → giữ nguyên, không tô. Số khác → sửa + tô vàng riêng ô đó. Phẩy → chấm, không làm tròn.
  Dòng đang ghi kiểu 2 chữ số thập phân có số 0 cuối (2.10, 5.90) → số mới cũng 2 chữ số; còn lại ghi đúng như nguồn.
- Ngân hàng có trên nguồn nhưng thiếu kỳ hạn → lấy kỳ hạn gần nhất (ưu tiên kỳ ngắn hơn liền kề, số vừa lấy lần này) – Trường hợp A.
- Không nguồn nào có ngân hàng → "-" – Trường hợp B (muốn lấy từ trang chính thức thì thêm nguồn nhập tay).
- Nguồn không truy cập được → giữ nguyên các ô nguồn đó phụ trách, báo cáo ghi "Chưa cập nhật được từ … do không truy cập được".
- Bảng có chú thích "Màu xanh … cao nhất … màu đỏ … thấp nhất" → tô lại màu từng cột (bỏ dòng Techcombank); ô đổi màu tô vàng, ghi báo cáo.
- Báo cáo tự cảnh báo: nguồn cũ hơn 3 ngày, kỳ hạn dài thấp hơn hẳn kỳ ngắn (≥ 0,8 điểm), số < 1%, ô đổi mạnh (≥ 0,8 điểm),
  ngân hàng không có trên một nguồn.
