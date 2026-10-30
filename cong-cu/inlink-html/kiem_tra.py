"""So cột HTML trên sheet (bản xuất .xlsx mới) với cells.json.
python3 kiem_tra.py <file.xlsx> <cells.json> <cot_html>   -> in các dòng còn sai
"""
import sys, json, unicodedata as u
import openpyxl
from openpyxl.utils import column_index_from_string
ws = openpyxl.load_workbook(sys.argv[1], data_only=True)['Plan internal links - Tổng']
c = column_index_from_string(sys.argv[3])
exp = json.load(open(sys.argv[2], encoding='utf-8'))
bad = [k for k, v in exp.items() if u.normalize('NFC', str(ws.cell(int(k), c).value or '')).strip() != u.normalize('NFC', v).strip()]
print('Tổng', len(exp), '| Sai/thiếu:', bad)
