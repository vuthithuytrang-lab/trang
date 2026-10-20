# -*- coding: utf-8 -*-
"""Hàm dùng chung: đọc config, chuẩn hoá URL, crawl và đo một trang."""
import json, os, re, unicodedata, warnings
warnings.filterwarnings('ignore')

SOCIAL = {'youtube.com', 'facebook.com', 'pinterest.com', 'google.com', 'tiktok.com',
          'instagram.com', 'vn.pinterest.com', 'kr.pinterest.com', 'm.youtube.com',
          'linkedin.com', 'vn.linkedin.com', 'x.com', 'twitter.com', 'shopee.vn',
          'lazada.vn', 'jobsgo.vn', 'vietnamworks.com', 'topcv.vn', 'vieclam24h.vn'}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")

DROP_TAGS = ["nav", "header", "footer", "aside", "script", "style", "noscript", "form"]
DROP_CLASS = {"menu", "nav", "navbar", "navigation", "footer", "sidebar", "breadcrumb",
              "breadcrumbs", "related", "comment", "comments", "widget", "banner",
              "popup", "modal", "cookie", "topbar", "megamenu"}


def load_config(path='config.json'):
    with open(os.path.expanduser(path)) as f:
        c = json.load(f)
    for k in ('csv', 'out_dir'):
        if c.get(k): c[k] = os.path.expanduser(c[k])
    c.setdefault('project', project_slug(c['domain'], c.get('prefix')))
    c.setdefault('prefix', re.split(r'[-.]', c['domain'])[0][:6])
    c.setdefault('cluster', {})
    c['cluster'].setdefault('min_shared', 4)
    c['cluster'].setdefault('merge_small', 3)
    c['cluster'].setdefault('merge_cluster', 0.7)
    c['cluster'].setdefault('depth', 10)
    c.setdefault('gsc_days', 90)
    c['out_dir'] = project_dir(c.get('out_dir'), c['domain'], c['project'])
    return c


HTML_ROOT = os.path.expanduser('~/html')


def project_slug(domain, override=None):
    """Tên thư mục dự án. khachhang-a.vn -> khachhang, example.com -> example."""
    if override:
        return slugify(override)
    d = re.sub(r'^https?://', '', str(domain or '')).split('/')[0].lower()
    d = re.sub(r'^www\.', '', d)
    return slugify(re.split(r'[-.]', d)[0]) if d else 'khac'


def project_dir(out_dir, domain, project=None):
    """Thư mục xuất riêng cho từng dự án: ~/html/<dự án>/.

    Truyền out_dir trỏ tới chỗ khác ~/html thì tôn trọng nguyên, không nối thêm.
    """
    d = os.path.expanduser(out_dir) if out_dir else HTML_ROOT
    d = d.rstrip('/') or '/'
    if d == HTML_ROOT:
        d = os.path.join(d, project_slug(domain, project))
    os.makedirs(d, exist_ok=True)
    return d


def dom(u):
    return re.sub(r'^https?://(www\.)?', '', u).split('/')[0].lower()


def clean(u):
    return u.split('?')[0].split('#')[0]


def nrm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s or '')).strip().lower()


def words_of(node):
    return len(re.findall(r'\w+', node.text_content(), flags=re.UNICODE))


def main_content(doc):
    """Nội dung chính. Hai lớp bảo vệ chống cắt nhầm cây con chứa bài viết."""
    import copy
    d = copy.deepcopy(doc)
    for tag in DROP_TAGS:
        for n in d.xpath('//' + tag):
            if n.getparent() is not None:
                n.getparent().remove(n)
    skeleton = copy.deepcopy(d)
    base = words_of(d)
    for n in d.xpath('//*[@class]'):
        cls = set(re.split(r'[\s_-]+', (n.get('class') or '').lower()))
        if cls & DROP_CLASS and n.getparent() is not None:
            n.getparent().remove(n)
    if words_of(d) < 0.3 * base:
        return skeleton, base
    return d, words_of(d)


