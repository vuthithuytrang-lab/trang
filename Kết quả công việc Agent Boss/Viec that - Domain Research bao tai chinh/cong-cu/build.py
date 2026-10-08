import json,re,sys,collections
from difflib import SequenceMatcher
sys.path.insert(0,'scripts'); from nz import nz; from topics import T,M
rows=json.load(open('keep.json'))
for r in rows: r['t']=nz(r['title'])
SITES=[('thitruongtaichinhtiente.vn','tttc'),('thoibaotaichinhvietnam.vn','tbtc'),('tapchitaichinh.vn','tc')]
SNAME={'tttc':'Thị trường Tài chính Tiền tệ','tbtc':'Thời báo Tài chính','tc':'Tạp chí Kinh tế - Tài chính'}
LBL={'Đã triển khai':'Đã có','Đã triển khai một phần':'Một phần','Đang trong kế hoạch':'Đã lên kế hoạch','Đã có trong scope keyword, chưa viết':'Mới','Chủ đề mới':'Mới'}
def concl(A,B,risk):
    if risk=='Cao': return 'Không phù hợp'
    if A>=2 and B>=2: return 'Phù hợp'
    if A>=2 and B==1: return 'Cân nhắc'
    return 'Không phù hợp'
hits={k:[r for r in rows if re.search(p,r[sc])] for k,(p,sc) in T.items()}
# cross-site duplicate stories (same press release): similar titles within 3 days on different sites
def dup_groups(arts):
    arts=sorted(arts,key=lambda r:r['date']); g=[]
    for r in arts:
        for grp in g:
            q=grp[0]
            if q['site']!=r['site'] and abs((int(r['date'].replace('-',''))-int(q['date'].replace('-',''))))<=3 and SequenceMatcher(None,q['t'],r['t']).ratio()>=0.75:
                grp.append(r); break
        else: g.append([r])
    return g
out={}; detail=[]; log={}
for dom,s in SITES:
    lst=[]
    for k,arts in hits.items():
        a=[r for r in arts if r['site']==s]
        if k not in M or len(a)<3: continue
        key,var,loai,tg,A,B,risk,prod,cta,reason,status,url,note,scope=M[k]
        c=concl(A,B,risk)
        if c=='Không phù hợp': continue
        allg=dup_groups(arts)
        nsites=len({r['site'] for r in arts})
        mon=collections.Counter(r['date'][5:7] for r in a)
        seq=[mon.get(m,0) for m in ('07','08','09','10')]
        # trend: compare Sep vs Aug (Jul & Oct partial)
        tr='tăng' if seq[2]>seq[1]*1.15 else ('giảm' if seq[2]<seq[1]*0.85 else 'ổn định')
        trend=f"{tr} (T7*:{seq[0]} · T8:{seq[1]} · T9:{seq[2]} · T10*:{seq[3]})"
        a.sort(key=lambda r:r['date'],reverse=True)
        dupn=sum(1 for grp in allg if len(grp)>1 and any(x['site']==s for x in grp))
        lst.append(dict(k=k,c=c,A=A,B=B,n=len(a),row=[dom,key,key.split(' (')[0],var,loai,tg,len(a),f"{nsites}/3",trend,a[0]['date'],"\n".join(r['url'] for r in a[:3]),A,B,risk,c,prod,cta,reason,status,url,note,scope,f"{dupn} tin trùng chéo với báo khác (cùng thông cáo/văn bản)" if dupn else "Không trùng chéo"]))
    lst.sort(key=lambda x:(x['c']!='Phù hợp',-(x['A']+x['B']+min(x['n'],30)/10),-x['n']))
    lst=lst[:15]
    out[dom]="\n".join(f"- {M[x['k']][0]} [{LBL[M[x['k']][10]]}]" for x in lst)
    detail+= [x['row'] for x in lst]
    tot=[r for r in rows if r['site']==s]
    cov=set()
    for k,arts in hits.items():
        if k not in M: continue
        for r in arts:
            if r['site']==s: cov.add(r['url'])
    log[dom]=dict(bai_trong_chuyen_muc_quet=len(tot),bai_quy_duoc_ve_chu_de=len(cov),bai_loai_buoc4=len(tot)-len(cov),so_chu_de_dat=len(lst),phu_hop=sum(x['c']=='Phù hợp' for x in lst),can_nhac=sum(x['c']=='Cân nhắc' for x in lst))
json.dump(dict(C=out,detail=detail,log=log),open('result.json','w'),ensure_ascii=False,indent=1)
for d,v in out.items(): print('##',d,'\n'+v)
print(json.dumps(log,ensure_ascii=False,indent=1))
