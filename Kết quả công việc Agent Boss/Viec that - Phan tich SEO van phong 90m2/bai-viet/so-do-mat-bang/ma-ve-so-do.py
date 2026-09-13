# -*- coding: utf-8 -*-
SC=66; PAD=58
KHACH='#0B6BCB'; NV='#0D8A5F'
def px(m): return m*SC
def rect(x,y,w,h,fill,stroke='#8A94A6',sw=1.4,dash=''):
    d=' stroke-dasharray="%s"'%dash if dash else ''
    return f'<rect x="{px(x)+PAD}" y="{px(y)+PAD}" width="{px(w)}" height="{px(h)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
def label(x,y,t,size=12.5,bold=True,fill='#1F2A44'):
    return (f'<text x="{px(x)+PAD}" y="{px(y)+PAD}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{size}" font-weight="{"700" if bold else "400"}" fill="{fill}" text-anchor="middle">{t}</text>')
def desk(x,y,w=1.2,h=0.7):
    return (f'<rect x="{px(x)+PAD}" y="{px(y)+PAD}" width="{px(w)}" height="{px(h)}" '
            f'fill="#FFFFFF" stroke="#5B6478" stroke-width="1.1" rx="2"/>')
def chair(cx,cy,r=0.15):
    return f'<circle cx="{px(cx)+PAD}" cy="{px(cy)+PAD}" r="{px(r)}" fill="#C7CEDB" stroke="#8A94A6" stroke-width="1"/>'
def row(x,y,n,gap=0.2):
    o=''
    for i in range(n):
        bx=x+i*(1.2+gap); o+=desk(bx,y)+chair(bx+0.6,y+0.95)
    return o
def win(a,b,c,vert=False):
    if vert: return (f'<line x1="{px(a)+PAD}" y1="{px(b)+PAD}" x2="{px(a)+PAD}" y2="{px(c)+PAD}" stroke="#0D9BE0" stroke-width="5" stroke-linecap="round"/>')
    return (f'<line x1="{px(a)+PAD}" y1="{px(c)+PAD}" x2="{px(b)+PAD}" y2="{px(c)+PAD}" stroke="#0D9BE0" stroke-width="5" stroke-linecap="round"/>')
def door(x,y,s=0.85,flip=False):
    X,Y=px(x)+PAD,px(y)+PAD; S=px(s)
    sweep=0 if flip else 1
    return (f'<path d="M {X} {Y} a {S} {S} 0 0 {sweep} {S} {S}" fill="none" stroke="#1F2A44" stroke-width="1.6"/>'
            f'<line x1="{X}" y1="{Y}" x2="{X}" y2="{Y+S}" stroke="#1F2A44" stroke-width="3"/>')
def dim(x1,x2,y,t):
    a,b,Y=px(x1)+PAD,px(x2)+PAD,px(y)+PAD
    return (f'<line x1="{a}" y1="{Y}" x2="{b}" y2="{Y}" stroke="#B42318" stroke-width="1.2"/>'
            f'<line x1="{a}" y1="{Y-5}" x2="{a}" y2="{Y+5}" stroke="#B42318" stroke-width="1.2"/>'
            f'<line x1="{b}" y1="{Y-5}" x2="{b}" y2="{Y+5}" stroke="#B42318" stroke-width="1.2"/>'
            f'<text x="{(a+b)/2}" y="{Y-7}" font-family="Arial" font-size="11.5" font-weight="700" fill="#B42318" text-anchor="middle">{t}</text>')
def flow(pts,color):
    d='M '+' L '.join('%.1f %.1f'%(px(x)+PAD,px(y)+PAD) for x,y in pts)
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.4" stroke-dasharray="9 6" '
            f'stroke-linecap="round" stroke-linejoin="round" marker-end="url(#ar{color[1:]})"/>')
def flabel(x,y,t,color,anchor='middle'):
    return (f'<text x="{px(x)+PAD}" y="{px(y)+PAD}" font-family="Arial" font-size="11.5" '
            f'font-weight="700" fill="{color}" text-anchor="{anchor}">{t}</text>')
def defs():
    o='<defs>'
    for c in (KHACH,NV):
        o+=(f'<marker id="ar{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5" '
            f'markerHeight="5.5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>')
    return o+'</defs>'
