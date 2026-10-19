# reg.py '<json list from upload agent>' — ghi id file Docs đã tải lên vào uploaded.json
import json,sys,os
W='/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/pil/'
reg=json.load(open(W+'uploaded.json')) if os.path.exists(W+'uploaded.json') else {}
for x in json.loads(sys.argv[1]):
    k=x['file'].replace(W,''); reg.setdefault(k,[]).append(x['id'])
json.dump(reg,open(W+'uploaded.json','w'),indent=1); print(len(reg),'files registered')
