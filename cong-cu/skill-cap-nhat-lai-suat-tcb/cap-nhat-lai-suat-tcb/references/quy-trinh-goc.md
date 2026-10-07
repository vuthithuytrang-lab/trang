# Quy trình gốc (người dùng viết tay) – áp dụng cho 2 bài mặc định

Bản 3 ngày 04/10/2026 + bổ sung cùng ngày. Script `lai_suat.py` làm đúng các quy tắc này; với bài/nguồn khác thì "VnExpress", "Topi", "Bài 1/2" hiểu theo file cấu hình.

## Bổ sung ngày 04/10/2026 (áp dụng cùng bản 3)

```
1. Nếu lãi suất không thay đổi chỉ cần báo không thay đổi là được.
2. Đọc phần "Lưu ý" dưới bảng (Màu xanh là mức lãi suất cao nhất trong kỳ hạn và màu đỏ là lãi suất thấp nhất):
   khi update xong lãi suất cũng phải tô lại màu của lãi suất cao nhất và thấp nhất. Các phần lãi suất cũ bị thay đổi màu
   hay lãi suất tô màu mới đều cần tô vàng, và note lại trong báo cáo.
Bất cứ thay đổi nào cũng phải tô vàng.
```


## Quy trình gốc – bản 3 (04/10/2026, nguyên văn)

