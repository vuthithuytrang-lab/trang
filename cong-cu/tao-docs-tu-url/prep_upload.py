# prep_upload.py <batch> '<json titles>' — ghi report/upload.json, chạy kiemtra
import json,sys,os,subprocess
W='/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/pil/'
b=sys.argv[1]; D=W+b+'/'
if len(sys.argv)>2: json.dump(json.loads(sys.argv[2]),open(D+'report.json','w'),ensure_ascii=False)
rep=json.load(open(D+'report.json'))
ok=[r for r in rep if r.get('status','ok')=='ok' and os.path.exists(D+f"final/r{r['row']}.html")]
json.dump([{"file":D+f"final/r{r['row']}.html","title":r['title']} for r in ok],open(D+'upload.json','w'),ensure_ascii=False)
k=json.loads(subprocess.run(['python3','-I',W+'kiemtra.py',D],capture_output=True,text=True).stdout)
for row,v in k.items(): print(row,'OK' if v['ok'] else v['loi'])
print('upload:',len(ok),'| lỗi/bỏ:',[r['row'] for r in rep if r not in ok])
