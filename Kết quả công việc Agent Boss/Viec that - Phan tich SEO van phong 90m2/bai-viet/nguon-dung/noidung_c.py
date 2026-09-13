# -*- coding: utf-8 -*-
C=[]; P=C.append

# ---------------- MUC 5 — LUONG DI CHUYEN ----------------
P(('h2','5. Khách đi lối nào, nhân viên đi lối nào trong văn phòng 90m2?'))
P(('p','Ở 70m² thì không có gì để bàn: mặt bằng nhỏ, ai cũng đi chung một lối. Từ 90m² trở lên, hai luồng này tách được, và nếu không tách, doanh nghiệp sẽ trả giá mỗi ngày bằng những phiền toái nhỏ mà không ai gọi tên ra được.'))

P(('h3','5.1. Hai luồng cần tách trong văn phòng 90m2'))
P(('table',
   ['','Luồng khách','Luồng nhân viên'],
   [['Đi từ đâu tới đâu','Cửa → lễ tân → khu chờ hoặc phòng họp','Cửa → lối đi → chỗ ngồi, pantry, WC'],
    ['Tần suất','Vài lượt mỗi ngày','Hàng chục lượt mỗi ngày'],
    ['Yêu cầu','Ngắn, dễ hiểu, không phải hỏi đường','Không cắt ngang chỗ người khác đang ngồi'],
    ['Hỏng thì sao','Khách lúng túng, phải đi xuyên chỗ làm việc','Mỗi lần đi pantry là một dãy bàn ngẩng lên']]))
P(('p','Nguyên tắc gọn nhất: **khách không được đi sâu quá phòng họp, nhân viên không phải đi vòng qua lễ tân.** Nếu trên bản vẽ hai đường này cắt nhau quá một lần, bố cục cần sửa.'))

P(('h3','5.2. Ba lỗi hay gặp khi thiết kế văn phòng 90m2 về đường đi lại'))
P(('table',
   ['Lỗi','Biểu hiện hằng ngày','Cách chữa trên bản vẽ'],
   [['Phòng họp đặt ở trong cùng','Khách đi dọc hết khu làm việc mới tới nơi; mỗi lượt khách làm gián đoạn cả sàn','Đổi chỗ phòng họp lên sát lễ tân. Nếu vướng cửa sổ thì dùng vách kính có rèm để vẫn lấy sáng'],
    ['Pantry nằm cạnh khu làm việc','Tiếng máy pha, mùi đồ ăn và các cuộc trò chuyện lọt thẳng vào chỗ ngồi','Đẩy pantry về cuối lối đi, cách khu làm việc ít nhất một vách; lắp cửa kín và hút mùi'],
    ['Lối đi chính đâm thẳng vào lưng người ngồi','Người ngồi cuối dãy bị đi qua sau lưng cả ngày, không tập trung được','Xoay dãy bàn vuông góc với lối đi, hoặc kê một dãy tủ thấp 1,1 – 1,2m làm lớp chắn']]))

P(('h3','5.3. Cách tách tiếng ồn trong văn phòng 90m2 mà không xây thêm tường'))
P(('p','Ở mật độ 15 – 18 người trên 90m², tiếng ồn là vấn đề có thật chứ không phải chuyện lý thuyết. Ba cách xử lý theo thứ tự từ rẻ tới đắt:'))
P(('ul',[
  '**Tủ thấp 1,1 – 1,2m làm vách mềm.** Chặn được đường truyền âm ngang tầm ngồi, không chắn sáng, không tính là hạng mục xây dựng. Rẻ nhất.',
  '**Tấm tiêu âm treo trần phía trên khu làm việc.** Chi phí khoảng 300.000 – 600.000đ/m² trần, xử lý được phần tiếng vọng, không đụng tới mặt bằng.',
  '**Vách kính hai lớp cho phòng họp.** Đắt nhất trong ba cách nhưng là cách duy nhất cách âm thật sự cho cuộc họp có khách.']))
P(('p','Với 90m², cách phổ biến nhất là kết hợp một và hai: tủ thấp chia khu, trần tiêu âm phủ khu làm việc chung, và chỉ đầu tư vách kính cách âm cho đúng phòng họp.'))
P(('img','b80-28','Vách kính khung thép chia phòng họp mà vẫn giữ tầm nhìn, cách tách tiếng ồn không làm mặt bằng bị cắt vụn (Ảnh tham khảo)'))
P(('img','b80-09','Tủ thấp và bảng di động làm vách mềm giữa khu làm việc và khu trao đổi nhóm (Ảnh tham khảo)'))

