# Sinh mã dán WordPress cho nganhangquoctevib.wordpress.com. Chạy: python3 tao-ma.py
import pathlib
D = pathlib.Path(__file__).parent
SITE = "https://nganhangquoctevib.wordpress.com"
MAIN = "https://www.vib.com.vn"
LOGO = SITE + "/wp-content/uploads/2026/09/cropped-avatar-vib.jpg?w=96"
BLUE, ORANGE = "#005BAA", "#F27C24"
FONT = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"

goc = (D / "nguon/trang-chu-goc.txt").read_text(encoding="utf-8")
# Sửa lỗi hiển thị: chữ link ở chân trang bị dính cú pháp markdown
goc = goc.replace("[www.vib.com.vn](https://www.vib.com.vn)", "www.vib.com.vn")
TP = '<!-- wp:template-part {"slug":"header","theme":"pub/assembler"} /-->'
assert goc.startswith(TP)
i = goc.index('<!-- wp:group {"metadata":{"name":"Chân trang"}')
than = goc[len(TP):i].strip() + "\n"
chan = goc[i:].strip() + "\n"

def link(href, text, ext=True):
    t = ' target="_blank" rel="noopener"' if ext else ""
    return f'<a href="{href}"{t} style="color:{BLUE};text-decoration:none;padding:4px 0;">{text}</a>'

header = f'''<!-- wp:html -->
<div style="background:#ffffff;border-bottom:3px solid {ORANGE};padding:12px 20px;{FONT}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="{SITE}/" style="display:flex;align-items:center;gap:12px;text-decoration:none;"><img src="{LOGO}" alt="Logo VIB – Ngân hàng TMCP Quốc Tế Việt Nam" width="46" height="46" style="width:46px;height:46px;border-radius:10px;display:block;" /><span style="color:{BLUE};font-size:18px;font-weight:800;line-height:1.2;">Ngân hàng Quốc tế VIB</span></a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:6px 24px;font-size:15px;font-weight:600;">
{link(SITE + "/", "Trang chủ", False)}
{link(MAIN + "/vn/the-tin-dung", "Thẻ tín dụng")}
{link(MAIN + "/vn/ngan-hang-so/myvib", "Ngân hàng số")}
{link(MAIN + "/vn/promotion", "Ưu đãi")}
{link(SITE + "/tin-tuc/", "Tin tức", False)}
<a href="{MAIN}/" target="_blank" rel="noopener" style="background:{BLUE};color:#ffffff;text-decoration:none;padding:9px 18px;border-radius:999px;">Website chính thức</a>
</div>
</div>
</div>
<!-- /wp:html -->
'''

MAIN_OPEN = '<!-- wp:group {"tagName":"main","style":{"spacing":{"blockGap":"0","margin":{"top":"0"}}},"layout":{"type":"default"}} -->\n<main class="wp-block-group" style="margin-top:0">'
MAIN_CLOSE = '</main>\n<!-- /wp:group -->\n'

# A. Trang chủ (mẫu Blog Home): header VIB thay header theme, phần còn lại giữ nguyên
(D / "A-MAU-TRANG-CHU.txt").write_text(header + "\n" + than + "\n" + chan, encoding="utf-8")

# B. Mẫu Pages: header VIB + nội dung trang + chân trang như trang chủ
(D / "B-MAU-PAGES.txt").write_text(
    header + "\n" + MAIN_OPEN + '<!-- wp:post-content {"layout":{"type":"constrained"}} /-->' + MAIN_CLOSE + "\n" + chan,
    encoding="utf-8")

