import json,sys
d=json.load(open(sys.argv[1]))
d=d.get('content',d)
body=d['tabs'][0]['documentTab']['body']['content']
end=body[-1]['endIndex']
paras=[]
def walk(cs):
    for c in cs:
        if 'paragraph' in c: paras.append(c)
        elif 'table' in c:
            for r in c['table']['tableRows']:
                for cell in r['tableCells']: walk(cell['content'])
walk(body)
# status
ls=set(p['paragraph']['paragraphStyle'].get('lineSpacing') for p in paras)
fonts=set();sizes={}
for p in paras:
    st=p['paragraph']['paragraphStyle'].get('namedStyleType')
    for e in p['paragraph']['elements']:
        ts=e.get('textRun',{}).get('textStyle',{})
        fonts.add(ts.get('weightedFontFamily',{}).get('fontFamily'))
        sizes.setdefault(st,set()).add(ts.get('fontSize',{}).get('magnitude'))
print("STATUS",json.dumps({'end':end,'lineSpacing':list(ls),'fonts':list(fonts),'sizes':{k:list(v) for k,v in sizes.items()}},ensure_ascii=False),file=sys.stderr)
# normal ranges (merge contiguous)
hs=[(p['startIndex'],p['endIndex']) for p in paras if p['paragraph']['paragraphStyle'].get('namedStyleType','NORMAL_TEXT')!='NORMAL_TEXT']
rngs=[];cur=1
for a,b in sorted(hs):
    if a>cur: rngs.append([cur,a])
    cur=max(cur,b)
if cur<end-1: rngs.append([cur,end-1])
reqs=[{"updateParagraphStyle":{"range":{"startIndex":1,"endIndex":end-1},"paragraphStyle":{"lineSpacing":150},"fields":"lineSpacing"}},
{"updateTextStyle":{"range":{"startIndex":1,"endIndex":end-1},"textStyle":{"weightedFontFamily":{"fontFamily":"Google Sans"}},"fields":"weightedFontFamily"}}]
for s,e in rngs:
    reqs.append({"updateTextStyle":{"range":{"startIndex":s,"endIndex":e},"textStyle":{"fontSize":{"magnitude":11,"unit":"PT"}},"fields":"fontSize"}})
print(json.dumps({"rev":d['revisionId'],"requests":reqs},ensure_ascii=False))
