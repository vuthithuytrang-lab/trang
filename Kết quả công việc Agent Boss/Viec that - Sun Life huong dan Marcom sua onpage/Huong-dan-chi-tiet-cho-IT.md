# Sun Life – Checklist Technical: cột "Hướng dẫn chi tiết" cho IT

Định hướng hướng sửa cho IT (không phải code chi tiết). Các phần trong [ngoặc vuông] là chỗ IT điền thông tin thật.

---

## 19 – Cấu trúc URL / Trang 404

```
Mục tiêu: mọi URL không tồn tại trên website đều trả về mã 404 và hiển thị trang 404 tùy chỉnh. URL trên thanh địa chỉ giữ nguyên, không bị chuyển hướng.

Hiện tại:
- URL có /vn/ (vd: https://www.sunlife.com.vn/vn/ve-csdvdav): đã đúng, không cần sửa.
- URL không có /vn/ (vd: https://www.sunlife.com.vn/abc): đang bị 301 về trang chủ https://www.sunlife.com.vn/vn/?vgnLocale=vi_VN → cần sửa.

Hướng sửa:
1. Tìm quy tắc chuyển hướng đang áp dụng cho các URL không có /vn/ (thường nằm trong cấu hình máy chủ web, file rewrite hoặc cấu hình định tuyến của CMS).
2. Thu hẹp quy tắc đó lại:
- Trang chủ gốc https://www.sunlife.com.vn/ → giữ chuyển về /vn/ như hiện tại.
- URL không có /vn/ nhưng có trang tương ứng (vd: /abc mà /vn/abc tồn tại) → 301 về đúng trang tương ứng đó, không đẩy về trang chủ.
- URL không có trang tương ứng → không chuyển hướng, trả mã 404 và hiển thị trang 404 tùy chỉnh đang dùng cho nhánh /vn/.
3. Trang 404 phải trả đúng mã 404, không trả mã 200.

Cách kiểm tra: dán https://www.sunlife.com.vn/abc vào công cụ httpstatus.io → đạt khi kết quả chỉ có 1 bước, mã 404, không có 301.
```

## 21 – Schema trang chủ (Organization)

```
Hướng sửa: dán đoạn mã dưới đây vào thẻ <head> của trang chủ https://www.sunlife.com.vn/vn/ (chỉ trang chủ). Điền thông tin thật vào các chỗ trong [ngoặc vuông]; trường nào không có thì xóa cả dòng đó.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Tên pháp lý đầy đủ của công ty]",
  "alternateName": "Sun Life Việt Nam",
  "url": "https://www.sunlife.com.vn/vn/",
  "logo": "[URL file ảnh logo]",
  "telephone": "[Số tổng đài]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Số nhà, tên đường]",
    "addressLocality": "[Quận/Phường]",
    "addressRegion": "[Tỉnh/Thành phố]",
    "addressCountry": "VN"
  },
  "sameAs": [
    "[Link Facebook]",
    "[Link YouTube]",
    "[Link LinkedIn]"
  ]
}
</script>

Cách kiểm tra: dán URL trang chủ vào https://validator.schema.org → thấy mục Organization, không báo lỗi là đạt.
```

## 23 – Schema trang sản phẩm (Product)

```
Hướng sửa: cài 1 lần vào template trang sản phẩm để mọi trang sản phẩm tự sinh schema, không làm tay từng trang.

Mẫu cho 1 trang (vd: https://www.sunlife.com.vn/vn/ca-nhan/tai-nan/song-an-20/). Các chỗ trong [ngoặc vuông] là trường lấy tự động từ dữ liệu của từng sản phẩm:

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Tên sản phẩm – lấy theo H1 của trang]",
  "description": "[Mô tả ngắn – lấy theo meta description hoặc đoạn giới thiệu đầu trang]",
  "image": "[URL ảnh banner/ảnh đại diện sản phẩm]",
  "url": "[URL trang sản phẩm]",
  "category": "[Tên danh mục – vd: Bảo hiểm tai nạn]",
  "brand": {
    "@type": "Brand",
    "name": "Sun Life Việt Nam"
  }
}
</script>

Lưu ý:
- Sản phẩm nào thiếu trường nào thì bỏ trường đó, không để trống.
- Nội dung trong schema phải khớp với nội dung hiển thị trên trang.

Cách kiểm tra: dán URL 2–3 trang sản phẩm bất kỳ vào https://validator.schema.org → mỗi trang đều có Product với đúng tên sản phẩm của trang đó.
```

