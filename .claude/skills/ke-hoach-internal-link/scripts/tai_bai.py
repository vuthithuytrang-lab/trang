"""Tải nội dung bài blog về dạng khối (h1/h2/h3/p/li/td) để đọc và chọn chỗ chèn link.

Cách dùng:
    python3 tai_bai.py danh-sach-url.txt thu-muc-luu/

Mỗi bài lưu thành <thu-muc-luu>/<slug>.json gồm url, blocks, links (các link nội bộ có sẵn trong bài).
Chỉ dùng thư viện chuẩn của Python, không cần cài thêm.
"""
import json
import os
import sys
import time
import urllib.request
from html.parser import HTMLParser

TAGS = {"h1", "h2", "h3", "h4", "p", "li", "td"}
SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header"}


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self.links = [], []
        self.stack, self.buf, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith("/"):
                href = "https://techcombank.com" + href
            if "techcombank.com" in href:
                self.links.append(href.split("#")[0])
        if tag in TAGS:
            self.flush()
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in SKIP and self.skip:
            self.skip -= 1
        if tag in TAGS and self.stack and self.stack[-1] == tag:
            self.flush()
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and not self.skip:
            self.buf.append(data)

    def flush(self):
        text = " ".join("".join(self.buf).split())
        if self.stack and text:
            self.blocks.append([self.stack[-1], text])
        self.buf = []


def tai(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (internal-link-audit)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    p = Parser()
    p.feed(html)
    p.flush()
    return {"url": url, "blocks": p.blocks, "links": sorted(set(p.links))}


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    urls = [u.strip() for u in open(src, encoding="utf-8") if u.strip().startswith("http")]
    loi = []
    for i, u in enumerate(urls, 1):
        slug = u.rstrip("/").split("/")[-1]
        f = os.path.join(out, slug + ".json")
        if os.path.exists(f):
            continue
        try:
            json.dump(tai(u), open(f, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception as e:  # ghi lại để báo thật, không đoán nội dung
            loi.append((u, str(e)))
        if i % 25 == 0:
            print(f"{i}/{len(urls)}")
        time.sleep(0.3)
    print(f"Xong. Lỗi: {len(loi)}")
    for u, e in loi:
        print("  ", u, e)


if __name__ == "__main__":
    main()
