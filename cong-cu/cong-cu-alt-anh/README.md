# App soát và chèn alt ảnh

## 🌐 Địa chỉ web miễn phí

**https://vuthithuytrang-lab.github.io/trang/alt/**

Chạy trên GitHub Pages của chính kho này — **miễn phí vĩnh viễn, không dính tài khoản Claude**.
Mở được từ mọi máy, mọi điện thoại. Gửi link cho ai cũng dùng được.

Muốn cập nhật app: sửa `soat-alt-anh.html` ở đây, rồi copy đè file đó vào `alt/index.html`
trên nhánh `gh-pages`. Khoảng 1 phút sau là địa chỉ web đổi theo.

File: **`soat-alt-anh.html`**

Mở bằng Chrome là chạy. Không cần cài gì, không cần đăng nhập, không tốn token.
Cần mạng để **tải ảnh về xem và đo kích thước** — phần soát luật thì chạy offline.

### Xem ảnh cho rõ rồi mới viết

- Ảnh hiện **to 320px** ngay cạnh ô gõ, và **dính lại** khi bạn cuộn xuống
- **Bấm vào ảnh** → mở toàn màn hình, kèm alt cũ + chú thích + câu bạn đang viết ở dưới
- **Esc** hoặc bấm ra ngoài để đóng · nút **Mở tab mới** để xem ảnh gốc
- Ảnh nào máy chủ khách chặn, app **tự thử tải lại** một lần theo cách khác

---

## Dùng thế nào

1. Mở file `soat-alt-anh.html` bằng Chrome
2. Dán **HTML bài viết** vào ô 1
3. Dán **danh sách key** vào ô 2 — mỗi dòng một key, dòng nào là key chính thì ghi thêm `- key chính` ở cuối
4. Dán **đường dẫn ảnh thumb** vào ô 3
5. Ô 4 **không phải điền gì** — app tự nhớ ảnh của mọi bài bạn đã quét
6. Bấm **Quét bài** — đợi app tải ảnh về
7. Ảnh hiện **to 320px**, bấm vào ảnh (hoặc nút **🔍 Xem ảnh to**) để xem **toàn màn hình**.
   Cuộn xuống gõ thì ảnh vẫn **dính lại** bên trái cho bạn nhìn. Bấm **Esc** để đóng
8. Mỗi ảnh hiện **một khung xanh** (câu app đề xuất) và **một ô** bên dưới đã điền sẵn câu đó
9. Nhìn ảnh → ưng thì bấm **Thay thế**; chưa ưng thì sửa trong ô rồi bấm **Thay thế**.
   Muốn câu khác thì bấm **Đổi câu khác**
10. Sang tab **HTML đã chèn** → bấm Copy → dán thẳng vào CMS.
   Không bấm nút nào cũng copy được, nhưng app sẽ nhắc còn bao nhiêu ô chưa duyệt
11. Hoặc sang tab **Bảng để copy** nếu chỉ cần bảng text

Chú thích ảnh nằm gọn sau dòng **"+ Sửa chú thích ảnh"** — không bấm vào thì giữ nguyên chú thích cũ.

---

## App làm được gì

**Tự dò lỗi bài** — đúng những lỗi vẫn hay gặp ở bài AIG:

| Lỗi | Mức |
|---|---|
| Khai `height` sai so với kích thước file thật | nặng |
| Ảnh không có thẻ `alt`, hoặc `alt` rỗng | nặng |
| Hai ảnh dùng chung một chú thích | nặng |
| Cùng một file ảnh dùng hai lần trong bài | nặng |
| Ảnh đã dùng ở bài trước (app tự nhớ, báo kèm tên bài cũ) | nặng |
| Lỗi link Markdown `[chữ](đường-dẫn)` dán nhầm vào HTML | nặng |
| Link còn đuôi `utm_source=chatgpt` | nặng |
| Ảnh trỏ về server nháp (`dangbai.`, `staging`…) | nặng |
| Alt cũ thừa dấu cách đầu hoặc cuối | nhẹ |
| Alt cũ giống hệt chú thích | nhẹ |
| Thẻ link rỗng, không có chữ bên trong | nhẹ |

**Tự kiểm từng câu alt khi đang gõ:**

- Đếm ký tự **đúng như Python `len()`** (đếm ký tự, không đếm byte — tiếng Việt đếm byte là sai)
- Báo nếu chạm hoặc vượt 120 ký tự
- Báo nếu thiếu key đã gán cho ảnh đó
- Báo nếu chứa **từ cấm**: `banner`, `ảnh bìa`, `cover image`, `ảnh ghép`, `khung tròn`,
  `khung hình tròn`, `hình tròn ghép`, `collage`, `bố cục`, `ảnh thiết kế`, `nền bản đồ`
- Riêng ô **Description**: báo nếu mở đầu bằng `Bài viết của…`, `Trang dịch vụ…`, `Cover image for…`
- Báo nếu **trùng câu** với một ô khác
- Báo nếu thừa dấu cách, hoặc có ký tự `< > " &` làm vỡ thẻ HTML

**Tự chia key** cho các ảnh (bạn đổi lại được bằng ô chọn ở từng ảnh).

**Đề xuất sẵn câu cho mọi ô** — quét xong là mỗi ảnh đã có một câu trong khung xanh,
ô sửa bên dưới điền sẵn câu đó. Mỗi ảnh chỉ còn **hai nút**: *Đổi câu khác* và *Thay thế*.
Ở đầu trang có *Đề xuất lại cả bài* và *Thay thế hết*.