## 24 – Schema trang bài viết (Article)

```
Hướng sửa: website đã có schema Article nhưng còn thiếu trường. IT đối chiếu với mẫu dưới đây, bổ sung các trường còn thiếu vào template bài viết để tất cả bài viết tự lấy dữ liệu. Trường nào bài viết không có thì bỏ qua.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Tiêu đề bài – lấy theo H1]",
  "description": "[Meta description của bài]",
  "image": "[URL ảnh đại diện bài viết]",
  "datePublished": "[Ngày đăng – dạng 2026-10-01]",
  "dateModified": "[Ngày cập nhật gần nhất – dạng 2026-10-01]",
  "author": {
    "@type": "Organization",
    "name": "Sun Life Việt Nam"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Sun Life Việt Nam",
    "logo": {
      "@type": "ImageObject",
      "url": "[URL file ảnh logo]"
    }
  },
  "mainEntityOfPage": "[URL bài viết]"
}
</script>

Nếu bài có phần Câu hỏi thường gặp thì thêm schema FAQPage cho phần đó (cách làm như mục 25).

Cách kiểm tra: dán URL 2–3 bài viết vào https://validator.schema.org → Article đủ các trường trên, không báo lỗi.
```

## 25 – Schema trang FAQ (FAQPage)

```
Hướng sửa: cài vào template trang Câu hỏi thường gặp https://www.sunlife.com.vn/vn/dich-vu-khach-hang/cau-hoi-thuong-gap/ để tự lấy toàn bộ các cặp câu hỏi – câu trả lời đang hiển thị trên trang. Mẫu với 2 câu hỏi, các câu còn lại lặp lại theo cùng cấu trúc:

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Câu hỏi 1]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Câu trả lời 1]"
      }
    },
    {
      "@type": "Question",
      "name": "[Câu hỏi 2]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Câu trả lời 2]"
      }
    }
  ]
}
</script>

Lưu ý: câu hỏi và câu trả lời trong schema phải giống hệt chữ hiển thị trên trang. Câu hỏi nằm ở tab ẩn/thu gọn vẫn đưa vào được.

Cách kiểm tra: dán URL trang vào https://validator.schema.org → có FAQPage, số câu hỏi đúng bằng số câu trên trang.
```

## 34 – Meta robots

```
Hướng sửa: sửa trong template dùng chung của website.

1. Các trang cần lên Google (trang chủ, sản phẩm, danh mục, bài viết, trang tĩnh): đổi
<meta name="robots" content="index"/>
thành
<meta name="robots" content="index, follow">

2. Các trang không cần lên Google (trang 404, trang cảm ơn sau khi gửi form, trang kết quả tìm kiếm nội bộ): đặt
<meta name="robots" content="noindex, nofollow">

3. Mỗi trang chỉ có 1 thẻ meta robots.

Cách kiểm tra: mở trang, nhấn Ctrl + U, Ctrl + F tìm chữ "robots" → chỉ có 1 kết quả, đúng giá trị như trên.
```

## 44 – Heading trang chủ

