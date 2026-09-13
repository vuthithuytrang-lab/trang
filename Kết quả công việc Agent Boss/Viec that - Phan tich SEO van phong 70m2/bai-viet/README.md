# Bài viết "thiết kế văn phòng 70m2" — bản hoàn thiện

Giao ngày 13/09/2026. 5.938 chữ · 49 ảnh · 6 bảng · 3 sơ đồ mặt bằng tự vẽ.
Chủ đề xuyên suốt: **bố trí, đánh đổi và tối ưu diện tích**.

## Bản chính để Trang xem

**Google Docs (ảnh đã nhúng đủ):**
https://docs.google.com/document/d/1afBnIvJ3Ip2yNWdybjvMzpnPJBW9IS2tMJyS5l2MRfc/edit

## Các file trong thư mục này

| File | Dùng khi nào |
|---|---|
| `bai-viet-thiet-ke-van-phong-70m2.docx` | Bản Word, 49 ảnh nhúng sẵn chất lượng cao hơn bản Docs |
| `ma-dan-vao-wordpress.html` | Mã dán thẳng vào WordPress — ảnh trỏ về link sẵn có trên website |
| `ban-doc-duyet.html` | Mở bằng trình duyệt để đọc duyệt, ảnh nhúng sẵn, không cần mạng |
| `anh-bai-viet/` | 49 ảnh bản nhẹ (JPG) đúng thứ tự trong bài |
| `so-do-mat-bang/` | 3 sơ đồ bản gốc PNG + `ma-ve-so-do.py` để vẽ lại khi cần sửa |
| `nguon-dung/` | Mã dựng file — sửa nội dung ở đây rồi chạy lại là ra cả 3 bản |

## Ba sơ đồ mặt bằng

| Sơ đồ | Hình dạng | Kích thước | Chỗ ngồi |
|---|---|---|---|
| 1 | Hẹp và dài | 14m × 5m | 10 chỗ |
| 2 | Vuông cân xứng | 8,4m × 8,4m | 12 chỗ |
| 3 | Lô góc | 10m × 7m | 11 chỗ |

Cả ba cùng 70m², cùng giữ đủ phòng giám đốc, phòng họp 6 chỗ và pantry — chỉ khác hình dạng.

## Muốn sửa bài thì làm thế nào

Sửa chữ trong `nguon-dung/noidung_a.py` … `noidung_e.py`, rồi chạy:

```
python3 dung.py        # ra file Word
python3 dung_html.py   # ra bản đọc duyệt + mã WordPress
python3 dung_docs.py   # ra bản HTML để nhập vào Google Docs
```

⚠️ Trước khi nhập lại vào Google Docs, đọc mục 7 trong
`cong-cu/toi-uu-content-seo/ky-thuat-ban-giao.md` — ảnh nặng quá thì Google bỏ qua hết mà không báo lỗi.
