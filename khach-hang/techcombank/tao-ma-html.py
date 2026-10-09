# Trang chủ + Tin tức Techcombank (web vệ tinh WordPress.com). Chạy: python3 tao-ma-html.py
# Màu lấy từ file logo gốc techcombank_logo_svg (fill #ec1c24 và #061922).
import pathlib
D = pathlib.Path(__file__).parent
M = "https://techcombank.com"
DAM = M + "/content/dam/techcombank/public-site/"
LOGO = DAM + "seo/techcombank_logo_svg_86201e50d1.svg"
IMG_HERO = DAM + "imported-assets/card-2-2856cb5f58-4aa44f7fac.png.rendition/cq5dam.web.1280.1280.webp"
IMG_APP = DAM + "imported-assets/card-3-850f67eade-a75c15204d.png.rendition/cq5dam.web.1280.1280.webp"
IMG_CN = DAM + "en/images/personal-banking/Chi-nhanh-Phong-giao-dich-Techcombank-toan-quoc-00490b3a25.jpg.rendition/cq5dam.web.1280.1280.webp"
R, K = "#EC1C24", "#061922"          # đỏ + xanh đen của logo
TXT, MUTED, LINE, SOFT = "#061922", "#061922b3", "#06192214", "#0619220a"
F = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"
EXT = ' target="_blank" rel="noopener"'

def header(home):
    pre = "" if home else "/"
    a = lambda h, t: f'<a href="{h}" style="color:{K};text-decoration:none;padding:4px 0;">{t}</a>'
    return f'''<div style="background:#ffffff;border-bottom:3px solid {R};padding:14px 20px;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="/" style="display:flex;align-items:center;text-decoration:none;"><img src="{LOGO}" alt="Logo Techcombank – Ngân hàng TMCP Kỹ thương Việt Nam" width="200" height="27" style="width:200px;height:auto;display:block;" /></a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:6px 24px;font-size:15px;font-weight:600;">
{a(pre + "#gioi-thieu", "Giới thiệu")}
{a(pre + "#khach-hang", "Khách hàng")}
{a(pre + "#san-pham", "Sản phẩm")}
{a("/tin-tuc/", "Tin tức")}
{a(pre + "#lien-he", "Liên hệ")}
<a href="{M}/"{EXT} style="background:{R};color:#ffffff;text-decoration:none;padding:9px 18px;border-radius:999px;">Website chính thức</a>
</div>
</div>
</div>
'''

