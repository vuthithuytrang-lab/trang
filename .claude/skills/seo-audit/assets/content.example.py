# -*- coding: utf-8 -*-
"""Mẫu phần định tính — agent viết file này rồi chạy:

QUY TẮC SỐ MỘT: KHÔNG BỊA. Mọi con số trong file này phải là số đo được từ
data/pages.json, data/kw.json hoặc data/gsc_qp.json. Mọi domain nhắc tới phải có trong
tập đã crawl. Mọi mục nội dung của đối thủ phải có trong headings đã crawl.
Viết xong chạy: python3 scripts/verify_claims.py --data data --content content.py
Chi tiết: references/no-fabrication.md


    python3 scripts/build_report.py --data data --prefix demo --content content.py

Khoá của C là TÊN CỤM, đúng như trong data/clusters.json sau khi đã đặt tên tiếng Việt.
Mọi con số trong phần lý do phải lấy từ kết quả các script, không ước lượng.

Bảy khoá dùng được cho mỗi cụm — thiếu khoá nào thì mục đó không xuất hiện:

  rivals    : dict {domain: (mạnh ở, yếu ở, chỗ chen vào)}  → hiện ở mục 2
  meta      : list (thành phần, hiện tại, đề xuất, lý do)   → mục 9
  outline   : list (nhãn, tiêu đề H2, mô tả, [(nhãn, H3, ghi chú)]) → mục 10
              nhãn: keep · fix · new · gap · brand
  faq       : list (câu hỏi, hướng trả lời, vì sao đưa vào) → mục 11
  media     : list (hạng mục, hiện tại, đối thủ tốt nhất, mục tiêu) → mục 12
  alt       : list (tên file, alt text)                     → phụ của mục 12
  schema    : list (loại, trạng thái, việc cần làm)         → mục 13
  checklist : list (đợt, việc, vì sao ưu tiên, công sức)    → mục 14

Có thể thêm khoá '__tong_hop__' là chuỗi HTML, sẽ được chèn vào cuối file tổng hợp.
"""

C = {}

C['Nội thất ngân hàng'] = dict(

    rivals={
        'doithu-a.vn': (
            'Top 3 ở 20/26 từ khoá. Cụm "thiết kế nội thất ngân hàng" 14 lần, nhỉnh hơn mình 11 lần.',
            'Chỉ 2.294 từ, bằng 44% trang mình. Không có ngôn ngữ chuyên ngành: "chi nhánh" 0 lần. '
            'Cập nhật 25/09/2024, cũ gần 2 năm.',
            'Mình đang đứng trên ở toàn bộ 26 từ khoá. Giữ khoảng cách bằng cách cập nhật dự án '
            'và thêm FAQ có schema.'),
    },

    meta=[
        ('Title',
         'Dịch vụ tư vấn, thiết kế nội thất ngân hàng hiện đại, chuyên nghiệp (67 ký tự)',
         'Thiết kế nội thất ngân hàng trọn gói — chi nhánh và phòng giao dịch (66 ký tự)',
         'Title hiện thiếu hai cụm đang có từ khoá: "trọn gói" và "phòng giao dịch". '
         'Đối thủ đứng thứ hai đặt "trọn gói" ngay title.'),
        ('dateModified', '24/06/2026', 'Cập nhật sau mỗi đợt bổ sung dự án',
         'Cũ nhất trong nhóm trang dịch vụ chính, dù đây là nhóm có giá trị đơn hàng cao nhất.'),
    ],

    # MỖI MỤC PHẢI CÓ: nhãn · tiêu đề H2 · mật độ hiện tại → mục tiêu · độ dài · lý do có số
    # Số mật độ lấy từ mục 6 (ma trận mật độ) do script sinh, không ước lượng.
    outline=[
        ('keep', 'H2 1–7 hiện có',
         'GIỮ NGUYÊN — 5.265 từ, 7 H2 / 23 H3, trang đang thắng 26/26 từ khoá. '
         'Cụm "nội thất ngân hàng" 19 lần, cao nhất trong 6 trang đo được của cụm. '
         'Không tái cấu trúc, mọi thay đổi lớn đều là rủi ro thuần.', []),
        ('fix', 'H2 3. Tư vấn thiết kế nội thất ngân hàng trọn gói',
         'SỬA — nâng cụm "thiết kế nội thất ngân hàng" từ <b>11 lên 18–22 lần</b>, bám mức '
         'doithu-a.vn (14 lần trên trang chỉ 2.294 từ đang đứng thứ hai). '
         'Độ dài mục 450–600 từ, thêm 3–4 ảnh dự án chi nhánh.', [
            ('new', 'Gói trọn gói gồm những hạng mục nào',
             'Nhắm 5 từ khoá đuôi "trọn gói" đang ở vị trí 1. Dùng cụm đầy đủ ít nhất 3 lần.'),
            ('new', 'Tiến độ thi công và bàn giao',
             '4/14 trang top 10 có mục tiến độ, trang mình chưa có mục riêng.'),
        ]),
        ('new', 'H2 8. Câu hỏi thường gặp',
         'MỚI — 6/14 trang top 10 của nhóm có FAQ hiển thị, trang mình chưa có. '
         'Độ dài 350–450 từ, 8 câu, mỗi câu 40–60 từ. Xem bộ câu hỏi ở mục 11.', [
            ('new', 'Thiết kế chi nhánh khác phòng giao dịch thế nào',
             'Giữ thế mạnh cụm chuyên ngành: "chi nhánh" 7 lần và "phòng giao dịch" 7 lần, '
             'trong khi doithu-a.vn lần lượt 0 và 3.'),
        ]),
    ],

    faq=[
        ('Thiết kế nội thất ngân hàng trọn gói gồm những gì?',
         'Liệt kê đủ hạng mục từ khảo sát tới bàn giao.',
         'Nhắm nhóm từ khoá đuôi trọn gói'),
        ('Chi nhánh và phòng giao dịch thiết kế khác nhau ra sao?',
         'So sánh theo diện tích, luồng khách, khu quầy.',
         'Giữ thế mạnh: "chi nhánh" 7 lần, đối thủ 0 lần'),
    ],

    media=[
        ('Ảnh nội dung', '62', 'doithu-a.vn 26', 'Giữ nguyên'),
        ('Ảnh WebP', '2/62', 'doithu-a.vn 6', 'Toàn bộ'),
    ],
    alt=[('thiet-ke-noi-that-ngan-hang-chi-nhanh-200m2-01.webp',
          'Thiết kế nội thất ngân hàng chi nhánh 200m2')],

    schema=[
        ('FAQPage', 'Chưa có', 'Khai sau khi render thật ra HTML.'),
        ('Organization / LocalBusiness', 'Chưa có trên bất kỳ trang nào của site',
         'Khai một lần ở cấp template, hiệu lực toàn site.'),
    ],

    checklist=[
        ('1', 'Không sửa cấu trúc, không viết lại',
         'Trang đang thắng 26/26 từ khoá.', 'Không'),
        ('2', 'Cập nhật dự án mới và làm tươi dateModified',
         'Mốc hiện tại 24/06/2026, cũ nhất trong nhóm trang dịch vụ.', 'Thấp'),
        ('3', 'Thêm khối FAQ có schema',
         '6/14 trang top 10 của nhóm có FAQ hiển thị, trang mình chưa có.', 'Thấp'),
    ],
)
