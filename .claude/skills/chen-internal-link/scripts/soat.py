# Tự soát Bước 2: vị trí %, heading, đoạn kề có link, link trùng URL đích
import sys, json
sys.path.insert(0, sys.argv[1]); from blocks import load, bodypct
SP = sys.argv[1]
TG = json.load(open(f'{SP}targets.json', encoding='utf-8'))  # {id: [[anchor, slug], ...]}
for r in TG:
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