def footer():
    h = lambda t: f'<p style="margin:0 0 14px;color:#ffffff;font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">{t}</p>'
    li = lambda u, t: f'<p style="margin:0 0 8px;"><a href="{M}{u}"{EXT} style="color:#ffffffbf;text-decoration:none;">{t}</a></p>'
    col = lambda title, items: '<div style="flex:1 1 170px;min-width:0;">\n' + h(title) + "\n" + "\n".join(li(u, t) for u, t in items) + "\n</div>"
    return f'''<div style="background:{K};border-top:4px solid {R};color:#ffffffbf;padding:52px 20px 0;font-size:15px;line-height:1.65;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:32px 44px;padding-bottom:36px;">
<div style="flex:1.6 1 300px;min-width:0;">
<div style="display:inline-block;background:#ffffff;border-radius:10px;padding:12px 16px;margin-bottom:18px;"><img src="{LOGO}" alt="Logo Techcombank" width="180" height="25" style="width:180px;height:auto;display:block;" /></div>
<p style="margin:0 0 12px;">Ngân hàng TMCP Kỹ thương Việt Nam. Đặt khách hàng là trọng tâm, Techcombank sẵn sàng cùng bạn nâng tầm giá trị sống vượt trội.</p>
<p style="margin:0 0 6px;"><strong style="color:#ffffff;">KH cá nhân:</strong> 1800 588 822 (miễn phí, 24/7)</p>
<p style="margin:0 0 6px;"><strong style="color:#ffffff;">KH doanh nghiệp:</strong> 1800 6556 (miễn phí)</p>
<p style="margin:0;"><strong style="color:#ffffff;">Email:</strong> <a href="mailto:call_center@techcombank.com.vn" style="color:#ffffffbf;text-decoration:none;">call_center@techcombank.com.vn</a></p>
</div>
{col("Khách hàng cá nhân", [("/khach-hang-ca-nhan/chi-tieu/the/the-tin-dung","Thẻ tín dụng"),("/khach-hang-ca-nhan/vay/vay-tieu-dung","Vay tiêu dùng"),("/khach-hang-ca-nhan/ngan-hang-truc-tuyen/ngan-hang-so/techcombank-mobile","Techcombank Mobile"),("/khach-hang-uu-tien","Khách hàng ưu tiên"),("/khach-hang-ca-nhan/uu-dai","Chương trình ưu đãi")])}
{col("Doanh nghiệp", [("/ho-kinh-doanh-va-doanh-nghiep-nho/ho-kinh-doanh","Hộ kinh doanh"),("/ho-kinh-doanh-va-doanh-nghiep-nho/doanh-nghiep-nho","Doanh nghiệp vừa và nhỏ"),("/khach-hang-doanh-nghiep","Doanh nghiệp lớn"),("/nha-dau-tu","Nhà đầu tư")])}
{col("Về chúng tôi", [("/ve-chung-toi/ve-techcombank","Về Techcombank"),("/ve-chung-toi/tin-tuc-va-bao-chi","Tin tức và báo chí"),("/ve-chung-toi/phat-trien-ben-vung","Phát triển bền vững"),("/cong-cu-tien-ich/ty-gia","Tỷ giá"),("/lien-he","Liên hệ")])}
</div>
<div style="max-width:1200px;margin:0 auto;border-top:1px solid #ffffff26;padding:18px 0 22px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:14px;color:#ffffff99;">
<p style="margin:0;">© 2026 Techcombank – Ngân hàng TMCP Kỹ thương Việt Nam</p>
<p style="margin:0;">Website chính thức: <a href="{M}/"{EXT} style="color:#ffffff;text-decoration:none;font-weight:700;border-bottom:2px solid {R};">techcombank.com</a></p>
</div>
</div>
'''

def eyebrow(t, center=False):
    c = "text-align:center;" if center else ""
    return f'<p style="margin:0 0 10px;color:{R};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;{c}">{t}</p>'
def h2(t, center=False, mb=36, color=K):
    c = "text-align:center;margin-left:auto;margin-right:auto;" if center else ""
    return f'<h2 style="margin:0 0 {mb}px;color:{color};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;max-width:760px;{c}">{t}</h2>'
def section(inner, bg="#ffffff", id_=""):
    i = f' id="{id_}"' if id_ else ""
    return f'<section{i} style="padding:clamp(56px,8vw,92px) 20px;background:{bg};">\n<div style="max-width:1200px;margin:0 auto;">\n{inner}\n</div>\n</section>\n'
def btn(href, t, bg=R, color="#ffffff"):
    return f'<a href="{href}"{EXT} style="display:inline-block;background:{bg};color:{color};text-decoration:none;font-weight:700;padding:13px 26px;border-radius:999px;">{t}</a>'

