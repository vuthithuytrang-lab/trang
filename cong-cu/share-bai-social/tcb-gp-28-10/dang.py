#!/usr/bin/env python3
"""Công cụ đợt share bài GP Techcombank (28/10/2026) — WordPress, Wix, Mastodon.

Chìa KHÔNG nằm trong repo: đọc từ thư mục KEYS (mặc định scratchpad của phiên),
bản dự phòng ở Google Drive "chia-share-social-TCB-RIENG-TU.json".
Không in chìa ra màn hình.

Lệnh:
  fetch <so>                 tải bài GP về nguon/<so>.txt
  check <so> <wp|wix|ma>     tự soát bài viết
  anh <so> <wp|wix>          dựng ảnh đại diện 1200x630
  dang <so> <wp|wix|ma>      đăng ngay (ghi vào da-dang.jsonl)
  lich                       in các mục đến hạn / mục kế tiếp
"""
import html, json, os, re, ssl, sys, time, uuid, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = os.environ.get("KEYS", "/tmp/claude-0/-home-user-trang/0c0bf5bb-3813-5d56-99a9-455f2d789fc5/scratchpad/ext/share-bai-social-agent/.claude/skills")
VN = timezone(timedelta(hours=7))
WP_SITE = "nganhangtechcombank3.wordpress.com"
WIX_KEY = "tuanytyma.wixsite.com/techcombank-blogs"
MA_KEY = "techcombankvietnam@mastodon.social"
BANNED = ["nhất", "số 1", "số một", "hàng đầu", "duy nhất"]
OK_NHAT = ["chậm nhất", "sớm nhất", "thứ nhất", "mới nhất", "ít nhất", "gần nhất", "nhất định", "thống nhất", "cập nhật", "duy nhất một", "đồng nhất"]

_ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()


def keys(name):
    f = {"wp": "share-bai-wp/wp-accounts.local.json", "wix": "share-bai-wix/wix-accounts.local.json",
         "ma": "share-bai-mastodon/mastodon-accounts.local.json"}[name]
    d = json.load(open(os.path.join(KEYS, f)))
    return d[{"wp": WP_SITE, "wix": WIX_KEY, "ma": MA_KEY}[name]]


def req(method, url, headers=None, body=None, timeout=60):
    if isinstance(body, (dict, list)):
        body = json.dumps(body).encode()
        headers = {**(headers or {}), "Content-Type": "application/json"}
    r = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, context=_ctx, timeout=timeout) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw[:1] in (b"{", b"[") else raw)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw[:500]


def multipart(fields, files):
    b = "----tcb" + uuid.uuid4().hex
    out = b""
    for k, v in fields.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (fn, data, mime) in files.items():
        out += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{fn}"\r\nContent-Type: {mime}\r\n\r\n'.encode() + data + b"\r\n"
    return out + f"--{b}--\r\n".encode(), "multipart/form-data; boundary=" + b


def p(*a):
    print(*a, flush=True)


# ---------- dữ liệu bài ----------
def ds():
    return json.load(open(os.path.join(HERE, "danh-sach.json")))


def item(so):
    for x in ds():
        if x["so"] == int(so):
            return x
    sys.exit(f"không có bài số {so}")


def bai_path(so, nen):
    return os.path.join(HERE, "bai", f"{int(so):02d}", {"wp": "wp.html", "wix": "wix.html", "ma": "ma.txt"}[nen])


def meta(so):
    f = os.path.join(HERE, "bai", f"{int(so):02d}", "meta.json")
    return json.load(open(f)) if os.path.exists(f) else {}


# ---------- tải bài nguồn ----------
class Text(HTMLParser):
    def __init__(s):
        super().__init__(); s.out = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in ("script", "style", "noscript", "nav", "footer", "header", "aside"): s.skip += 1
        if t in ("p", "h1", "h2", "h3", "h4", "li", "br", "tr", "div"): s.out.append("\n")
        if t in ("h1", "h2", "h3", "h4"): s.out.append("#" * int(t[1]) + " ")
    def handle_endtag(s, t):
        if t in ("script", "style", "noscript", "nav", "footer", "header", "aside") and s.skip: s.skip -= 1
    def handle_data(s, d):
        if not s.skip: s.out.append(d)


