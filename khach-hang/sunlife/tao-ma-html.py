# Trang chủ + Tin tức Sun Life Việt Nam (web vệ tinh WordPress.com). Chạy: python3 tao-ma-html.py
# sunlife.com.vn chặn bot (captcha) -> logo, ảnh, câu giới thiệu lấy từ sunlife.com (bản toàn cầu), dịch sang tiếng Việt.
# Màu đo từ file logo gốc sunlife-logo-horizontal-rgb-primary-public.svg: #FEBE10 (vàng) + #003946 (xanh đậm).
# CHƯA có: hotline, địa chỉ, tên sản phẩm VN -> chờ Trang dán nội dung sunlife.com.vn rồi bổ sung.
import pathlib
D = pathlib.Path(__file__).parent
M = "https://www.sunlife.com.vn/vn/"
LOGO = "https://www.sunlife.com/content/dam/sunlife/global/logos/sunlife/sunlife-logo-horizontal-rgb-primary-public.svg"
G = "https://www.sunlife.com/content/dam/sunlife/regional/global-marketing/images/com/"
IMG_HERO = G + "adobestock458560224-who-we-are-540x345jpg.jpg"
IMG_ABOUT = G + "adobestock-562334540-home-regions.jpg"
IMG_LIFE = G + "homepage-image-corporate-720x480.png"
Y, K = "#FEBE10", "#003946"
MUTED, LINE, SOFT = "#003946b3", "#00394614", "#FEBE1014"
F = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"
EXT = ' target="_blank" rel="noopener"'

def header(home):
    pre = "" if home else "/"
    a = lambda h, t: f'<a href="{h}" style="color:{K};text-decoration:none;padding:4px 0;">{t}</a>'
    return f'''<div style="background:#ffffff;border-bottom:4px solid {Y};padding:14px 20px;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="/" style="display:flex;align-items:center;text-decoration:none;"><img src="{LOGO}" alt="Logo Sun Life Việt Nam" width="150" height="38" style="width:150px;height:auto;display:block;" /></a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:6px 24px;font-size:15px;font-weight:600;">
{a(pre + "#gioi-thieu", "Giới thiệu")}
{a(pre + "#giai-phap", "Giải pháp")}
{a(pre + "#dong-hanh", "Đồng hành")}
{a("/tin-tuc/", "Tin tức")}
{a(pre + "#lien-he", "Liên hệ")}
<a href="{M}"{EXT} style="background:{Y};color:{K};text-decoration:none;padding:9px 18px;border-radius:999px;font-weight:700;">Website chính thức</a>
</div>
</div>
</div>
'''

def footer():
    # Nền sáng để logo gốc (chữ xanh đậm) đứng thẳng trên nền, không cần khung trắng
    h = lambda t: f'<p style="margin:0 0 14px;color:{K};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">{t}</p>'
    li = lambda t: f'<p style="margin:0 0 8px;"><a href="{M}"{EXT} style="color:{MUTED};text-decoration:none;">{t}</a></p>'
    col = lambda title, items: '<div style="flex:1 1 170px;min-width:0;">\n' + h(title) + "\n" + "\n".join(li(t) for t in items) + "\n</div>"
    return f'''<div style="background:#fff6dc;border-top:4px solid {Y};color:{MUTED};padding:52px 20px 0;font-size:15px;line-height:1.65;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:32px 44px;padding-bottom:36px;">
<div style="flex:1.6 1 300px;min-width:0;">
<img src="{LOGO}" alt="Logo Sun Life" width="150" height="38" style="width:150px;height:auto;display:block;margin-bottom:18px;" />
<p style="margin:0 0 12px;">Sun Life là tập đoàn dịch vụ tài chính hàng đầu, giúp khách hàng đạt được sự an tâm tài chính trọn đời và sống khỏe mạnh hơn.</p>
<p style="margin:0;">Thông tin liên hệ, sản phẩm và mạng lưới tại Việt Nam: <a href="{M}"{EXT} style="color:{K};text-decoration:none;font-weight:800;border-bottom:2px solid {Y};">sunlife.com.vn</a></p>
</div>
{col("Giải pháp", ["Bảo hiểm", "Đầu tư và tích lũy", "Sức khỏe", "Quản lý tài sản"])}
{col("Sun Life Việt Nam", ["Về Sun Life Việt Nam", "Sản phẩm", "Hỗ trợ khách hàng", "Liên hệ"])}
</div>
<div style="max-width:1200px;margin:0 auto;border-top:1px solid #00394626;padding:18px 0 22px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:14px;color:{MUTED};">
<p style="margin:0;">© 2026 Sun Life Việt Nam</p>
<p style="margin:0;">Website chính thức: <a href="{M}"{EXT} style="color:{K};text-decoration:none;font-weight:800;border-bottom:2px solid {Y};">www.sunlife.com.vn</a></p>
</div>
</div>
'''

