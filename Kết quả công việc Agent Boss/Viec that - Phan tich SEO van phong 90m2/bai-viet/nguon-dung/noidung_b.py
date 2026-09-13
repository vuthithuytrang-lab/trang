# -*- coding: utf-8 -*-
B=[]; P=B.append

# ---------------- MUC 2 ----------------
P(('h2','2. Văn phòng 90m2 khác gì 70m2 và 80m2?'))
P(('p','Rất nhiều bài viết gộp chung cả dải 60 – 90m² thành một, như thể bốn diện tích đó là một bài toán. Thực tế chúng khác nhau ở đúng một chỗ: **diện tích nào thì hết phải hy sinh**.'))
P(('table',
   ['','70m²','80m²','90m²'],
   [['Chỗ ngồi (mức phổ biến)','10 – 13 chỗ','12 – 16 chỗ','**15 – 18 chỗ**'],
    ['Lễ tân riêng','Quầy nhỏ, ghép vào lối vào','Quầy riêng, chưa có chỗ chờ','**Quầy riêng + khu chờ 2 – 4 chỗ**'],
    ['Phòng giám đốc','Được, nhưng mất 2 chỗ ngồi','Được, mất 1 – 2 chỗ ngồi','**Được, gần như không ảnh hưởng**'],
    ['Phòng họp','6 chỗ, thường phải dùng vách kính','6 – 8 chỗ','**8 chỗ, vách đặc được nếu cần kín tiếng**'],
    ['Pantry','2 – 4m², chỉ đủ kê tủ bếp mini','4 – 5m²','**4 – 6m², kê được bàn ăn nhỏ**'],
    ['Bài toán chính','Phải bỏ bớt cái gì','Cân bằng phong cách và công năng','**Sắp thứ tự các khu cho vận hành trơn**']]))
P(('p','Đọc bảng theo cột cuối: ở 70m², giữ phòng giám đốc riêng là **trả bằng 2 chỗ ngồi** — đó là bài toán đánh đổi. Lên 90m², cũng phòng giám đốc đó gần như không lấy đi chỗ nào, vì phần diện tích tăng thêm đủ bù. Câu hỏi vì thế đổi hẳn: không còn là “phải bỏ gì”, mà là **“sắp thế nào cho khách và nhân viên không giẫm chân nhau”**.'))
P(('p','Đó cũng là lý do toàn bộ phần còn lại của bài này nói về phân khu và luồng di chuyển, chứ không nói về cách cắt bớt.'))

# ---------------- MUC 3 ----------------
P(('h2','3. Bố trí văn phòng 90m2: chia 5 khu và bảng phân bổ diện tích'))
P(('p','Một văn phòng 90m² vận hành đủ cần năm khu. Bảng dưới đây là khung phân bổ dùng được cho phần lớn doanh nghiệp 15 – 20 người.'))
P(('table',
   ['Khu vực','Tỷ lệ','Diện tích','Sức chứa','Vai trò trong luồng vận hành'],
   [['Lễ tân và khu chờ','8 – 12%','7 – 11 m²','2 – 4 chỗ chờ','Điểm dừng đầu tiên, chặn khách lại trước khi vào trong'],
    ['Khu làm việc chung','45 – 52%','40 – 47 m²','15 – 18 chỗ','Vùng cần yên tĩnh nhất, phải nằm ngoài đường đi của khách'],
    ['Phòng họp','11 – 15%','10 – 14 m²','6 – 8 chỗ','Đặt gần lối vào để khách không đi sâu vào trong'],
    ['Phòng giám đốc','9 – 11%','8 – 10 m²','1 + 2 chỗ tiếp khách','Cần vị trí có view, nhưng không nên chắn lối đi chính'],
    ['Pantry','4 – 7%','4 – 6 m²','4 chỗ','Đặt xa khu làm việc và xa lễ tân — mùi và tiếng ồn'],
    ['Lối đi, kho, tủ kỹ thuật','12 – 15%','11 – 14 m²','—','Phần không ngồi được nhưng quyết định bài toán còn lại']]))
P(('p','Hai con số cần canh: **khu làm việc chung phải giữ được ít nhất 45%** — thấp hơn là mặt bằng đang bị chia quá vụn. Và **lối đi không nên vượt 15%** — vượt là đang lãng phí, thường do mặt bằng quá dài hoặc do đặt phòng kín sai chỗ khiến phải chạy vòng.'))
P(('img','b80-24','Nội thất thay vách ngăn để chia khu mà không dựng thêm tường — cách giữ tỷ lệ khu làm việc chung trên 45% (Ảnh tham khảo)'))

