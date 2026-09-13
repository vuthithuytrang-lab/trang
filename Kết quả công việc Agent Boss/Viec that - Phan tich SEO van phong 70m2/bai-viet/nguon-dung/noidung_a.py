# -*- coding: utf-8 -*-
# Phần A: mở bài + mục 1, 2, 3
A = []
P = A.append

P(('h1','Thiết kế văn phòng 70m2: bố trí thế nào cho đủ 10–15 chỗ ngồi'))
P(('meta','Tác giả: Đặng Trường Minh — Giám đốc Thiết kế · Cập nhật 13/09/2026'))

P(('sapo','**Thiết kế văn phòng 70m2** là bài toán của sự lựa chọn: giữ phòng giám đốc riêng, giữ phòng họp kín hay giữ đủ chỗ ngồi cho cả đội — rất khó có cả ba cùng lúc.'))
P(('sapo','Cùng một mặt bằng 70m², có nơi bố trí được 10 chỗ ngồi, có nơi lên tới 15. Chênh lệch đó không đến từ diện tích mà đến từ những gì doanh nghiệp chấp nhận bỏ bớt ngay trên bản vẽ đầu tiên. Bỏ sai chỗ thì hoặc thiếu chỗ ngồi chỉ sau một năm, hoặc có phòng họp mà gần như không ai dùng.'))
P(('sapo','Bài viết đưa bảng phân bổ diện tích từng khu, bảng "giữ gì — mất gì", ba sơ đồ mặt bằng vẽ theo ba hình dạng thực tế, các mẫu thiết kế theo phong cách và chi phí tham khảo theo giá thị trường — để doanh nghiệp có căn cứ chốt phương án ngay từ đầu.'))

P(('img','a70-01','Thiết kế văn phòng 70m2 — cùng một diện tích nhưng số chỗ ngồi thay đổi theo cách chia mặt bằng'))

# ---------------- MUC 1 ----------------
P(('h2','1. Văn phòng 70m2 bố trí được bao nhiêu người?'))
P(('p','Đây là câu hỏi phải trả lời trước tiên, vì nó quyết định mọi thứ còn lại: có làm nổi phòng giám đốc riêng không, phòng họp mấy chỗ, pantry đặt ở đâu. Trả lời sai ở bước này thì bản vẽ đẹp đến mấy cũng phải làm lại.'))

P(('h3','1.1. Ba mức bố trí và số chỗ ngồi tương ứng'))
P(('p','Diện tích trung bình cho mỗi người là con số quyết định. Cùng 70m², chỉ cần đổi từ 4m² sang 7m² mỗi người là số chỗ ngồi giảm đi một nửa.'))
P(('table',
   ['Mức bố trí','Diện tích mỗi người','Số chỗ ngồi trong 70m²','Phù hợp với'],
   [['Tiết kiệm','3 – 4 m²','14 – 18 chỗ','Bàn nhỏ, ít chỗ lưu trữ, gần như không có phòng kín'],
    ['Trung bình — phổ biến nhất','5 – 6 m²','10 – 13 chỗ','Đủ thoải mái cho công việc giấy tờ, vẫn giữ được 1–2 phòng kín'],
    ['Chuẩn','7 – 10 m²','6 – 9 chỗ','Vị trí cần không gian riêng: lãnh đạo, tư vấn, luật sư']]))
P(('note','Cơ sở tham khảo: TCVN 4601:2012 — Công sở cơ quan hành chính nhà nước (tiêu chuẩn diện tích làm việc) và các tài liệu tiêu chuẩn diện tích văn phòng thương mại. Đây là khoảng tham khảo, không phải con số bắt buộc.'))

P(('h3','1.2. Vì sao mỗi nơi lại nói một con số khác nhau?'))
P(('p','Nếu tra cứu, doanh nghiệp sẽ gặp ba câu trả lời vênh nhau cho cùng một diện tích 70m²: có tài liệu nói 6 – 10 người, có nơi nói 10 – 15 người, có nơi nói tới 30 người. Cả ba đều không sai — chúng chỉ đang nói về ba cách chia khác nhau.'))
P(('p','Ba yếu tố tạo ra khoảng chênh đó:'))
P(('ul',[
  '**Số phòng kín.** Mỗi phòng kín lấy đi 8 – 12m² và thêm một phần tường, vách. Văn phòng ba phòng kín và văn phòng không phòng kín nào chênh nhau khoảng 5 chỗ ngồi.',
  '**Kích thước bàn.** Bàn 1,2m × 0,6m và bàn 1,6m × 0,8m chênh nhau gần gấp đôi diện tích mặt bàn. Trên 70m², chọn bàn lớn hơn đồng nghĩa mất 3 – 4 chỗ.',
  '**Bề rộng lối đi.** Lối đi chính 1,2m và lối đi 1,5m chênh nhau vài mét vuông trên toàn mặt bằng — đủ để mất thêm một đến hai chỗ ngồi.']))
