---
name: lich-noi-dung-tuan
description: Chạy trọn chuỗi nội dung hàng tuần cho ShopOne — đọc lịch đăng, bung brief gửi thiết kế (hạn nộp lùi 3 ngày, né cuối tuần), soạn email riêng cho từng nhóm khách theo bảng định vị, đưa Trang duyệt rồi mới gửi qua Resend, cuối cùng xuất bảng theo dõi cho sếp. Dùng skill này bất cứ khi nào Trang nhắc tới lịch nội dung tuần, brief gửi thiết kế, gửi email cho nhóm khách, chạy tuần mới, hay hỏi "tuần này đăng gì" — kể cả khi chị không gọi đúng tên skill. Nếu chị chỉ nhờ một chặng (chỉ bung brief, hoặc chỉ soạn email), vẫn dùng skill này và làm đúng chặng đó với dữ liệu đã cài sẵn bên trong.
---

# Chạy lịch nội dung hàng tuần — ShopOne

Skill này đóng gói chuỗi việc Trang làm mỗi tuần. Mục đích là để lần nào chạy cũng
ra kết quả giống nhau về chất lượng, không phải nhắc lại quy tắc từ đầu.

**Trang là người Nontech.** Nói bằng lời thường, không thuật ngữ. Tự làm hết phần
kỹ thuật. Chỉ nhờ chị khi việc đó nằm ngoài tay mình (bấm nút, cấp quyền, chốt quyết định).

---

## 🔒 Chốt chặn quan trọng nhất

**Không gửi bất kỳ email nào cho tới khi Trang đọc và gật.**

Đây không phải phép lịch sự mà là điều kiện bắt buộc: email gửi đi rồi thì không rút
lại được, và người nhận là khách hàng thật của công ty chị. Một thư sai giọng hoặc sai
thông tin sẽ làm hỏng quan hệ với khách và ảnh hưởng uy tín người gửi cho những lần sau.

Trình tự đúng: làm hết mọi thứ → đưa toàn bộ nội dung ra cho chị đọc → chờ chị nói
"gật"/"ok"/"gửi đi" → **lúc đó mới** gọi Resend.

Chị im lặng, chị hỏi lại, chị nhận xét mà chưa chốt — đều tính là **chưa gật**.

---

## Năm chặng

### Chặng 1 — Mở lịch đăng và bảng định vị

Đọc hai nguồn:
- Lịch đăng: `Tài liệu Mẫu Agent Boss/lich-dang-thang.xlsx` (cột: Ngày đăng · Thứ ·
  Kênh · Chủ đề · Định dạng · Thông điệp chính)
- Bảng định vị: `Kết quả công việc Agent Boss/Bài 7/Bang-dinh-vi-ShopOne.html`

Nếu Trang đưa file mới thì dùng file mới. Nếu không tìm thấy file nào, **hỏi chị**
thay vì đoán đường dẫn.

### Chặng 2 — Bung brief gửi thiết kế

Lọc các bài có ngày đăng nằm trong **tuần tới** (thứ Hai → Chủ nhật kế tiếp).

Với mỗi bài, tạo một file Word riêng từ mẫu `Tài liệu Mẫu Agent Boss/mau-brief.docx`.
**Giữ nguyên bố cục 7 mục của mẫu**, chỉ thay nội dung. Cách làm an toàn nhất là copy
file mẫu rồi thay chữ trong từng đoạn — đừng dựng file Word mới từ đầu, vì sẽ mất
định dạng công ty đã thống nhất.

Đặt tên file: `Brief_<NgàyĐăng>_<Kênh>.docx`, ngày viết kiểu `2026-09-01`
(gạch ngang — tên file không nhận dấu gạch chéo).

Lưu vào `Kết quả công việc Agent Boss/Bài <số>/` hoặc thư mục Trang chỉ định.

#### Quy tắc tính hạn nộp

```
Hạn nộp = Ngày đăng − 3 ngày
Nếu hạn nộp rơi vào thứ Bảy  → lùi tiếp 1 ngày về thứ Sáu
Nếu hạn nộp rơi vào Chủ nhật → lùi tiếp 2 ngày về thứ Sáu
```