def head(W,H,title,sub):
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{px(W)+PAD*2}" height="{px(H)+PAD*2+104}">'
       f'<rect width="100%" height="100%" fill="#FFFFFF"/>'+defs())
    s+=f'<text x="{PAD}" y="32" font-family="Arial" font-size="17" font-weight="700" fill="#1F2A44">{title}</text>'
    y0=px(H)+PAD+34
    s+=(f'<line x1="{PAD}" y1="{y0}" x2="{PAD+26}" y2="{y0}" stroke="{KHACH}" stroke-width="3.4" stroke-dasharray="9 6"/>'
        f'<text x="{PAD+34}" y="{y0+4}" font-family="Arial" font-size="12.5" font-weight="700" fill="{KHACH}">Luồng khách</text>'
        f'<line x1="{PAD+150}" y1="{y0}" x2="{PAD+176}" y2="{y0}" stroke="{NV}" stroke-width="3.4" stroke-dasharray="9 6"/>'
        f'<text x="{PAD+184}" y="{y0+4}" font-family="Arial" font-size="12.5" font-weight="700" fill="{NV}">Luồng nhân viên</text>')
    s+=f'<text x="{PAD}" y="{y0+30}" font-family="Arial" font-size="12" fill="#5B6478">{sub}</text>'
    s+=rect(0,0,W,H,'#F5F7FA','#1F2A44',2.4)
    return s
SUB='Đơn vị đo: mét. Vạch xanh nhạt là cửa sổ, cung tròn là cửa ra vào, vạch đỏ là chiều rộng lối đi.'

# ---------- 1. HEP DAI 18 x 5 = 90m2 — 15 cho ----------
W,H=18,5
a=head(W,H,'Sơ đồ 1 — Mặt bằng hẹp và dài (18m × 5m = 90m²) · 15 chỗ ngồi',SUB)
a+=rect(0,0,2.2,5,'#E8EEF7'); a+=label(1.1,2.2,'LỄ TÂN'); a+=label(1.1,2.6,'& KHU CHỜ'); a+=label(1.1,3.05,'11 m²',11.5,False,'#5B6478')
a+=rect(12.6,0,2.8,5,'#E8EEF7'); a+=label(14.0,2.2,'PHÒNG HỌP'); a+=label(14.0,2.6,'8 chỗ'); a+=label(14.0,3.05,'14 m²',11.5,False,'#5B6478')
a+=rect(15.4,0,2.6,3.2,'#DDE7F5'); a+=label(16.7,1.4,'PHÒNG'); a+=label(16.7,1.8,'GIÁM ĐỐC'); a+=label(16.7,2.25,'8,3 m²',11.5,False,'#5B6478')
a+=rect(15.4,3.4,2.6,1.6,'#EFF3E8'); a+=label(16.7,4.1,'PANTRY',12); a+=label(16.7,4.5,'4,2 m²',11.5,False,'#5B6478')
a+=rect(2.4,0,10.0,3.7,'#FFFFFF','#8A94A6',1.4,'6 4'); a+=label(7.4,0.82,'KHU LÀM VIỆC CHUNG — 14 chỗ · 36 m²')
a+=row(2.6,1.1,7)+row(2.6,2.4,7)
a+=rect(2.4,3.8,10.0,1.2,'#FFFFFF','#8A94A6',1.4,'6 4'); a+=label(7.4,4.18,'LỐI ĐI CHÍNH DỌC TRỤC DÀI',12); a+=label(7.4,4.52,'dài 10 m',11.5,False,'#5B6478')
a+=dim(2.4,12.4,4.95,'1,2 m')
a+=flow([(2.3,0.42),(6.0,0.42),(10.0,0.42),(13.6,0.42)],KHACH)
a+=flow([(2.3,4.45),(6.0,4.45),(11.6,4.45)],NV)
a+=win(0.15,12.3,0.03)+win(12.9,17.85,0.03)
a+=door(2.05,0.05)+'</svg>'

