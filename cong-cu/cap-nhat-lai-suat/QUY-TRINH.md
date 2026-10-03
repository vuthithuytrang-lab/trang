# Quy trình cập nhật lãi suất tiết kiệm hằng ngày – bài blog Techcombank

> Trang giao việc này ngày 03/10/2026: **"Từ giờ bạn sẽ cập nhật lãi suất hằng ngày theo hướng dẫn dưới đây."**
> Mọi phiên Claude làm việc này phải làm đúng quy trình gốc ở cuối file, không tự thêm bớt.

## Ghi chú kỹ thuật (cho Claude, không phải cho Trang)

| Việc | Cách làm đã chạy được (03/10/2026) |
|---|---|
| File docs đích | `1Q8SQtVPK0TMDahc1K56vjQEA1Sp6jbnwBewuuo9x__Y` |
| Sửa file docs | **Cần connector Google Docs** (đọc/sửa tại chỗ, tô nền vàng). Connector Google Drive chỉ đọc được, không sửa được. |
| Techcombank | `curl` thẳng vào được (bảng nằm sẵn trong HTML) |
| VnExpress | Bảng nạp bằng JavaScript. Lấy thẳng từ API: `https://gw.vnexpress.net/th?types=bank_rate_offline` (Tại quầy) và `...types=bank_rate_online` (Online). Trường `update` ghi dạng tháng/ngày/năm (`9/21/2026` = 21/09/2026). |
| Topi | `curl` thẳng vào được. 2 bảng đầu tiên trong trang = bảng Tại quầy và bảng Online của mục I. Ngày cập nhật đứng ngay trước chữ "Trang chủ > Blog". |
| Chạy đối chiếu | `python3 lay-so-lieu.py` → in ra ô cần sửa, ô theo kỳ hạn gần nhất, ghi `tam/result.json` |
| Báo cáo | Lưu vào `bao-cao/YYYY-MM-DD.md` |

Tên ghép đã chắc chắn: MBBank = MB = MB Bank · OceanBank = MBV = MBV (OceanBank) · VCB Neo (CBBank) / CBBank = VCBNeo = VCBNeo (CBBank) ·
Viet Capital Bank (BVBANK) = BVBank · BAOVIET Bank = BaoVietBank = Bảo Việt · PG Bank = PGBank · PVcomBank = PVCombank ·
Kienlongbank = Kiên Long · Vikki Bank = Vikkibank (Đông Á) · NamABank = Nam Á Bank · BacABank = Bắc Á · VietBank = Vietbank.

---

## Quy trình gốc của Trang (nguyên văn)

