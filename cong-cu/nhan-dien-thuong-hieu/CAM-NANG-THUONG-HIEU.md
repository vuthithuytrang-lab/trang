# Cẩm nang nhận diện thương hiệu — SEONGON

> **Agent đọc file này TRƯỚC KHI thiết kế bất cứ ấn phẩm nào cho Trang.**
> Áp dụng cho: trang web, landing page, email, báo cáo, slide, ảnh mạng xã hội, brief gửi thiết kế.
>
> Phiên bản 1 — dựng ngày 08/09/2026. **Chưa đủ chất liệu, xem mục 9.**

---

## 1. Chất liệu này lấy từ đâu

Mọi con số dưới đây đọc thẳng từ tài sản thật của công ty, không phải nhìn ảnh đoán màu:

| Thứ | Lấy từ |
|---|---|
| Mã màu | File định kiểu của trang chủ `seongon.com` (`main.min.css`, `all.min.css`) |
| Màu logo | Đếm điểm ảnh trong chính file logo trên web |
| Kiểu chữ | Dòng `body{font-family:Gilroy,sans-serif}` trong mã nguồn trang chủ |
| Phong cách hình ảnh | Ảnh thật đang chạy trên trang chủ |
| File logo | Tải từ thư viện ảnh của website |

**Chưa có:** file logo gốc độ phân giải cao, bộ ấn phẩm công ty đang dùng. Xem mục 9.

---

## 2. Logo — quy tắc cứng

### File gốc phải dùng

```
cong-cu/nhan-dien-thuong-hieu/logo-goc/SEONGON-logo-ngang.webp
cong-cu/nhan-dien-thuong-hieu/logo-goc/SEONGON-favicon.ico
```

### ⛔ Tuyệt đối không vẽ lại logo

Không dựng lại chữ SEONGON bằng font khác. Không vẽ lại mũi tên. Không tự chế biểu tượng "na ná".
**Mọi ấn phẩm phải nhúng đúng file trên.** Logo vẽ tay trông giống 95% vẫn là logo sai.

### Logo gồm hai phần

1. **Chữ SEONGON** — chữ in đậm, màu xanh dương `#004AEF`
2. **Dòng phụ** — `AI-First` (xanh mint `#07EF9C`) + mũi tên chéo lên + `Search Marketing Growth Partner` (xanh dương)

Không tách rời, không đổi thứ tự, không dịch dòng phụ sang tiếng Việt.

### Đặt logo thế nào

| Việc | Quy tắc |
|---|---|
| Khoảng trống quanh logo | Chừa trống ít nhất bằng **chiều cao chữ S** ở mọi phía. Không để chữ, ảnh hay viền lấn vào |
| Bề rộng nhỏ nhất | **140px** trên màn hình · **35mm** khi in. Nhỏ hơn là dòng phụ không đọc được |
| Vị trí quen thuộc | Góc trên bên trái (web, tài liệu) hoặc chính giữa trên cùng (thư, bìa) |
| Nền dùng được | Trắng, hoặc xám rất nhạt `#F3F3F6` |
| **Nền tối** | **Không đặt thẳng logo lên nền xanh/navy.** Chữ SEONGON cũng màu xanh nên chìm gần hết — đã thử và chụp lại làm bằng. Phải **kê một tấm nền trắng bo góc** bên dưới logo |
| Nền không dùng được | Ảnh chụp rối, mọi nền xanh khi chưa kê tấm trắng, nền màu nóng |

---

## 3. Màu — bảng mã chính thức

### Màu chủ đạo

| Màu | Mã | Dùng vào |
|---|---|---|
| 🔵 **Xanh SEONGON** | `#004AEF` | **Màu của logo.** Nút bấm chính, tiêu đề lớn, đường nhấn |
| 🔵 Xanh sáng | `#0D53F0` | Nền khối, dải màu, phiên bản sáng hơn của màu chính |
| 🔵 Xanh navy đậm | `#002992` | Nền tối, chân trang, chữ tiêu đề trên nền sáng |

### Màu phụ

