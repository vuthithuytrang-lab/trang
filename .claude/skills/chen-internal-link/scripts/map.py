import sys
sys.path.insert(0, sys.argv[1]); from blocks import load, bodypct
for f in sys.argv[2:]:
    s,bl=load(f); pc=bodypct(bl); print('=====',f)
    for i,t in enumerate(bl):
        if i<6: continue
        L=len(t.find_all('a')); img='IMG ' if t.find('img') else ''
        hrefs=','.join(a.get('href','').split('/')[-1][:30] for a in t.find_all('a'))
        print(f"{i:3} {pc[i]:5.1f} {t.name:5} {'L:'+hrefs if L else ''} {img}{t.get_text(' ',strip=True)[:160]}")
