# -*- coding: utf-8 -*-
# Phần B: mục 3 — phân bổ diện tích + 3 sơ đồ
B = []
P = B.append

P(('h2','3. Chia 70m2 thành những khu nào? Bảng phân bổ và 3 sơ đồ mặt bằng'))
P(('p','Sau khi đã chốt giữ gì bỏ gì, bước tiếp theo là chia diện tích. Tỷ lệ dưới đây là khung phân bổ dùng được cho phần lớn văn phòng 70m² của doanh nghiệp vừa và nhỏ.'))

P(('h3','3.1. Bảng phân bổ diện tích chuẩn cho 70m²'))
P(('table',
   ['Khu vực','Tỷ lệ','Diện tích','Sức chứa'],
   [['Khu làm việc chung','50 – 60%','35 – 42 m²','10 – 15 chỗ'],
    ['Phòng họp và khu tiếp khách','18 – 22%','12 – 15 m²','6 – 8 chỗ'],
    ['Pantry','5 – 8%','3 – 5 m²','4 chỗ'],
    ['Lối đi, kho, tủ kỹ thuật','12 – 18%','8 – 12 m²','—']]))
P(('p','Nếu khu làm việc chung tụt xuống dưới 50%, gần như chắc chắn mặt bằng đang bị chia quá vụn — đây là lỗi phổ biến nhất ở diện tích 70m².'))

P(('h3','3.2. Ba sơ đồ mặt bằng — cùng 70m2, chênh nhau 2 chỗ ngồi'))
P(('p','Ba sơ đồ dưới đây do đội thiết kế vẽ riêng cho bài viết này, theo ba hình dạng mặt bằng 70m² hay gặp nhất khi thuê văn phòng tại Hà Nội và TP.HCM. Cả ba đều cùng một diện tích, cùng giữ đủ phòng giám đốc, phòng họp 6 chỗ và pantry — chỉ khác hình dạng. Kết quả là số chỗ ngồi chênh nhau tới 2 chỗ.'))
P(('p','Cụ thể ba sơ đồ đó là:'))
P(('table',
   ['Sơ đồ','Hình dạng mặt bằng','Kích thước','Chỗ ngồi','Điều quyết định'],
   [['Sơ đồ 1','Hẹp và dài','14m × 5m','10 chỗ','Lối đi dọc phải chạy suốt 8,8m nên ăn mất nhiều diện tích nhất'],
    ['Sơ đồ 2','Vuông cân xứng','8,4m × 8,4m','12 chỗ','Khu làm việc sâu 6,4m nên xếp được 4 dãy bàn'],
    ['Sơ đồ 3','Lô góc','10m × 7m','11 chỗ','Được hai mặt kính, nhưng góc đẹp nhất phải nhường cho phòng giám đốc']]))
P(('p','Mỗi sơ đồ đều nhìn từ trên xuống, ghi rõ kích thước từng khu, vị trí cửa ra vào (cung tròn), cửa sổ (vạch xanh) và bề rộng lối đi (vạch đỏ).'))

P(('h4','Sơ đồ 1 — mặt bằng hẹp và dài (14m × 5m) · 10 chỗ ngồi'))
P(('sodo','so-do-70-hep-dai','Sơ đồ mặt bằng văn phòng 70m2 dạng hẹp và dài 14m × 5m, bố trí được 10 chỗ ngồi'))
P(('p','Phòng giám đốc 13m² và phòng họp 13m² đặt ở hai đầu, khu làm việc chung 29m² nằm giữa với hai dãy bàn 5 chỗ, pantry 2,6m² kê ở góc cuối. Lối đi chính rộng 1,2m phải chạy suốt 8,8m theo trục dài — riêng lối đi đã chiếm gần 7m², nhiều nhất trong ba sơ đồ. Vì khu làm việc chỉ sâu 3,6m nên chỉ xếp được đúng hai dãy bàn, đó là lý do sơ đồ này ít chỗ ngồi nhất.'))

P(('h4','Sơ đồ 2 — mặt bằng vuông cân xứng (8,4m × 8,4m) · 12 chỗ ngồi'))
P(('sodo','so-do-70-vuong','Sơ đồ mặt bằng văn phòng 70m2 dạng vuông cân xứng 8,4m × 8,4m, bố trí được 12 chỗ ngồi'))
P(('p','Lễ tân và khu chờ 8,3m² nằm ngay cửa vào. Phòng giám đốc 7,7m², pantry 3,8m² và phòng họp 6 chỗ 7,7m² xếp dọc một cạnh. Khu làm việc chung 29m² chiếm trọn nửa còn lại, sâu 6,4m nên xếp được bốn dãy bàn 3 chỗ. Lối đi 1,4m chạy thẳng một trục, ngắn hơn sơ đồ 1 nên tiết kiệm được diện tích để dành cho chỗ ngồi.'))

P(('h4','Sơ đồ 3 — mặt bằng lô góc (10m × 7m) · 11 chỗ ngồi'))
P(('sodo','so-do-70-lo-goc','Sơ đồ mặt bằng văn phòng 70m2 dạng lô góc 10m × 7m, bố trí được 11 chỗ ngồi'))
P(('p','Hai mặt tiếp xúc cửa sổ nên đây là sơ đồ sáng nhất. Phòng giám đốc 8,3m² đặt đúng vào góc hai mặt kính, phòng họp 8,8m² nằm ngay dưới. Lễ tân 4m² và pantry 4,3m² kê dọc cạnh trên, khu làm việc chung 29m² xếp ba dãy bàn cho 11 chỗ. Đánh đổi ở đây rõ ràng: vị trí đẹp nhất mặt bằng đã dành cho phòng giám đốc, nên khu làm việc chung không tận dụng được góc kính.'))

P(('p','**Đọc ba sơ đồ này thế nào:** nếu doanh nghiệp đang đi xem mặt bằng, hãy đo chiều sâu của phần dự kiến làm khu làm việc chung. Cứ mỗi 1,3m chiều sâu là thêm được một dãy bàn. Mặt bằng sâu dưới 4m thì gần như chắc chắn chỉ xếp được hai dãy.'))