hero = f'''<section style="background:{K};color:#ffffff;padding:clamp(44px,7vw,84px) 20px;">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1 1 420px;min-width:0;">
<p style="display:inline-block;margin:0 0 18px;padding:6px 14px;border:1px solid {R};border-radius:999px;color:#ffffff;font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Ngân hàng TMCP Kỹ thương Việt Nam</p>
<h1 style="margin:0 0 18px;color:#ffffff;font-size:clamp(30px,4.6vw,50px);line-height:1.15;font-weight:800;">Techcombank – Vượt&nbsp;trội hơn mỗi&nbsp;<span style="color:{R};">ngày</span></h1>
<p style="margin:0 0 28px;font-size:clamp(16px,1.6vw,19px);color:#ffffffd9;max-width:560px;">Đặt khách hàng là trọng tâm, Techcombank sẵn sàng cùng bạn nâng tầm giá trị sống vượt trội. Khám phá ngay các dịch vụ từ ngân hàng số hàng đầu cho khách&nbsp;hàng.</p>
<div style="display:flex;flex-wrap:wrap;gap:12px;">
{btn(M + "/khach-hang-ca-nhan/chi-tieu/the/the-tin-dung", "Mở thẻ tín dụng")}
<a href="{M}/khach-hang-ca-nhan/ngan-hang-truc-tuyen/ngan-hang-so/techcombank-mobile"{EXT} style="border:1.5px solid #ffffff;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 26px;border-radius:999px;">Techcombank Mobile</a>
</div>
</div>
<div style="flex:1 1 440px;min-width:0;">
<img src="{IMG_HERO}" alt="Gia đình trải nghiệm dịch vụ ngân hàng số Techcombank" style="width:100%;height:auto;display:block;border-radius:16px;box-shadow:0 20px 50px #00000066;" />
</div>
</div>
</section>
'''

stat = lambda n, t, c: f'<div style="flex:1 1 200px;padding:24px 22px;border-bottom:1px solid {LINE};"><p style="margin:0;font-size:32px;font-weight:800;color:{c};line-height:1.1;">{n}</p><p style="margin:6px 0 0;font-size:14px;color:{MUTED};">{t}</p></div>'
stats = f'''<section style="background:#ffffff;padding:0 20px;">
<div style="max-width:1200px;margin:-36px auto 0;background:#ffffff;border-radius:16px;box-shadow:0 12px 36px #06192224;display:flex;flex-wrap:wrap;">
{stat("300","Chi nhánh, phòng giao dịch",R)}
{stat("34","Tỉnh thành có mặt",K)}
{stat("24/7","Tổng đài khách hàng cá nhân",R)}
{stat("1800 588 822","Hotline miễn phí",K)}
</div>
</section>
'''

seg = lambda title, text, u, accent: f'''<a href="{M}{u}"{EXT} style="flex:1 1 210px;min-width:0;display:block;text-decoration:none;background:#ffffff;border-radius:16px;padding:26px 22px;border-top:4px solid {accent};box-shadow:0 6px 20px #06192212;">
<h3 style="margin:0 0 10px;color:{K};font-size:20px;line-height:1.3;font-weight:800;">{title}</h3>
<p style="margin:0 0 14px;color:{MUTED};font-size:15px;">{text}</p>
<span style="color:{R};font-weight:700;font-size:15px;">Xem thêm →</span>
</a>'''
segments = section(f'''{eyebrow("Khách hàng", True)}
{h2("Chúng tôi sẵn sàng phục&nbsp;vụ", True, 12)}
<p style="margin:0 auto 36px;color:{MUTED};font-size:17px;text-align:center;max-width:720px;">Techcombank đồng hành với mọi phân khúc khách hàng để cùng người dân Việt Nam có một cuộc sống tài chính tốt đẹp&nbsp;hơn.</p>
<div style="display:flex;flex-wrap:wrap;gap:20px;">
{seg("Khách hàng cá nhân","Với Techcombank, mỗi khách hàng là một cá thể riêng biệt và đều được phục vụ bằng những sản phẩm được thiết kế dựa trên nhu cầu của mỗi khách hàng.","/khach-hang-ca-nhan",R)}
{seg("Doanh nghiệp vừa&nbsp;và&nbsp;nhỏ","Techcombank sẵn sàng mang đến những sản phẩm đa dạng, quy trình đơn giản với mục đích mang lại những lợi ích tối ưu cho những doanh nghiệp vừa và nhỏ.","/ho-kinh-doanh-va-doanh-nghiep-nho",K)}
{seg("Doanh nghiệp lớn","Cùng đội ngũ chuyên gia tài chính uy tín, Techcombank mang đến những giải pháp tài chính toàn diện, được thiết kế riêng cho những doanh nghiệp lớn.","/khach-hang-doanh-nghiep",R)}
{seg("Nhà đầu tư","Techcombank cam kết mang lại những lợi ích lâu dài để đáp lại niềm tin tưởng của những nhà đầu tư.","/nha-dau-tu",K)}
</div>''', bg=SOFT, id_="khach-hang")