# ---------------- MUC 4 — SO DO ----------------
P(('h2','4. Ba sơ đồ mặt bằng văn phòng 90m2 và hai luồng di chuyển'))
P(('p','Ba sơ đồ dưới đây do đội thiết kế vẽ riêng cho bài viết này, theo ba hình dạng mặt bằng 90m² hay gặp nhất khi thuê văn phòng tại Hà Nội và TP.HCM. Cả ba đều cùng diện tích, cùng giữ đủ năm khu — chỉ khác hình dạng. Trên mỗi sơ đồ có vẽ thêm hai đường: **luồng khách** (nét xanh) và **luồng nhân viên** (nét lục).'))
P(('p','Ba sơ đồ đó là:'))
P(('table',
   ['Sơ đồ','Hình dạng mặt bằng','Kích thước','Chỗ ngồi','Luồng khách chạy thế nào'],
   [['Sơ đồ 1','Hẹp và dài','18m × 5m','15 chỗ','**Buộc phải đi dọc qua khu làm việc** mới tới phòng họp'],
    ['Sơ đồ 2','Vuông cân xứng','9,5m × 9,5m','17 chỗ','Dừng gọn ở lễ tân, không vào sâu'],
    ['Sơ đồ 3','Lô góc','12m × 7,5m','16 chỗ','**Đi trọn trong khu tiếp khách rồi rẽ thẳng vào phòng họp**']]))
P(('p','Mỗi sơ đồ nhìn từ trên xuống, ghi rõ kích thước từng khu, vị trí cửa ra vào (cung tròn), cửa sổ (vạch xanh nhạt) và bề rộng lối đi (vạch đỏ).'))

P(('h4','Sơ đồ 1 — mặt bằng hẹp và dài (18m × 5m) · 15 chỗ ngồi'))
P(('sodo','so-do-90-hep-dai','Sơ đồ mặt bằng văn phòng 90m2 dạng hẹp và dài 18m × 5m, bố trí 15 chỗ ngồi, có vẽ luồng khách và luồng nhân viên'))
P(('p','Lễ tân và khu chờ 11m² nằm ngay cửa. Khu làm việc chung 36m² với hai dãy bàn 7 chỗ chạy dọc trục dài. Phòng họp 14m² cho 8 chỗ và phòng giám đốc 8,3m² dồn về đầu kia, pantry 4,2m² kê ở góc cuối. Lối đi chính rộng 1,2m chạy suốt 10m.'))
P(('p','**Vấn đề luồng:** phòng họp nằm ở cuối mặt bằng nên khách buộc phải đi dọc hết khu làm việc mới tới nơi. Mỗi lần có khách là cả hai dãy bàn ngẩng lên. Cách chữa duy nhất ở dạng này là đổi chỗ phòng họp lên sát lễ tân và đẩy phòng giám đốc xuống cuối — đổi lại giám đốc mất vị trí gần cửa.'))

P(('h4','Sơ đồ 2 — mặt bằng vuông cân xứng (9,5m × 9,5m) · 17 chỗ ngồi'))
P(('sodo','so-do-90-vuong','Sơ đồ mặt bằng văn phòng 90m2 dạng vuông cân xứng 9,5m × 9,5m, bố trí 17 chỗ ngồi, có vẽ luồng khách và luồng nhân viên'))
P(('p','Lễ tân và khu chờ 10,8m² nằm ngay cửa vào. Bốn dãy bàn 4 chỗ chiếm trọn nửa trái, tổng 39m² cho 16 chỗ. Phòng giám đốc 9m², pantry 5m² và phòng họp 8 chỗ 12m² xếp dọc cạnh phải. Lối đi 1,3m chạy thẳng một trục từ cửa xuống cuối nhà.'))
P(('p','**Vấn đề luồng:** đây là sơ đồ gọn nhất — khách dừng ở lễ tân ngay bên trái cửa, nhân viên rẽ phải theo trục dọc. Hai luồng tách nhau ngay từ ngưỡng cửa. Đổi lại, pantry nằm giữa phòng giám đốc và phòng họp nên phải làm cửa kín và hút mùi tốt.'))

P(('h4','Sơ đồ 3 — mặt bằng lô góc (12m × 7,5m) · 16 chỗ ngồi'))
P(('sodo','so-do-90-lo-goc','Sơ đồ mặt bằng văn phòng 90m2 dạng lô góc 12m × 7,5m, bố trí 16 chỗ ngồi, có vẽ luồng khách và luồng nhân viên'))
P(('p','Hai mặt tiếp xúc cửa sổ nên đây là sơ đồ sáng nhất. Phòng giám đốc 8,1m² đặt đúng vào góc hai mặt kính. Lễ tân 6,6m² và **khu tiếp khách riêng 10,1m²** chiếm dải trên — thứ chỉ từ 90m² mới làm nổi. Khu làm việc chung 40m² với ba dãy bàn 5 chỗ nằm trọn phía dưới, phòng họp 8,1m² và pantry 3,6m² dồn về cạnh phải.'))
P(('p','**Vấn đề luồng:** đây là sơ đồ sạch nhất về đường đi. Khách vào là ở luôn trong dải tiếp khách phía trên, muốn họp thì rẽ xuống lối đi 1,4m — **không một lần nào bước vào khu làm việc**. Đổi lại, phòng họp chỉ còn 8,1m² nên tối đa 6 chỗ, và pantry bị đẩy xuống cuối lối đi.'))
P(('p','**Đọc ba sơ đồ này thế nào:** nếu doanh nghiệp đang đi xem mặt bằng, hãy đứng ở cửa và hỏi đúng một câu — “từ đây tới phòng họp, khách phải đi qua mấy chỗ ngồi?” Câu trả lời là 0 thì mặt bằng đó tốt. Từ 5 chỗ trở lên là sẽ phiền mỗi ngày.'))