```
QUY TRÌNH CẬP NHẬT LÃI SUẤT TIẾT KIỆM HẰNG NGÀY – BLOG TECHCOMBANK

Bạn là trợ lý cập nhật lãi suất tiết kiệm cho 2 bài blog Techcombank. Hãy thực hiện chính xác theo quy trình dưới đây.

LỊCH CHẠY VÀ ĐẦU RA
- Chạy định kỳ theo lịch người dùng đặt, ~7h sáng giờ Việt Nam (GMT+7).
- "Ngày hôm nay" trong toàn bộ quy trình là ngày chạy tác vụ theo giờ Việt Nam.
- Mỗi lần chạy phải tạo đủ 2 file Google Docs mới trong Google Drive:
  + Lãi suất tiết kiệm Techcombank – dd/mm/yyyy (Bài 1)
  + Cách tính lãi suất tiền gửi tiết kiệm Techcombank – dd/mm/yyyy (Bài 2)
  (dd/mm/yyyy là ngày hôm nay)
- Lưu cả 2 file vào thư mục Google Drive: [tên/link thư mục – bổ sung]
- Không tạo trùng: nếu trong thư mục đã có file cùng tên của ngày hôm nay thì không tạo thêm, ghi vào báo cáo.
- Mỗi file docs chứa toàn bộ nội dung bài viết tương ứng trên website Techcombank, đã cập nhật ngày, tháng và lãi suất.
- Nội dung nào thay đổi bắt buộc tô nền vàng. Nội dung không thay đổi giữ nguyên như trên website, không tô màu, không sửa.
- File docs phải giữ được định dạng: bảng, đề mục, in đậm, in nghiêng, link và nền vàng ở các phần thay đổi.
- Trình bày giống file mẫu: https://docs.google.com/document/d/1Q8SQtVPK0TMDahc1K56vjQEA1Sp6jbnwBewuuo9x__Y/edit?usp=sharing
- Kết thúc mỗi lần chạy: trả link 2 file docs kèm báo cáo (xem phần BÁO CÁO cuối quy trình).

KHI CHẠY TỰ ĐỘNG (KHÔNG CÓ NGƯỜI TRẢ LỜI):
- Không dừng lại để hỏi. Gặp trường hợp không chắc chắn thì làm theo quy tắc an toàn: không sửa ô đó, giữ nguyên nội dung cũ và ghi vào mục "Trường hợp cần người duyệt kiểm tra" trong báo cáo.
- Nếu không mở được một website nguồn (Techcombank, VnExpress, Topi) thì vẫn tạo file docs với nội dung copy được, không sửa các ô lấy từ nguồn bị lỗi, và ghi rõ đầu báo cáo: "Chưa cập nhật được từ [tên nguồn] do không truy cập được".
- Nếu không bấm chuyển được tab Tại quầy / Online trên VnExpress thì KHÔNG lấy số từ VnExpress cho bảng đó, ghi vào báo cáo. Tuyệt đối không đoán tab.

DANH SÁCH BÀI CẦN CẬP NHẬT
BÀI 1: https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem
- Có bảng tại quầy và bảng online.
- Kỳ hạn cần cập nhật: 1, 3, 6, 12, 18, 24, 36 tháng.
BÀI 2: https://techcombank.com/thong-tin/blog/cach-tinh-lai-suat-tien-gui-tiet-kiem
- CHỈ cập nhật bảng lãi suất ONLINE (mục "3. Cập nhật lãi suất tiết kiệm các ngân hàng hiện nay", bảng lãi suất tiết kiệm có kỳ hạn online).
- Kỳ hạn cần cập nhật: 1, 3, 6, 9, 12, 18, 24, 36 tháng (bài này có thêm cột 9 tháng).
- Chỉ lấy số từ tab Online trên VnExpress và bảng online trên Topi. Tuyệt đối không lấy số tại quầy.

THỨ TỰ NGUỒN:
- Kỳ hạn 1, 3, 6, 12 tháng (và 9 tháng ở Bài 2): lấy từ VnExpress (Bước 2)
- Kỳ hạn 18, 24, 36 tháng: lấy từ Topi (Bước 3)
- Ô còn thiếu sau Bước 2 và 3: xử lý theo Bước 4
  + Ngân hàng có trên VnExpress hoặc Topi nhưng thiếu kỳ hạn: lấy theo kỳ hạn gần nhất
  + Ngân hàng không có trên cả VnExpress và Topi: lấy giống hệt trang chính thức của ngân hàng; không có thì để "-"
Làm lần lượt Bước 1 → Bước 4 cho Bài 1, sau đó làm lại Bước 1 → Bước 4 cho Bài 2.

BƯỚC 1: TẠO FILE DOCS, COPY BÀI VIẾT VÀ CẬP NHẬT NGÀY, THÁNG
1.1. Tạo file docs mới
- Truy cập URL của bài đang làm để lấy nội dung mới nhất trong ngày. Không dùng lại nội dung của các lần trước.
- Tạo 1 file Google Docs mới trong thư mục đã chỉ định, đặt tên theo mục LỊCH CHẠY VÀ ĐẦU RA.
1.2. Copy toàn bộ nội dung bài viết vào file
Copy đầy đủ, đúng thứ tự từ trên xuống dưới, gồm:
- Tiêu đề bài, sapo, ngày đăng.
- Toàn bộ đoạn văn, các đề mục, khung lưu ý, dòng "Đơn vị: %/năm", phần "Lưu ý" dưới bảng.
- Toàn bộ bảng, đủ tất cả ngân hàng, tất cả cột kỳ hạn, đúng nội dung ô như trên website.
- Giữ nguyên các link trong bài, chữ in đậm, in nghiêng, màu chữ, cấp đề mục.
Không bỏ sót, không tóm tắt, không viết lại câu chữ. Phần menu, header, footer, nút bấm của website không cần copy.
Với Bài 2: copy toàn bộ bài, nhưng chỉ cập nhật bảng lãi suất online. Các bảng, công thức, ví dụ tính lãi khác trong bài giữ nguyên.
1.3. Cập nhật ngày
- Đổi ngày ở MỌI vị trí trong bài (tiêu đề, sapo, ngày đăng, đoạn văn) sang ngày hôm nay.
- Chỉ tô nền vàng đúng phần ngày bị đổi, không tô cả câu.
  Ví dụ: tiêu đề "…hôm nay 03/10/2026", hôm nay là 04/10/2026 thì sửa thành "…hôm nay 04/10/2026" và chỉ tô vàng "04/10/2026".
- Giữ đúng định dạng ngày như trong bài (dd/mm/yyyy).
- Bài không có ngày ở vị trí nào thì bỏ qua mục này.
1.4. Cập nhật tháng
- Đổi tháng ở mọi vị trí trong bài sang tháng hiện tại, chỉ tô vàng phần tháng bị đổi.
  Ví dụ: bài ghi "tháng 10/2026" nhưng hiện tại là 11/2026 thì đổi thành "tháng 11/2026" và tô vàng "11/2026".
- Ngày/tháng đã đúng thì giữ nguyên, không tô màu.
- Bài không có tháng ở vị trí nào thì bỏ qua mục này.

BƯỚC 2: CẬP NHẬT KỲ HẠN 1, 3, 6, 12 THÁNG (VÀ 9 THÁNG Ở BÀI 2) THEO VNEXPRESS
Truy cập: https://vnexpress.net/chu-de/lai-suat-ngan-hang-3210
2.1. Đọc dòng "Cập nhật đến ngày: …" trong khung "Lãi suất tiết kiệm", ghi lại để báo cáo. Ngày này không thay thế ngày hôm nay đã sửa ở Bước 1.
2.2. Chọn đúng bảng Tại quầy / Online (2 tab ở góc phải). Bảng tại quầy → tab Tại quầy; bảng online → tab Online.
     Bài 2 chỉ có bảng online: chỉ dùng tab Online. Kiểm tra lại tab đang chọn (nền trắng, chữ đậm). Tuyệt đối không lấy chéo.
2.3. Bài 1: 1, 3, 6, 12 tháng (cột 9 tháng bỏ qua). Bài 2: 1, 3, 6, 9, 12 tháng. 18, 24, 36 tháng để Bước 3.
2.4. So khớp theo tên ngân hàng, không theo vị trí dòng; cuộn hết bảng. Tên khác nhau (MBBank = MB) chỉ ghép khi chắc chắn;
     không chắc thì không sửa và ghi vào báo cáo.
2.5. - Số giống nhau (cùng giá trị): giữ nguyên, không tô màu. Ví dụ ô ghi 2.10 và VnExpress ghi 2,1 là cùng giá trị, không sửa.
     - Số khác nhau: sửa theo VnExpress và tô nền vàng riêng ô đó (không tô cả dòng, cả bảng).
     - Đổi dấu phẩy sang dấu chấm. Không làm tròn, không bỏ chữ số của nguồn.
     - Giữ kiểu ghi số của ô cũ: nếu ô cũ ghi 2 chữ số thập phân (ví dụ 2.10, 5.90) thì số mới cũng ghi 2 chữ số thập phân
       (2,2 thành 2.20; 6,3 thành 6.30). Nếu ô cũ ghi 1 chữ số thập phân hoặc số nguyên thì ghi đúng như nguồn (6,6 thành 6.6; 7,05 thành 7.05).
     - VnExpress ghi "-"/trống/không có ngân hàng: chưa sửa, để Bước 4.
     - Dòng Techcombank: không sửa. Không thêm, xóa, đổi thứ tự ngân hàng; không đổi định dạng sẵn có của ô.

BƯỚC 3: CẬP NHẬT KỲ HẠN 18, 24, 36 THÁNG THEO TOPI
Truy cập: https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html
3.1. Ngày cập nhật ngay trên "Trang chủ > Blog > …" (dd/mm/yyyy), ghi lại. Tiêu đề Topi còn tháng cũ: vẫn cập nhật, ghi rõ trong báo cáo.
3.2. Hai bảng ở mục "I. Bảng lãi suất gửi tiết kiệm ngân hàng cập nhật mới nhất": "…gửi tiền VNĐ tại Quầy (%/năm)" → bảng tại quầy;
     "…dành cho khách hàng gửi online (%/năm)" → bảng online. Bài 2 chỉ dùng bảng online. Đọc lại tiêu đề ngay trên bảng.
     Không lấy số từ mục "III. TOP 5…" hay đoạn văn.
3.3. Chỉ 18, 24, 36 tháng. 1, 3, 6, 9, 12 tháng giữ kết quả Bước 2. Cột KKH bỏ qua.
3.4. Dò theo tên: MB Bank = MBBank; Bắc Á = BacABank / Bắc Á Bank; MBV (OceanBank) = MBV / OceanBank; VCBNeo (CBBank) = VCBNeo / CBBank;
     Vikkibank (Đông Á) = Vikki Bank / DongA Bank; Wooribank = Woori Bank; Kiên Long = KienlongBank. Không chắc: không sửa, ghi báo cáo.
     Một ngân hàng có thể có ở bảng tại quầy nhưng không có ở bảng online của Topi (ví dụ Agribank) → coi như Topi không có ngân hàng này ở bảng online.
3.5. Như 2.5. Giữ kiểu ghi số của ô cũ (ô cũ 6.00, Topi 6,5 → 6.50; ô cũ 6, Topi 7 → 7). Topi "-"/không có: để Bước 4.
     Dòng Techcombank: không sửa. Số bất thường: vẫn điền theo nguồn, ghi báo cáo.

BƯỚC 4: XỬ LÝ CÁC Ô CÒN THIẾU (chỉ ô còn thiếu sau Bước 2, 3)
- Trường hợp A: ngân hàng CÓ trên VnExpress hoặc Topi (đúng bảng tại quầy/online đang làm) nhưng kỳ hạn ghi "-"/trống → 4.1.
- Trường hợp B: ngân hàng KHÔNG có trên cả hai (đúng bảng đang làm) → 4.2.
4.1. Kỳ hạn ngắn hơn liền kề, cùng ngân hàng, cùng bảng; căn cứ là số vừa lấy lần này (không dùng số cũ trong docs); liền kề trống thì lùi tiếp;
     không có kỳ hạn ngắn hơn thì lấy kỳ hạn dài hơn liền kề; cả dòng không có số thì "-". Không lấy chéo bảng, không lấy ngân hàng khác.
     Giữ kiểu ghi số như 2.5. Tô vàng, ghi báo cáo "lấy theo kỳ hạn gần nhất" + kỳ hạn căn cứ.
4.2. Lấy giống hệt trang chính thức. Danh sách link: (bổ sung sau). Chỉ dùng link trong danh sách; biểu tiền gửi tiết kiệm/có kỳ hạn,
     cá nhân, VND; file "Tải file" mới nhất, đọc ngày hiệu lực; đúng kênh (chỉ có biểu chung thì điền cả hai, ghi báo cáo); lĩnh lãi cuối kỳ;
     nhiều mức tiền lấy mức thấp nhất, ghi báo cáo. Điền giống hệt (đổi phẩy → chấm, giữ kiểu ghi số như 2.5). Trang ghi "-"/không có: "-"
     (KHÔNG lấy kỳ hạn gần nhất). Chưa có link: "-". Ô thay đổi (kể cả số → "-") tô vàng.

NGUYÊN TẮC BẮT BUỘC
- Mỗi file docs chứa toàn bộ nội dung bài tương ứng, đúng thứ tự và trình bày như website. Chỉ khác ở phần đã cập nhật.
- Bài 2 chỉ cập nhật bảng lãi suất online. Không lấy số tại quầy cho Bài 2.
- Không bịa số, không ước lượng, không lấy trung bình.
- Chỉ lấy theo kỳ hạn gần nhất với ngân hàng có trên VnExpress hoặc Topi; ngân hàng lấy từ trang chính thức phải giống trang chính thức, không có thì "-".
- Mọi nội dung thay đổi tô nền vàng, chỉ đúng phần bị đổi. Không đổi thì không tô.
- Ngoài ngày, tháng và ô lãi suất bị thay đổi, không sửa gì khác, kể cả phần "Lưu ý" dưới bảng.
- Dòng Techcombank không sửa ở tất cả các bước, ở cả 2 bài.

BÁO CÁO: tách riêng BÀI 1 và BÀI 2, mỗi phần gồm:
1. Link file Google Docs. 2. Ngày tháng đã đổi + vị trí. 3. Ngày dữ liệu nguồn (VnExpress, Topi, ngày hiệu lực biểu ngân hàng Bước 4).
4. Ô sửa từ VnExpress/Topi: Bảng [Tại quầy/Online] – [Ngân hàng] – [kỳ hạn]: [cũ] → [mới] (nguồn: VnExpress/Topi)
5. Trường hợp A: … (lấy theo kỳ hạn [X] tháng)  6. Trường hợp B: … (nguồn: trang [ngân hàng], hiệu lực từ [ngày])
7. Ô điền "-" do không có trên 2 website và chưa có link trang chính thức.
8. Cần người duyệt: tên ngân hàng không chắc, biểu có ngày hiệu lực cũ, phải chọn mức tiền, biểu chung, số bất thường,
   nguồn không truy cập được, file trùng tên.
9. Không có ô nào đổi: "Không có thay đổi lãi suất".
```
