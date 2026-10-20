# Phân cụm theo SERP

Không phân cụm bằng regex chủ đề. Google quyết định từ khoá nào cùng một trang, nên
tập URL đang xếp hạng mới là căn cứ khách quan.

## Thuật toán

1. **Tập SERP mỗi từ khoá**: mọi URL trong top N (N = độ sâu file check top, mặc định 10),
   loại domain của mình và loại mạng xã hội, video.
2. **Gom theo centroid, không theo liên thông.** Liên thông gây chuỗi A–B–C khiến A và C
   cùng cụm dù không liên quan; đã kiểm chứng: liên thông gom 168/302 từ khoá vào một cụm.
   - Lặp: chọn từ khoá có nhiều liên kết nhất làm hạt giống
   - Gom mọi từ khoá còn lại có `|SERP ∩ SERP_hạt giống| >= min_shared`
   - Loại cả cụm khỏi tập, lặp tiếp
3. **Gộp cụm nhỏ**: cụm dưới 3 từ khoá nhập vào cụm lớn nếu overlap >= merge_small.
4. **Gộp hai cụm lớn**: chỉ khi tập URL của hai hạt giống trùng >= merge_cluster (mặc định 0,7).
   **Không gộp theo domain** — các cụm khác nhau vẫn chung domain lớn, gộp theo domain
   đã kiểm chứng là sai: gom 175/302 từ khoá vào một cụm.
5. **Không bỏ sót từ khoá nào.** Cụm nhỏ không gộp được thì đứng riêng thành cụm của chính nó,
   **kể cả cụm chỉ có một từ khoá**. Không có nhóm "đơn lẻ" gom chung — một từ khoá đứng riêng
   nghĩa là SERP của nó khác hẳn phần còn lại, và đó là thông tin cần giữ, không phải rác.
   `cluster_serp.py` có assert kiểm tổng số từ khoá sau khi phân cụm phải bằng tổng đầu vào.

## Tham số

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `min_shared` | 4 | Số URL chung tối thiểu để cùng cụm. 3 thì cụm quá to, 5 thì quá vụn |
| `merge_small` | 3 | Ngưỡng gộp cụm nhỏ vào cụm lớn |
| `merge_cluster` | 0,7 | Tỷ lệ trùng URL để gộp hai cụm lớn |
| `depth` | 10 | Độ sâu SERP dùng để so. Nếu file chỉ có top 10 thì bằng 10 |

Kiểm chứng trên bộ 302 từ khoá ngành nội thất văn phòng, `min_shared=4`: **60 cụm, 302/302
từ khoá** — 11 cụm từ 5 kw trở lên, 13 cụm 2–4 kw, 36 cụm 1 kw.

Cụm 1 kw nhiều là bình thường ở bộ từ khoá rộng: đó là các truy vấn có SERP riêng biệt,
không chia sẻ đủ URL với nhóm nào. Đưa chúng vào bảng khoảng cách vẫn có giá trị vì mỗi
từ khoá vẫn đếm vào mục tiêu chung.

## Đặt tên cụm

Cụm một từ khoá lấy luôn từ khoá đó làm tên. Các cụm còn lại được sinh tên gợi ý bằng n-gram đặc trưng, tính theo `(tần suất trong cụm / tần suất toàn bộ)`.
Tên này thường cắt cụt giữa từ ghép.

**Agent bắt buộc đọc lại và đặt tên tiếng Việt có nghĩa** trước khi dựng báo cáo. Tên cụm
xuất hiện trong tên file và tiêu đề, không được để tên máy sinh.
