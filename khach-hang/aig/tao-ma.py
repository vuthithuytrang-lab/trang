# Ghép các phần thành mã dán vào WordPress + bản xem trước.
# Chạy: python3 tao-ma.py
import pathlib
D = pathlib.Path(__file__).parent
SITE = "https://asiaingredientsgroup.wordpress.com"
MAIN = "https://asiagroup-vn.com"
FONT = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"

def header(home):
    pre = "" if home else SITE + "/"
    def link(href, text):
        return f'<a href="{href}" style="color:#0A2360;text-decoration:none;padding:4px 0;">{text}</a>'
    return f'''<div style="background:#ffffff;border-bottom:1px solid #0A23601a;padding:14px 20px;{FONT}">
<div style="max-width:1160px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="{SITE}/" style="display:flex;align-items:center;text-decoration:none;"><img src="{MAIN}/wp-content/uploads/2025/04/logo_aig.png" alt="Logo Tập đoàn Nguyên liệu Á Châu AIG" width="120" height="58" style="width:120px;height:auto;display:block;" /></a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:6px 26px;font-size:15px;font-weight:600;">
{link(pre + "#gioi-thieu", "Giới thiệu")}
{link(pre + "#giai-phap", "Giải pháp")}
{link(pre + "#cong-nghe", "Công nghệ")}
{link(SITE + "/tin-tuc/", "Tin tức")}
{link(pre + "#lien-he", "Liên hệ")}
<a href="{MAIN}" style="background:#DDA727;color:#0A2360;text-decoration:none;padding:9px 18px;border-radius:999px;">Website chính thức</a>
</div>
</div>
</div>
'''

def footer(home):
    pre = "" if home else SITE + "/"
    li = lambda href, t: f'<p style="margin:0 0 10px;"><a href="{href}" style="color:#ffffffcc;text-decoration:none;">{t}</a></p>'
    h = lambda t: f'<p style="margin:0 0 16px;color:#DDA727;font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">{t}</p>'
    return f'''<div style="background:#0A2360;border-top:4px solid #DDA727;color:#ffffffcc;padding:56px 20px 0;font-size:15px;line-height:1.65;{FONT}">
<div style="max-width:1160px;margin:0 auto;display:flex;flex-wrap:wrap;gap:36px 48px;padding-bottom:40px;">
<div style="flex:1.4 1 280px;min-width:0;">
<div style="display:inline-block;background:#ffffff;border-radius:12px;padding:10px 16px;margin-bottom:18px;"><img src="{MAIN}/wp-content/uploads/2025/04/logo_aig.png" alt="Logo AIG" width="130" height="62" style="width:130px;height:auto;display:block;" /></div>
<p style="margin:0 0 14px;color:#ffffffcc;">Tập đoàn Nguyên liệu Á Châu (AIG) – tập đoàn hàng đầu Việt Nam trong lĩnh vực sản xuất nguyên liệu tự nhiên và cung ứng giải pháp nguyên liệu toàn diện cho lĩnh vực khoa học đời sống.</p>
<p style="margin:0;color:#DDA727;font-weight:700;">Your True Partner</p>
</div>
<div style="flex:1 1 180px;min-width:0;">
{h("Khám phá")}
{li(pre + "#gioi-thieu", "Về chúng tôi")}
{li(pre + "#giai-phap", "Giải pháp")}
{li(pre + "#cong-nghe", "Ứng dụng &amp; Đổi mới")}
{li(SITE + "/tin-tuc/", "Tin tức")}
{li(MAIN, "Website chính thức")}
</div>
<div style="flex:1.4 1 280px;min-width:0;">
{h("Liên hệ")}
<p style="margin:0 0 10px;"><strong style="color:#ffffff;">Trụ sở chính:</strong> Tòa nhà AIG – Lô TH-1B Đường số 7, Khu Thương mại Nam Khu Chế Xuất Tân Thuận, Phường Tân Thuận, TP HCM, Việt Nam</p>
<p style="margin:0 0 10px;"><strong style="color:#ffffff;">Điện thoại:</strong> <a href="tel:+842854111557" style="color:#ffffffcc;text-decoration:none;">+84 28 5411 1557</a></p>
<p style="margin:0;"><strong style="color:#ffffff;">Email:</strong> <a href="mailto:info@asiagroup-vn.com" style="color:#ffffffcc;text-decoration:none;">info@asiagroup-vn.com</a></p>
</div>
</div>
<div style="max-width:1160px;margin:0 auto;border-top:1px solid #ffffff26;padding:18px 0 22px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:14px;color:#ffffff99;">
<p style="margin:0;">© Tập đoàn Nguyên liệu Á Châu AIG · UPCoM: AIG</p>
<p style="margin:0;">Website chính thức: <a href="{MAIN}" style="color:#DDA727;text-decoration:none;">asiagroup-vn.com</a></p>
</div>
</div>
'''