| Màu | Mã | Dùng vào |
|---|---|---|
| 🟢 **Xanh mint** | `#07EF9C` | **Màu nhấn số 1.** Chữ cần bật lên, con số thành tích, mũi tên tăng trưởng |
| 🟢 Xanh ngọc | `#00EFB0` | Biến thể mint cho dải màu |
| 🔷 Xanh cyan | `#0DD1FF` | Cuối dải màu, biểu đồ, hình minh hoạ |
| 🟡 Vàng | `#FFCE00` | Nhấn mạnh nhẹ, huy hiệu, ngôi sao |
| 🟠 Cam | `#F68B1F` | Cảnh báo, số liệu cần chú ý. Dùng dè |

### Màu chữ và nền

| Màu | Mã | Dùng vào |
|---|---|---|
| ⚫ Đen chữ | `#151515` | Chữ nội dung trên nền sáng |
| ⚪ Trắng | `#FFFFFF` | Chữ trên nền xanh, nền ấn phẩm |
| ⚪ Xám nền | `#F3F3F6` | Nền khối phụ, nền bảng |
| ⚪ Xám viền | `#DCDCDC` | Đường kẻ, viền ô |

### Tỉ lệ dùng màu

Nhìn trang chủ mà rút ra: **xanh dương chiếm phần lớn, mint chỉ chấm phá.**

```
Xanh dương  ████████████████░░░░  ~60%   nền, khối lớn, tiêu đề
Trắng/xám   ██████░░░░░░░░░░░░░░  ~30%   chữ, khoảng thở
Mint        █░░░░░░░░░░░░░░░░░░░  ~10%   chỉ chỗ muốn người ta nhìn vào
```

Mint mà dùng nhiều thì hết thiêng. Mỗi khối chỉ nên có **một** thứ màu mint.

---

## 4. Kiểu chữ

### Chữ chính thức: **Gilroy**

Đây là font trả tiền, không có sẵn trên máy mọi người. Nên viết đầy đủ như sau:

```css
font-family: Gilroy, "Montserrat", -apple-system, BlinkMacSystemFont,
             "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

Máy nào có Gilroy thì hiện Gilroy. Máy không có sẽ rơi xuống **Montserrat** (miễn phí trên Google Fonts, hình dáng gần Gilroy nhất — cùng kiểu chữ tròn, không chân).

**Trên web công khai** thì dùng Montserrat cho chắc, vì không được phép nhúng font trả tiền lên máy chủ nếu chưa mua bản quyền web.

### Cách dùng cỡ chữ

| Loại | Cỡ | Độ đậm | Ghi chú |
|---|---|---|---|
| Tiêu đề lớn | 32–44px | 700–800 | Chữ hoa cho khẩu hiệu ngắn, chữ thường cho câu dài |
| Tiêu đề mục | 22–26px | 700 | |
| Nội dung | 15–17px | 400 | Giãn dòng 1.6–1.7 cho dễ đọc |
| Chú thích | 12–13px | 400 | Màu xám `#5A6B66` |
| Số liệu nổi bật | 28–40px | 700–800 | Màu mint hoặc xanh dương |

⚠️ **Tiếng Việt phải đủ dấu.** Font nào không có dấu tiếng Việt thì loại thẳng, không dùng.

---

## 5. Phong cách hình ảnh

Nhìn ảnh thật đang chạy trên trang chủ, phong cách rất rõ:

### Nên

- **Nền chuyển màu xanh** — từ xanh dương đậm `#002992` chuyển sang cyan `#0DD1FF`, chéo hoặc từ trên xuống
- **Hình khối 3D bóng bẩy** — biểu đồ cột, bia đích, cúp, mũi tên. Bóng mềm, không gắt
- **Mũi tên đi lên** — mô típ lặp lại xuyên suốt, thể hiện tăng trưởng
- **Số to** — "14+ NĂM", "2500+" viết cỡ lớn, tô mint để bật lên
- **Nhiều khoảng thở** — không nhồi chữ kín ảnh
- **Chữ trắng in hoa** đặt trên nền xanh cho khẩu hiệu ngắn

### Không nên

- Ảnh chụp người ở văn phòng kiểu ảnh kho (stock) chung chung
- Nền màu nóng: đỏ, tím, hồng
- Hiệu ứng đổ bóng nặng, viền dày, chữ nghệ thuật uốn éo
- Trộn quá 3 màu trong một hình

