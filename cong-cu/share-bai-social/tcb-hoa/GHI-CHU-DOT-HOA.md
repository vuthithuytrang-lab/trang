# Đợt Hoa — 40 bài WordPress nganhangtechcombankvn (10–11/10/2026)

- Bài 1 đăng 03:08 sáng 10/10; 39 bài hẹn giờ, cách nhau đúng 55 phút; bài cuối 14:53 Chủ nhật 11/10.
- Sheet tab "Share social": 40 dòng ngay dưới "WordPress - Trang" của từng nhóm, cột H `WordPress - Hoa`, I link đẹp, J ngày đăng.
- Danh sách id/giờ/link: `da-dang.jsonl`. Lịch: `lich-dang.json`.
- Công cụ: `kiem-tra.py` (soát quy tắc), `post-hoa.py` (đăng; tự chặn nếu cách bài khác <55 phút hoặc sau 17h 11/10), `cap-nhat.py` (cập nhật nội dung giữ giờ), `so-sanh.py` (đối chiếu bản trên site với file), `dang-loat.sh`.

## Điểm bài gốc cần Trang biết (đã xử lý trong bài)
- Bảng C5 đã áp: lỗ kết chuyển "trừ" (760, 903, 914); Luật Quản lý thuế năm 2019 (771); 800/110 ≈ 7,27 (716); bỏ công thức lợi nhuận sai (804); phí bảo lãnh không ghi đơn vị (551); bỏ "hạn mức cao nhất thị trường" (848).
- Lỗi mới phát hiện trong bài gốc: 540 ghi mức nộp 0,5–3% (luật chỉ 0,5–1,5% cho tổng vốn đầu tư khi chọn nhà đầu tư); 925 công thức VAT trên giá đã gồm thuế bị sai; 815 hoán đổi tiêu đề "cơ quan thuế"/"Kho bạc"; 705 số bước séc/giấy rút mâu thuẫn; 870 nói L/C 11 bước nhưng liệt kê ~10.
- Trang gốc gắn nhãn "đã hết hạn" nhưng vẫn viết (ghi rõ cần hỏi lại ngân hàng): 892, 903, 936, 826. Ưu đãi hết hạn 30/06/2026 đã bỏ: 617, 628, 639, 650, 661, 672, 683, 694.
- Cùng 1 chương trình ưu đãi, bài gốc ghi 2 hạn khác nhau (30/06 vs 31/12/2026): 606 giữ, 694 bỏ.
- Nơi nộp hồ sơ: "Sở Tài chính" (617) vs "Sở KH&ĐT" (661, 881) — giữ theo từng bài gốc.
- 793: công cụ đọc web trả bản tóm tắt tiếng Anh, số liệu đã đối chiếu với bài đồng nghiệp.
- Bài tool kia (chỉ báo, không sửa): vài bài Blogger/WP - Trang có mục "Kết luận"/"Tóm lại"; bài Blogger 529 có hotline + email.

## Chuyển sang Blogger (10–11/10/2026)
- WordPress nganhangtechcombankvn bị khóa (410) chiều 10/10 → không xóa được bài qua API; đã gỡ 40 dòng "WordPress - Hoa" trên sheet.
- 40 bài (cùng nội dung bản Hoa) hẹn giờ lên **nganhangtechcombankvietnam.blogspot.com**: bài 1 lúc 18:10 10/10, bài 40 lúc 17:46 11/10, cách nhau 33–38 phút. Tạo bài theo đợt 3 bài/giờ, mỗi bài cách 4 phút; không lần nào bị Blogger chặn.
- Sheet: 40 dòng `Blog - Hoa` ở đúng dòng cũ (ngay dưới "WordPress - Trang"). Danh sách: `da-dang-blogger.jsonl`, lịch: `lich-blogger.json`.
- Quyền Blogger hết hạn khoảng 17/10/2026.
