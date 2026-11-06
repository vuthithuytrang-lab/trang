import json,sys
d=json.load(open(sys.argv[1])); a,b=int(sys.argv[2]),int(sys.argv[3])
body=d['tabs'][0]['documentTab']['body']['content'] if 'tabs' in d else d['body']['content']
for el in body:
    p=el.get('paragraph')
    if not p or el['endIndex']<=a or el['startIndex']>=b: continue
    print('== P',el['startIndex'],el['endIndex'],p['paragraphStyle'].get('alignment'))
    for r in p['elements']:
        t=r.get('textRun')
        if not t: print('  [obj]',r['startIndex']); continue
        st=t.get('textStyle',{}); k=[x for x in ('bold','italic') if st.get(x)]
        if 'backgroundColor' in st: k.append('BG')
        if 'foregroundColor' in st: k.append('FG'+str(st['foregroundColor'].get('color',{}).get('rgbColor')))
        if 'link' in st: k.append('LINK:'+st['link'].get('url','')[-40:])
        print(f"  {r['startIndex']}-{r['endIndex']} {k} {t['content']!r}")