Lý do lùi: thiết kế không làm cuối tuần, để hạn rơi vào T7/CN là thực chất mất 2 ngày.

Trong file brief, ghi rõ cả lý do khi có lùi, ví dụ:
`Thứ Sáu, 04/09/2026 (lùi từ Thứ Bảy 05/09 về thứ Sáu)` — để thiết kế khỏi thắc mắc.

Sau đó **liệt kê riêng ra cho Trang** những bài bị lùi hạn.

#### Khi lịch thiếu thông tin

Bài nào lịch chưa ghi **Thông điệp chính** hoặc **Định dạng**: để trống, ghi
`cần bổ sung`, rồi liệt kê những bài đó cho Trang xem lại.

**Đừng đoán.** Brief là thứ đưa thẳng cho thiết kế làm; đoán sai thì cả ê-kíp làm sai
theo, phát hiện ra thì đã tốn công.

### Chặng 3 — Soạn email cho từng nhóm khách

Ba nhóm, **mỗi nhóm một tiêu đề riêng và một đoạn mở đầu riêng**. Đừng gửi cùng một
nội dung cho cả ba — khách ba nhóm có nỗi lo khác nhau, dùng chung một thư là phí cơ hội.

Bám đúng bảng dưới đây (lấy từ bảng định vị Bài 7).

### Chặng 4 — Đưa duyệt rồi mới gửi

Trình bày cho Trang: mỗi nhóm gồm **tiêu đề + toàn văn nội dung + tệp Resend sẽ gửi tới**.

Chờ chị gật. Gật rồi mới gửi qua Resend tới đúng tệp của nhóm đó — xem mục
"Tệp khách trong Resend" bên dưới.

### Chặng 5 — Xuất bảng theo dõi cho sếp

Một bảng gọn, đọc 30 giây là nắm:

| Ngày đăng | Kênh | Chủ đề | Brief đã gửi? | Hạn nộp | Thư đã gửi cho nhóm nào | Số thư gửi | Ai đã mở |
|---|---|---|---|---|---|---|---|

Phần "Ai đã mở" lấy từ Resend: gọi `GET /emails/{id}` và đọc `last_event`
(`delivered` = đã tới, `opened` = đã mở). Nếu Resend chưa có dữ liệu mở thư thì ghi
`chưa có dữ liệu` — **đừng suy đoán** con số cho đẹp báo cáo.

Lưu thành file HTML tự viết, tiếng Việt đủ dấu. Tự chụp ảnh trang đọc lại soát trước
khi gửi cho Trang.

---

## Ba nhóm khách — thông điệp NÊN DÙNG

### Nhóm 1 — Chủ cửa hàng 1–3 điểm bán
*Đang quản lý bằng sổ tay hoặc Excel · Gói Cơ bản 18tr / Tiêu chuẩn 36tr*

Nỗi lo lớn nhất: **sợ mất số liệu khi đổi sang phần mềm**.

Thông điệp: "Chuyển dữ liệu từ Excel **miễn phí**" · "nhập liệu nhanh, thao tác gọn" ·
câu lõi "gọn trong một màn hình".

### Nhóm 2 — Chuỗi 5–15 cửa hàng
*Cần nhìn số liệu tập trung · Gói Nâng cao 78tr*

Nỗi lo lớn nhất: **phải gọi từng cửa hàng hỏi doanh số**.

Thông điệp: "nhìn số liệu tập trung, một màn hình" · "kết nối nhiều sàn TMĐT" ·
"hỗ trợ 24/7 — **từ gói Nâng cao trở lên**".

⚠️ Luôn ghi rõ điều kiện "từ gói Nâng cao trở lên" khi nhắc hỗ trợ 24/7. Nói trống
không là hứa sai với khách gói thấp.

⚠️ Chuỗi 11–15 cửa hàng hiện **chưa có gói tương ứng** (bảng giá chỉ có "chuỗi 5–10"
rồi nhảy lên "chuỗi lớn"). Gặp khách cỡ này thì ghi `cần hỏi lại nội bộ`, đừng tự gán gói.

### Nhóm 3 — Hộ kinh doanh mới mở
*Cần đơn giản, chi phí thấp · Gói Cơ bản 18tr*

