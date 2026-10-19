# ghi.py — lập danh sách ô H/E cần ghi cho các file đã soát đạt (thiếu chữ = 0, hoặc chỉ thiếu chữ Hán do PDF)
import json,os,subprocess,re
W='/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/pil/'
v=json.load(open(W+'verified.json')); written=json.load(open(W+'written.json')) if os.path.exists(W+'written.json') else {}
extra=json.load(open(W+'ghichu_them.json')) if os.path.exists(W+'ghichu_them.json') else {}
out={}
for rel,x in v.items():
    ok = x['thieu']<=1 or (x['thieu']<=3 and all(re.fullmatch(r'[\u4e00-\u9fff]+',t) or len(t)<=2 for t in x['thieu_mau']))  # chữ Hán / mảnh chữ do dấu tách khi đọc PDF
    b,f=rel.split('/')[0],rel.split('/')[-1]; row=int(f[1:-5])
    slug=[r['B'] for r in json.load(open(W+b+'/rows.json')) if r['row']==row][0].lower()
    if not ok and x['thieu']<=3 and all(t.isascii() and t.lower() in slug for t in x['thieu_mau']): ok=True  # chữ trong đường dẫn URL bị ngắt dòng khi đọc PDF
    if rel in (json.load(open(W+'chapnhan.json')) if os.path.exists(W+'chapnhan.json') else []): ok=True  # đã xem tay: chỉ là chữ bị tách khi đọc PDF
    if not ok: continue
    if written.get(str(row))==x['id']: continue
    k=json.loads(subprocess.run(['python3','-I',W+'kiemtra.py',W+b+'/'],capture_output=True,text=True).stdout)[str(row)]
    e=k['ghichu_E'] + (('\n'+extra[str(row)]) if str(row) in extra else '')
    out[row]=dict(H=f"https://docs.google.com/document/d/{x['id']}/edit",E=e)
json.dump(out,open(W+'canghi.json','w'),ensure_ascii=False,indent=1)
print(sorted(out))
