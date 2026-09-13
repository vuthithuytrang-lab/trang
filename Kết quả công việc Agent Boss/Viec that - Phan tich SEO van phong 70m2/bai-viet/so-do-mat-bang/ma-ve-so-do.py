# -*- coding: utf-8 -*-
SC=72; PAD=58
def px(m): return m*SC
def rect(x,y,w,h,fill,stroke='#8A94A6',sw=1.4,dash=''):
    d=' stroke-dasharray="%s"'%dash if dash else ''
    return f'<rect x="{px(x)+PAD}" y="{px(y)+PAD}" width="{px(w)}" height="{px(h)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'
def label(x,y,t,size=13,bold=True,fill='#1F2A44'):
    w='700' if bold else '400'
    return (f'<text x="{px(x)+PAD}" y="{px(y)+PAD}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="middle">{t}</text>')
def desk(x,y,w=1.2,h=0.7):
    return (f'<rect x="{px(x)+PAD}" y="{px(y)+PAD}" width="{px(w)}" height="{px(h)}" '
            f'fill="#FFFFFF" stroke="#5B6478" stroke-width="1.2" rx="2"/>')
def chair(cx,cy,r=0.16):
    return f'<circle cx="{px(cx)+PAD}" cy="{px(cy)+PAD}" r="{px(r)}" fill="#C7CEDB" stroke="#8A94A6" stroke-width="1"/>'
def win(a,b,c,vert=False):
    if vert:
        return (f'<line x1="{px(a)+PAD}" y1="{px(b)+PAD}" x2="{px(a)+PAD}" y2="{px(c)+PAD}" '
                f'stroke="#0D9BE0" stroke-width="5" stroke-linecap="round"/>')
    return (f'<line x1="{px(a)+PAD}" y1="{px(c)+PAD}" x2="{px(b)+PAD}" y2="{px(c)+PAD}" '
            f'stroke="#0D9BE0" stroke-width="5" stroke-linecap="round"/>')
def door(x,y,s=0.85):
    X,Y=px(x)+PAD,px(y)+PAD; S=px(s)
    return (f'<path d="M {X} {Y} a {S} {S} 0 0 1 {S} {S}" fill="none" stroke="#1F2A44" stroke-width="1.6"/>'
            f'<line x1="{X}" y1="{Y}" x2="{X}" y2="{Y+S}" stroke="#1F2A44" stroke-width="3"/>')
def dim(x1,x2,y,t):
    a,b,Y=px(x1)+PAD,px(x2)+PAD,px(y)+PAD
    return (f'<line x1="{a}" y1="{Y}" x2="{b}" y2="{Y}" stroke="#B42318" stroke-width="1.2"/>'
            f'<line x1="{a}" y1="{Y-5}" x2="{a}" y2="{Y+5}" stroke="#B42318" stroke-width="1.2"/>'
            f'<line x1="{b}" y1="{Y-5}" x2="{b}" y2="{Y+5}" stroke="#B42318" stroke-width="1.2"/>'
            f'<text x="{(a+b)/2}" y="{Y-8}" font-family="Arial" font-size="12" font-weight="700" fill="#B42318" text-anchor="middle">{t}</text>')
def head(W,H,title,sub):
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{px(W)+PAD*2}" height="{px(H)+PAD*2+86}">'
       f'<rect width="100%" height="100%" fill="#FFFFFF"/>')
    s+=f'<text x="{PAD}" y="32" font-family="Arial" font-size="17" font-weight="700" fill="#1F2A44">{title}</text>'
    s+=f'<text x="{PAD}" y="{px(H)+PAD+52}" font-family="Arial" font-size="12.5" fill="#5B6478">{sub}</text>'
    s+=rect(0,0,W,H,'#F5F7FA','#1F2A44',2.4)
    return s
def row(x,y,n,gap=0.28):
    o=''
    for i in range(n):
        bx=x+i*(1.2+gap); o+=desk(bx,y)+chair(bx+0.6,y+1.0)
    return o
SUB='Đơn vị đo: mét. Vạch xanh là cửa sổ, cung tròn là cửa ra vào, vạch đỏ là chiều rộng lối đi.'

# ---------- 1. HEP VA DAI: 14m x 5m — 10 cho ----------
W,H=14,5
a=head(W,H,'Sơ đồ 1 — Mặt bằng hẹp và dài (14m × 5m = 70m²) · 10 chỗ ngồi',SUB)
a+=rect(0,0,2.6,5,'#DDE7F5'); a+=label(1.3,2.1,'PHÒNG'); a+=label(1.3,2.5,'GIÁM ĐỐC'); a+=label(1.3,2.95,'13 m²',12,False,'#5B6478')
a+=rect(11.4,0,2.6,5,'#E8EEF7'); a+=label(12.7,2.1,'PHÒNG HỌP'); a+=label(12.7,2.5,'6 chỗ'); a+=label(12.7,2.95,'13 m²',12,False,'#5B6478')
a+=rect(3.0,0,8.0,3.6,'#FFFFFF','#8A94A6',1.4,'6 4'); a+=label(7.0,0.6,'KHU LÀM VIỆC CHUNG — 10 chỗ · 29 m²')
a+=row(3.4,1.0,5,0.3)+row(3.4,2.4,5,0.3)
a+=rect(3.0,3.8,5.6,1.2,'#FFFFFF','#8A94A6',1.4,'6 4'); a+=label(5.8,4.28,'LỐI ĐI CHÍNH DỌC TRỤC DÀI',12); a+=label(5.8,4.62,'dài 8,8 m',12,False,'#5B6478')
a+=rect(8.8,3.8,2.2,1.2,'#EFF3E8'); a+=label(9.9,4.28,'PANTRY',12); a+=label(9.9,4.62,'2,6 m²',12,False,'#5B6478')
a+=dim(3.0,8.6,4.95,'1,2 m')
a+=win(0.15,6.0,0.03)+win(7.5,13.85,0.03)
a+=door(2.65,0.05)+'</svg>'