def cmd_fetch(so):
    x = item(so)
    r = urllib.request.Request(x["url"], headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"})
    raw = urllib.request.urlopen(r, context=_ctx, timeout=60).read().decode("utf8", "replace")
    m = re.search(r"<article.*?</article>", raw, re.S) or re.search(r'class="[^"]*(entry-content|post-content|detail-content|content-detail|news-content|article-content)[^"]*".*', raw, re.S)
    t = Text(); t.feed(m.group(0) if m else raw)
    txt = re.sub(r"\n\s*\n+", "\n\n", "".join(t.out)).strip()
    title = html.unescape((re.search(r"<title>(.*?)</title>", raw, re.S) or [None, ""])[1]).strip()
    links = sorted(set(re.findall(r'href="(https?://[^"]*techcombank[^"]*)"', raw)))
    os.makedirs(os.path.join(HERE, "nguon"), exist_ok=True)
    open(os.path.join(HERE, "nguon", f"{int(so):02d}.txt"), "w").write(f"URL: {x['url']}\nTITLE: {title}\nTCB_LINKS: {links}\n\n{txt}\n")
    p("ok", len(txt.split()), "từ |", title)


# ---------- soát bài ----------
def plain(h):
    return html.unescape(re.sub(r"<[^>]+>", " ", h))


def cmd_check(so, nen, quiet=False):
    x = item(so); f = bai_path(so, nen); s = open(f).read(); errs = []
    if nen == "ma":
        n = len(re.sub(r"https?://\S+", "x" * 23, s))
        if n > 500: errs.append(f"dài {n} ký tự (>500)")
        if s.count("http") != 1 or x["url"] not in s: errs.append("phải có đúng 1 link về bài GP")
    else:
        w = len(plain(s).split())
        if not 900 <= w <= 1100: errs.append(f"{w} từ (cần 900–1100)")
        links = re.findall(r'<a [^>]*href="([^"]+)"', s)
        if links != [x["url"]]: errs.append(f"link sai: {links}")
        bad = set(re.findall(r"</?([a-z0-9]+)", s)) - {"p", "h2", "h3", "ul", "ol", "li", "strong", "a"}
        if bad: errs.append(f"thẻ không cho phép: {bad}")
        if re.search(r"<h2[^>]*>\s*(kết luận|tóm lại|tổng kết)", s, re.I): errs.append("có mục kết luận/tóm tắt")
        cau = lambda t: {" ".join(c.split()) for c in re.split(r"(?<=[.!?:])\s+", t) if len(c.split()) > 6}
        mine = cau(plain(s))
        src = os.path.join(HERE, "nguon", f"{int(so):02d}.txt")
        if os.path.exists(src) and mine & cau(open(src).read()): errs.append(f"chép câu bài gốc: {list(mine & cau(open(src).read()))[:2]}")
        other = bai_path(so, "wix" if nen == "wp" else "wp")
        if os.path.exists(other) and mine & cau(plain(open(other).read())): errs.append("trùng câu với bản nền tảng kia")
    low = plain(s).lower()
    for ok in OK_NHAT: low = low.replace(ok, "")
    for b in BANNED:
        if re.search(r"(?<!\w)" + re.escape(b) + r"(?!\w)", low): errs.append(f"có từ cấm '{b}'")
    if re.search(r"1800\s?\d|@techcombank|call_center", low): errs.append("có hotline/email")
    m = meta(so).get(nen, {})
    if nen != "ma" and not 50 <= len(m.get("title", "")) <= 75: errs.append(f"tiêu đề {len(m.get('title',''))} ký tự")
    if not quiet: p("OK" if not errs else "LỖI: " + "; ".join(errs))
    return errs


# ---------- ảnh đại diện ----------
def cmd_anh(so, nen):
    from PIL import Image, ImageDraw, ImageFont
    m = meta(so)[nen]; W, H = 1200, 630
    F = "/usr/share/fonts/truetype/inter/"
    def font(sz, bold=False):
        for c in ([F + "Inter-Bold.ttf", F + "InterDisplay-Bold.ttf"] if bold else [F + "Inter-Regular.ttf", F + "InterDisplay-Regular.ttf"]):
            if os.path.exists(c): return ImageFont.truetype(c, sz)
        import subprocess
        path = subprocess.run(["fc-match", "-f", "%{file}", "Inter:bold" if bold else "Inter"], capture_output=True, text=True).stdout
        return ImageFont.truetype(path, sz)
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    if nen == "wp":   # kiểu 1: dải dọc bên trái, chữ căn trái
        for y in range(H): d.line([(0, y), (W, y)], fill=(8, 28 + y // 30, 64 + y // 12))
        d.rectangle([0, 0, 18, H], fill=(56, 132, 255))
        x0, y0 = 80, 90
    else:             # kiểu 2: khung viền, chữ căn giữa
        for y in range(H): d.line([(0, y), (W, y)], fill=(4, 40 + y // 25, 78 - y // 20))
        d.rounded_rectangle([40, 40, W - 40, H - 40], radius=28, outline=(120, 180, 255), width=3)
        x0, y0 = 110, 110
    def wrap(t, fnt, maxw):
        lines, cur = [], ""
        for w in t.split():
            if d.textlength((cur + " " + w).strip(), font=fnt) <= maxw: cur = (cur + " " + w).strip()
            else: lines.append(cur); cur = w
        return lines + [cur]
    small, kw, tt = font(28), font(44, True), font(56, True)
    d.text((x0, y0), "Kiến thức tài chính cá nhân", font=small, fill=(150, 195, 255))
    y = y0 + 60
    for ln in wrap(m["tu_khoa"].upper() if nen == "wp" else m["tu_khoa"], kw, W - 2 * x0)[:2]:
        d.text((x0, y), ln, font=kw, fill=(120, 230, 200)); y += 58
    y += 20
    for ln in wrap(m["title"], tt, W - 2 * x0)[:4]:
        d.text((x0, y), ln, font=tt, fill="white"); y += 70
    out = os.path.join(HERE, "bai", f"{int(so):02d}", f"anh-{nen}.png"); im.save(out)
    p("ok", out)
    return out


# ---------- nội dung theo nền tảng ----------
def to_gutenberg(h):
    out = []
    for tag, attrs, inner in re.findall(r"<(p|h2|h3|ul|ol)([^>]*)>(.*?)</\1>", h, re.S):
        inner = inner.strip()
        if tag == "p": out.append(f"<!-- wp:paragraph -->\n<p>{inner}</p>\n<!-- /wp:paragraph -->")
        elif tag == "h2": out.append(f'<!-- wp:heading {{"style":{{"typography":{{"fontSize":"26px"}}}}}} -->\n<h2 class="wp-block-heading" style="font-size:26px">{inner}</h2>\n<!-- /wp:heading -->')
        elif tag == "h3": out.append(f'<!-- wp:heading {{"level":3,"style":{{"typography":{{"fontSize":"21px"}}}}}} -->\n<h3 class="wp-block-heading" style="font-size:21px">{inner}</h3>\n<!-- /wp:heading -->')
        else:
            lis = re.findall(r"<li>(.*?)</li>", inner, re.S)
            o = ' {"ordered":true}' if tag == "ol" else ""
            items = "\n".join(f"<!-- wp:list-item -->\n<li>{li.strip()}</li>\n<!-- /wp:list-item -->" for li in lis)
            out.append(f"<!-- wp:list{o} -->\n<{tag} class=\"wp-block-list\">\n{items}\n</{tag}>\n<!-- /wp:list -->")
    return "\n\n".join(out)


def ricos_text(inner):
    nodes = []
    for part in re.split(r"(<a [^>]*>.*?</a>|<strong>.*?</strong>)", inner, flags=re.S):
        if not part: continue
        dec = []
        m = re.match(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', part, re.S)
        if m: dec = [{"type": "LINK", "linkData": {"link": {"url": m.group(1), "target": "BLANK"}}}]; part = m.group(2)
        m = re.match(r"<strong>(.*?)</strong>", part, re.S)
        if m: dec = [{"type": "BOLD", "fontWeightValue": 700}]; part = m.group(1)
        t = html.unescape(re.sub(r"<[^>]+>", "", part))
        if t: nodes.append({"type": "TEXT", "id": "", "textData": {"text": t, "decorations": dec}})
    return nodes


def to_ricos(h):
    nid = lambda: uuid.uuid4().hex[:8]
    out = []
    for tag, attrs, inner in re.findall(r"<(p|h2|h3|ul|ol)([^>]*)>(.*?)</\1>", h, re.S):
        if tag == "p": out.append({"type": "PARAGRAPH", "id": nid(), "nodes": ricos_text(inner), "paragraphData": {}})
        elif tag in ("h2", "h3"): out.append({"type": "HEADING", "id": nid(), "nodes": ricos_text(inner), "headingData": {"level": int(tag[1])}})
        else:
            lis = [{"type": "LIST_ITEM", "id": nid(), "nodes": [{"type": "PARAGRAPH", "id": nid(), "nodes": ricos_text(li), "paragraphData": {}}]}
                   for li in re.findall(r"<li>(.*?)</li>", inner, re.S)]
            out.append({"type": "BULLETED_LIST" if tag == "ul" else "ORDERED_LIST", "id": nid(), "nodes": lis})
    return out


# ---------- đăng ----------
def log(rec):
    rec["luc"] = datetime.now(VN).isoformat(timespec="seconds")
    open(os.path.join(HERE, "da-dang.jsonl"), "a").write(json.dumps(rec, ensure_ascii=False) + "\n")


def da_dang():
    f = os.path.join(HERE, "da-dang.jsonl")
    return [json.loads(l) for l in open(f)] if os.path.exists(f) else []


def cmd_dang(so, nen):
    if any(r["so"] == int(so) and r["nen"] == nen and r.get("ok") for r in da_dang()):
        sys.exit(f"bài {so} {nen} đã đăng rồi — bỏ qua")
    gio = next((e["gio"] for e in json.load(open(os.path.join(HERE, "lich.json"))) if e["so"] == int(so) and e["nen"] == nen), None)
    if gio and datetime.fromisoformat(gio) > datetime.now(VN) and not os.environ.get("CHO_PHEP_SOM"):
        sys.exit(f"chưa đến giờ ({gio}) — không đăng sớm")
    if cmd_check(so, nen, quiet=True):
        sys.exit("bài chưa đạt soát: " + "; ".join(cmd_check(so, nen, quiet=True)))
    x = item(so); m = meta(so).get(nen, {}); body = open(bai_path(so, nen)).read()
    if nen == "wp":
        k = keys("wp"); H = {"Authorization": "Bearer " + k["access_token"]}
        img = cmd_anh(so, "wp")
        data, ct = multipart({}, {"media[]": (m["slug"] + ".png", open(img, "rb").read(), "image/png")})
        st, r = req("POST", f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/media/new", {**H, "Content-Type": ct}, data)
        mid = r["media"][0]["ID"] if st == 200 and r.get("media") else None
        if not mid: p("⚠ tải ảnh lỗi", st, str(r)[:200])
        payload = {"title": m["title"], "content": to_gutenberg(body), "slug": m["slug"], "status": "publish", "excerpt": m.get("mo_ta", "")}
        if mid: payload["featured_image"] = mid
        st, r = req("POST", f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_SITE}/posts/new", H, payload)
        ok = st == 200 and r.get("status") == "publish"
        rec = {"so": int(so), "nen": "wp", "ok": ok, "http": st, "link": r.get("URL") if ok else None, "id": r.get("ID"), "anh": bool(mid)}
        if not ok: rec["loi"] = str(r)[:300]
    elif nen == "wix":
        k = keys("wix"); H = {"Authorization": k["api_key"], "wix-site-id": k["site_id"]}
        img = cmd_anh(so, "wix"); media = None
        st, r = req("POST", "https://www.wixapis.com/site-media/v1/files/generate-upload-url", H, {"mimeType": "image/png", "fileName": m["slug"] + ".png"})
        if st == 200:
            st2, r2 = req("PUT", r["uploadUrl"] + "?filename=" + urllib.parse.quote(m["slug"] + ".png"), {"Content-Type": "image/png"}, open(img, "rb").read(), timeout=120)
            fd = (r2 or {}).get("file", {}) if isinstance(r2, dict) else {}
            if fd.get("id"):
                media = {"wixMedia": {"image": {"id": fd["id"], "width": 1200, "height": 630}}, "displayed": True, "custom": True}
        if not media: p("⚠ tải ảnh Wix lỗi", st, str(r)[:200])
        dp = {"title": m["title"], "memberId": k["member_id"], "richContent": {"nodes": to_ricos(body), "metadata": {"version": 1}},
              "excerpt": m.get("mo_ta", "")}
        if media: dp["media"] = media
        st, r = req("POST", "https://www.wixapis.com/blog/v3/draft-posts?fieldsets=URL", H, {"draftPost": dp, "publish": True})
        post = r.get("draftPost", {}) if isinstance(r, dict) else {}
        ok = st == 200 and bool(post.get("id"))
        link = None
        if ok:
            st3, r3 = req("PATCH", f"https://www.wixapis.com/blog/v3/draft-posts/{post['id']}?fieldsets=URL", H,
                          {"draftPost": {"id": post["id"], "memberId": k["member_id"], "seoSlug": m["slug"]}, "action": "UPDATE_PUBLICATION"})
            if st3 != 200: p("⚠ đổi slug Wix lỗi", st3, str(r3)[:200])
            time.sleep(3)
            st4, r4 = req("GET", f"https://www.wixapis.com/blog/v3/posts/{post['id']}?fieldsets=URL", H)
            u = (r4.get("post", {}) if isinstance(r4, dict) else {}).get("url") or post.get("url") or {}
            link = (u.get("base", "") + urllib.parse.quote(u.get("path", ""))) if u else None
            # trang Wix cần vài chục giây mới mở được link mới — thử lại tối đa ~2 phút
            stc = None
            for _ in range(12):
                time.sleep(10)
                try:
                    stc, _ = req("GET", link)
                except Exception as e:
                    stc = str(e)
                if stc == 200: break
            if stc != 200: p("⚠ chưa mở được link Wix:", stc)
        rec = {"so": int(so), "nen": "wix", "ok": ok, "http": st, "link": link, "id": post.get("id"), "anh": bool(media)}
        if not ok: rec["loi"] = str(r)[:300]
    else:
        k = keys("ma")
        st, r = req("POST", k["instance_url"] + "/api/v1/statuses",
                    {"Authorization": "Bearer " + k["access_token"], "Idempotency-Key": f"gp-{so}-ma"},
                    {"status": body.strip(), "visibility": "public", "language": "vi"})
        ok = st == 200 and bool(r.get("url"))
        rec = {"so": int(so), "nen": "ma", "ok": ok, "http": st, "link": r.get("url") if ok else None, "id": r.get("id") if isinstance(r, dict) else None}
        if not ok: rec["loi"] = str(r)[:300]
    rec["gp"] = x["url"]
    log(rec)
    p(json.dumps(rec, ensure_ascii=False))


def cmd_lich():
    L = json.load(open(os.path.join(HERE, "lich.json")))
    done = {(r["so"], r["nen"]) for r in da_dang() if r.get("ok")}
    now = datetime.now(VN)
    due = [e for e in L if (e["so"], e["nen"]) not in done and datetime.fromisoformat(e["gio"]) <= now]
    nxt = [e for e in L if (e["so"], e["nen"]) not in done and datetime.fromisoformat(e["gio"]) > now]
    p("ĐẾN HẠN:", json.dumps(due, ensure_ascii=False))
    p("KẾ TIẾP:", json.dumps(nxt[:3], ensure_ascii=False))
    p("CÒN LẠI:", len(due) + len(nxt), "/", len(L))


if __name__ == "__main__":
    c, *a = sys.argv[1:]
    {"fetch": cmd_fetch, "check": cmd_check, "anh": cmd_anh, "dang": cmd_dang, "lich": cmd_lich}[c](*a)