prod = lambda title, text, u: f'''<a href="{M}{u}"{EXT} style="flex:1 1 300px;min-width:0;display:flex;flex-direction:column;gap:10px;text-decoration:none;background:#ffffff;border:1px solid {LINE};border-left:4px solid {R};border-radius:14px;padding:24px 24px;">
<h3 style="margin:0;color:{K};font-size:19px;line-height:1.3;font-weight:800;">{title}</h3>
<p style="margin:0;color:{MUTED};font-size:15px;flex:1 1 auto;">{text}</p>
<span style="color:{R};font-weight:700;font-size:15px;">Tìm hiểu →</span>
</a>'''
products = section(f'''{eyebrow("Sản phẩm & dịch vụ", True)}
{h2("Giải pháp tài chính cho mọi nhu&nbsp;cầu", True)}
<div style="display:flex;flex-wrap:wrap;gap:20px;">
{prod("Thẻ tín dụng","Tận hưởng ưu đãi hấp dẫn, chi tiêu trước trả sau linh hoạt và quản lý tài chính cá nhân dễ dàng với nhiều tiện ích vượt trội.","/khach-hang-ca-nhan/chi-tieu/the/the-tin-dung")}
{prod("Vay tiêu dùng","Giải ngân nhanh, đáp ứng mọi nhu cầu chi tiêu với nhiều gói vay đa dạng: du lịch, mua sắm, thanh toán hoá đơn, xây/sửa nhà...","/khach-hang-ca-nhan/vay/vay-tieu-dung")}
{prod("Techcombank Mobile","Ngân hàng số với các tính năng thông minh, bảo mật cao, giúp bạn thanh toán, chuyển khoản và quản lý tài chính dễ dàng hơn bao giờ hết.","/khach-hang-ca-nhan/ngan-hang-truc-tuyen/ngan-hang-so/techcombank-mobile")}
{prod("Techcombank Priority","Dịch vụ dành riêng cho Khách hàng Ưu tiên, tận hưởng phong cách sống đẳng cấp và các giải pháp tài chính được thiết kế riêng biệt.","/khach-hang-uu-tien")}
{prod("Hộ kinh doanh","Vay vốn linh hoạt lãi suất ưu đãi, thu hộ tiện lợi và ưu đãi đặc quyền giúp hộ kinh doanh quản lý dòng tiền hiệu quả.","/ho-kinh-doanh-va-doanh-nghiep-nho/ho-kinh-doanh")}
{prod("Chương trình ưu đãi","Tận hưởng trải nghiệm mua sắm với vô vàn ưu đãi, quà tặng và khuyến mãi hàng đầu dành riêng cho khách hàng cá nhân.","/khach-hang-ca-nhan/uu-dai")}
</div>''', id_="san-pham")

app = section(f'''<div style="display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1 1 380px;min-width:0;">
{eyebrow("Ngân hàng số")}
{h2("Techcombank Mobile – ngân hàng trong tầm&nbsp;tay", False, 18, "#ffffff")}
<p style="margin:0 0 26px;color:#ffffffd9;font-size:17px;">Trải nghiệm ngân hàng số Techcombank Mobile với các tính năng thông minh, bảo mật cao, giúp bạn thanh toán, chuyển khoản và quản lý tài chính dễ dàng hơn bao giờ&nbsp;hết.</p>
{btn(M + "/khach-hang-ca-nhan/ngan-hang-truc-tuyen/ngan-hang-so/techcombank-mobile", "Khám phá Techcombank Mobile")}
</div>
<div style="flex:1 1 420px;min-width:0;">
<img src="{IMG_APP}" alt="Tải ứng dụng Techcombank Mobile" style="width:100%;height:auto;display:block;border-radius:16px;" />
</div>
</div>''', bg=K)