# ---------- 2. VUONG 9.5 x 9.5 = 90m2 — 17 cho ----------
W,H=9.5,9.5
b=head(W,H,'Sơ đồ 2 — Mặt bằng vuông cân xứng (9,5m × 9,5m ≈ 90m²) · 17 chỗ ngồi',SUB)
b+=rect(0,0,5.4,2.0,'#E8EEF7'); b+=label(3.5,1.35,'LỄ TÂN & KHU CHỜ'); b+=label(3.5,1.78,'10,8 m²',11.5,False,'#5B6478')
b+=rect(6.7,0,2.8,3.2,'#DDE7F5'); b+=label(8.1,1.3,'PHÒNG'); b+=label(8.1,1.7,'GIÁM ĐỐC'); b+=label(8.1,2.15,'9 m²',11.5,False,'#5B6478')
b+=rect(6.7,3.4,2.8,1.8,'#EFF3E8'); b+=label(8.1,4.15,'PANTRY',12); b+=label(8.1,4.6,'5 m²',11.5,False,'#5B6478')
b+=rect(6.7,5.4,2.8,4.1,'#E8EEF7'); b+=label(8.1,7.1,'PHÒNG HỌP'); b+=label(8.1,7.5,'8 chỗ'); b+=label(8.1,7.95,'12 m²',11.5,False,'#5B6478')
b+=rect(5.4,0,1.3,9.5,'#FFFFFF','#8A94A6',1.2,'4 3'); b+=label(6.05,6.5,'LỐI',12); b+=label(6.05,6.9,'ĐI',12); b+=label(6.05,7.3,'1,3 m',11.5,False,'#5B6478')
b+=rect(0,2.2,5.4,7.3,'#FFFFFF','#8A94A6',1.4,'6 4'); b+=label(2.7,2.68,'KHU LÀM VIỆC CHUNG',12); b+=label(2.7,3.05,'16 chỗ · 39 m²',11.5,False,'#5B6478')
for yy in (3.4,4.8,6.2,7.6):
    b+=row(0.08,yy,4,0.15)
b+=dim(5.4,6.7,9.25,'1,3 m')
b+=flow([(5.25,0.6),(3.6,0.6),(1.5,0.6),(1.5,1.5)],KHACH)
b+=flow([(5.25,1.75),(6.05,1.75),(6.05,3.4),(6.05,5.6)],NV)
b+=win(0.15,5.2,0.03)+win(0.03,0.15,5.2,vert=True)
b+=door(5.05,0.05,0.85,flip=True)+'</svg>'

# ---------- 3. LO GOC 12 x 7.5 = 90m2 — 16 cho ----------
W,H=12,7.5
c=head(W,H,'Sơ đồ 3 — Mặt bằng lô góc (12m × 7,5m = 90m²) · 16 chỗ ngồi',SUB)
c+=rect(9.2,0,2.8,2.9,'#DDE7F5','#0D9BE0',2.2); c+=label(10.6,1.1,'PHÒNG GIÁM ĐỐC',12); c+=label(10.6,1.52,'ở góc hai mặt kính',11.5,False,'#5B6478'); c+=label(10.6,1.98,'8,1 m²',11.5,False,'#5B6478')
c+=rect(9.2,3.1,2.8,2.9,'#E8EEF7'); c+=label(10.6,4.25,'PHÒNG HỌP'); c+=label(10.6,4.65,'6 chỗ'); c+=label(10.6,5.1,'8,1 m²',11.5,False,'#5B6478')
c+=rect(9.2,6.2,2.8,1.3,'#EFF3E8'); c+=label(10.6,6.75,'PANTRY',12); c+=label(10.6,7.15,'3,6 m²',11.5,False,'#5B6478')
c+=rect(0,0,3.0,2.2,'#E8EEF7'); c+=label(1.5,0.95,'LỄ TÂN',12); c+=label(1.5,1.45,'6,6 m²',11.5,False,'#5B6478')
c+=rect(3.2,0,4.6,2.2,'#E8EEF7'); c+=label(5.5,0.6,'KHU TIẾP KHÁCH',12); c+=label(5.5,1.95,'10,1 m²',11.5,False,'#5B6478')
c+=rect(7.8,0,1.4,7.5,'#FFFFFF','#8A94A6',1.2,'4 3'); c+=label(8.5,5.4,'LỐI',12); c+=label(8.5,5.8,'ĐI',12); c+=label(8.5,6.2,'1,4 m',11.5,False,'#5B6478')
c+=rect(0,2.4,7.8,5.1,'#FFFFFF','#8A94A6',1.4,'6 4'); c+=label(5.4,2.9,'KHU LÀM VIỆC CHUNG — 15 chỗ · 40 m²',12)
c+=row(0.5,3.3,5)+row(0.5,4.6,5)+row(0.5,5.9,5)
c+=dim(7.8,9.2,7.25,'1,4 m')
c+=flow([(3.15,1.25),(6.0,1.25),(8.5,1.25),(8.5,3.9)],KHACH)
c+=flow([(3.15,1.85),(3.9,1.85),(3.9,2.6)],NV)
c+=win(0.15,11.85,0.03)+win(11.97,0.15,7.35,vert=True)
c+=door(2.95,0.05)+'</svg>'

for n,s in [('so-do-90-hep-dai',a),('so-do-90-vuong',b),('so-do-90-lo-goc',c)]:
    open(n+'.html','w',encoding='utf-8').write('<body style="margin:0">'+s+'</body>')
print('xong 3 so do 90m2')