Nỗi lo lớn nhất: **thiếu thời gian, sợ phức tạp**.

Thông điệp: "đơn giản" · "chi phí thấp" · câu lõi "bán sự nhẹ đầu, không bán tính năng".
Đừng liệt kê danh sách tính năng dài — đúng thứ nhóm này sợ.

---

## 🚫 Thông điệp NÊN TRÁNH — áp dụng cho MỌI nhóm

Đây là luật truyền thông nội bộ của ShopOne, ghi trong tài liệu thương hiệu:

1. **Không cam kết mức tăng doanh thu.** Cấm mọi câu kiểu "tăng 30% doanh thu",
   "chắc chắn lãi hơn". Hứa con số không có căn cứ là rủi ro pháp lý và mất tin cậy.
2. **Không so sánh trực tiếp bằng tên đối thủ.** Kể cả khi đã có dữ liệu đối thủ,
   bảng định vị chỉ dùng nội bộ để chọn góc nói — không bê tên đối thủ lên bài đăng.
3. **Không dùng ảnh khách hàng khi chưa xin phép.**

*Ghi chú thật: cột "thông điệp nên tránh vì đối thủ đã chiếm" trong bảng định vị hiện
**đang trống**, vì bộ tài liệu chưa có đối thủ nào. Khi nào Trang điền 3–5 đối thủ thật
vào `danh-sach-doi-thu-bai7-marketing.docx`, cập nhật lại mục này. Tới lúc đó, đừng bịa
ra thông điệp "đối thủ đã chiếm".*

---

## Giọng thương hiệu

- Nói tiếng thường, **không thuật ngữ kỹ thuật**
- Xưng **"chúng tôi"**, gọi khách là **"bạn"**
- Không phóng đại, không hứa con số doanh thu
- Sản phẩm chưa làm được gì thì **nói thẳng** — đây là điểm mạnh, không phải điểm yếu

Ba chỗ ShopOne chưa mạnh, nếu khách hỏi thì trả lời thật:
chưa có ứng dụng cho khách hàng cuối · chưa có phân hệ sản xuất ·
giao diện báo cáo nâng cao còn cần làm quen.

### Chữ ký cuối thư

```
— Đội ShopOne
```

### Dòng hủy nhận thư — bắt buộc, không được bỏ

Đây là quyền của người nhận. Thiếu nó, khách sẽ bấm "Báo cáo thư rác" — và cái đó phá
uy tín người gửi, khiến những lần gửi sau rơi vào Spam theo.

**Khi tên miền `seongon.com` CHƯA xác thực** (tình trạng hiện tại) — dùng cách trả lời thư,
và đặt `reply_to` về `vuthithuytrang@seongon.com` để thư về đúng tay Trang:

> Bạn nhận thư này vì đã quan tâm tới ShopOne.
> **Không muốn nhận thư nữa?** Bấm Trả lời (Reply) thư này và gõ một chữ **HỦY** —
> thư về thẳng hộp thư của chúng tôi, chúng tôi gỡ bạn khỏi danh sách và không gửi nữa.
> Không cần lý do.

**Khi tên miền ĐÃ xác thực** — chuyển sang gửi bằng chế độ Broadcast của Resend và dùng
biến `{{{RESEND_UNSUBSCRIBE_URL}}}` để có link hủy thật, Resend tự quản lý:

> Không muốn nhận thư nữa? [Hủy nhận thư]({{{RESEND_UNSUBSCRIBE_URL}}})

⚠️ **Đừng bao giờ đặt một đường link hủy nhận không tồn tại.** Resend không kiểm tra
chuyện này — thư vẫn gửi được bình thường — nên lỗi kiểu đó lọt rất dễ. Trước khi gửi,
tự hỏi: "bấm vào link này thì thư đi đâu, có người nhận thật không?"

---

## Tệp khách trong Resend

| Nhóm | Tên tệp trong Resend | Mã tệp (audience_id) |
|---|---|---|
| Nhóm 1 — Cửa hàng 1–3 điểm bán | `ShopOne - Nhom 1 - Cua hang 1-3 diem ban` | `b6d53ca7-6759-4543-a4d2-62af841a3d2b` |
| Nhóm 2 — Chuỗi 5–15 cửa hàng | `ShopOne - Nhom 2 - Chuoi 5-15 cua hang` | `a133297c-3801-4f5c-ad84-19f0694294d7` |
| Nhóm 3 — Hộ kinh doanh mới mở | `ShopOne - Nhom 3 - Ho kinh doanh moi mo` | `c88ff40c-fc5a-495f-aaf6-4651ad94b144` |

