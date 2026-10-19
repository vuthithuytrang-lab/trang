# Tự soát Bước 2: vị trí %, heading, đoạn kề có link, link trùng URL đích
import sys, json
sys.path.insert(0, sys.argv[1]); from blocks import load, bodypct
SP = sys.argv[1]
TG = {'r2': [('1 Tệ bằng bao nhiêu tiền Việt','1-te-bang-bao-nhieu-tien-viet-nam'),('tiền Nhật','/tien-nhat'),('1 Yên bằng bao nhiêu tiền Việt','1-yen-bang-bao-nhieu-tien-viet-nam'),('1 Won bằng bao nhiêu tiền Việt','1-won-bang-bao-nhieu-tien-viet'),('nhận tiền từ nước ngoài','cach-nhan-tien-tu-nuoc-ngoai-ve-viet-nam')],
      'r3': [('1 đô bằng bao nhiêu tiền Việt','1-dong-do-la-my-bang-bao-nhieu-tien-viet-nam'),('tiền Nhật','/tien-nhat'),('1 Yên bằng bao nhiêu tiền Việt','1-yen-bang-bao-nhieu-tien-viet-nam'),('1 Won bằng bao nhiêu tiền Việt','1-won-bang-bao-nhieu-tien-viet')],
      'r4': [('1 Tệ bằng bao nhiêu tiền Việt','1-te-bang-bao-nhieu-tien-viet-nam'),('tỷ giá Won','1-won-bang-bao-nhieu-tien-viet'),('1 Man bằng bao nhiêu tiền Việt','1-man-bang-bao-nhieu-tien-viet'),('1 triệu đô bằng bao nhiêu tiền Việt','1-trieu-do-bang-bao-nhieu-tien-viet'),('1000 Won bằng bao nhiêu tiền Việt','1000-won-bang-bao-nhieu-tien-viet')]}
for r in ['r2','r3','r4']:
    print('=====', r)
    s, bl = load(f'{SP}out/{r}.html')
    for a, slug in TG[r]:
        old = [x['href'] for x in s.find_all('a', href=True) if x['href'].rstrip('/').endswith(slug)]
        print('  bài gốc đã có link tới', slug, ':', bool(old))
    s, bl = load(f'{SP}final/{r}.html')
    body = [b for b in bl[6:] if not (b.name=='p' and b.find('span', style='color:#ff0000'))]
    tot = sum(len(b.get_text()) for b in body); acc = 0
    for k, b in enumerate(body):
        new = b.find('span', style='background-color:#ffff00') and b.find('a')
        if new:
            def L(j):
                return j>=0 and j<len(body) and body[j].name not in ('h2','h3','h4') and bool(body[j].find('a'))
            def prevb(j, d):
                j += d
                while 0 <= j < len(body) and body[j].name in ('h2','h3','h4'): j += d
                return j
            pk, nk = prevb(k,-1), prevb(k,1)
            heads = 'heading' if b.name in ('h2','h3','h4') else ''
            print(f"  {acc*100/tot:5.1f}% {b.name} {heads} link-đoạn-trước:{L(pk)} link-đoạn-sau:{L(nk)} kề-trực-tiếp-trước:{L(k-1)} sau:{L(k+1)} | {b.get_text(' ',strip=True)[:70]}")
        acc += len(b.get_text())