# C. Nội dung trang Tin tức
news = f'''<!-- wp:group {{"align":"full","style":{{"spacing":{{"padding":{{"top":"0","bottom":"0","left":"0","right":"0"}},"blockGap":"0"}}}},"layout":{{"type":"default"}}}} -->
<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0"><!-- wp:html -->
<div style="background:{BLUE};color:#ffffff;padding:clamp(44px,7vw,80px) 20px;{FONT}">
<div style="max-width:1200px;margin:0 auto;">
<p style="margin:0 0 10px;color:#F9B812;font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Ưu đãi</p>
<h1 style="margin:0 0 12px;color:#ffffff;font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">Tin tức VIB</h1>
<p style="margin:0;color:#ffffffd9;font-size:17px;max-width:640px;">Cập nhật tin tức, ưu đãi và kiến thức tài chính từ Ngân hàng Thương mại Cổ phần Quốc tế Việt&nbsp;Nam&nbsp;(VIB).</p>
</div>
</div>
<!-- /wp:html -->

<!-- wp:group {{"align":"full","style":{{"spacing":{{"padding":{{"top":"56px","bottom":"72px","left":"20px","right":"20px"}}}},"color":{{"background":"#f6f7f9"}}}},"layout":{{"type":"constrained","contentSize":"1200px"}}}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#f6f7f9;padding-top:56px;padding-right:20px;padding-bottom:72px;padding-left:20px"><!-- wp:query {{"queryId":7,"query":{{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}}}} -->
<div class="wp-block-query"><!-- wp:post-template {{"style":{{"spacing":{{"blockGap":"28px"}}}},"layout":{{"type":"grid","columnCount":4}}}} -->
<!-- wp:post-featured-image {{"isLink":true,"aspectRatio":"16/9","style":{{"border":{{"radius":"14px"}}}}}} /-->

<!-- wp:post-date {{"style":{{"color":{{"text":"{ORANGE}"}},"typography":{{"fontSize":"14px","fontWeight":"700"}},"spacing":{{"margin":{{"top":"14px"}}}}}}}} /-->

<!-- wp:post-title {{"level":3,"isLink":true,"style":{{"typography":{{"fontSize":"20px","fontWeight":"800","lineHeight":"1.35"}},"elements":{{"link":{{"color":{{"text":"{BLUE}"}}}}}},"color":{{"text":"{BLUE}"}},"spacing":{{"margin":{{"top":"6px","bottom":"8px"}}}}}}}} /-->

<!-- wp:post-excerpt {{"moreText":"Đọc tiếp →","excerptLength":28,"style":{{"typography":{{"fontSize":"15px"}},"elements":{{"link":{{"color":{{"text":"{ORANGE}"}}}}}}}}}} /-->
<!-- /wp:post-template -->

<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Chưa có bài viết nào. Bài bạn đăng sẽ tự hiện ở đây.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results -->

<!-- wp:query-pagination {{"paginationArrow":"arrow","layout":{{"type":"flex","justifyContent":"center"}}}} -->
<!-- wp:query-pagination-previous {{"label":"Trang trước"}} /-->

<!-- wp:query-pagination-numbers /-->

<!-- wp:query-pagination-next {{"label":"Trang sau"}} /-->
<!-- /wp:query-pagination --></div>
<!-- /wp:query --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->
'''
(D / "C-NOI-DUNG-TRANG-TIN-TUC.txt").write_text(news, encoding="utf-8")

# D. Mẫu Single Posts: trang chi tiết bài viết
single = (header + "\n"
  + '<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"0"},"padding":{"top":"48px","bottom":"64px","left":"20px","right":"20px"}}},"layout":{"type":"constrained","contentSize":"780px"}} -->\n'
  + '<main class="wp-block-group" style="margin-top:0;padding-top:48px;padding-right:20px;padding-bottom:64px;padding-left:20px">'
  + f'<!-- wp:post-date {{"style":{{"color":{{"text":"{ORANGE}"}},"typography":{{"fontSize":"14px","fontWeight":"700"}}}}}} /-->\n\n'
  + f'<!-- wp:post-title {{"level":1,"style":{{"color":{{"text":"{BLUE}"}},"typography":{{"fontSize":"36px","fontWeight":"800","lineHeight":"1.25"}}}}}} /-->\n\n'
  + '<!-- wp:post-featured-image {"style":{"border":{"radius":"14px"}}} /-->\n\n'
  + '<!-- wp:post-content {"layout":{"type":"constrained"}} /-->\n\n'
  + '<!-- wp:paragraph -->\n<p><a href="' + SITE + '/tin-tuc/">← Quay lại trang Tin tức</a></p>\n<!-- /wp:paragraph -->'
  + MAIN_CLOSE + "\n" + chan)
(D / "D-MAU-BAI-VIET.txt").write_text(single, encoding="utf-8")

(D / "xem-truoc-dau-trang.html").write_text(
    '<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VIB – xem trước</title></head><body style="margin:0;">'
    + header.replace("<!-- wp:html -->", "").replace("<!-- /wp:html -->", "")
    + news.split("<!-- wp:html -->")[1].split("<!-- /wp:html -->")[0] + "</body></html>", encoding="utf-8")
print("xong")
