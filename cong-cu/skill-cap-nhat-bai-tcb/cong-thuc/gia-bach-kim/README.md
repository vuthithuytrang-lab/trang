# Công thức: cập nhật bài "Giá bạch kim" (Techcombank)

Bài: https://techcombank.com/thong-tin/blog/gia-bach-kim — đóng gói 06/11/2026. Trang tích ô trong Sheet "Update" hoặc nhắn
*"Update bài giá bạch kim"* — không hỏi gì thêm. Chạy không cần Claude:
`bash cong-cu/tu-dong/chay.sh gia-bach-kim <thư mục ra>` (khung chung `*)` của `chay.sh`).

## 1. Đã chốt

| Việc | Cách làm cố định |
|---|---|
| Nguồn chính | **Yahoo Finance, mã `PL=F`** = hợp đồng tương lai bạch kim tháng gần nhất trên **NYMEX** (USD/oz) — bài TCB cũng nhắc NYMEX. API biểu đồ công khai `query1/query2.finance.yahoo.com/v8/finance/chart/PL=F?range=1mo&interval=1d`, đọc bằng `curl` thường (không Chromium, không vượt chặn, giữ nguyên kiểm tra TLS) |
| Giá = gì | Giá **đóng cửa từng phiên** của hợp đồng NYMEX (không phải giá giao ngay London). Phiên mới nhất có thể là giá đang giao dịch nếu thị trường còn mở (tự ghi cần duyệt) |
| Thay đổi | Giá phiên này trừ giá phiên liền trước (cần ≥ 6 phiên → 5 dòng). Tính trong `lay_gia.py`, ghi rõ trong `chu_nguon` |
| Đối chiếu | TradingView scanner (POST): `NYMEX:PL1!` (cùng loại hợp đồng, phải gần trùng; lệch > 1% → cần duyệt) và `TVC:PLATINUM` (giao ngay, chỉ để tham khảo). Chạy thử 06/11/2026: Yahoo 1,514.30 (-10.10); PL1! 1,513.50 (-8.90); giao ngay 1,507.86 — khớp (chênh vài USD do giá đang chạy và hợp đồng so với giao ngay) |
| Bảng "Ngày \| Giá (USD/oz) \| Thay đổi (USD/oz)" | 5 dòng = 5 phiên mới nhất, dòng 1 mới nhất. Giá `1,522.00` (dấu nghìn `,`, 2 số lẻ); thay đổi luôn có dấu `+9.00` / `-100.00`. Xử lý cả khi bài web gộp dòng thành `05/11/2026 \| 1,522.00 \| -100.00 \|` |
| Câu "… mức khoảng X USD/oz, giảm/tăng khoảng Y USD/oz so với phiên trước" | X = giá phiên mới nhất (2 số lẻ). Y = \|thay đổi\| **làm tròn số nguyên** (đúng dạng bài, "khoảng 11"). Chữ tăng/giảm theo dấu + ghi cần duyệt. Y làm tròn bằng 0 → giữ nguyên + cần duyệt |
| Lưới an toàn | Số kiểu giá còn sót (có dấu nghìn / 2 số lẻ / "… USD") mà công thức không nhận ra và không bằng số nguồn nào → cần duyệt dòng **"SỐ GIÁ CHƯA CẬP NHẬT …"** |
| Không bịa số | Nguồn lỗi → `lay_gia.py` in `Yahoo Finance PL=F KHÔNG ĐỌC ĐƯỢC …`, ghi `null`; bài giữ nguyên mọi số + cần duyệt |
| Ngày trong tiêu đề/đoạn | Do `dung` + `doi_ngay_bai.py` của khung chung (ngày hôm sau). Ngày trong bảng là ngày phiên thật của nguồn (nên thường trễ hơn ngày tiêu đề) |

## 2. Chạy tay

```bash
CT=/home/user/trang/cong-cu/skill-cap-nhat-bai-tcb/cong-thuc/gia-bach-kim
python3 -I $CT/lay_gia.py cap-nhat/gia.json
python3 -I $CT/tao_sua.py --xem cap-nhat/xem.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html --ra cap-nhat/sua.json
python3 -I $CT/tao_sua.py --kiem --xem cap-nhat/xem2.txt --gia cap-nhat/gia.json --goc cap-nhat/tam/bai1.html   # "khớp hết"
```

## 3. Lưu ý

- Yahoo thỉnh thoảng trả `429 Too Many Requests` (đã gặp khi chạy liên tiếp nhiều lần). Script chỉ chờ rồi thử lại (query1 → query2, 3 vòng, nghỉ 10/20/30 giây), **không đổi danh tính hay lách giới hạn**. Vẫn lỗi → chạy lại sau ít phút hoặc để bài ở trạng thái "giữ nguyên + cần duyệt".
- Số trong bài cũ lệch vài USD so với Yahoo (vd 20/10: bài 1,630 / Yahoo 1,646.6): bài cũ có thể dùng nguồn khác (giao ngay). Trang cần biết khi duyệt.
- Cần `curl` và Python 3 (không thư viện ngoài); không cần Playwright.
