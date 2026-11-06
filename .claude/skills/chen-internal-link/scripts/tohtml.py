# tohtml.py <saved read_doc> <out.json> : read_doc JSON -> {"title","content":html} for docchk.py
import json,sys,html
d=json.load(open(sys.argv[1])); d=d.get('content',d)
out=[]
def para(p):
    st=p.get('paragraphStyle',{}).get('namedStyleType','NORMAL_TEXT')
    tag={'HEADING_1':'h1','HEADING_2':'h2','HEADING_3':'h3','TITLE':'h1'}.get(st,'li' if 'bullet' in p else 'p')
    s=''
    for e in p.get('elements',[]):
        tr=e.get('textRun')
        if not tr: continue
        ts=tr.get('textStyle',{}); t=html.escape(tr['content'])
        bg=ts.get('backgroundColor',{}).get('color',{}).get('rgbColor',{})
        y=bg.get('red',0)==1 and bg.get('green',0)==1 and bg.get('blue',0)==0
        t='<span style="background-color:#ffff00">%s</span>'%t if y else '<span>%s</span>'%t
        if 'link' in ts and ts['link'].get('url'): t='<a href="%s">%s</a>'%(html.escape(ts['link']['url']),t)
        s+=t
    return '<%s>%s</%s>'%(tag,s,tag)
def walk(cs):
    for el in cs:
        if 'paragraph' in el: out.append(para(el['paragraph']))
        elif 'table' in el:
            for r in el['table']['tableRows']:
                for c in r['tableCells']: walk(c['content'])
for t in d['tabs']: walk(t['documentTab']['body']['content'])
json.dump({'title':d.get('title'),'content':'<html><body>'+''.join(out)+'</body></html>'},open(sys.argv[2],'w'))