pl = lambda city, name, addr: f'''<div style="flex:1 1 240px;min-width:0;padding:4px 4px 4px 18px;border-left:3px solid {R};">
<p style="margin:0 0 4px;color:{R};font-size:13px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;">{city}</p>
<h3 style="margin:0 0 6px;color:{K};font-size:18px;font-weight:800;">{name}</h3>
<p style="margin:0;color:{MUTED};font-size:15px;">{addr}</p>
</div>'''
about = section(f'''<div style="display:flex;flex-wrap:wrap;gap:40px;align-items:center;">
<div style="flex:1 1 380px;min-width:0;">
<img src="{IMG_CN}" alt="Chi nhánh, phòng giao dịch Techcombank trên toàn quốc" style="width:100%;height:auto;display:block;border-radius:16px;" />
</div>
<div style="flex:1.2 1 420px;min-width:0;">
{eyebrow("Về Techcombank")}
{h2("Mạng lưới rộng&nbsp;khắp", False, 14)}
<p style="margin:0 0 26px;color:{MUTED};font-size:17px;">Hơn 300 chi nhánh, phòng giao dịch có mặt tại 34 tỉnh thành trên cả nước. Tầm nhìn kiên định của Ngân hàng là dài hạn, đảm bảo lợi ích cho cổ đông và sự phát triển bền vững cho tổ&nbsp;chức.</p>
<div style="display:flex;flex-wrap:wrap;gap:22px;margin-bottom:28px;">
{pl("Hà Nội","Hội sở chính","06 Phố Quang Trung, Phường Cửa Nam")}
{pl("Hà Nội","Trụ sở vận hành","119 Trần Duy Hưng, phường Yên Hòa")}
{pl("TP. Hồ Chí Minh","Hội sở chính","23 Lê Duẩn, phường Sài Gòn")}
</div>
{btn(M + "/ve-chung-toi/ve-techcombank", "Xem thêm về Techcombank", K)}
</div>
</div>''', id_="gioi-thieu")

box = lambda title, lines: f'<div style="flex:1 1 260px;min-width:0;background:#ffffff;border-radius:14px;padding:22px 24px;color:{K};font-size:15px;"><p style="margin:0 0 10px;color:{R};font-weight:800;">{title}</p>{lines}</div>'
contact = f'''<section id="lien-he" style="padding:0 20px clamp(56px,8vw,92px);background:#ffffff;">
<div style="max-width:1200px;margin:0 auto;background:{K};border-radius:20px;padding:clamp(32px,5vw,56px);">
<div style="display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start;">
<div style="flex:1.2 1 320px;min-width:0;">
{h2("Techcombank sẵn sàng hỗ&nbsp;trợ", False, 14, "#ffffff")}
<p style="margin:0 0 22px;color:#ffffffd9;font-size:17px;">Để được hỗ trợ nhanh nhất, bạn có thể gọi tổng đài, gửi email hoặc đặt lịch hẹn trước tại chi nhánh để không phải chờ&nbsp;đợi.</p>
{btn(M + "/lien-he", "Liên hệ Techcombank")}
</div>
{box("Khách hàng cá nhân & hộ kinh doanh", f'<p style="margin:0 0 6px;"><strong>Tổng đài 24/7:</strong> <a href="tel:1800588822" style="color:{K};text-decoration:none;">1800 588 822</a> (miễn phí)</p><p style="margin:0 0 6px;"><strong>Quốc tế:</strong> +84 24 3944 6699</p><p style="margin:0;"><strong>Email:</strong> <a href="mailto:call_center@techcombank.com.vn" style="color:{K};text-decoration:none;">call_center@techcombank.com.vn</a></p>')}
{box("Khách hàng doanh nghiệp", f'<p style="margin:0 0 6px;"><strong>Tổng đài:</strong> <a href="tel:18006556" style="color:{K};text-decoration:none;">1800 6556</a> (miễn phí)</p><p style="margin:0 0 6px;"><strong>Quốc tế:</strong> +84 24 7303 6556</p><p style="margin:0;"><strong>Email:</strong> <a href="mailto:hotrodoanhnghiep@techcombank.com.vn" style="color:{K};text-decoration:none;">hotrodoanhnghiep@techcombank.com.vn</a></p>')}
</div>
</div>
</section>
'''

