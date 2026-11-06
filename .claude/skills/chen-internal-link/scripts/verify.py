# verify.py <relpath final html> <tool-result json> — so chữ file Docs (PDF) với bản final; ghi kết quả vào verified.json
import json,base64,subprocess,re,difflib,sys,os,tempfile
W='/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/pil/'
rel,f=sys.argv[1],sys.argv[2]
d=json.load(open(f)); pdf=tempfile.mktemp(suffix='.pdf',dir=W+'soat3'); open(pdf,'wb').write(base64.b64decode(d['content']))
txt=subprocess.run(['pdftotext',pdf,'-'],capture_output=True,text=True).stdout; os.remove(pdf)
from bs4 import BeautifulSoup
src=BeautifulSoup(open(W+rel,encoding='utf-8').read(),'lxml').get_text(' ')
w=lambda t: re.findall(r'[\wÀ-ỹ]+',__import__('unicodedata').normalize('NFC',t.replace('\xa0',' ')))
a,b=w(src),w(txt); r=difflib.SequenceMatcher(None,a,b,autojunk=False).ratio()
from collections import Counter
miss=Counter(x for x in a if not x.isdigit())-Counter(x for x in b if not x.isdigit())
thieu=sum(miss.values())
v=json.load(open(W+'verified.json')) if os.path.exists(W+'verified.json') else {}
v[rel]=dict(id=d['id'],ratio=round(r*100,2),thieu=thieu,thieu_mau=list(miss)[:8],title=d.get('title')); json.dump(v,open(W+'verified.json','w'),indent=1,ensure_ascii=False)
print(rel,d['id'][:10],round(r*100,2),'% thiếu',thieu,list(miss)[:6])
