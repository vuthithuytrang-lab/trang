#!/usr/bin/env python3
"""So trang mình với từng đối thủ ở từng từ khoá. Sinh perkw.json cho các khối báo cáo."""
import argparse, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from lib import clean, is_js_rendered

ap = argparse.ArgumentParser()
ap.add_argument('--data', default='data')
ap.add_argument('--depth', type=int, default=10)
a = ap.parse_args()
ME = json.load(open(f'{a.data}/meta.json'))['domain']
KW = json.load(open(f'{a.data}/kw.json'))
P = {clean(p['url']): p for p in json.load(open(f'{a.data}/pages.json'))}
JS = {u for u, p in P.items() if is_js_rendered(p)}

def dens(page, term):
    return len(re.findall(re.escape(unicodedata.normalize('NFC', term).lower()), page['text']))

out = []
for r in KW:
    mine = P.get(clean(r['url'])) if r['url'] else None
    riv = []
    for p, d, u in r['serp']:
        if p > a.depth or d == ME: continue
        pg = P.get(u)
        if not pg or u in JS: continue
        riv.append(dict(pos=p, dom=d, url=pg['url'], words=pg['words'], imgs=pg['imgs_all'],
                        dens=dens(pg, r['kw']), kb=pg['kb'], h2=pg['h2'], h3=pg['h3'],
                        ilinks=pg['ilinks'], faq=pg['faq_schema'], title=pg['title']))
    out.append(dict(kw=r['kw'], pos=r['pos'], url=r['url'], nurl=r['nurl'],
                    my=(dict(words=mine['words'], imgs=mine['imgs_all'], dens=dens(mine, r['kw']),
                             kb=mine['kb'], h2=mine['h2'], h3=mine['h3'], ilinks=mine['ilinks'],
                             faq=mine['faq_schema'], title=mine['title']) if mine else None),
                    riv=riv))
json.dump(out, open(f'{a.data}/perkw.json', 'w'), ensure_ascii=False)
have = [r for r in out if r['my'] and r['riv']]
w = lambda k: sum(1 for r in have if r['my'][k] >= max(x[k] for x in r['riv']))
print(f"{len(have)}/{len(out)} từ khoá so sánh được (có trang mình và có đối thủ đo được)")
print(f"  mật độ cụm khoá >= mọi đối thủ: {w('dens')} = {w('dens')*100//max(len(have),1)}%")
print(f"  dài hơn mọi đối thủ           : {w('words')} = {w('words')*100//max(len(have),1)}%")
print(f"  nhiều ảnh hơn mọi đối thủ     : {w('imgs')} = {w('imgs')*100//max(len(have),1)}%")