def eyebrow(t, center=False, color="#9a6f00"):
    c = "text-align:center;" if center else ""
    return f'<p style="margin:0 0 10px;color:{color};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;{c}">{t}</p>'
def h2(t, center=False, mb=36, color=K):
    c = "text-align:center;margin-left:auto;margin-right:auto;" if center else ""
    return f'<h2 style="margin:0 0 {mb}px;color:{color};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;max-width:780px;{c}">{t}</h2>'
def section(inner, bg="#ffffff", id_=""):
    i = f' id="{id_}"' if id_ else ""
    return f'<section{i} style="padding:clamp(56px,8vw,92px) 20px;background:{bg};">\n<div style="max-width:1200px;margin:0 auto;">\n{inner}\n</div>\n</section>\n'
def btn(t, bg=Y, color=K):
    return f'<a href="{M}"{EXT} style="display:inline-block;background:{bg};color:{color};text-decoration:none;font-weight:800;padding:13px 26px;border-radius:999px;">{t}</a>'

hero = f'''<section style="background:{K};color:#ffffff;padding:clamp(44px,7vw,84px) 20px;">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1 1 420px;min-width:0;">
<p style="display:inline-block;margin:0 0 18px;padding:6px 14px;border:1px solid {Y};border-radius:999px;color:{Y};font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Sun Life Việt Nam</p>
<h1 style="margin:0 0 18px;color:#ffffff;font-size:clamp(30px,4.6vw,50px);line-height:1.15;font-weight:800;">An tâm tài chính trọn đời, sống khỏe mạnh&nbsp;<span style="color:{Y};">hơn</span></h1>
<p style="margin:0 0 28px;font-size:clamp(16px,1.6vw,19px);color:#ffffffd9;max-width:560px;">Sun Life giúp khách hàng xây dựng sự an tâm tài chính trọn đời và sống khỏe mạnh hơn – đồng hành trong những khoảnh khắc quan trọng của cuộc&nbsp;sống.</p>
<div style="display:flex;flex-wrap:wrap;gap:12px;">
{btn("Khám phá Sun Life Việt Nam")}
<a href="{M}"{EXT} style="border:1.5px solid #ffffff;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 26px;border-radius:999px;">Tìm hiểu giải pháp</a>
</div>
</div>
<div style="flex:1 1 440px;min-width:0;">
<img src="{IMG_HERO}" alt="Người mẹ và em bé – Sun Life đồng hành cùng gia đình" style="width:100%;height:auto;display:block;border-radius:16px;border-bottom:6px solid {Y};" />
</div>
</div>
</section>
'''

about = section(f'''<div style="display:flex;flex-wrap:wrap;gap:40px;align-items:center;">
<div style="flex:1 1 380px;min-width:0;">
<img src="{IMG_ABOUT}" alt="Chuyên viên tư vấn tài chính Sun Life làm việc" style="width:100%;height:auto;display:block;border-radius:16px;" />
</div>
<div style="flex:1.2 1 420px;min-width:0;">
{eyebrow("Về Sun Life")}
{h2("Tập đoàn bảo hiểm và quản lý tài sản toàn&nbsp;cầu", False, 18)}
<p style="margin:0 0 16px;color:{MUTED};font-size:17px;">Sun Life là tập đoàn quản lý tài sản và bảo hiểm hàng đầu thế giới, với hoạt động trải rộng trên các lĩnh vực quản lý tài sản, đầu tư tích lũy, bảo hiểm và sức khỏe.</p>
<p style="margin:0 0 26px;color:{MUTED};font-size:17px;">Tại mỗi thị trường, Sun Life kết hợp sức mạnh toàn cầu, am hiểu địa phương, tư vấn đáng tin cậy và năng lực số để đáp ứng nhu cầu của khách hàng, doanh nghiệp và tổ chức mà chúng tôi phục&nbsp;vụ.</p>
{btn("Xem thêm về Sun Life Việt Nam", K, "#ffffff")}
</div>
</div>''', id_="gioi-thieu")