```
Nguyên tắc: thẻ heading (H1–H6) chỉ dùng cho tiêu đề của nội dung chính trong trang. Các phần lặp lại trên mọi trang (header, menu, danh sách quốc gia, footer, form Đăng ký tư vấn, thông báo sau khi gửi form) không dùng thẻ heading.

Hướng sửa:
1. Sửa trong template dùng chung (header, menu, footer, form) để áp dụng cho toàn bộ website. Đổi các thẻ H2/H3/H4 ở các phần này thành thẻ thường (div, p hoặc span), giữ nguyên class CSS để giao diện không thay đổi.
Ví dụ: <h2 class="abc">Canada</h2> → <div class="abc">Canada</div>
Các phần cần đổi:
- Danh sách quốc gia: Bermuda, Canada, Trung Quốc…
- Menu: Khách hàng cá nhân, Khách hàng doanh nghiệp, Dịch vụ, Về Sun Life và các mục con
- Footer: Công ty Bảo hiểm Nhân thọ có Dịch vụ Khách hàng tốt nhất 2024, Truy cập nhanh, Sản phẩm, Cơ hội nghề nghiệp, Về chúng tôi, Liên hệ
- Form và thông báo: Đăng ký tư vấn…, Chuyên viên tư vấn của Sun Life sẽ…, Cảm ơn bạn đã đăng ký tư vấn, Sự cố kỹ thuật…, Đăng ký nhận tin quảng cáo…
2. Xóa các thẻ heading rỗng (không có chữ).
3. Thêm 1 thẻ H1 duy nhất cho trang chủ: "Công Ty Bảo Hiểm Nhân Thọ Sun Life Việt Nam" (có thể lấy theo title trang). H1 phải là chữ hiển thị trên trang (vd dòng chữ chính ở banner đầu trang), không dùng chữ ẩn.
4. Phần nội dung chính: giữ đúng cấp heading như cột "Phương án đề xuất". Heading nào không có trong danh sách đề xuất (vd: khối tin tức/chiến dịch SUN – Vững Bước, Sống Chất 2.0…, Các công cụ, Chọn sản phẩm Bảo hiểm, Trò chuyện cùng chuyên gia, mySunlife) thì đổi thành thẻ thường.

Cách kiểm tra: cài tiện ích Chrome "Detailed SEO Extension", mở trang → tab Headings: chỉ còn đúng các heading như đề xuất, có đúng 1 H1.
```

## 45 – Heading trang dịch vụ

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form và thông báo sau khi gửi form; xóa heading rỗng). Sửa 1 lần trong template là áp dụng cho toàn bộ website.

Riêng trang dịch vụ (vd: https://www.sunlife.com.vn/vn/dich-vu-khach-hang/), sửa trong template trang dịch vụ:
1. Giữ 1 H1: "Sun Life nỗ lực giúp khách hàng có cuộc sống tươi sáng hơn".
2. Đổi H4 "Sổ tay Khách Hàng", "Hướng dẫn thanh toán phí", "Yêu cầu quyền lợi bảo hiểm" thành H3.
3. Bỏ heading ở các thông báo sau khi gửi form ("Cảm ơn bạn đã đăng ký tư vấn…", "Sự cố kỹ thuật…") và phần "Thông tin liên hệ" lặp lại.
4. Các heading còn lại sắp xếp đúng như cột "Phương án đề xuất".

Cách kiểm tra: như mục 44.
```

## (Không có STT) – Heading trang danh mục lớn

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form; xóa heading rỗng).

Riêng trang danh mục lớn (vd: https://www.sunlife.com.vn/vn/ca-nhan/), sửa trong template trang danh mục lớn:
1. Trang đang có 2 H1, trong đó 1 H1 rỗng → xóa H1 rỗng, giữ 1 H1 duy nhất: "Bảo hiểm nhân thọ dành cho Khách hàng cá nhân".
2. Đổi tên các nhóm sản phẩm (Bảo hiểm tích lũy, Bảo Hiểm Sức Khỏe, Bảo hiểm đầu tư, Bảo Hiểm Tai Nạn, Bảo Vệ Vững Chắc) từ H4 thành H3.
3. Giữ H2 "Hỗ trợ". Các heading còn lại không có trong cột "Phương án đề xuất" thì đổi thành thẻ thường.

Cách kiểm tra: như mục 44.
```

## 46 – Heading trang danh mục con

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form; xóa heading rỗng).

Riêng trang danh mục con (vd: https://www.sunlife.com.vn/vn/ca-nhan/tiet-kiem/), sửa trong template trang danh mục con:
1. Xóa 1 H1 rỗng và 1 H2 rỗng, giữ 1 H1 duy nhất (vd: "Bảo hiểm tích lũy").
2. Tên các sản phẩm trong danh mục (vd: SUN – Khí Chất, SUN – Vì Nhà Mình) đổi từ H4 thành H3.
3. Các mục trong khối Hỗ trợ (Làm sao quản lý tài chính hiệu quả, Khoảnh khắc sống, Các công cụ, Bí quyết…) đổi từ H4 thành H3.
4. Sắp xếp đúng như cột "Phương án đề xuất".

Cách kiểm tra: như mục 44.
```

## 47 – Heading trang danh mục bài viết

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form; xóa heading rỗng).

Riêng trang danh mục bài viết (vd: https://www.sunlife.com.vn/vn/ca-nhan/lam-sao-quan-ly-tai-chinh-hieu-qua/), sửa trong template trang danh mục bài viết:
1. Xóa H1 rỗng, giữ 1 H1 duy nhất là tên danh mục (vd: "Làm sao quản lý tài chính hiệu quả").
2. Tiêu đề từng bài viết trong danh sách đang là H1 → đổi thành H3 (sửa trong khung hiển thị 1 bài viết của danh sách, áp dụng cho mọi danh mục).
3. Bỏ heading ở đoạn "Sống chủ động hơn cho bản thân và gia đình" và các khối phụ cuối trang ("Khởi đầu ngay cuộc sống tươi sáng hơn", "Giải pháp tài chính", "Khoảnh khắc sống") → đổi thành thẻ thường.

Cách kiểm tra: như mục 44.
```

## 48 – Heading trang bài viết

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form; xóa heading rỗng).

