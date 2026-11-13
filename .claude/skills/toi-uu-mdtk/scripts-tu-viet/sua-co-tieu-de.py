import json,sys
d=json.load(open(sys.argv[1]));d=d.get('content',d)
reqs=[]
def walk(cs):
    for c in cs:
        if 'table' in c:
            for r in c['table']['tableRows']:
                for cell in r['tableCells']: walk(cell['content'])
        p=c.get('paragraph')
        if not p or p['paragraphStyle'].get('namedStyleType','NORMAL_TEXT')=='NORMAL_TEXT': continue
        s=c['startIndex']; e0=p['elements'][0]
        fs=e0.get('textRun',{}).get('textStyle',{}).get('fontSize')
        reqs.append({"updateTextStyle":{"range":{"startIndex":s,"endIndex":s+1},"textStyle":({"fontSize":fs} if fs else {}),"fields":"fontSize"}})
walk(d['tabs'][0]['documentTab']['body']['content'])
print(d['documentId']);print(json.dumps(reqs))