# ---------------- MUC 6 — PHONG CACH ----------------
P(('h2','6. Mẫu thiết kế văn phòng 90m2 hiện đại theo từng phong cách'))
P(('p','Phong cách không chỉ là chuyện đẹp xấu. Ở 90m², phong cách quyết định luôn việc phân khu dễ hay khó: phong cách dùng nhiều vách đặc thì chia khu bằng tường, phong cách dùng kính và nội thất nhẹ thì chia khu bằng đồ đạc và giữ được cả sàn liền mạch. Năm phong cách dưới đây được doanh nghiệp chọn nhiều nhất cho diện tích này, kèm con số cụ thể cho thấy mỗi phong cách ảnh hưởng thế nào tới chỗ ngồi và tới chi phí. Cả năm đều được trình bày theo cách làm hiện đại đã nói ở mục 3, tức chia khu bằng kính và nội thất thay vì bằng tường. Phong cách hiện đại đặt đầu tiên vì đó là mặc định an toàn nhất; bốn phong cách còn lại là bốn cách khoác lớp áo khác lên cùng một bộ khung ấy.'))

P(('h3','6.1. Mẫu thiết kế văn phòng 90m2 phong cách hiện đại'))
P(('p','Phong cách hiện đại đi theo đường nét thẳng, mặt phẳng gọn, không hoa văn trang trí. Vật liệu chủ đạo là kính, kim loại sơn tĩnh điện và gỗ công nghiệp phủ melamine hoặc laminate. Bảng màu giữ ở tông trung tính, chỉ dùng màu thương hiệu ở tường lễ tân hoặc mặt vách phòng họp. Đây là phong cách an toàn nhất cho văn phòng 90m2 vì hợp hầu hết loại hình doanh nghiệp và dễ thay đổi về sau.'))
P(('lead','Ưu điểm với mặt bằng 90m²'))
P(('ul',[
  '**Chia được 5 khu mà sàn vẫn liền mạch.** Vách kính cho phòng họp và phòng giám đốc không cắt vụn tầm nhìn.',
  '**Nội thất mỏng, chiếm ít sàn.** Bàn chân sắt hộp và tủ treo tường thay tủ đứng, trả lại diện tích cho lối đi.',
  '**Dễ nâng cấp từng phần.** Đổi màu ghế, đổi mặt bàn là văn phòng đã khác, không phải đập vách.',
  '**Chi phí ở mức giữa.** Vật liệu công nghiệp có sẵn theo mô-đun nên ít phát sinh gia công tại công trường.']))
P(('p','So sánh trực tiếp trên cùng mặt bằng 90m²: phòng họp 8 chỗ làm bằng vách thạch cao hai lớp chiếm khoảng 14m² tính cả tường; cũng phòng họp đó làm bằng vách kính khung nhôm chỉ chiếm khoảng 12m². Cộng thêm phòng giám đốc, hai vách kính trả lại khoảng 4m², đúng bằng **hai chỗ ngồi**. Đó là lý do phong cách hiện đại thường cho ra 17 – 18 chỗ, trong khi phương án vách đặc dừng ở 15 – 16.'))
P(('img','b80-08','Buồng họp lắp ghép và vách tiêu âm di động, cách chia khu trong văn phòng 90m2 mà không xây tường (Ảnh tham khảo)'))
P(('img','b80-43','Phòng họp nhỏ bằng vách kính khung đen đặt ngay trong khu làm việc, đủ kín cho cuộc gọi quan trọng (Ảnh tham khảo)'))
P(('img','b80-34','Màn hình lớn và bồn cây thấp phân vùng khu làm việc chung mà không chắn tầm nhìn (Ảnh tham khảo)'))
P(('img','a70-16','Phòng giám đốc 8 – 10m² với tủ âm tường chạy suốt một mặt để giải phóng sàn (Ảnh tham khảo)'))
P(('img','b80-19','Bàn kê đối xứng hai dãy, đèn thả lệch trục để màn hình không bị bóng đổ (Ảnh tham khảo)'))

P(('h3','6.2. Mẫu thiết kế văn phòng 90m2 phong cách tối giản (Minimalism)'))
P(('p','Tối giản không phải là làm ít đồ cho rẻ, mà là bỏ hết những gì không có công năng: không phào chỉ, không trần giật cấp nhiều lớp, không tủ trang trí. Đồ lưu trữ giấu vào tường hoặc gom vào một hệ tủ duy nhất. Bảng màu thường chỉ hai đến ba màu gồm trắng, be, gỗ sáng, cộng đúng một màu nhấn.'))
P(('lead','Ưu điểm với mặt bằng 90m²'))
P(('ul',[
  '**Không gian không bị rối mắt.** Với 15 – 18 người trên cùng một sàn, ít chi tiết thị giác là yếu tố giữ được cảm giác rộng.',
  '**Tiết kiệm chi phí thật.** Bỏ phào chỉ và trần giật cấp cắt được phần thi công tốn công nhất tại công trường.',
  '**Dễ giữ gọn về sau.** Ít bề mặt trang trí đồng nghĩa ít chỗ để đồ bừa bộn tích tụ.',
  '**Hợp doanh nghiệp thuê ngắn hạn.** Hạng mục chủ yếu là nội thất rời, hết hạn thuê tháo mang đi được.']))