```
ĐẦU RA BẮT BUỘC: 1 file docs đã cập nhật ngày, tháng và lãi suất. Nội dung nào thay đổi bắt buộc tô nền vàng. Nội dung khác không được thay đổi.

THỨ TỰ NGUỒN:
- Kỳ hạn 1, 3, 6, 12 tháng: lấy từ VnExpress (Bước 2)
- Kỳ hạn 18, 24, 36 tháng: lấy từ Topi (Bước 3)
- Ô còn thiếu sau Bước 2 và 3: xử lý theo Bước 4
  + Ngân hàng có trên VnExpress hoặc Topi nhưng thiếu kỳ hạn: lấy theo kỳ hạn gần nhất
  + Ngân hàng không có trên cả VnExpress và Topi: lấy giống hệt trang chính thức của ngân hàng; không có thì để "-"

BƯỚC 1: LẤY DỮ LIỆU MỚI NHẤT VÀ CẬP NHẬT NGÀY, THÁNG
1.1. Truy cập https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem và copy toàn bộ dữ liệu ra file docs:
     https://docs.google.com/document/d/1Q8SQtVPK0TMDahc1K56vjQEA1Sp6jbnwBewuuo9x__Y/edit?usp=sharing
     Lưu ý: phải vào URL này lấy dữ liệu mới nhất mỗi ngày trước khi cập nhật, không dùng lại dữ liệu cũ.
1.2. Cập nhật ngày: đổi ngày trong bài sang ngày hôm nay và tô nền vàng.
     Ví dụ: hôm nay là 4/10, nội dung trên website ghi 3/10 thì trong file docs đổi thành 4/10 và tô vàng.
1.3. Cập nhật tháng: đổi tháng trong bài sang tháng hiện tại và tô nền vàng.
     Ví dụ: nội dung trong bài là 10/2026 nhưng hiện tại là 11/2026 thì đổi sang 11/2026.
     Ngày/tháng đã đúng thì giữ nguyên, không tô màu.

BƯỚC 2: CẬP NHẬT KỲ HẠN 1, 3, 6, 12 THÁNG THEO VNEXPRESS
Truy cập: https://vnexpress.net/chu-de/lai-suat-ngan-hang-3210
2.1. Kiểm tra ngày dữ liệu nguồn: đọc dòng "Cập nhật đến ngày: …" trong khung "Lãi suất tiết kiệm", ghi lại để báo cáo.
     Ngày này không thay thế ngày hôm nay đã sửa ở Bước 1.
2.2. Chọn đúng bảng Tại quầy / Online (2 tab ở góc phải). Bảng docs "tại quầy" → tab Tại quầy; bảng docs "online" → tab Online.
     Kiểm tra lại tab đang chọn trước khi đọc số. Tuyệt đối không lấy chéo.
2.3. Chỉ cập nhật 1, 3, 6, 12 tháng. 18/24/36 để Bước 3. Cột 9 tháng: bỏ qua.
2.4. So khớp theo tên ngân hàng, không theo vị trí dòng. Cuộn hết bảng. Tên khác nhau (MBBank = MB) chỉ ghép khi chắc chắn;
     không chắc thì không sửa và ghi vào báo cáo.
2.5. Số giống: giữ nguyên, không tô. Số khác: sửa theo VnExpress, tô vàng riêng ô đó.
     Đổi dấu phẩy sang dấu chấm, không làm tròn. VnExpress ghi "-"/trống/không có ngân hàng: chưa sửa, để Bước 4.
     Dòng Techcombank: không sửa. Không thêm/xóa/đổi thứ tự ngân hàng, không đổi định dạng ô, chỉ thay số và thêm nền vàng.

BƯỚC 3: CẬP NHẬT KỲ HẠN 18, 24, 36 THÁNG THEO TOPI
Truy cập: https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html
3.1. Ngày cập nhật nằm ngay trên "Trang chủ > Blog > …" (dd/mm/yyyy). Ghi lại để báo cáo.
     Tiêu đề Topi vẫn là tháng cũ: vẫn cập nhật nhưng ghi rõ trong báo cáo.
3.2. Hai bảng ở mục "I. Bảng lãi suất gửi tiết kiệm ngân hàng cập nhật mới nhất":
     "…gửi tiền VNĐ tại Quầy (%/năm)" → bảng tại quầy; "…dành cho khách hàng gửi online (%/năm)" → bảng online.
     Đọc lại tiêu đề ngay trên bảng. Không lấy số từ mục "III. TOP 5…" hay đoạn văn.
3.3. Chỉ cập nhật 18, 24, 36 tháng. 1/3/6/12 giữ kết quả Bước 2. Cột KKH: bỏ qua.
3.4. So khớp theo tên: MB Bank = MBBank; Bắc Á = BacABank; MBV (OceanBank) = MBV/OceanBank; VCBNeo (CBBank) = VCBNeo/CBBank;
     Vikkibank (Đông Á) = Vikki Bank/DongA Bank; Wooribank = Woori Bank; Kiên Long = KienlongBank. Không chắc: không sửa, ghi báo cáo.
3.5. Như 2.5. Số nguyên trên Topi (6, 7) điền đúng như vậy; nếu ô cũ ghi dạng 6.0 thì giữ kiểu ghi của file docs.
     Topi "-"/không có: để Bước 4. Dòng Techcombank: không sửa. Số bất thường: vẫn điền theo nguồn, ghi báo cáo.

BƯỚC 4: XỬ LÝ CÁC Ô CÒN THIẾU (chỉ ô còn thiếu sau Bước 2, 3)
- Trường hợp A: ngân hàng CÓ trên VnExpress hoặc Topi nhưng kỳ hạn ghi "-"/trống → 4.1.
- Trường hợp B: ngân hàng KHÔNG có trên cả hai → 4.2.
4.1. Lấy kỳ hạn ngắn hơn liền kề, cùng ngân hàng, cùng bảng. Căn cứ phải là số vừa lấy từ VnExpress/Topi lần này
     (không dùng số cũ trong docs). Liền kề trống thì lùi tiếp. Không có kỳ hạn ngắn hơn: lấy kỳ hạn dài hơn liền kề.
     Cả dòng không có số: "-". Không lấy chéo tại quầy/online, không lấy ngân hàng khác.
     Tô vàng, ghi báo cáo "lấy theo kỳ hạn gần nhất" + kỳ hạn căn cứ.
4.2. Lấy giống hệt trang chính thức. Danh sách link: (bổ sung sau).
     Chỉ dùng link trong danh sách. Chỉ biểu tiền gửi tiết kiệm/có kỳ hạn, cá nhân, VND. File "Tải file": lấy file mới nhất,
     đọc ngày hiệu lực. Đúng kênh (quầy/online); chỉ có biểu chung thì điền cả hai và ghi báo cáo. Lĩnh lãi cuối kỳ.
     Nhiều mức tiền: lấy mức thấp nhất, ghi báo cáo. Điền giống hệt (chỉ đổi phẩy → chấm). Trang ghi "-"/không có: "-"
     (KHÔNG lấy kỳ hạn gần nhất). Chưa có link: "-". Ô thay đổi (kể cả số → "-") tô vàng.

NGUYÊN TẮC BẮT BUỘC
- Không bịa số, không ước lượng, không lấy trung bình.
- Chỉ lấy theo kỳ hạn gần nhất với ngân hàng có trên VnExpress hoặc Topi.
- Mọi nội dung thay đổi tô nền vàng; không đổi thì không tô.
- Ngoài ngày, tháng và ô lãi suất bị thay đổi, không sửa gì khác.
- Dòng Techcombank không sửa ở tất cả các bước.

BÁO CÁO SAU KHI CẬP NHẬT
1. Ngày/tháng đã đổi ở Bước 1.
2. Ngày dữ liệu nguồn: VnExpress, Topi, ngày hiệu lực biểu lãi suất ngân hàng (Bước 4).
3. Ô sửa từ VnExpress/Topi: Bảng [Tại quầy/Online] – [Ngân hàng] – [kỳ hạn]: [cũ] → [mới] (nguồn: VnExpress/Topi)
4. Ô Trường hợp A: … (lấy theo kỳ hạn [X] tháng)
5. Ô Trường hợp B: … (nguồn: trang [ngân hàng], hiệu lực từ [ngày])
6. Ô điền "-" do không có trên 2 website và chưa có link trang chính thức.
7. Cần người duyệt kiểm tra: tên không chắc, biểu cũ, chọn mức tiền, biểu chung, số bất thường.
8. Không có ô nào đổi: ghi "Không có thay đổi lãi suất".
```
