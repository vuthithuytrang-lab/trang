import re, sys, json, html as H
def clean(s):
    s=re.sub(r'<[^>]+>','',s); return re.sub(r'\s+',' ',H.unescape(s)).strip()
def extract(path, url):
    h=open(path,encoding='utf-8').read()
    m=re.search(r'<h1[^>]*>(.*?)</h1>',h,re.S); title=clean(m.group(1)) if m else ''
    # body: from h1 to related posts
    start=m.end() if m else 0
    end=h.find('article-related-post_title')
    body=h[start:end if end>0 else len(h)]
    toks=re.finditer(r'<(h2|h3|p|li|img)\b([^>]*)>(.*?)(?=<(?:h2|h3|p|li|img|/ul|/ol|div|table)\b|$)',body,re.S)
    out={'url':url,'title':title,'sapo':'','sections':[],'images':[]}
    cur=None; pre=[]
    for t in toks:
        tag,attrs,inner=t.group(1),t.group(2),t.group(3)
        if tag=='img':
            src=re.search(r'src="([^"]+)"',attrs); alt=re.search(r'alt="([^"]*)"',attrs)
            if src and ('/articles/' in src.group(1) or re.search(r'\.(jpe?g|png|webp)$',src.group(1),re.I) and not re.search(r'imported-assets|com_img|common/|/seo/|logo|rendition|/etc\.clientlibs',src.group(1))):
                u=re.sub(r'/_jcr_content.*$','',src.group(1)); out['images'].append({'src':'https://techcombank.com'+u if u.startswith('/') else u,'_':'https://techcombank.com'+src.group(1) if src.group(1).startswith('/') else src.group(1),'alt':H.unescape(alt.group(1)) if alt else '','after_h2':cur['h2'] if cur else None})
            continue
        txt=clean(inner)
        if not txt: continue
        if tag=='h2':
            cur={'h2':txt,'content':[]}; out['sections'].append(cur)
        elif cur is None: pre.append(txt)
        else: cur['content'].append(('### ' if tag=='h3' else '- ' if tag=='li' else '')+txt)
    out['intro']=pre
    return out
if __name__=='__main__':
    print(json.dumps(extract(sys.argv[1],sys.argv[2]),ensure_ascii=False,indent=1))
