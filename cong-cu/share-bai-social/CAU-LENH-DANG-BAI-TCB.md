# Câu lệnh đăng bài TCB — bản dùng lại

> Đây là câu lệnh agent đã chạy cho đợt **TCB 10/10/2026** (40 từ khóa × WordPress + Webflow + Wix).
> Lần sau chỉ cần sửa các chỗ trong **[ngoặc vuông]** rồi dán cả khung bên dưới vào chat.
> Chi tiết kỹ thuật (cách kết nối, quy tắc viết, lỗi bài gốc) nằm ở `HUONG-DAN-TCB.md`. Câu lệnh này bắt agent đọc file đó trước.

---

```text
Đăng bài share Techcombank đợt [TCB 10/10].

1. ĐỌC TRƯỚC
- Đọc CLAUDE.md, cong-cu/share-bai-social/HUONG-DAN-TCB.md và các skill share-bai-wp, share-bai-webflow, share-bai-wix.
- Chìa đăng nhập: tôi đính kèm file .txt / .json. Không in chìa ra màn hình, không gắn vào link, không commit.

2. DANH SÁCH BÀI
- Sheet: 1UQYdaL67rujn4WBbV2r3QYTvQWuIMhLZCJyU0K8TzVk, tab "Share social".
- Lấy [40] từ khóa ở cột D, từ dòng [529] đến dòng [958]. URL bài gốc ở cột F (techcombank.com/thong-tin/blog/...).
- Đăng lên: [WordPress, Webflow, Wix]. Mỗi từ khóa 1 bài trên mỗi nền tảng.

3. VIẾT BÀI
- Đọc bài gốc qua công cụ đọc web. Không đọc được thì bỏ qua và báo tôi, tuyệt đối không bịa.
- Làm đúng quy tắc phần C của HUONG-DAN-TCB.md: 900–1100 từ, giữ đúng số liệu, không chép câu,
  đúng 1 link trên từ khóa chính trỏ về URL cột F, không hotline/email, không từ "nhất / số 1 / hàng đầu".
- Cùng 1 từ khóa thì bài ở mỗi nền tảng phải khác tiêu đề, khác đoạn mở, khác cách sắp ý, khác đường dẫn (slug).
- Tự soát theo mục C6 trước khi đăng.

4. ẢNH ĐẠI DIỆN (bắt buộc mọi bài)
- Tự dựng ảnh 1200×630: nền xanh đậm, dòng nhỏ "Kiến thức tài chính doanh nghiệp", từ khóa, tiêu đề.
  Không dùng logo Techcombank. Mỗi nền tảng một kiểu ảnh khác nhau.
- Đăng xong mở bài kiểm tra ảnh đã hiện.

5. NHỊP ĐĂNG — tránh chết tài khoản
- Mỗi nền tảng cách nhau khoảng 25–55 phút một bài, lệch giờ ngẫu nhiên, các nền tảng so le nhau.
- Không gửi hàng loạt lệnh lên cùng một trang. Bị chặn (403/429) thì dừng, chờ vài giờ rồi thử lại.
- WordPress được hẹn giờ trước. Webflow và Wix: chuẩn bị bản nháp trước ~13 phút, đến giờ mới bấm đăng.
- Phải xong trong [ngày ...]. Nếu không kịp thì báo tôi, không rút ngắn khoảng cách.
- Tự đặt nhắc (send_later) cho bước kế tiếp, mỗi lúc chỉ 1 nhắc chờ.
  Thêm 1 nhắc mỗi giờ để kiểm tra vòng chạy còn sống; nếu có bài quá hạn mà chưa đăng thì đăng bù ngay.

6. GHI LINK VÀO SHEET (sau mỗi bài đăng xong)
- Tìm lại khối của từ khóa mỗi lần ghi (người khác hay chèn/xóa dòng). Khối = từ dòng có từ khóa ở cột D
  đến dòng ngay trước từ khóa kế tiếp.
- Ghi vào dòng trống đầu tiên trong khối: H = "[WordPress / Webflow / Wix] - Trang", I = link bài, J = ngày đăng (d/m/yyyy).
- Số dòng = dòng đầu của vùng đọc + vị trí đếm từ 0. Đọc lại trước và ngay sau khi ghi.
- Không ghi đè ô có sẵn, không chèn dòng, không sang khối khác. Khối hết dòng trống thì báo tôi.
- WordPress: ghi link đẹp /năm/tháng/ngày/slug/ theo ngày bài thật sự lên. Link không kết thúc bằng "/" (trừ WordPress).

7. KHI XONG
- Kiểm tra lại từng nền tảng đủ [40/40] bài đã lên thật, kể cả bài WordPress hẹn giờ
  (WordPress có lúc không tự đăng bài hẹn giờ thì đăng tay và sửa link trên sheet).
- Xóa các nhắc tự động của đợt này.
- Lưu nhật ký các bài đã đăng vào cong-cu/share-bai-social/[tcb-dot-10-10]/, commit và push.
- Gửi tôi bản tổng kết bằng lời dễ hiểu: mỗi nền tảng bao nhiêu bài, bài nào trễ hoặc lỗi, vì sao.
  Nói thật nếu có gián đoạn.

Chỉ nhắn tôi khi có thay đổi đáng kể hoặc khi cần tôi làm gì.
```

---

## Ghi chú từ đợt 10/10 (để lần sau làm tốt hơn)

| Chuyện đã xảy ra | Lần sau |
|---|---|
| Blogger bị chặn 403 sau ~19 bài liên tục → chuyển các bài còn lại sang Webflow | Blogger tạo từng bài, cách ≥ 20 phút |
| Một lần ghi nhầm dòng sheet (đè dòng "Wix" của khối "thuế vat là gì"), đã khôi phục | Luôn đọc lại khối trước và sau khi ghi |
| Phiên chạy bị dừng từ 21:20 ngày 11/10 đến sáng 14/10 → 2 bài Wix và 1 bài WordPress lên trễ | Nhắc mỗi giờ phải kiểm tra bài quá hạn và đăng bù ngay |
| Bài WordPress hẹn 21:52 ngày 11/10 không tự lên | Khi chốt sổ, kiểm tra bài hẹn giờ đã thật sự lên chưa |
