#!/usr/bin/env python3
"""Lấy số liệu lãi suất hằng ngày cho bài blog Techcombank và so với bảng trên bài.
Chạy: python3 lay-so-lieu.py  (tạo thư mục tam/ chứa dữ liệu nguồn và result.json)
VnExpress: bảng trên trang chủ đề được nạp từ API gw.vnexpress.net/th?types=bank_rate_offline|bank_rate_online
"""
import subprocess,os
os.makedirs('tam',exist_ok=True); os.chdir('tam')
def get(u,f): subprocess.run(['curl','-sS','-L','-m','40','-A','Mozilla/5.0','-o',f,u],check=True)
get('https://techcombank.com/thong-tin/blog/lai-suat-tiet-kiem','88bfca.html')
get('https://topi.vn/lai-suat-tiet-kiem-ngan-hang-nao-cao-nhat.html','340b92.html')
for t in ['bank_rate_offline','bank_rate_online']: get('https://gw.vnexpress.net/th?types='+t,t+'.json')
import re as _re,html as _h,json as _j
_s=open('88bfca.html',encoding='utf-8').read()
_txt=lambda x:_re.sub(r'\s+',' ',_h.unescape(_re.sub(r'<[^>]+>',' ',x))).strip()
_out=[]
for tb in _re.findall(r'<table.*?</table>',_s,_re.S):
    rows=[[_txt(c) for c in _re.findall(r'<t[dh].*?</t[dh]>',r,_re.S)] for r in _re.findall(r'<tr.*?</tr>',tb,_re.S)]
    if len(rows)>10: _out.append(rows)
_j.dump(_out,open('tcb_tables.json','w'),ensure_ascii=False)
import json,re,html
tcb=json.load(open('tcb_tables.json'))
vne={'quay':{r['bank']:r for r in json.load(open('bank_rate_offline.json'))['data']['bank_rate_offline']},
     'online':{r['bank']:r for r in json.load(open('bank_rate_online.json'))['data']['bank_rate_online']}}
s=open('340b92.html',encoding='utf-8').read()
def txt(x): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',x))).strip()
tabs=re.findall(r'<table.*?</table>',s,re.S)[:2]
topi={}
for key,tb in zip(['quay','online'],tabs):
    rows=[[txt(c) for c in re.findall(r'<t[dh].*?</t[dh]>',r,re.S)] for r in re.findall(r'<tr.*?</tr>',tb,re.S)]
    topi[key]={r[0]:dict(zip(['1','3','6','12','18','24','36'],r[2:])) for r in rows[1:]}
VN={'MBBank':'MB','PVcomBank':'PVCombank','BAOVIET Bank':'BaoVietBank','Viet Capital Bank (BVBANK)':'BVBank','PG Bank':'PGBank','VCB Neo (CBBank)':'VCBNeo','CBBank':'VCBNeo','OceanBank':'MBV'}
TP={'MBBank':'MB Bank','Kienlongbank':'Kiên Long','VietBank':'Vietbank','NamABank':'Nam Á Bank','Vikki Bank':'Vikkibank (Đông Á)','BAOVIET Bank':'Bảo Việt','Viet Capital Bank (BVBANK)':'BVBank','PG Bank':'PGBank','BacABank':'Bắc Á','VCB Neo (CBBank)':'VCBNeo (CBBank)','CBBank':'VCBNeo (CBBank)','OceanBank':'MBV (OceanBank)'}
T=['1','3','6','12','18','24','36']
def num(x):
    try: return float(str(x).replace(',','.'))
    except: return None
def fmt(v,old):
    st=('%g'%v)
    if '.' not in st and re.fullmatch(r'\d+\.\d+',old): st+='.0'
    return st
changes=[];caseA=[];same_caseA=[];notes=[]
for key,tb in zip(['quay','online'],tcb):
    for row in tb[1:]:
        name=re.sub(r'\s+',' ',row[0]).strip()
        name=name.replace('(BVBANK)',' (BVBANK)').replace('(CBBank)',' (CBBank)').replace('  ',' ')
        if name=='Techcombank': continue
        v=vne[key].get(VN.get(name,name)); t=topi[key].get(TP.get(name,name))
        if v is None: notes.append(f'{key} {name}: không thấy trên VnExpress')
        if t is None: notes.append(f'{key} {name}: không thấy trên Topi')
        new={}
        for k in ['1','3','6','12']:
            new[k]=(num(v['rate_'+k]) if v else None,'VnExpress')
        for k in ['18','24','36']:
            new[k]=(num(t[k]) if t else None,'Topi')
        for i,k in enumerate(T):
            if new[k][0] is None:
                base=None
                for j in range(i-1,-1,-1):
                    if new[T[j]][0] is not None and new[T[j]][1]!='A': base=T[j];break
                if base is None:
                    for j in range(i+1,7):
                        if new[T[j]][0] is not None and new[T[j]][1]!='A': base=T[j];break
                new[k]=(new[base][0],'A',base) if base else ('-','A',None)
        for i,k in enumerate(T):
            old=row[i+1].strip(); val=new[k]
            same = val[0]=='-' and old=='-' or (val[0]!='-' and num(old)==val[0])
            rec=(('Tại quầy' if key=='quay' else 'Online'),name,k,old,val[0] if val[0]=='-' else fmt(val[0],old),val[1],val[2] if len(val)>2 else None)
            if val[1]=='A': (same_caseA if same else caseA).append(rec)
            elif not same: changes.append(rec)
print('CHANGES (VnE/Topi):');[print(c) for c in changes]
print('CASE A changed:');[print(c) for c in caseA]
print('CASE A same:');[print(c) for c in same_caseA]
print('NOTES:',notes)
json.dump({'changes':changes,'caseA':caseA,'sameA':same_caseA},open('result.json','w'),ensure_ascii=False,indent=1)