Riêng trang bài viết (vd: https://www.sunlife.com.vn/vn/ca-nhan/lam-sao-quan-ly-tai-chinh-hieu-qua/bao-hiem-nhan-tho/bao-hiem-nhan-tho-hon-hop-la-gi-khi-nao-la-lua-chon-phu-hop/), sửa trong template trang bài viết:
1. Giữ nguyên H1 là tiêu đề bài và các heading trong thân bài (H2, H3 do người viết đặt). Phần này đã đúng.
2. Bỏ heading ở các khối phụ cuối bài: "Khởi đầu ngay cuộc sống tươi sáng hơn", "Giải pháp tài chính", "Khoảnh khắc sống" → đổi thành thẻ thường.

Cách kiểm tra: như mục 44. Danh sách heading chỉ còn H1 và các heading trong thân bài.
```

## 49 – Heading Page tĩnh

```
Phần chung: làm như mục 44, bước 1 và 2 (bỏ heading ở header, menu, footer, form; xóa heading rỗng).

Riêng trang tĩnh (vd: https://www.sunlife.com.vn/vn/ve-chung-toi/gioi-thieu-cong-ty/), sửa trong template trang tĩnh:
1. Bỏ heading H2 "Thông tin chung" (đang nằm trước H1) → đổi thành thẻ thường.
2. Giữ 1 H1 là tên trang (vd: "Giới thiệu Công ty") và các H3 nội dung bên dưới như cột "Phương án đề xuất".

Cách kiểm tra: như mục 44.
```

## (Không có STT) – Menu

```
Hướng sửa: gắn link cho tên các danh mục sản phẩm lớn trên menu (Bảo hiểm tích lũy, Bảo hiểm tai nạn, Bảo hiểm sức khỏe…) để khi bấm vào sẽ dẫn về trang danh mục tương ứng.
Ví dụ: "Bảo hiểm tích lũy" → https://www.sunlife.com.vn/vn/ca-nhan/tiet-kiem/

Với các mục chưa có trang đích phù hợp (theo phản hồi của Sun Life): tạm giữ dạng chữ không gắn link, gửi danh sách các mục này cho SEONGON để đề xuất trang đích sau.

Cách kiểm tra: bấm vào từng tên danh mục trên menu → mở đúng trang danh mục, không ra trang lỗi.
```

## 79 – Nofollow link

```
Mục tiêu: link trỏ ra website bên ngoài (không thuộc hệ thống của Sun Life) có thuộc tính rel="nofollow".
Ví dụ: <a href="https://www.website-ben-ngoai.com/" rel="nofollow">chữ gắn link</a>

Cách check trong CMS:
1. Mở 1 bài viết bất kỳ, chèn thử 1 link ra website bên ngoài.
2. Xem hộp thoại chèn link có tùy chọn nofollow / thuộc tính rel không.
3. Nếu không có: chuyển trình soạn thảo sang chế độ HTML, tự thêm rel="nofollow" vào link, lưu và xuất bản.
4. Mở bài ngoài website, nhấn Ctrl + U, tìm link vừa chèn → còn rel="nofollow" là CMS hỗ trợ; bị mất là CMS đang tự xóa thuộc tính này.

Hướng sửa nếu CMS chưa hỗ trợ (chọn 1 trong 2):
- Cách 1: thêm ô tích "nofollow" trong hộp thoại chèn link của trình soạn thảo.
- Cách 2 (khuyến nghị): cài tự động: mọi link có tên miền khác sunlife.com.vn và các website trong hệ thống của Sun Life đều tự gắn rel="nofollow" khi hiển thị ra trang.
```
