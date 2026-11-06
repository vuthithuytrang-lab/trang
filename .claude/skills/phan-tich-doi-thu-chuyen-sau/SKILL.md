---
name: phan-tich-doi-thu-chuyen-sau
description: >-
  Phân tích chuyên sâu một từ khóa SEO theo cách đã chạy cho các bài deco (key 80m2,
  70m2, 90m2) và bài OSAKAR — tự mở từng URL đối thủ mà đọc, tự vào website khách hàng
  bóc dữ liệu thật từ sơ đồ trang và trang sản phẩm, rà bài cũ đang xếp hạng để không
  tự cạnh tranh, bắt lỗi website khách tự nói ngược nhau, dựng bảng CẮT và bảng BỔ SUNG,
  học luật đặt heading từ chính bài đang top, rồi xuất HTML đúng định dạng site khách.
  Dùng skill này khi Trang đưa một từ khóa kèm link đối thủ và nhờ "phân tích chi tiết",
  "phân tích sâu", "làm như bài deco", "làm như key 80m2", "đối thủ đáp ứng gì mình chưa
  đáp ứng gì", "bài này đang tụt", "tối ưu bài cũ", hay khi cần lấy số liệu thật từ
  website khách hàng — kể cả khi chị không gọi đúng tên skill.
---

# Phân tích đối thủ chuyên sâu & tối ưu bài đang có

Cách làm này rút từ hai lần chạy thật: loạt bài văn phòng 70/80/90m2 và bài
"xe máy điện Vespa" của OSAKAR. Khác với skill `toi-uu-content-seo` (chạy quy trình
9 chặng cho bài mới), skill này dùng khi **khách đã có bài trên site** và cần biết
bài đó thua đối thủ ở đâu.

**Trang là người Nontech.** Nói bằng lời thường, tự làm hết phần kỹ thuật.
Chỉ nhờ chị thứ nằm ngoài tay mình: ảnh chụp trang kết quả Google, số liệu nội bộ
của khách, quyết định chốt.

## Tài liệu kèm theo — đọc trước khi chạy

| File | Dùng cho |
|---|---|
| `cong-cu/phan-tich-doi-thu-chuyen-sau/KY-THUAT-BOC-DU-LIEU.md` | Lệnh tải trang, bóc thông số, vượt chặn |
| `cong-cu/phan-tich-doi-thu-chuyen-sau/LUAT-DAT-HEADING.md` | Cách đặt tên heading và rải từ khóa |
| `cong-cu/phan-tich-doi-thu-chuyen-sau/VI-DU-OSAKAR.md` | Ca mẫu đã chạy, có số liệu thật |
| `cong-cu/toi-uu-content-seo/luat-viet-content.md` | 14 luật viết content của Trang |

---

## 🔒 Bốn chốt chặn

**1. Tự mở link mà đọc.** Không bắt Trang copy nội dung ra. Mở không được thì
**báo rõ bị chặn ở đâu, đã thử mấy cách**, tuyệt đối không đoán nội dung bài đó.

**2. Không bịa số.** Mọi con số phải trích được từ nguồn cụ thể. Thiếu thì ghi
`[CẦN TRANG BỔ SUNG: …]`. Cấm tự nghĩ hộ giá, thông số, tên khách, giải thưởng.

**3. Dừng hỏi sau mỗi chặng.** Trang gật mới đi tiếp.

**4. Soi website khách TRƯỚC khi đề xuất cấu trúc.** Chặng 2 là chặng hay bị bỏ qua
nhất và cũng là chặng tìm ra nhiều thứ nhất. Bỏ nó là đề xuất sai hướng.

---

## Chặng 1 — Nhận nguyên liệu và chốt intent

Trang thường đưa: **từ khóa + bài của khách + URL đối thủ**. Có đủ thì chạy luôn.

Chốt 3W trong **một đoạn ngắn**, không dài dòng:
- **Who** — ai gõ cụm này, đang ở giai đoạn nào
- **What** — họ muốn thấy cái gì trên trang
- **Why** — vì sao họ không tự giải quyết được

Rồi kết luận **dạng truy vấn**: tìm hiểu / so sánh / mua hàng. Dạng truy vấn
quyết định thứ gì phải nằm ở nửa trên của bài.

**Mẹo đọc từ khóa:** tách từng chữ ra xem chữ nào mang ý. Ví dụ "xe điện **giống**
vespa" — chữ "giống" cho biết người đọc **đã biết** đây không phải Vespa thật,
nên bài không cần giải thích Vespa là gì nữa.

⏸ Hỏi Trang.

## Chặng 2 — Soi website khách hàng (chặng quan trọng nhất)

Đây là chặng làm nên khác biệt. Làm đủ năm việc:

**2.1. Lấy sơ đồ trang** — `sitemap.xml`, `post-sitemap.xml`, `product-sitemap.xml`.
Có danh sách toàn bộ URL là biết site có gì.

**2.2. Tải toàn bộ trang sản phẩm liên quan**, bóc bảng thông số và giá. Đây là
nguồn số liệu thật, chính xác hơn mọi thứ Trang nhớ hoặc bài cũ viết.

**2.3. Rà bài đã đăng cạnh tranh với từ khóa.** Lọc tên URL theo từ khóa.
Lập bảng: *bài nào đã chiếm phần nào*. Nếu tìm thấy bài trùng ý với bài đang định viết
⇒ **báo ngay**, vì viết bài mới là tự cạnh tranh, cả hai cùng tụt.

