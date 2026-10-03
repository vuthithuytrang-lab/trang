#!/usr/bin/env python3
"""Viết báo cáo 9 mục theo quy trình bản 2.
Chạy: python3 tao-bao-cao.py dd/mm/yyyy <link-google-docs> "<ngày VnExpress>" "<ngày Topi + ghi chú>"  (sau tao-file-docs.py)"""
import json, sys
ngay, link, vne, topi = sys.argv[1:5]
r = json.load(open('tam/result.json'))
doi = json.load(open('tam/doi-ngay.json'))
k = lambda x: f'{x} tháng'
L = [f'# Báo cáo cập nhật lãi suất – {ngay}', '',
     f'## 1. Link file Google Docs', '', link, '',
     '## 2. Ngày tháng đã đổi (Bước 1)', '']
L += [f'- {d}' for d in doi] or ['- Ngày, tháng trong bài đã đúng, không đổi.']
L += ['- Tháng (10/2026) trong các đoạn văn đã đúng tháng hiện tại → giữ nguyên, không tô.' if not any('tháng' in d for d in doi) else '', '',
      '## 3. Ngày dữ liệu nguồn', '', f'- VnExpress: {vne}', f'- Topi: {topi}',
      '- Biểu lãi suất ngân hàng (Bước 4.2): không dùng — mọi ngân hàng trong bài đều có trên VnExpress hoặc Topi.', '',
      f'## 4. Ô đã sửa từ VnExpress và Topi ({len(r["changes"])} ô)', '']
for tb in ['Tại quầy', 'Online']:
    L += [f'**Bảng {tb}**', '']
    L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (nguồn: {c[5]})' for c in r['changes'] if c[0] == tb]
    L.append('')
L += [f'## 5. Ô lấy theo kỳ hạn gần nhất – Trường hợp A ({len(r["caseA"])} ô có đổi)', '']
L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} → {c[4]} (lấy theo kỳ hạn {c[6]} tháng)' for c in r['caseA']] or ['- Không có.']
L += ['', 'Ô cũng thuộc Trường hợp A nhưng số trùng số cũ (không sửa, không tô):', '']
L += [f'- Bảng {c[0]} – {c[1]} – {k(c[2])}: {c[3]} (theo kỳ hạn {c[6]} tháng)' for c in r['sameA']]
L += ['', '## 6. Ô lấy từ trang chính thức – Trường hợp B', '', 'Không có.', '',
      '## 7. Ô điền "-" do không có trên 2 website và chưa có link trang chính thức', '', 'Không có.', '']
open(f'bao-cao/{ngay[6:]}-{ngay[3:5]}-{ngay[:2]}.md', 'w').write('\n'.join(L))
print('\n'.join(L))
