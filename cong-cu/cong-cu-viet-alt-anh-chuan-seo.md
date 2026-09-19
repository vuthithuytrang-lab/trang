# Công cụ viết alt ảnh chuẩn SEO

> Bộ quy tắc Trang đã chốt dần qua các bài thực tế. Mở bài mới thì đọc file này trước.
> Cập nhật lần cuối: 19/09/2026.

## 1. Trang đưa gì, tôi trả gì

Trang gửi: **URL bài + HTML + danh sách key** (key chính, key phụ).

Tôi trả **bảng ngay trong chat**, không xuất file .txt:

| # | Tên file ảnh | Alt đề xuất | Ký tự |
|---|---|---|---|

Nếu ảnh có khối `[caption]` thì làm thêm bảng chú thích cùng định dạng.
Chỉ xuất file HTML khi Trang nói rõ **"xuất file"**.

## 2. Luật viết alt

- **Một câu có nghĩa**, không phải liệt kê từ khóa.
- **Dưới 120 ký tự** — đếm bằng Python `len()` trên chuỗi UTF-8.
  ⚠️ Không dùng `awk length` hay `wc -c`: tiếng Việt nhiều byte, đếm sai.
- **Chứa key** — mỗi ảnh một key riêng, rải đều hết danh sách key.
- **Tả đúng ảnh thật.** Phải tải ảnh về xem tận mắt, không đoán theo tên file
  hay theo chú thích cũ.
- **Đa dạng cấu trúc câu** để không đọc ra kiểu nhồi key: đổi chủ ngữ, đổi
  cách mở đầu (danh từ / động từ / mệnh đề phụ).
- Không câu nào trùng câu nào.

## 3. Luật viết chú thích ảnh

- Cùng luật với alt, nhưng **bám ngữ cảnh đoạn văn** nhiều hơn.
- Ảnh có đánh số mẫu → mở đầu bằng **"Mẫu 01:"**, "Mẫu 02:"…
- **Giữ nguyên dấu nguồn ở cuối** nếu ảnh gốc đang có:
  `(Nguồn: Internet)` hoặc `(Ảnh tham khảo)`.
- Dấu nguồn **chỉ để trong chú thích**, không đưa vào alt.

## 4. Ảnh thumb — điền cả 4 ô trong WordPress

Mỗi ô một việc khác nhau, **không dán cùng một câu vào cả 4 ô**:

| Ô | Việc của nó | Cách viết |
|---|---|---|
| **Alt Text** | máy đọc màn hình + Google Ảnh | Tả ảnh, có key, dưới 120 ký tự |
| **Title** | tên trong thư viện ảnh | **Viết y như alt** — không để cụt vài chữ |
| **Image Caption** | dòng chữ hiện dưới ảnh | Câu giới thiệu cho người đọc, có key |
| **Description** | nội dung trang đính kèm | **Viết y như alt**: một câu tả ảnh, có key, dưới 120 ký tự |
| **File URL** | — | Giữ nguyên nếu tên file đã có key, không dấu |

**Luật chung cho cả 4 ô (chốt 19/09/2026):** cả bốn đều viết theo luật của alt —
một câu có nghĩa, tả đúng cái ảnh, có key, dưới 120 ký tự. **Bốn câu phải khác nhau**:
cùng một ảnh nhưng mỗi ô tả một góc khác, đổi cấu trúc câu, đổi thứ tự chi tiết.

⛔ **Title không viết cụt** kiểu `Nguyên liệu cho ngành sữa - AIG` hay
`Nhà máy trái cây đông lạnh MDG - AIG`. Viết thành câu đủ, ví dụ
*"Bàn gỗ xanh bày đủ sữa tươi, phô mai và bơ — nhóm nguyên liệu cho ngành sữa của AIG"*.

### ⛔ Những điều Trang cấm

1. **Alt Text của thumb: bỏ chữ "banner"** — và bỏ cả "ảnh bìa" ở bài tiếng Việt.
   Thay bằng cách tả thẳng nội dung ảnh, rồi nối bằng *"minh họa…"* /
   *"introducing…"* / *"illustrating…"*.
2. **Description: không mở đầu bằng "Cover image for the…"**.
3. **Description: không tóm tắt bài viết** (chốt 19/09/2026). Cấm các kiểu mở đầu
   *"Bài viết của … giới thiệu…"*, *"Trang dịch vụ … của…"*, *"HR2B guide to…"*.
   Ô này viết **đúng luật của alt**: một câu tả chính cái ảnh, có key, dưới 120 ký tự,
   và **khác câu** đã dùng ở ô Alt Text (cùng ảnh nhưng đổi góc tả, đổi cấu trúc câu).

   | | Sai | Đúng |
   |---|---|---|
   | Description | Bài viết của AIG giới thiệu Mekong Delta Gourmet (MDG) - công ty sản xuất trái cây đông lạnh IQF với nhà máy hơn 33.000 m²… | Xoài, thơm, chuối và thanh long cắt khối xếp trong tô gỗ tại công ty sản xuất trái cây đông lạnh MDG |

Đừng bấm nút **"Generate Alt"** của WordPress: nó sinh alt tiếng Anh chung chung,
không có key, không đúng ngữ cảnh bài.

## 5. Giữ nguyên HTML (khi Trang yêu cầu xuất file)

Chỉ thay giá trị `alt="…"` và phần chữ chú thích. Không đổi thẻ, shortcode,
id ảnh, kích thước — không một ký tự nào khác.

Cách chứng minh (chạy bằng Python):

1. Số dòng file gốc = số dòng file mới.
2. Với mỗi dòng có thay đổi, sau khi thay `alt="…"` → `alt="~"` và phần chữ
   chú thích → `~`, hai dòng phải **giống hệt nhau**.
3. Đếm lại `<img`, `alt="`, `[caption`, `<table`, `<h2`, `<h3` — phải khớp.

## 6. Luôn soát và báo thật

Xem ảnh thật xong thì báo Trang những gì lệch, đừng viết alt che lỗi:

- Ảnh **sai loại nguyên liệu / sai sản phẩm** so với bài.
- Ảnh **stock** đặt dưới tên một công ty cụ thể → alt không được khẳng định
  đó là ảnh của công ty đó.
- Ảnh **ghép nhiều ô**, ảnh **dựng AI có chữ lỗi**, ảnh **trùng nhau** dùng cho
  hai mục khác nhau.
- **Bản vẽ sai số liệu** (sai diện tích, sai đơn vị, số vô lý).
- Chú thích cũ **hứa thứ ảnh không có** (ví dụ nói "biểu đồ tiêu hóa" mà ảnh
  không có số liệu nào).
- **Lỗi kỹ thuật trong bài**: alt rỗng, thiếu hẳn thẻ `alt`, ảnh trỏ về server
  nháp, đoạn `<p>` bị cắt đôi giữa câu, thẻ `<p><strong>` dùng thay `<h3>`.
- **Rác sót lại khi copy-paste**: mã giao diện ChatGPT, câu brief gửi người viết.
- **Key sai ngữ pháp tiếng Anh** (`outsource` thay vì `outsourced`,
  `head hunter` thay vì `headhunter`): vẫn chèn nguyên văn như Trang giao,
  nhưng đưa kèm bản sửa để Trang chọn.

## 7. Kết thúc mỗi lần giao việc

Hỏi Trang đúng hai câu:

1. Dán vào WordPress rồi, có ảnh nào vỡ layout hay mất dấu tiếng Việt không?
2. Có ưng cách viết không, muốn chỉnh gì?
