# Năm cổng chặn bắt buộc

Năm lỗi dưới đây đều dẫn tới kết luận sai, phần lớn đã xảy ra thật trong lần chạy đầu tiên.
Chạy đủ năm kiểm chứng trước khi viết bất cứ đề xuất nào.

## 1. Trang render bằng JavaScript

Dấu hiệu: dưới 300 từ nội dung chính mà HTML trên 80KB.

Nếu vẫn đưa vào bảng so sánh thì trang của mình sẽ thắng mọi chỉ số và hệ thống kết luận
"nội dung đã đủ" — sai hoàn toàn vì thực ra không đo được đối thủ.

Xử lý: loại khỏi mọi bảng so sánh, đếm và ghi rõ số lượng.
Lần chạy tham chiếu: 26/764 trang bị loại.

## 2. Tình trạng thật của URL — kiểm trước khi kết luận bất cứ điều gì

**Không đề xuất sửa một trang khi chưa biết trang đó còn sống hay không.** Một URL xuất hiện
trong file check top hoặc Search Console không có nghĩa là nó đang hoạt động: dữ liệu có độ trễ
hàng tuần tới hàng tháng.

Chạy `scripts/verify_urls.py` cho **mọi URL nội bộ**, không chỉ URL nghi ngờ. Script phân loại
và mỗi loại có cách xử lý riêng:

| Tình trạng | Nghĩa là | Phải làm gì trước khi viết đề xuất |
|---|---|---|
| 200, index được | Bình thường | Dùng như thường |
| **404 hoặc 410** | Trang đã mất | Xử lý trước tiên: khôi phục nội dung hoặc 301 về trang thay thế. Tuyệt đối không viết "bổ sung H2 cho trang này" |
| **5xx** | Lỗi máy chủ | Kiểm hạ tầng trước. Mọi kết luận về nội dung đều vô nghĩa khi trang không phục vụ được |
| **301 / 302** | Đã chuyển hướng | Loại khỏi phép đếm ăn thịt từ khoá. Không đề xuất sửa. Kiểm cả chuỗi: nếu chặng cuối không phải 200 thì chuỗi hỏng, đó mới là việc cần làm |
| **noindex** | Không bao giờ lên top được | Đừng đề xuất tối ưu nội dung. Việc cần làm là quyết định có bỏ noindex không |
| **canonical trỏ nơi khác** | Thứ hạng dồn về trang canonical | Xét lại vai trò hai trang trước khi kết luận trang nào đang ăn thịt trang nào |
| **200 nhưng dưới 300 từ** | Có thể render bằng JavaScript | Xem cổng chặn 1 |

Ba lỗi hay gặp nhất nếu bỏ qua bước này:

1. Báo cáo "ba trang đang ăn thịt nhau" trong khi chúng đã 301 đúng. Đã xảy ra thật:
   4/159 URL trong lần chạy tham chiếu là 301, riêng một URL còn 3.783 lượt hiển thị trong
   Search Console dù đã chuyển hướng nhiều tháng.
2. Viết cả một outline chi tiết cho trang đã 404.
3. Đề xuất nâng mật độ từ khoá cho trang đang noindex.

Kết quả lưu ở `data/url_status.json`. Các script sau đọc lại file này để loại URL đã 301
khỏi phép đếm ăn thịt từ khoá.

## 3. Đã được lập chỉ mục chưa — kiểm bằng API, không dùng cú pháp site:

Mục 2 trả lời "trang có thể index được không". Mục này trả lời câu khác hẳn:
**Google đã thực sự index chưa, và có gộp trang này vào trang khác không.**

Một trang trả 200, không noindex, canonical tự trỏ — vẫn có thể chưa được index.
Khi đó mọi việc tối ưu nội dung đều vô nghĩa cho tới khi trang vào được chỉ mục.

### Không dùng `site:`

| Cách | Vì sao không dùng |
|---|---|
| Gõ `site:example.com/duong-dan` trên Google | Google chặn truy vấn tự động. Đã kiểm chứng ở skill `seo-gap`: trang không tải xong sau 45 giây |
| Đọc số kết quả của `site:domain` | Con số đó là ước lượng thô, dao động mạnh giữa hai lần tra, và không cho biết **vì sao** một URL không được index |

### Dùng URL Inspection API

```bash
python3 scripts/index_status.py --data data --site <property>
```

Cùng credential Search Console đã dùng ở bước 4. Trả về đúng thứ cần biết:

