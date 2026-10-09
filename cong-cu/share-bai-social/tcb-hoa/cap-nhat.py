#!/usr/bin/env python3
"""Cập nhật nội dung + tiêu đề bài đã đăng/hẹn giờ theo bản mới nhất (giữ nguyên giờ đăng). Usage: cap-nhat.py <row>..."""
import json,os,sys,subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(HERE,'post-hoa.py')).read().replace('\nmain()\n','\n')
ns={'__file__':os.path.join(HERE,'post-hoa.py')};exec(src,ns)
ids={json.loads(l)['row']:json.loads(l)['id'] for l in open(os.path.join(HERE,'da-dang.jsonl'))}
for row in sys.argv[1:]:
    d=os.path.join(HERE,'bai',row)
    if subprocess.run([sys.executable,'-I',os.path.join(HERE,'kiem-tra.py'),d]).returncode: print(row,'chua qua kiem tra'); continue
    m=json.load(open(os.path.join(d,'meta.json'),encoding='utf-8'))
    code,r=ns['curl'](['-X','POST',ns['API']+f'/posts/{ids[int(row)]}'],{'title':m['title'],'content':ns['to_gutenberg'](open(os.path.join(d,'wp-hoa.html'),encoding='utf-8').read()),'excerpt':m.get('excerpt','')})
    print(row,code,r.get('status'),r.get('date'))
