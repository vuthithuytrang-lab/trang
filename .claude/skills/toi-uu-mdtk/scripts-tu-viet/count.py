import json,sys,re
d=json.load(open(sys.argv[1]));c=d.get('content',d);body=c['tabs'][0]['documentTab']['body']
lines=[]
def w(cs):
  for el in cs:
    if 'paragraph' in el:
      t=''.join(r.get('textRun',{}).get('content','') for r in el['paragraph']['elements'])
      lines.append((el['startIndex'],el['paragraph'].get('paragraphStyle',{}).get('namedStyleType',''),t))
    elif 'table' in el:
      for r in el['table']['tableRows']:
        for cell in r['tableCells']: w(cell['content'])
w(body['content'])
start=int(sys.argv[2])
for k in sys.argv[3:]:
  hits=[(i,s[:9]) for i,s,t in lines if i>=start for _ in range(t.lower().count(k))]
  print(len(hits),k,hits)