def html_block(inner):
    return "<!-- wp:html -->\n" + inner + "<!-- /wp:html -->\n"

def full_group(inner):
    return ('<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->\n'
            '<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0">'
            + inner + '</div>\n<!-- /wp:group -->\n')

main_home = (D / "nguon/than-trang-chu.html").read_text(encoding="utf-8")

home_inner = f'<div style="{FONT}color:#0A2360;line-height:1.65;background:#ffffff;margin:0;">\n' + header(True) + main_home + footer(True) + "</div>\n"
(D / "MA-TRANG-CHU.txt").write_text(full_group(html_block(home_inner)), encoding="utf-8")

news_top = f'''<div style="background:#0A2360;color:#ffffff;padding:clamp(44px,7vw,80px) 20px;{FONT}">
<div style="max-width:1160px;margin:0 auto;">
<p style="margin:0 0 10px;color:#DDA727;font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Sự kiện</p>
<h1 style="margin:0 0 12px;color:#ffffff;font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">Tin tức AIG</h1>
<p style="margin:0;color:#ffffffd9;font-size:17px;max-width:640px;">Cập nhật hoạt động, sự kiện và câu chuyện phát triển của Tập đoàn Nguyên liệu Á&nbsp;Châu&nbsp;AIG.</p>
</div>
</div>
'''

news_query = '''<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"56px","bottom":"72px","left":"20px","right":"20px"}},"color":{"background":"#f5f6f9"}},"layout":{"type":"constrained","contentSize":"1160px"}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#f5f6f9;padding-top:56px;padding-right:20px;padding-bottom:72px;padding-left:20px"><!-- wp:query {"queryId":7,"query":{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query"><!-- wp:post-template {"style":{"spacing":{"blockGap":"28px"}},"layout":{"type":"grid","columnCount":4}} -->
<!-- wp:post-featured-image {"isLink":true,"aspectRatio":"16/9","style":{"border":{"radius":"14px"}}} /-->

<!-- wp:post-date {"style":{"color":{"text":"#DDA727"},"typography":{"fontSize":"14px","fontWeight":"700"},"spacing":{"margin":{"top":"14px"}}}} /-->

<!-- wp:post-title {"level":3,"isLink":true,"style":{"typography":{"fontSize":"20px","fontWeight":"800","lineHeight":"1.35"},"elements":{"link":{"color":{"text":"#0A2360"}}},"color":{"text":"#0A2360"},"spacing":{"margin":{"top":"6px","bottom":"8px"}}}} /-->

<!-- wp:post-excerpt {"moreText":"Đọc tiếp →","excerptLength":28,"style":{"color":{"text":"#0A2360c7"},"typography":{"fontSize":"15px"},"elements":{"link":{"color":{"text":"#DDA727"}}}}} /-->
<!-- /wp:post-template -->

<!-- wp:query-no-results -->
<!-- wp:paragraph -->
<p>Chưa có bài viết nào. Bài bạn đăng sẽ tự hiện ở đây.</p>
<!-- /wp:paragraph -->
<!-- /wp:query-no-results -->

<!-- wp:query-pagination {"paginationArrow":"arrow","layout":{"type":"flex","justifyContent":"center"}} -->
<!-- wp:query-pagination-previous {"label":"Trang trước"} /-->

<!-- wp:query-pagination-numbers /-->

<!-- wp:query-pagination-next {"label":"Trang sau"} /-->
<!-- /wp:query-pagination --></div>
<!-- /wp:query --></div>
<!-- /wp:group -->
'''
# Trang Tin tức: dán vào nội dung trang (đầu trang + danh sách bài + chân trang)
full_news = html_block(header(False) + news_top) + "\n" + news_query + "\n" + html_block(footer(False))
(D / "MA-TRANG-TIN-TUC.txt").write_text(full_group(full_news), encoding="utf-8")

prev = ('<!doctype html>\n<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Tập đoàn Nguyên liệu Á Châu AIG – Xem trước</title></head>\n<body style="margin:0;">\n' + home_inner + '</body></html>\n')
(D / "xem-truoc.html").write_text(prev, encoding="utf-8")
print("xong")