P(('p','Vì vậy khi một đơn vị báo "70m² ngồi được 20 người", doanh nghiệp nên hỏi lại ngay: 20 người đó có bao gồm phòng họp và phòng giám đốc không, bàn rộng bao nhiêu, lối đi bao nhiêu mét.'))

P(('h3','1.3. Ở 70m2, cách chia quan trọng hơn diện tích'))
P(('p','Đây là điểm khác biệt lớn nhất giữa văn phòng 70m² và văn phòng vài trăm mét vuông. Ở diện tích lớn, thừa vài mét vuông không ảnh hưởng gì. Ở 70m², mỗi mét vuông bố trí sai là mất thẳng một phần chỗ ngồi — và chỗ ngồi là thứ doanh nghiệp cảm nhận được hằng ngày.'))
P(('p','Toàn bộ phần còn lại của bài viết đi theo đúng logic đó: trước hết là những gì phải bỏ bớt, sau đó mới đến cách chia và phong cách.'))
P(('img','a70-17','Bản vẽ bố trí mặt bằng văn phòng 70m2 — khu làm việc chung, phòng họp nhỏ và phòng làm việc riêng trên cùng một sàn'))

# ---------------- MUC 2 ----------------
P(('h2','2. Ở 70m2, giữ thêm một phòng riêng là mất mấy chỗ ngồi?'))
P(('p','Trên mặt bằng 70m², mọi thứ đều phải trả giá bằng chỗ ngồi. Bảng dưới đây quy đổi thẳng từng hạng mục quen thuộc ra số chỗ ngồi bị mất, để doanh nghiệp cân nhắc bằng con số thay vì bằng cảm tính.'))
P(('table',
   ['Muốn giữ','Chiếm diện tích','Trả bằng'],
   [['Phòng giám đốc riêng','8 – 12 m²','−2 chỗ ngồi'],
    ['Phòng họp kín tiếng (vách đặc, cách âm)','10 – 12 m²','−2 đến −3 chỗ ngồi'],
    ['Pantry riêng có bàn ăn','3 – 5 m²','−1 chỗ ngồi'],
    ['Lối đi rộng đúng chuẩn (1,4 – 1,5m thay vì 1,2m)','thêm 3 – 5 m² lối đi','−1 đến −2 chỗ ngồi']]))
P(('p','Cộng cả bốn hạng mục là mất 6 – 8 chỗ ngồi. Đó chính là lý do vì sao cùng 70m² mà nơi này ngồi 10 người, nơi kia ngồi 16 người.'))

P(('h3','2.1. Ba tổ hợp thường dùng theo loại hình doanh nghiệp'))
P(('p','Không có phương án nào đúng cho tất cả. Ba tổ hợp dưới đây là ba cách chọn phổ biến nhất, kèm loại hình doanh nghiệp thường chọn chúng.'))
P(('table',
   ['Tổ hợp','Giữ gì — bỏ gì','Số chỗ ngồi','Hợp với'],
   [['A — Ưu tiên lãnh đạo','Giữ phòng giám đốc riêng, bỏ phòng họp kín (họp ngay tại bàn dài hoặc khu tiếp khách)','13 – 14 chỗ','Công ty tư vấn, luật, tài chính: lãnh đạo tiếp khách riêng thường xuyên, họp nội bộ ít'],
    ['B — Ưu tiên đội nhóm','Bỏ phòng giám đốc, giữ phòng họp vách kính 6 chỗ','14 – 15 chỗ','Công ty công nghệ, agency: họp nhóm liên tục, lãnh đạo ngồi chung với đội'],
    ['C — Giữ cả hai','Giữ cả phòng giám đốc và phòng họp, chấp nhận ít chỗ ngồi','10 – 11 chỗ','Công ty ít người nhưng tiếp khách nhiều']]))
P(('p','Một mẹo giúp đỡ đau đầu: phòng họp bằng **vách kính** thay vì vách đặc giữ lại được cảm giác rộng và ánh sáng cho cả sàn, đổi lại chỉ giảm khả năng cách âm. Với đa số doanh nghiệp dưới 15 người, đây là đánh đổi đáng giá.'))
P(('img','a70-19','Cách bố trí khu vực chức năng trong văn phòng 70m2 — khu làm việc chung, phòng họp lớn, phòng họp nhỏ và pantry trên cùng một mặt bằng'))