card = lambda title, text, accent: f'''<a href="{M}"{EXT} style="flex:1 1 210px;min-width:0;display:block;text-decoration:none;background:#ffffff;border-radius:16px;padding:26px 22px;border-top:5px solid {accent};box-shadow:0 6px 20px #00394612;">
<h3 style="margin:0 0 10px;color:{K};font-size:20px;line-height:1.3;font-weight:800;">{title}</h3>
<p style="margin:0 0 14px;color:{MUTED};font-size:15px;">{text}</p>
<span style="color:{K};font-weight:800;font-size:15px;border-bottom:2px solid {Y};">Tìm hiểu →</span>
</a>'''
solutions = section(f'''{eyebrow("Giải pháp", True)}
{h2("Giải pháp cho mọi giai đoạn cuộc&nbsp;sống", True, 12)}
<p style="margin:0 auto 36px;color:{MUTED};font-size:17px;text-align:center;max-width:720px;">Bốn lĩnh vực cốt lõi giúp Sun Life đồng hành cùng khách hàng qua nhiều khoảnh khắc quan trọng hơn trong&nbsp;đời.</p>
<div style="display:flex;flex-wrap:wrap;gap:20px;">
{card("Bảo hiểm","Bảo vệ những người bạn yêu thương trước những rủi ro bất ngờ của cuộc sống.",Y)}
{card("Đầu tư và tích lũy","Giải pháp và tư vấn giúp khách hàng tiết kiệm, đầu tư, lập kế hoạch nghỉ hưu và xây dựng sự an tâm tài chính.",K)}
{card("Sức khỏe","Các quyền lợi và giải pháp sức khỏe hỗ trợ khách hàng chăm sóc sức khỏe và sự an lành.",Y)}
{card("Quản lý tài sản","Năng lực và giải pháp đầu tư phục vụ khách hàng cá nhân và tổ chức.",K)}
</div>''', bg=SOFT, id_="giai-phap")

moment = lambda t: f'<div style="flex:1 1 220px;min-width:0;display:flex;gap:12px;align-items:flex-start;"><span style="flex:0 0 26px;height:26px;border-radius:999px;background:{Y};color:{K};font-weight:900;text-align:center;line-height:26px;">✓</span><p style="margin:0;color:#ffffffe6;font-size:16px;">{t}</p></div>'
journey = section(f'''<div style="display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1.2 1 420px;min-width:0;">
{eyebrow("Đồng hành", False, Y)}
{h2("Đồng hành cùng bạn trong từng khoảnh khắc", False, 16, "#ffffff")}
<p style="margin:0 0 24px;color:#ffffffd9;font-size:17px;">Sứ mệnh của Sun Life định hướng cách chúng tôi hỗ trợ khách hàng suốt cuộc đời:</p>
<div style="display:flex;flex-wrap:wrap;gap:16px 24px;margin-bottom:28px;">
{moment("Bảo vệ những người bạn yêu thương")}
{moment("Tiếp cận quyền lợi sức khỏe")}
{moment("Xây dựng và quản lý tài sản")}
{moment("Lập kế hoạch nghỉ hưu")}
{moment("Đầu tư cho tương lai")}
</div>
{btn("Tư vấn cùng Sun Life Việt Nam")}
</div>
<div style="flex:1 1 380px;min-width:0;">
<img src="{IMG_LIFE}" alt="Sống khỏe mạnh hơn cùng Sun Life" style="width:100%;height:auto;display:block;border-radius:16px;" />
</div>
</div>''', bg=K, id_="dong-hanh")