**2.4. Đối chiếu chéo tìm chỗ site tự nói ngược nhau.** So:
- Giá trên trang sản phẩm ↔ giá trong bài thông báo điều chỉnh giá
- Phần chữ quảng cáo ↔ bảng thông số kỹ thuật của cùng một sản phẩm
- Bài A nói con số này ↔ bài B nói con số khác cho cùng sản phẩm
- Tiêu đề/mô tả trang ↔ nội dung thật của trang

**2.5. Lấy thông tin thương hiệu** — số đại lý, hotline, chính sách bảo hành,
hình thức thanh toán. Dùng cho mục "mua ở đâu" và phần E-E-A-T.

⏸ Báo Trang những gì tìm được, nhất là chỗ mâu thuẫn và nguy cơ trùng bài.

## Chặng 3 — Đọc từng đối thủ

Mở **từng URL**. Với mỗi bài ghi:
- **Dạng trang**: bài viết hay trang danh mục sản phẩm?
  *(Nhiều trang danh mục trong kết quả = truy vấn mua hàng, bài viết muốn thắng
  phải nhìn giống trang bán hàng ở nửa trên.)*
- **Dàn ý đầy đủ** theo thứ tự
- **Có gì ngoài chữ**: bảng, ảnh thật, giá, hỏi đáp
- **Bộ lọc sản phẩm** nếu là trang danh mục — bộ lọc cho biết chính xác người mua
  cân nhắc tiêu chí gì
- **Điểm mạnh / điểm yếu**, mỗi ý kèm trích dẫn

Bài nào chặn thì ghi rõ: *"thử 3 cách, đều 403, không đoán nội dung"*.

⏸ Hỏi Trang.

## Chặng 4 — Bảng khoảng trống

Dựng bảng: **nội dung người đọc cần × từng đối thủ × bài của khách**.

Đọc ra ba nhóm:
- Mình ❌ đối thủ ✅ → **đang thua, bù trước tiên**
- Cả hàng ❌ → **khoảng trống vàng**
- Cả hàng ✅ → bắt buộc có, nhưng phải viết khác đi

⚠️ **Luật đã học:** khoảng trống vàng **không tự động là cơ hội**. Phải hỏi thêm:
*người đọc có thật sự cần thứ đó ở giai đoạn này không?* Thứ nào không qua được
câu hỏi đó thì bỏ, đừng nhét vào cho đủ.

⏸ Hỏi Trang.

## Chặng 5 — Bảng CẮT và bảng BỔ SUNG

Không đập đi xây lại. Chỉ hai việc:

**Bảng CẮT — nội dung thừa:**

| Mục hiện tại | Cắt gì | Còn lại |
|---|---|---|

Dấu hiệu thừa: nhiều mục lý thuyết liên tiếp trước khi tới thứ người đọc vào để xem ·
hai mục nói cùng một chuyện · đoạn khen chung chung không số liệu · nội dung đã có
bài riêng trên site.

**Bảng BỔ SUNG — thứ người đọc cần mà đối thủ chưa có:**

| Bổ sung | Lấy dữ liệu ở đâu | Vì sao chắc ăn |
|---|---|---|

Xếp theo thứ tự ưu tiên: bù chỗ **đang thua** trước, rồi mới tới khoảng trống vàng.

Ghi rõ **cắt bao nhiêu từ, thêm bao nhiêu từ** — mục tiêu là bài không dài thêm
nhưng mọi chữ đều phục vụ intent.

⏸ Hỏi Trang.

## Chặng 6 — Đề xuất cấu trúc

**Nếu bài cũ đang có thứ hạng: giữ nguyên bộ khung và giữ nguyên URL.**
Không đổi tên những mục đã chạy được. Chỉ đổi tên mục khi nội dung bên trong
thay đổi thật sự.

**Học luật đặt heading từ chính bài đang top của khách**, đừng áp luật của mình.
Cách học: liệt kê toàn bộ heading của bài đó, tìm ra công thức lặp lại.
Chi tiết ở `LUAT-DAT-HEADING.md`.

Kèm theo cấu trúc phải có:
- **Bảng phân bổ từ khóa**: key chính ở đâu, key mở rộng ở đâu, bao nhiêu lần
- **Danh sách liên kết nội bộ** sang các bài đã có, để không tự cạnh tranh
- **Danh sách lỗi sai trong bài cũ phải vá**

⏸ Hỏi Trang.

## Chặng 7 — Viết và xuất

Đọc `cong-cu/toi-uu-content-seo/luat-viet-content.md` trước khi đặt bút.

**Xuất đúng định dạng site khách.** Xin Trang mã HTML của một bài đã đăng, soi ra
quy ước của họ rồi bắt chước y hệt: cách bọc thẻ, cách chèn ảnh, cách làm bảng,
khối liên kết nội bộ. Dán vào là ăn theo giao diện sẵn, không phải sửa tay.

Trang thường muốn **mã HTML xuất thẳng trong khung chat** để copy, không cần file.
Hỏi trước nếu chưa rõ.

Kèm theo bài:
- Danh sách `[CẦN TRANG BỔ SUNG: …]`
- Việc cần làm sau khi dán (chèn ảnh, gắn liên kết, xóa mục lục cũ)
- Số liệu nào còn đang chờ khách chốt

**Luôn hỏi hai câu:** (a) nhìn có lỗi hiển thị gì không, (b) có ưng không, muốn chỉnh gì.