| Trường | Cho biết |
|---|---|
| `verdict` | PASS nghĩa là đã index; khác PASS thì chưa |
| `coverageState` | Vì sao chưa index: đã thu thập nhưng chưa index, đã phát hiện nhưng chưa thu thập, bị loại vì trang trùng lặp… |
| `googleCanonical` so với `userCanonical` | **Hai giá trị khác nhau là bằng chứng trực tiếp Google gộp trang này vào trang khác** — mạnh hơn mọi suy luận từ thứ hạng |
| `lastCrawlTime` | Trang lâu chưa được crawl thì nội dung mới sửa chưa có tác dụng |
| `pageFetchState`, `robotsTxtState`, `indexingState` | Vướng ở khâu nào |

Quota: 2.000 URL mỗi ngày và 600 mỗi phút cho mỗi property. Script lưu tiến độ và chạy tiếp
được, ưu tiên URL có nhiều lượt hiển thị trước.

### Hai dạng ăn thịt từ khoá, phân biệt bằng canonical

| Dạng | Dấu hiệu | Cách xử lý |
|---|---|---|
| **Google đã gộp trang** | `googleCanonical` khác `userCanonical` | Google đã chọn xong trang đại diện. Việc cần làm là xác nhận nó chọn đúng trang; nếu sai thì sửa tín hiệu để đổi lựa chọn của Google |
| **Google đang phân vân** | Canonical trùng nhau ở mọi trang, nhưng cùng một truy vấn lại có nhiều URL nội bộ nhận hiển thị trên Search Console | Google chưa gộp, mỗi lần tìm lại chọn một trang. Việc cần làm là phân vai dứt khoát: gỡ nội dung trùng, đổi anchor liên kết nội bộ, cho một trang thắng rõ ràng |

Đo thật trên dự án tham chiếu: 70 URL nhiều lượt hiển thị nhất, **không URL nào** có
`googleCanonical` khác `userCanonical`, trong khi Search Console cho thấy 231/302 từ khoá có
từ hai URL nội bộ cùng nhận hiển thị. Kết luận: site đó thuộc dạng thứ hai — Google phân vân,
chưa gộp. Nếu chỉ nhìn thứ hạng thì hai dạng trông giống nhau, nhưng cách chữa khác nhau.

### Ba việc bắt buộc rút ra

1. **URL chưa index thì không viết việc tối ưu nội dung.** Việc cần làm là đưa nó vào chỉ mục:
   sửa liên kết nội bộ, gửi sitemap, xử lý nguyên nhân trong `coverageState`.
2. **`googleCanonical` khác `userCanonical` thì phải nêu trong báo cáo.** Đây là ăn thịt từ khoá
   đã được Google xác nhận, không còn là suy đoán. Ghi rõ Google đang gộp về trang nào.
3. **`lastCrawlTime` quá cũ thì ghi kèm khi đề xuất sửa nội dung** — người đọc cần biết bao lâu
   nữa thay đổi mới có hiệu lực.

## 4. Trang đã tồn tại

File check top chỉ thấy trang lọt top 100. Trang yếu không lọt vẫn tồn tại và vẫn nhận
hiển thị. Đề xuất "tạo trang mới" khi trang đã có là lỗi nặng: tốn tiền viết lại từ đầu
thay vì tối ưu trang sẵn có.

Xử lý: bước 5 bắt buộc — lấy danh sách trang từ Search Console, đối chiếu với tập đã crawl,
crawl phần thiếu. Chỉ đề xuất tạo mới sau khi xác nhận không có trang nào phục vụ chủ đề đó.
Lần chạy tham chiếu: 3 trang được đề xuất "tạo mới" thực ra đã tồn tại, trong đó một trang
9.041 từ mạnh hơn mọi đối thủ trong cụm.

## 5. Vị trí trung bình không phải thứ hạng

Vị trí của Search Console là trung bình có trọng số theo lượt hiển thị, gộp mọi thiết bị,
mọi tỉnh thành, cả kỳ đo. Nó luôn thấp hơn thứ hạng đo tại một điểm — đó là đặc tính của
phép đo, không phải bằng chứng thứ hạng kém hơn.

Xử lý: file check top là dữ liệu thật. Search Console chỉ dùng cho ăn thịt từ khoá,
trang ngoài top, hiển thị và tỷ lệ nhấp. Khi trình bày hai con số cạnh nhau phải giải thích
chúng đo hai thứ khác nhau.

## Kiểm chứng thêm khi có nghi ngờ

- Chỉ số bất thường trên một trang: crawl lại trực tiếp trang đó, đừng tin cache
- Vị trí GSC tốt bất ngờ trên mẫu nhỏ: yêu cầu tối thiểu 100 lượt hiển thị mới kết luận
- Trang chủ hoặc trang danh mục xếp hạng tốt hơn trang dịch vụ: kiểm bằng cả hai nguồn