contact = f'''<section id="lien-he" style="padding:clamp(56px,8vw,92px) 20px;background:#ffffff;">
<div style="max-width:1200px;margin:0 auto;background:{Y};border-radius:20px;padding:clamp(32px,5vw,56px);display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between;">
<div style="flex:1 1 420px;min-width:0;">
{h2("Liên hệ Sun Life Việt&nbsp;Nam", False, 12)}
<p style="margin:0;color:{K};font-size:17px;">Tìm hiểu sản phẩm, tìm tư vấn viên và nhận hỗ trợ khách hàng trên website chính thức của Sun Life Việt&nbsp;Nam.</p>
</div>
<a href="{M}"{EXT} style="display:inline-block;background:{K};color:#ffffff;text-decoration:none;font-weight:800;padding:14px 28px;border-radius:999px;">Truy cập sunlife.com.vn →</a>
</div>
</section>
'''

def html_block(x): return "<!-- wp:html -->\n" + x + "<!-- /wp:html -->\n"
def full_group(x):
    return ('<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->\n'
            '<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0">' + x + '</div>\n<!-- /wp:group -->\n')

home_inner = f'<div style="{F}color:{K};line-height:1.65;background:#ffffff;margin:0;">\n' + header(True) + hero + about + solutions + journey + contact + footer() + "</div>\n"
(D / "HTML-TRANG-CHU.txt").write_text(full_group(html_block(home_inner)), encoding="utf-8")

news_top = f'''<div style="background:{K};color:#ffffff;padding:clamp(44px,7vw,80px) 20px;{F}">
<div style="max-width:1200px;margin:0 auto;">
<p style="margin:0 0 10px;color:{Y};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Chia sẻ</p>
<h1 style="margin:0 0 12px;color:#ffffff;font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">Tin tức Sun Life Việt Nam</h1>
<p style="margin:0;color:#ffffffd9;font-size:17px;max-width:660px;">Kiến thức bảo hiểm, đầu tư tích lũy và sống khỏe – cùng bạn xây dựng sự an tâm tài chính trọn&nbsp;đời.</p>
</div>
</div>
'''
news_query = f'''<!-- wp:group {{"align":"full","style":{{"spacing":{{"padding":{{"top":"56px","bottom":"72px","left":"20px","right":"20px"}}}},"color":{{"background":"#fffbf0"}}}},"layout":{{"type":"constrained","contentSize":"1200px"}}}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#fffbf0;padding-top:56px;padding-right:20px;padding-bottom:72px;padding-left:20px"><!-- wp:query {{"queryId":7,"query":{{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}}}} -->
<div class="wp-block-query"><!-- wp:post-template {{"style":{{"spacing":{{"blockGap":"28px"}}}},"layout":{{"type":"grid","columnCount":4}}}} -->
<!-- wp:post-featured-image {{"isLink":true,"aspectRatio":"16/9","style":{{"border":{{"radius":"14px"}}}}}} /-->

<!-- wp:post-date {{"style":{{"color":{{"text":"#9a6f00"}},"typography":{{"fontSize":"14px","fontWeight":"700"}},"spacing":{{"margin":{{"top":"14px"}}}}}}}} /-->

<!-- wp:post-title {{"level":3,"isLink":true,"style":{{"typography":{{"fontSize":"20px","fontWeight":"800","lineHeight":"1.35"}},"elements":{{"link":{{"color":{{"text":"{K}"}}}}}},"color":{{"text":"{K}"}},"spacing":{{"margin":{{"top":"6px","bottom":"8px"}}}}}}}} /-->

<!-- wp:post-excerpt {{"moreText":"Đọc tiếp →","excerptLength":28,"style":{{"typography":{{"fontSize":"15px"}},"elements":{{"link":{{"color":{{"text":"{K}"}}}}}}}}}} /-->
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
<!-- /wp:group -->
'''
news = html_block(header(False) + news_top) + "\n" + news_query + "\n" + html_block(footer())
(D / "HTML-TRANG-TIN-TUC.txt").write_text(full_group(news), encoding="utf-8")
(D / "HTML-MAU-PAGES-3-DONG.txt").write_text(
    '<!-- wp:group {"tagName":"main","style":{"spacing":{"blockGap":"0","margin":{"top":"0"}}},"layout":{"type":"default"}} -->\n'
    '<main class="wp-block-group" style="margin-top:0"><!-- wp:post-content {"layout":{"type":"constrained"}} /--></main>\n'
    '<!-- /wp:group -->\n', encoding="utf-8")
(D / "xem-truoc-trang-chu.html").write_text('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sun Life Việt Nam – Xem trước</title></head><body style="margin:0;">' + home_inner + "</body></html>", encoding="utf-8")
print("xong")