def html_block(x): return "<!-- wp:html -->\n" + x + "<!-- /wp:html -->\n"
def full_group(x):
    return ('<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->\n'
            '<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0">' + x + '</div>\n<!-- /wp:group -->\n')

home_inner = f'<div style="{F}color:{TXT};line-height:1.65;background:#ffffff;margin:0;">\n' + header(True) + hero + stats + segments + products + app + about + contact + footer() + "</div>\n"
(D / "HTML-TRANG-CHU.txt").write_text(full_group(html_block(home_inner)), encoding="utf-8")

news_top = f'''<div style="background:{K};color:#ffffff;padding:clamp(44px,7vw,80px) 20px;{F}">
<div style="max-width:1200px;margin:0 auto;">
<p style="margin:0 0 10px;color:{R};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Chia sẻ</p>
<h1 style="margin:0 0 12px;color:#ffffff;font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">Tin tức Techcombank</h1>
<p style="margin:0;color:#ffffffd9;font-size:17px;max-width:660px;">Cập nhật tin tức thị trường, khám phá xu hướng tài chính, trải nghiệm sản phẩm dịch vụ và tận hưởng phong cách sống hiện&nbsp;đại.</p>
</div>
</div>
'''
news_query = f'''<!-- wp:group {{"align":"full","style":{{"spacing":{{"padding":{{"top":"56px","bottom":"72px","left":"20px","right":"20px"}}}},"color":{{"background":"#f5f6f6"}}}},"layout":{{"type":"constrained","contentSize":"1200px"}}}} -->
<div class="wp-block-group alignfull has-background" style="background-color:#f5f6f6;padding-top:56px;padding-right:20px;padding-bottom:72px;padding-left:20px"><!-- wp:query {{"queryId":7,"query":{{"perPage":20,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}}}} -->
<div class="wp-block-query"><!-- wp:post-template {{"style":{{"spacing":{{"blockGap":"28px"}}}},"layout":{{"type":"grid","columnCount":4}}}} -->
<!-- wp:post-featured-image {{"isLink":true,"aspectRatio":"16/9","style":{{"border":{{"radius":"14px"}}}}}} /-->

<!-- wp:post-date {{"style":{{"color":{{"text":"{R}"}},"typography":{{"fontSize":"14px","fontWeight":"700"}},"spacing":{{"margin":{{"top":"14px"}}}}}}}} /-->

<!-- wp:post-title {{"level":3,"isLink":true,"style":{{"typography":{{"fontSize":"20px","fontWeight":"800","lineHeight":"1.35"}},"elements":{{"link":{{"color":{{"text":"{K}"}}}}}},"color":{{"text":"{K}"}},"spacing":{{"margin":{{"top":"6px","bottom":"8px"}}}}}}}} /-->

<!-- wp:post-excerpt {{"moreText":"Đọc tiếp →","excerptLength":28,"style":{{"typography":{{"fontSize":"15px"}},"elements":{{"link":{{"color":{{"text":"{R}"}}}}}}}}}} /-->
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
(D / "xem-truoc-trang-chu.html").write_text('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Techcombank – Xem trước</title></head><body style="margin:0;">' + home_inner + "</body></html>", encoding="utf-8")
print("xong")