---

## 6. Giọng chữ

Từ chính khẩu hiệu của công ty: *"AI-First. Search Marketing Growth Partner"*

- Xưng **đối tác**, không xưng nhà cung cấp
- Nói bằng **con số cụ thể**, tránh tính từ rỗng ("tốt nhất", "hàng đầu" mà không có gì đỡ)
- Câu ngắn, chủ động, đi thẳng vào việc
- Tiếng Anh chỉ giữ ở thuật ngữ ngành đã quen (SEO, Search, AI-First). Còn lại viết tiếng Việt

⚠️ **Không mang cách xưng hô riêng giữa Agent và Trang** ("bạn xinh đẹp") vào bất kỳ ấn phẩm nào.
Đó là chuyện riêng trong chat.

---

## 7. Những điều nên tránh — danh sách kiểm trước khi gửi

- [ ] ❌ Vẽ lại logo thay vì nhúng file gốc
- [ ] ❌ Đổi màu logo, kéo méo, xoay nghiêng, thêm bóng đổ
- [ ] ❌ Đặt logo lên nền rối hoặc nền xanh cùng tông
- [ ] ❌ Logo nhỏ hơn 140px bề ngang
- [ ] ❌ Dùng màu ngoài bảng ở mục 3
- [ ] ❌ Dùng mint tràn lan làm mất tác dụng nhấn
- [ ] ❌ Font không có dấu tiếng Việt
- [ ] ❌ Nhúng font Gilroy lên web công khai khi chưa mua bản quyền web
- [ ] ❌ Đưa số liệu không có nguồn vào ấn phẩm
- [ ] ❌ Nền màu nóng (đỏ, tím, hồng)

---

## 8. Đoạn mã dùng lại — dán thẳng vào file HTML

```css
:root {
  /* Màu chủ đạo */
  --sg-xanh:        #004AEF;   /* màu logo, nút chính */
  --sg-xanh-sang:   #0D53F0;
  --sg-navy:        #002992;

  /* Màu phụ */
  --sg-mint:        #07EF9C;   /* màu nhấn — dùng ít */
  --sg-ngoc:        #00EFB0;
  --sg-cyan:        #0DD1FF;
  --sg-vang:        #FFCE00;
  --sg-cam:         #F68B1F;

  /* Chữ và nền */
  --sg-den:         #151515;
  --sg-xam-nen:     #F3F3F6;
  --sg-xam-vien:    #DCDCDC;

  --sg-chu: Gilroy, "Montserrat", -apple-system, BlinkMacSystemFont,
            "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

  --sg-dai-mau: linear-gradient(135deg, #002992 0%, #004AEF 55%, #0DD1FF 100%);
}
```

---

## 9. Còn thiếu — cần Trang bổ sung

Cẩm nang này dựng từ **website công ty**. Ba thứ sau chưa có, có thì cẩm nang chắc hơn hẳn:

| Thiếu | Vì sao cần |
|---|---|
| **File logo gốc độ phân giải cao** (`.ai` · `.svg` · `.png` nền trong) | File đang có chỉ rộng **500 điểm ảnh** — đủ cho web, **in ra là vỡ**. Có file gốc mới làm được ấn phẩm in |
| **Logo bản trắng (knockout)** | Chưa có bản trắng nên mỗi lần nền tối phải kê tấm nền trắng dưới logo. Có bản trắng thì đặt thẳng lên nền xanh được |
| **Bộ ấn phẩm công ty đang dùng** (slide, hồ sơ năng lực, ảnh mạng xã hội) | Để bắt đúng cách công ty đang trình bày thật, không chỉ suy từ web |
| **Bản nhận diện chính thức nếu công ty đã có** | Nếu phòng thiết kế đã có sẵn thì bản đó là chuẩn, cẩm nang này chỉ nên chép lại |

Trang gửi tới đâu, Agent cập nhật cẩm nang tới đó và ghi rõ ngày sửa.

---

*Sửa lần cuối: 08/09/2026 · Dựng từ mã nguồn thật của seongon.com*
