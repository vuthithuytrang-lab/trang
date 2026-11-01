import json,sys
raw,spec,out=sys.argv[1:4]
d=json.load(open(raw)); c=d.get('content',d)
body=c['tabs'][0]['documentTab']['body']
paras={}
def walk(content):
    for el in content:
        if 'paragraph' in el:
            t=''.join(r.get('textRun',{}).get('content','') for r in el['paragraph']['elements'])
            paras[el['startIndex']]=t
        elif 'table' in el:
            for r in el['table']['tableRows']:
                for cell in r['tableCells']: walk(cell['content'])
walk(body['content'])
sp=json.load(open(spec)); kws=[k.lower() for k in sp['keywords']]
ops=[]
for e in sp['edits']:
    t=paras[e['para']]; old,new=e['old'],e['new']
    assert t.count(old)==1,(e['para'],old)
    base=e['para']+t.index(old)
    p=0
    while p<min(len(old),len(new)) and old[p]==new[p]: p+=1
    s=0
    while s<min(len(old),len(new))-p and old[-1-s]==new[-1-s]: s+=1
    ins=new[p:len(new)-s]; dl=(base+p,base+len(old)-s)
    a,b=p,len(new)-s; nl=new.lower()
    for k in kws:
        i=nl.find(k)
        while i>=0:
            if i<b and i+len(k)>a: a,b=min(a,i),max(b,i+len(k))
            i=nl.find(k,i+1)
    ops.append((base+p,dl,ins,base+a,base+b))
ops.sort(key=lambda o:-o[0])
reqs=[]
for start,dl,ins,ha,hb in ops:
    if dl[1]>dl[0]: reqs.append({'deleteContentRange':{'range':{'startIndex':dl[0],'endIndex':dl[1]}}})
    if not ins: continue
    reqs.append({'insertText':{'location':{'index':start},'text':ins}})
    # highlight range in post-edit coordinates of this edit; later edits are at lower indices so unaffected
    reqs.append({'updateTextStyle':{'range':{'startIndex':ha,'endIndex':hb},'textStyle':{'backgroundColor':{'color':{'rgbColor':{'red':1,'green':1,'blue':0}}}},'fields':'backgroundColor'}})
json.dump({'requests':reqs,'revisionId':c['revisionId']},open(out,'w'),ensure_ascii=False)
print(len(ops),'edits',len(reqs),'requests; rev',c['revisionId'][:12])