P(('p','Phần trang trí thuần túy gồm phào chỉ, trần giật cấp và tủ trưng bày thường chiếm 10 – 15% tổng chi phí thi công. Với văn phòng 90m² làm gói tiêu chuẩn (360 – 630 triệu), bỏ hẳn nhóm này tiết kiệm khoảng **36 – 95 triệu**, đủ để nâng cấp toàn bộ ghế làm việc và bù cho một phòng họp vách kính cách âm. Về diện tích, thay bốn tủ đứng cao 2m bằng hệ tủ âm tường trả lại khoảng 3 – 4m² sàn, tức thêm được một đến hai chỗ ngồi.'))
P(('img','b80-15','Tối giản trong văn phòng 90m2: tông trắng, mảng xanh nhạt và cửa sổ lớn thay cho trang trí (Ảnh tham khảo)'))
P(('img','b80-36','Bố cục tối giản, thay tranh trang trí bằng cây xanh để không gian có sức sống (Ảnh tham khảo)'))
P(('img','b80-12','Tủ hồ sơ âm tường chạy suốt một mặt tường, giải phóng sàn cho chỗ ngồi (Ảnh tham khảo)'))
P(('img','b80-11','Một mảng tường sẫm duy nhất làm điểm nhấn, phần còn lại giữ trắng (Ảnh tham khảo)'))
P(('img','a70-06','Tông trắng be kết hợp sàn gỗ sáng màu, hoàn toàn chú trọng vào công năng (Nguồn: Internet)'))

P(('h3','6.3. Mẫu thiết kế văn phòng 90m2 phong cách xanh (Eco / Green Office)'))
P(('p','Phong cách xanh đưa cây xanh, vật liệu tự nhiên và ánh sáng trời thành thành phần chính của thiết kế chứ không phải đồ trang trí thêm vào cuối. Ở 90m², cách làm phổ biến là dùng bồn cây và giá cây thay cho vách ngăn, kết hợp lam gỗ, sàn gỗ và rèm sáng màu. Đây là phong cách tốn ít chi phí xây dựng nhất trong năm phong cách.'))
P(('lead','Ưu điểm với mặt bằng 90m²'))
P(('ul',[
  '**Chia khu mà không xây tường.** Một hàng bồn cây cao 1,2m tách được khu làm việc với lối đi mà không chắn sáng, không tính là vách, đúng thứ mặt bằng 90m² cần.',
  '**Tạo điểm nhấn rẻ nhất.** Mảng tường cây 3 – 5m² ở khu chờ gây ấn tượng mạnh hơn ốp đá cùng diện tích, chi phí thấp hơn hẳn.',
  '**Cải thiện cảm nhận không khí.** Ở mật độ 15 – 18 người, yếu tố này cảm nhận rõ hơn văn phòng thưa người.',
  '**Phù hợp định vị thương hiệu bền vững.** Khách nhìn thấy ngay từ khu chờ.']))
P(('p','Xét cùng một nhiệm vụ là tách khu làm việc chung khỏi lối đi trên mặt bằng 90m²: một vách thạch cao cao 1,2m dài 6m chiếm khoảng 0,6m² sàn nhưng chặn tầm nhìn và phải thi công tại chỗ; một dãy bồn cây cùng chiều dài chiếm khoảng 0,9m² sàn, không chặn sáng, lắp trong một buổi và tháo dời được khi đổi bố cục. Chênh 0,3m² là không đáng kể so với việc giữ được ánh sáng tự nhiên cho cả 16 chỗ ngồi phía trong.'))
P(('img','b80-37','Rèm sáng màu, cây lớn và bàn thấp ở khu tiếp khách, phong cách xanh áp dụng cho khu khách nhìn thấy đầu tiên (Ảnh tham khảo)'))
P(('img','b80-18','Cây cao và bàn dài dùng chung dưới giếng trời, cách lấy sáng cho khu làm việc sâu trong nhà (Ảnh tham khảo)'))
P(('img','b80-33','Giá sắt kết hợp chậu cây làm vách ngăn, chia khu mà không chắn sáng (Ảnh tham khảo)'))
P(('img','b80-31','Cây xanh là cách tạo điểm nhấn tiết kiệm nhất vì không phải xây thêm gì (Ảnh tham khảo)'))
P(('img','a70-08','Cây leo trần kết hợp lam gỗ ở khu tiếp khách (Ảnh tham khảo)'))
