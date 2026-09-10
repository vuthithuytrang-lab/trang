# Schema cho deco-crystal.com — bộ 13 trang dịch vụ

Mỗi file `.txt` là một đoạn code **dán sẵn** (đã bọc thẻ `<script>`) cho đúng 1 trang.
Tên file trùng với đường dẫn (slug) của trang.

## Bảng theo dõi

| Trang (slug) | Có trường giá? | Nguồn FAQ |
|---|---|---|
| thiet-ke-noi-that-showroom | Có (đ/m²) | 2 câu (đã có) |
| thiet-ke-thi-cong-noi-that-van-phong | Có (đ/m²) | **10 câu THẬT** — có sẵn trên trang |
| thi-cong-noi-that-van-phong-ha-noi | Có (đ/m²) | 3 câu — **cần đăng lên trang** |
| bao-gia-thiet-ke-noi-that-van-phong | Có (đ/m²) | 3 câu — **cần đăng lên trang** |
| thiet-ke-van-phong-nha-khoa | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-van-phong-giao-dich | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-van-phong-cong-ty-bat-dong-san | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-van-phong-cho-thue | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-van-phong-1000m2 | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-noi-that-van-phong-luat | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-noi-that-van-phong-cong-ty-du-lich | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-noi-that-van-phong-cong-nghe | Không | 3 câu — **cần đăng lên trang** |
| thiet-ke-ngan-hang | Không | 3 câu — **cần đăng lên trang** |

## Cách chèn (WordPress + Yoast + Flatsome)
1. Vào `wp-admin` → **Trang** → mở đúng trang → dán khối code vào cuối nội dung:
   - Gutenberg: khối **HTML tùy chỉnh (Custom HTML)**
   - Classic Editor: tab **Text**
   - UX Builder (Flatsome): phần tử **HTML**
2. Bấm **Cập nhật**.
3. Kiểm tra tại `https://search.google.com/test/rich-results` (dán link trang).

## LƯU Ý QUAN TRỌNG (đọc kỹ)
1. **FAQ "cần đăng lên trang":** 11 trang chưa có FAQ hiển thị. Google yêu cầu câu hỏi–trả lời
   phải **nhìn thấy được trên trang**. Vì vậy phải chèn nội dung FAQ (dạng chữ) vào bài,
   rồi mới dùng schema FAQ — nếu không sẽ bị coi là vi phạm.
2. **Điểm đánh giá 4.9 / 156 là số BỊA** (theo yêu cầu). Đây là rủi ro bị Google phạt thủ công.
   Khuyến nghị: dùng **một** điểm đánh giá THẬT ở cấp doanh nghiệp (Google Maps/Facebook)
   thay vì gắn số bịa lên từng trang.
3. **Giá:** 9 trang không nêu giá cụ thể nên không thêm trường giá (tránh sai lệch).

> Dữ liệu (ảnh bìa, mô tả, giá theo m², FAQ thật) đều lấy từ chính nội dung trang, đã kiểm tra ngày 10/09/2026.