# ---------- 2. VUONG CAN XUNG: 8.4m x 8.4m — 12 cho ----------
W,H=8.4,8.4
b=head(W,H,'Sơ đồ 2 — Mặt bằng vuông cân xứng (8,4m × 8,4m ≈ 70m²) · 12 chỗ ngồi',SUB)
b+=rect(0,0,4.6,1.8,'#E8EEF7'); b+=label(2.3,0.85,'LỄ TÂN & KHU CHỜ'); b+=label(2.3,1.3,'8,3 m²',12,False,'#5B6478')
b+=rect(6.0,0,2.4,3.2,'#DDE7F5'); b+=label(7.2,1.35,'PHÒNG'); b+=label(7.2,1.75,'GIÁM ĐỐC'); b+=label(7.2,2.2,'7,7 m²',12,False,'#5B6478')
b+=rect(6.0,3.4,2.4,1.6,'#EFF3E8'); b+=label(7.2,4.05,'PANTRY',12); b+=label(7.2,4.45,'3,8 m²',12,False,'#5B6478')
b+=rect(6.0,5.2,2.4,3.2,'#E8EEF7'); b+=label(7.2,6.5,'PHÒNG HỌP'); b+=label(7.2,6.9,'6 chỗ'); b+=label(7.2,7.35,'7,7 m²',12,False,'#5B6478')
b+=rect(4.6,0,1.4,8.4,'#FFFFFF','#8A94A6',1.2,'4 3'); b+=label(5.3,4.0,'LỐI',12); b+=label(5.3,4.4,'ĐI',12); b+=label(5.3,4.8,'1,4 m',12,False,'#5B6478')
b+=rect(0,2.0,4.6,6.4,'#FFFFFF','#8A94A6',1.4,'6 4'); b+=label(2.3,2.55,'KHU LÀM VIỆC CHUNG',12); b+=label(2.3,2.92,'12 chỗ · 29 m²',12,False,'#5B6478')
for yy in (3.2,4.5,5.8,7.1):
    b+=row(0.3,yy,3,0.2)
b+=dim(4.6,6.0,8.2,'1,4 m')
b+=win(0.15,4.4,0.03)+win(0.03,0.15,4.4,vert=True)
b+=door(4.25,0.05)+'</svg>'

# ---------- 3. LO GOC: 10m x 7m — 11 cho ----------
W,H=10,7
c=head(W,H,'Sơ đồ 3 — Mặt bằng lô góc (10m × 7m = 70m²) · 11 chỗ ngồi',SUB)
c+=rect(7.4,0,2.6,3.2,'#DDE7F5','#0D9BE0',2.2); c+=label(8.7,1.2,'PHÒNG GIÁM ĐỐC',12); c+=label(8.7,1.62,'ở góc hai mặt kính',12,False,'#5B6478'); c+=label(8.7,2.1,'8,3 m²',12,False,'#5B6478')
c+=rect(7.4,3.6,2.6,3.4,'#E8EEF7'); c+=label(8.7,4.9,'PHÒNG HỌP'); c+=label(8.7,5.3,'6 chỗ'); c+=label(8.7,5.75,'8,8 m²',12,False,'#5B6478')
c+=rect(0,0,2.2,1.8,'#E8EEF7'); c+=label(1.1,0.85,'LỄ TÂN',12); c+=label(1.1,1.3,'4 m²',12,False,'#5B6478')
c+=rect(3.6,0,2.4,1.8,'#EFF3E8'); c+=label(4.8,0.85,'PANTRY',12); c+=label(4.8,1.3,'4,3 m²',12,False,'#5B6478')
c+=rect(6.0,0,1.4,7.0,'#FFFFFF','#8A94A6',1.2,'4 3'); c+=label(6.7,3.3,'LỐI',12); c+=label(6.7,3.7,'ĐI',12); c+=label(6.7,4.1,'1,4 m',12,False,'#5B6478')
c+=rect(0,2.2,6.0,4.8,'#FFFFFF','#8A94A6',1.4,'6 4'); c+=label(3.0,2.75,'KHU LÀM VIỆC CHUNG — 11 chỗ · 29 m²',12)
c+=row(0.35,3.0,4,0.15)+row(0.35,4.3,4,0.15)+row(0.35,5.6,3,0.15)
c+=dim(6.0,7.4,6.8,'1,4 m')
c+=win(0.15,9.85,0.03)+win(9.97,0.15,6.85,vert=True)
c+=door(2.15,0.05)+'</svg>'

for n,s in [('so-do-70-hep-dai',a),('so-do-70-vuong',b),('so-do-70-lo-goc',c)]:
    open(n+'.html','w',encoding='utf-8').write('<body style="margin:0">'+s+'</body>')
print('xong 3 so do 70m2')