def measure(url, timeout=30):
    """Đo 21 chỉ số nội dung của một trang. Trả dict, có khoá error nếu hỏng."""
    import requests, time
    from lxml import html as LH
    try:
        t0 = time.time()
        r = requests.get(url, headers={'User-Agent': UA, 'Accept-Language': 'vi,en;q=0.8'},
                         timeout=timeout, verify=False)
        ttfb = round((time.time() - t0) * 1000)
        raw = r.text
    except Exception as e:
        return dict(url=url, error=str(e)[:120])
    doc = LH.fromstring(raw)
    mc, w = main_content(doc)
    allimgs = doc.xpath('//img')
    lazy = sum(1 for i in allimgs if i.get('loading') == 'lazy' or i.get('data-src')
               or i.get('data-lazy-src') or 'lazy' in (i.get('class') or '').lower())
    srcset = sum(1 for i in allimgs if i.get('srcset') or i.get('data-srcset'))
    webp = sum(1 for i in allimgs
               if '.webp' in ((i.get('src') or '') + (i.get('data-src') or '') + (i.get('srcset') or '')).lower())
    h1 = [x.text_content().strip() for x in doc.xpath('//h1')]
    hd = [t.strip() for t in doc.xpath('//h2//text()|//h3//text()') if t.strip()]
    schemas, faq_schema, datemod = set(), False, ''
    for s in doc.xpath("//script[@type='application/ld+json']/text()"):
        for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', s):
            schemas.add(m.group(1))
        if 'FAQPage' in s: faq_schema = True
        m = re.search(r'"dateModified"\s*:\s*"([^"]+)"', s)
        if m and not datemod: datemod = m.group(1)
    txt = mc.text_content()
    host = dom(url)
    seq = [int(e.tag[1]) for e in doc.iter()
           if isinstance(e.tag, str) and re.fullmatch(r'h[1-6]', e.tag)]
    return dict(
        url=url, code=r.status_code, ttfb=ttfb, words=w,
        kb=round(len(raw.encode()) / 1024), imgs=len(mc.xpath('//img')), imgs_all=len(allimgs),
        lazy=lazy, srcset=srcset, webp=webp, noalt=sum(1 for i in allimgs if not (i.get('alt') or '').strip()),
        h2=len(mc.xpath('//h2')), h3=len(mc.xpath('//h3')), h1n=len(h1), h1=(h1[0][:120] if h1 else ''),
        title=(doc.xpath('//title/text()') or [''])[0].strip(),
        desc=(doc.xpath("//meta[@name='description']/@content") or [''])[0].strip(),
        canonical=(doc.xpath("//link[@rel='canonical']/@href") or [''])[0],
        robots=(doc.xpath("//meta[@name='robots']/@content") or [''])[0],
        og=len(doc.xpath("//meta[starts-with(@property,'og:')]")),
        scripts=len(doc.xpath('//script[@src]')), inline=len(doc.xpath('//script[not(@src)]')),
        css=len(doc.xpath("//link[@rel='stylesheet']")),
        jumps=sum(1 for a, b in zip(seq, seq[1:]) if b - a > 1),
        headings=hd[:150], schemas=sorted(schemas), faq_schema=faq_schema,
        faq_render=bool(re.search(r'(câu hỏi thường gặp|faq|hỏi đáp)', txt, re.I)),
        datemod=datemod,
        ilinks=sum(1 for a in mc.xpath('//a/@href') if host in a or a.startswith('/')),
        tel=len(doc.xpath("//a[starts-with(@href,'tel:')]")),
        forms=len(doc.xpath('//form')),
        text=nrm(re.sub(r'\s+', ' ', txt))[:400000])


def crawl_many(urls, workers=10):
    import concurrent.futures as cf
    out = []
    with cf.ThreadPoolExecutor(workers) as ex:
        for r in ex.map(measure, urls):
            out.append(r)
    return out


def is_js_rendered(p):
    return p.get('words', 0) < 300 and p.get('kb', 0) > 80


# Ba mức chuyển đổi tham chiếu theo tầng vị trí nguồn: (tầng, thận trọng, cơ sở, triệt để).
# Dùng chung cho analyze.py (in ra terminal) và overview.py (dựng file tổng hợp) — một nguồn
# duy nhất, sửa ở đây là đổi cả hai. Chi tiết và xuất xứ số ở references/metrics.md mục 5.
REF_RATES = {
    'top10': [('11-20', .75, .85, .92), ('21-50', .45, .55, .68), ('>50', .25, .35, .45)],
    'top5': [('6-10', .45, .60, .72), ('11-20', .18, .28, .38), ('21-50', .05, .09, .14)],
    'top3': [('4-5', .45, .60, .72), ('6-10', .20, .30, .40), ('11-20', .06, .11, .16)],
}

TIERS = {'4-5': (4, 5), '6-10': (6, 10), '11-20': (11, 20), '21-50': (21, 50), '>50': (51, 10 ** 6)}


def tier_pool(KW, tier, exclude=()):
    """Số từ khoá đang nằm ở một tầng vị trí. Không có thứ hạng thì tính vào tầng >50."""
    lo, hi = TIERS[tier]
    out = []
    for r in KW:
        if r['kw'] in exclude:
            continue
        p = r.get('pos')
        if p is None:
            if tier == '>50':
                out.append(r)
        elif lo <= p <= hi:
            out.append(r)
    return out


SLUG_STOP = {'va', 'theo', 'cua', 'tai', 'la', 'cho', 'voi', 'cac', 'nhanh'}


def slugify(s, maxwords=5):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('đ', 'd')
    s = re.sub(r'[^a-z0-9\s-]', ' ', s)
    w = [x for x in s.split() if x not in SLUG_STOP]
    return '-'.join(w[:maxwords]) or 'nhom'