Lấy danh sách người nhận: `GET /audiences/{audience_id}/contacts`.
Bỏ qua contact có `unsubscribed: true` — họ đã xin thôi nhận, gửi tiếp là vi phạm.

Gói Resend miễn phí **chỉ cho 3 tệp**. Cần tệp thứ 4 thì phải xoá bớt hoặc nâng gói —
báo Trang quyết, đừng tự xoá tệp có người trong đó.

---

## Chìa khoá Resend — đọc thế nào cho an toàn

**Đừng bao giờ in chìa ra màn hình, gắn vào URL, hay commit vào kho.**
Kho `vuthithuytrang-lab/trang` là kho công khai.

Thứ tự tìm chìa:
1. File `cong-cu/resend.env` (nếu có) — đọc bằng lệnh, không in nội dung
2. Nếu không có: **nhờ Trang đính kèm file chứa chìa vào khung chat** (biểu tượng kẹp
   giấy), đừng bảo chị gõ chìa ra chat

Gọi Resend qua header `Authorization: Bearer <chìa>`.

---

## Tình trạng gửi thư hiện tại

Tên miền `seongon.com` **chưa xác thực** trong Resend, nên:

- Chỉ gửi được tới **`vuthithuytrang@seongon.com`** (email đăng ký tài khoản)
- Mọi địa chỉ khác bị từ chối với lỗi `403`
- Địa chỉ người gửi bắt buộc là `onboarding@resend.dev`
- **Chế độ Broadcast không dùng được** (Resend chặn broadcast từ `resend.dev`)

Nguyên nhân: tên miền do một tài khoản Cloudflare khác quản lý (nameserver `nelly` +
`dave`), không phải tài khoản cá nhân của Trang (`anuj` + `tara`). Ba bản ghi DNS cần
gắn nằm ở `Kết quả công việc Agent Boss/Bài 8/DNS-can-gan-cho-seongon.com.md`.

Khi chạy skill mà tên miền vẫn chưa xanh: **cứ soạn thư đầy đủ và đưa Trang duyệt như
bình thường**, nhưng nói rõ trước là thư chỉ gửi được về địa chỉ của chị. Báo cáo cuối
phải ghi trung thực bao nhiêu thư gửi được, bao nhiêu bị từ chối và vì sao.

---

## Bẫy đã mắc — đừng lặp lại

**Chữ in đậm bị tách xuống dòng trong các khung màu.** Khi viết CSS cho khung cảnh báo,
nếu đặt `.box b{display:block}` thì *mọi* chữ in đậm bên trong khung đều xuống dòng riêng,
làm gãy câu giữa chừng. Chỉ dòng tiêu đề mới cần xuống dòng, nên viết:

```css
.box > b:first-child{display:block}   /* đúng — chỉ tiêu đề */
.box b{display:block}                 /* sai — gãy hết câu bên trong */
```

Lỗi này đã mắc 2 lần (bảng định vị Bài 7, bảng theo dõi tuần). Nó chỉ lộ ra khi nhìn ảnh
chụp trang — đọc mã HTML không thấy. Đó là lý do bước tự chụp ảnh soát lại là bắt buộc,
không phải hình thức.

---

## Báo cáo cuối mỗi lần chạy

Kể lại bằng lời thường, đánh số, không thuật ngữ:

1. Tuần này có mấy bài đăng, kênh nào
2. Bung được mấy brief, bài nào bị lùi hạn về thứ Sáu
3. Bài nào thiếu thông tin cần Trang bổ sung
4. Gửi mấy thư, thư nào cho nhóm nào, địa chỉ nào bị từ chối và vì sao
5. Đường dẫn tới bảng theo dõi cho sếp

Rồi hỏi Trang hai câu: **(a)** nhìn có chỗ nào hiển thị lỗi không, **(b)** có ưng không,
muốn chỉnh gì.
