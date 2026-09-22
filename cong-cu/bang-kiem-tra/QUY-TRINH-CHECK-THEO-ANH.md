# Quy trình: Check ảnh tình trạng theo bảng tiêu chuẩn

> Trang thiết lập ngày 22/09/2026.

## 1. Cách làm việc Trang yêu cầu

Có hai loại ảnh Trang gửi vào chat:

**Loại 1 — Ảnh tài liệu (bảng tiêu chuẩn).**
Đây là bảng gốc liệt kê các vấn đề cần kiểm tra. Nhiệm vụ: đọc, học, ghi nhớ
vào file này. Không nhận xét gì cả.

**Loại 2 — Ảnh tình trạng hiện tại.**
Đây là ảnh chụp thực tế cần soi. Nhiệm vụ: đối chiếu với bảng tiêu chuẩn ở
mục 2, rồi trả lời đúng 2 phần:

1. **Nhận xét** — 1 dòng ngắn gọn, lời thường, không thuật ngữ.
2. **Đề xuất sửa** — nói rõ sửa cái gì, sửa thế nào.

Không viết dài dòng. Không kèm bảng phân tích nếu Trang không hỏi.

## 2. Bảng tiêu chuẩn

**Cấu trúc cột** (từ ảnh Trang gửi 22/09/2026):
A = STT · B–C = Các vấn đề cần kiểm tra · D = Chi tiết · J = Yêu cầu đầu ra · K = Cách check.

Chép nguyên văn từ ảnh, không diễn giải lại. Mỗi vấn đề một mục con dưới đây.

---

### 2.1. sitemap.xml

**Chi tiết cần trả lời**
- Website có sitemap.xml chưa?
- File sitemap.xml đã chuẩn chưa?
- File sitemap có gặp vấn đề gì không?

**Yêu cầu đầu ra**

*1. File sitemap.xml*
- Đúng chuẩn XML Sitemap, truy cập và đọc được.
- Chỉ chứa URL canonical, có khả năng index và cần index.
- Không chứa URL 404/410, redirect, 5xx, noindex hoặc bị chặn bởi robots.txt.
- Không có URL trùng lặp.
- lastmod chính xác nếu có sử dụng.
- Sitemap được cập nhật khi có URL mới hoặc thay đổi quan trọng.

*2. Khai báo sitemap*
- Có khai báo sitemap trong robots.txt.
- Đã submit sitemap trên Google Search Console và Bing Webmaster Tools.
- Sitemap không phát sinh lỗi khi Google/Bing thu thập.

*3. Nếu có HTML Sitemap*
- Chứa các trang quan trọng, liên kết hợp lệ và hỗ trợ người dùng điều hướng website.

**Cách check**
Truy cập URL sitemap của website → kiểm tra sitemap có tồn tại, đọc được và đúng
cấu trúc → crawl/kiểm tra các URL trong sitemap để đối chiếu Status Code,
Indexability, Canonical, Robots.txt → kiểm tra sitemap đã được khai báo trong
robots.txt và Google Search Console.

---

### 2.2. (các vấn đề tiếp theo)

*Cần bổ sung* — Trang gửi tiếp ảnh các dòng sau thì chép vào đây.

## 3. Cách xin ảnh cho đủ

Nếu ảnh Trang gửi bị cắt, nói thật và xin lại, gợi ý cụ thể:

- Chụp cả màn hình (không chỉ dòng tiêu đề), hoặc chụp làm 2–3 ảnh cuộn dần xuống.
- Hoặc gọn nhất: đính kèm thẳng file Excel/Google Sheet gốc vào khung chat.
- Nếu file nằm trên Google Drive (hoaa8k58@gmail.com), có thể đọc trực tiếp từ đó.
