import json,subprocess,sys,re,importlib.util,os
sys.argv=['x','0','2000-01-01T00:00:00+00:00']
src=open('post-hoa.py').read().replace('\nmain()\n','\n')
ns={'__file__':os.path.abspath('post-hoa.py')};exec(src,ns)
for l in open('da-dang.jsonl'):
    x=json.loads(l)
    code,r=ns['curl']([ns['API']+f"/posts/{x['id']}?context=edit&fields=content"])
    local=ns['to_gutenberg'](open(f"bai/{x['row']}/wp-hoa.html",encoding='utf-8').read())
    norm=lambda s:re.sub(r'\s+',' ',s).strip()
    print(x['row'],'GIONG' if norm(r['content'])==norm(local) else 'KHAC')