⚠️ **Câu nháp KHÔNG phải alt dùng được.** Máy không nhìn hiểu được ảnh nên không tả được ảnh.
Nó chỉ ghép lại chất liệu đã có sẵn trong bài — chú thích cũ, tên mục, alt cũ — rồi gắn key
và canh cho dưới 120 ký tự. Bạn **nhìn ảnh rồi sửa lại phần tả** cho khớp với ảnh thật.

Ô nào còn là câu đề xuất chưa ai duyệt thì có nhãn vàng ⚠. Bấm **Thay thế** thì đổi thành nhãn xanh ✓.
Tab **HTML đã chèn** đếm và nhắc còn bao nhiêu ô chưa duyệt.

Khi dựng, app tự bỏ dấu nguồn `(Nguồn: Internet)`, bỏ số thứ tự mục `2.3.`, bỏ từ cấm,
và dùng **mẫu câu khác nhau cho từng ô** để bốn ô thumb không ra bốn câu giống hệt.

**Xuất HTML nguyên vẹn** — chỉ thay giá trị trong `alt="…"`, không đụng một ký tự nào khác.
Kèm bảng chứng minh: đếm lại `<img`, `<h2`, `<h3`, `<table`, `<tr`, `<td`, `<ul`, `<li`,
`<a `, `[caption`, `<p `, `<strong`, `<em`, `&amp;` và so phần chữ đọc được với bản gốc.

---

## 🤖 Máy nhìn ảnh — cần chìa Gemini (miễn phí)

Dán **chìa Gemini** vào ô 5 ở màn hình đầu thì mỗi ảnh hiện thêm nút **🤖 Máy nhìn ảnh**,
và đầu tab Soạn alt có nút **🤖 Máy nhìn hết ảnh và viết alt**.

Lấy chìa: vào `aistudio.google.com/apikey` → đăng nhập Gmail → **Create API key** → Copy.
**Miễn phí, không cần thẻ ngân hàng.**

Khi bấm, app tải ảnh về, gửi sang Google kèm **nguyên bộ luật** (dưới 120 ký tự, phải có key,
cấm từ dàn trang, Description không tóm tắt bài…) rồi nhận câu tiếng Việt về.

**Hai loại câu, app gắn nhãn khác nhau:**

| Nhãn | Nghĩa |
|---|---|
| ⚠ **câu ghép máy móc** | Máy KHÔNG nhìn ảnh, chỉ ghép chú thích cũ + tên mục + key. Hay sai |
| 🤖 **máy đã nhìn ảnh** | Máy thật sự xem tấm ảnh rồi tả. Đúng hơn nhiều |

⚠️ **Cả hai loại vẫn phải bạn đọc lại rồi bấm Thay thế.** Máy nhìn được ảnh nhưng
không biết bài đang nói về công ty nào, nên vẫn nhầm được.

### Chìa khoá được giữ thế nào

- Lưu trong **trình duyệt máy này**, không bao giờ đưa lên GitHub
- Không in ra màn hình (ô nhập là dạng chấm tròn)
- Chỉ gửi tới Google, không gửi đi đâu khác
- Có nút **Xoá chìa** bất cứ lúc nào
- ⛔ **Đừng dán chìa vào khung chat với AI** — lịch sử chat lưu nhiều nơi

### Không có chìa thì sao

App vẫn chạy đủ: soát lỗi, đếm ký tự, dựng câu ghép, xuất HTML. Chỉ là không có nút 🤖.

---

## App KHÔNG làm được gì

**Không thay bạn quyết định.** Kể cả khi máy nhìn được ảnh, nó không biết bài bạn
đang viết cho khách nào, không biết ảnh stock hay ảnh thật của công ty đó.
Câu cuối cùng vẫn do **bạn duyệt**.

### Thư viện ảnh — app tự nhớ

Mỗi lần bạn bấm **Quét bài**, app tự ghi đường dẫn ảnh của bài đó vào bộ nhớ trình duyệt,
kèm tên bài. Bài sau dùng lại đúng đường dẫn nào thì app báo ngay, **nói rõ ảnh đó của bài nào**.
Bạn không phải dán gì cả. Quét lại chính bài cũ thì app **không** báo trùng.

Ô 4 có nút **Xem danh sách** và **Xoá hết thư viện**.

⚠️ Ba điều cần biết:

1. Thư viện lưu trong **trình duyệt của máy này**. Đổi máy, đổi trình duyệt là bắt đầu lại từ 0.
2. Xoá lịch sử duyệt web (phần "dữ liệu trang web") có thể xoá luôn thư viện.
3. App **chỉ so theo đường dẫn file**, **không so được nội dung ảnh** — trình duyệt không đọc
   được điểm ảnh của ảnh từ tên miền khác. Cùng một bức ảnh mà khách tải lên hai lần với
   **hai tên file khác nhau** thì app không phát hiện được. Loại đó vẫn phải soi bằng mắt.

---

## Câu lệnh để dán cho AI viết hộ câu

File **`cau-lenh-viet-alt.md`** ở cùng thư mục này chứa hai câu lệnh dán được ngay:

- **Bản đầy đủ** — mở chat mới với Claude/ChatGPT, hoặc giao cho bạn thực tập đọc
- **Bản rút gọn** — nhắc nhanh khi AI đang viết lệch luật giữa chừng

App này soát luật và đếm ký tự; câu lệnh kia dùng khi cần người/AI **viết hộ câu chữ**.

---

## Luật lấy từ đâu

Toàn bộ luật trong app lấy từ `cong-cu/cong-cu-viet-alt-anh-chuan-seo.md`.
Sửa luật ở file đó thì nhớ sửa cả trong app (mục `GIOI_HAN`, `TU_CAM`, `MO_DAU_CAM`
nằm ngay đầu phần `<script>`).
