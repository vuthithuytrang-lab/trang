# Trang chủ + Tin tức VIB dạng HTML tự thiết kế (giống cách làm AIG). Chạy: python3 tao-ma-html.py
import pathlib
D = pathlib.Path(__file__).parent
SITE = "https://nganhangquoctevib.wordpress.com"
UP = SITE + "/wp-content/uploads/2026/09/"
M = "https://www.vib.com.vn"
B, O, Y = "#005BAA", "#F27C24", "#F9B812"
F = "font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif;"
EXT = ' target="_blank" rel="noopener"'

def header(home):
    pre = "" if home else SITE + "/"
    a = lambda h, t, e="": f'<a href="{h}"{e} style="color:{B};text-decoration:none;padding:4px 0;">{t}</a>'
    return f'''<div style="background:#ffffff;border-bottom:3px solid {O};padding:12px 20px;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 28px;">
<a href="{SITE}/" style="display:flex;align-items:center;gap:12px;text-decoration:none;"><img src="{UP}cropped-avatar-vib.jpg?w=96" alt="Logo VIB – Ngân hàng TMCP Quốc Tế Việt Nam" width="46" height="46" style="width:46px;height:46px;border-radius:10px;display:block;" /><span style="color:{B};font-size:18px;font-weight:800;line-height:1.2;">Ngân hàng Quốc tế VIB</span></a>
<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:6px 24px;font-size:15px;font-weight:600;">
{a(pre + "#gioi-thieu", "Giới thiệu")}
{a(pre + "#the-tin-dung", "Thẻ tín dụng")}
{a(pre + "#dich-vu", "Dịch vụ")}
{a(pre + "#uu-dai", "Ưu đãi")}
{a(SITE + "/tin-tuc/", "Tin tức")}
<a href="{M}/"{EXT} style="background:{B};color:#ffffff;text-decoration:none;padding:9px 18px;border-radius:999px;">Website chính thức</a>
</div>
</div>
</div>
'''

def footer():
    h = lambda t: f'<p style="margin:0 0 14px;color:{Y};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">{t}</p>'
    li = lambda href, t: f'<p style="margin:0 0 8px;"><a href="{href}"{EXT} style="color:#ffffffcc;text-decoration:none;">{t}</a></p>'
    col = lambda title, items: '<div style="flex:1 1 160px;min-width:0;">\n' + h(title) + "\n" + "\n".join(li(M + u, t) for u, t in items) + "\n</div>"
    return f'''<div style="background:{B};border-top:4px solid {O};color:#ffffffcc;padding:52px 20px 0;font-size:15px;line-height:1.65;{F}">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;gap:32px 44px;padding-bottom:36px;">
<div style="flex:1.6 1 300px;min-width:0;">
<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><img src="{UP}cropped-avatar-vib.jpg?w=96" alt="Logo VIB" width="48" height="48" style="width:48px;height:48px;border-radius:10px;border:2px solid #ffffff;display:block;" /><p style="margin:0;color:#ffffff;font-weight:800;font-size:17px;line-height:1.3;">Ngân hàng TMCP Quốc Tế Việt Nam (VIB)</p></div>
<p style="margin:0 0 10px;"><strong style="color:#ffffff;">Hội sở chính:</strong> Tầng 1 (tầng trệt) và tầng 2 Tòa nhà Sailing Tower, 111A Pasteur, P. Sài Gòn, TP.HCM (trước là P. Bến Nghé, Q.1, TP.HCM)</p>
<p style="margin:0 0 10px;"><strong style="color:#ffffff;">Hỗ trợ tại quầy:</strong> Thứ 2 đến Thứ 6 (08:00 – 12:00 &amp; 13:00 – 17:00), Thứ 7 (08:00 – 12:00)</p>
<p style="margin:0;"><strong style="color:#ffffff;">Liên hệ:</strong> Tổng đài 1900 2200 (1.000 đ/phút) · <a href="mailto:dvkh247@vib.com.vn" style="color:#ffffffcc;text-decoration:none;">dvkh247@vib.com.vn</a></p>
</div>
{col("Sản phẩm", [("/vn/the-tin-dung","Thẻ tín dụng"),("/vn/tai-khoan","Tài khoản"),("/vn/tiet-kiem","Tiết kiệm"),("/vn/san-pham-vay","Vay"),("/vn/bao-hiem","Bảo hiểm"),("/vn/ngan-hang-so/myvib","Ngân hàng số MyVIB")])}
{col("Về VIB", [("/vn/about-vib","Về chúng tôi"),("/vn/nha-dau-tu","Nhà đầu tư"),("/vn/tuyen-dung","Tuyển dụng"),("/vn/news","Tin tức"),("/vn/promotion","Ưu đãi")])}
{col("Hỗ trợ", [("/vn/lien-he","Liên hệ"),("/vn/atm-chinhanh","ATM &amp; Chi nhánh"),("/vn/ty-gia","Tỷ giá"),("/vn/dieu-khoan-su-dung","Điều khoản sử dụng"),("/vn/an-toan-bao-mat","An toàn bảo mật")])}
</div>
<div style="max-width:1200px;margin:0 auto;border-top:1px solid #ffffff33;padding:18px 0 22px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 24px;font-size:14px;color:#ffffffb3;">
<p style="margin:0;">Website chính thức của VIB: <a href="{M}/"{EXT} style="color:{Y};text-decoration:none;">www.vib.com.vn</a> · Tổng đài 1900 2200</p>
<p style="margin:0;"><a href="https://www.facebook.com/VIB.NHQT"{EXT} style="color:#ffffffcc;text-decoration:none;">Facebook</a> · <a href="https://www.linkedin.com/company/vietnam-international-bank/"{EXT} style="color:#ffffffcc;text-decoration:none;">LinkedIn</a> · <a href="https://www.youtube.com/channel/UCGs80MaxY_sKvgiWLOmjEbQ"{EXT} style="color:#ffffffcc;text-decoration:none;">YouTube</a></p>
</div>
</div>
'''

def eyebrow(t, center=False):
    c = "text-align:center;" if center else ""
    return f'<p style="margin:0 0 10px;color:{O};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;{c}">{t}</p>'
def h2(t, center=False, color=B):
    c = "text-align:center;margin-left:auto;margin-right:auto;" if center else ""
    return f'<h2 style="margin:0 0 36px;color:{color};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;max-width:760px;{c}">{t}</h2>'
def section(inner, bg="#ffffff", id_=""):
    i = f' id="{id_}"' if id_ else ""
    return f'<section{i} style="padding:clamp(56px,8vw,92px) 20px;background:{bg};">\n<div style="max-width:1200px;margin:0 auto;">\n{inner}\n</div>\n</section>\n'
def btn(href, t, bg=O, color="#ffffff"):
    return f'<a href="{href}"{EXT} style="display:inline-block;background:{bg};color:{color};text-decoration:none;font-weight:700;padding:13px 26px;border-radius:999px;">{t}</a>'

hero = f'''<section style="background:{B};color:#ffffff;padding:clamp(44px,7vw,84px) 20px;">
<div style="max-width:1200px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;gap:40px;">
<div style="flex:1 1 420px;min-width:0;">
<p style="display:inline-block;margin:0 0 18px;padding:6px 14px;border:1px solid {Y};border-radius:999px;color:{Y};font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;">Thành lập từ 1996</p>
<h1 style="margin:0 0 18px;color:#ffffff;font-size:clamp(30px,4.6vw,50px);line-height:1.15;font-weight:800;">Ngân hàng Quốc tế <span style="color:{Y};">VIB</span></h1>
<p style="margin:0 0 28px;font-size:clamp(16px,1.6vw,19px);color:#ffffffe6;max-width:560px;">VIB là Ngân hàng Thương mại Cổ phần Quốc tế hàng đầu Việt Nam, đi đầu trong lĩnh vực thẻ tín dụng và ngân hàng&nbsp;số.</p>
<div style="display:flex;flex-wrap:wrap;gap:12px;">
{btn(M + "/vn/the-tin-dung", "Khám phá thẻ tín dụng")}
<a href="{M}/vn/ngan-hang-so/myvib"{EXT} style="border:1.5px solid #ffffff;color:#ffffff;text-decoration:none;font-weight:700;padding:12px 26px;border-radius:999px;">Tải MyVIB</a>
</div>
</div>
<div style="flex:1 1 440px;min-width:0;">
<img src="{UP}banner-vib.jpg?w=960" alt="VIB – Ngân hàng Thương mại Cổ phần Quốc tế Việt Nam" style="width:100%;height:auto;display:block;border-radius:16px;box-shadow:0 20px 50px #00000059;" />
</div>
</div>
</section>
'''

stat = lambda n, t, c: f'<div style="flex:1 1 170px;padding:24px 22px;border-bottom:1px solid #005BAA14;"><p style="margin:0;font-size:32px;font-weight:800;color:{c};line-height:1.1;">{n}</p><p style="margin:6px 0 0;font-size:14px;color:#4a5568;">{t}</p></div>'
stats = f'''<section style="background:#ffffff;padding:0 20px;">
<div style="max-width:1200px;margin:-36px auto 0;background:#ffffff;border-radius:16px;box-shadow:0 12px 36px #005BAA24;display:flex;flex-wrap:wrap;">
{stat("1996","Năm thành lập",B)}
{stat("34.000+ tỷ","Vốn điều lệ",O)}
{stat("202","Điểm giao dịch",B)}
{stat("33","Tỉnh, thành phố",O)}
{stat("10.000+","Nhân viên",B)}
</div>
</section>
'''

P = 'style="margin:0 0 16px;color:#2d3748;font-size:17px;"'
about = section(f'''<div style="display:flex;flex-wrap:wrap;gap:40px;align-items:flex-start;">
<div style="flex:1 1 300px;min-width:0;">
{eyebrow("Giới thiệu")}
<h2 style="margin:0 0 24px;color:{B};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;">Ngân hàng TMCP Quốc Tế Việt&nbsp;Nam</h2>
{btn(M + "/", "Tìm hiểu thêm", B)}
</div>
<div style="flex:1.6 1 420px;min-width:0;">
<p {P}><strong>Ngân hàng Thương mại Cổ phần Quốc tế Việt Nam (VIB)</strong> được thành lập từ năm 1996, là một trong những ngân hàng thương mại tư nhân có vị thế vững chắc và uy tín hàng đầu trong hệ thống tài chính Việt Nam. Trải qua hành trình phát triển mạnh mẽ, VIB luôn kiên trì với <strong>mục tiêu chuyển đổi số toàn diện</strong> và <strong>lấy khách hàng làm trọng tâm</strong> để xây dựng các giải pháp tài chính thông minh, hiệu quả.</p>
<p style="margin:0;color:#2d3748;font-size:17px;">Tại VIB, chúng tôi khẳng định vị thế dẫn đầu xu hướng thị trường thông qua các sản phẩm bán lẻ mũi nhọn. VIB là <strong>một trong những ngân hàng dẫn đầu thị trường thẻ tín dụng tại Việt Nam</strong>, tự hào mang đến các dòng thẻ tín dụng dẫn đầu xu hướng như <strong>Max Card, VIB Family Link, VIB IvyLink</strong>, đáp ứng đa dạng nhu cầu từ mua sắm trực tuyến đến chi tiêu gia đình với mức hoàn tiền và ưu đãi hấp dẫn. Bên cạnh đó, hệ sinh thái <strong>ngân hàng số MyVIB ứng dụng công nghệ Big Data và Trí tuệ nhân tạo (AI)</strong> liên tục nhận được nhiều giải thưởng quốc tế lớn, mang đến trải nghiệm giao dịch an toàn, bảo mật và mượt mà cho hàng triệu người dùng.</p>
</div>
</div>''', id_="gioi-thieu")

qr = lambda img, alt, href, t: f'''<div style="flex:1 1 260px;min-width:0;max-width:380px;background:#ffffff;border-radius:16px;padding:28px;text-align:center;box-shadow:0 6px 20px #005BAA14;">
<img src="{UP}{img}?w=400" alt="{alt}" width="220" height="220" style="width:220px;max-width:100%;height:auto;display:block;margin:0 auto 16px;" />
{btn(href, t, B)}
</div>'''
eco = section(f'''{eyebrow("Hệ sinh thái số VIB", True)}
<h2 style="margin:0 auto 10px;color:{B};font-size:clamp(26px,3.4vw,38px);line-height:1.2;font-weight:800;text-align:center;">Quét mã để tải ứng dụng</h2>
<p style="margin:0 auto 36px;color:#4a5568;font-size:17px;text-align:center;">Giao dịch an toàn, bảo mật và mượt mà ngay trên điện thoại.</p>
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:24px;">
{qr("1-2.webp","Mã QR tải ứng dụng ngân hàng số MyVIB",M+"/vn/ngan-hang-so/myvib","Tải ngân hàng số MyVIB")}
{qr("2-1.webp","Mã QR tải ứng dụng MAX của VIB",M+"/i/max-app","Tải ứng dụng MAX")}
</div>''', bg="#f5f8fc")

card = lambda img, name, href: f'''<a href="{href}"{EXT} style="flex:1 1 280px;min-width:0;display:block;text-decoration:none;background:#ffffff;border:1px solid #005BAA1f;border-radius:16px;padding:24px;text-align:center;box-shadow:0 6px 20px #005BAA12;">
<img src="{UP}{img}?w=400" alt="Thẻ tín dụng {name}" style="width:100%;height:auto;aspect-ratio:16/10;object-fit:contain;display:block;margin:0 0 16px;" />
<h3 style="margin:0;color:{B};font-size:20px;font-weight:800;">{name} <span style="color:{O};">→</span></h3>
</a>'''
cards = section(f'''{eyebrow("Thế giới thẻ VIB", True)}
{h2("Thẻ tín dụng dẫn đầu xu&nbsp;hướng", True)}
<div style="display:flex;flex-wrap:wrap;gap:24px;">
{card("image-1.png","VIB Family Link",M+"/vn/the-tin-dung/vib-family-link")}
{card("image-2.png","VIB One Card",M+"/vn/the-tin-dung/vib-one-card")}
{card("image-3.png","VIB Business Card",M+"/vn/the-tin-dung/vib-business-card")}
</div>''', id_="the-tin-dung")

svc = [("/vn/the-tin-dung","Thẻ tín dụng"),("/vn/the-thanh-toan","Thẻ thanh toán"),("/vn/tai-khoan-sieu-loi-suat","Tài khoản siêu lợi suất"),("/vn/tiet-kiem","Tiền gửi có kỳ hạn"),("/vn/super-cash","Tài khoản vay siêu linh hoạt"),("/vn/ngan-hang-so/myvib","Ngân hàng số"),("/vn/vay-tieu-dung","Vay tiêu dùng"),("/vn/vay-mua-nha","Vay bất động sản"),("/vn/vay-mua-xe","Vay mua xe"),("/vn/tai-khoan","Tài khoản thanh toán"),("/vn/bao-hiem","Bảo hiểm"),("/vn/nguon-von-va-ngoai-hoi","Ngoại hối")]
pill = lambda u, t: f'<a href="{M}{u}"{EXT} style="flex:1 1 230px;min-width:0;display:flex;justify-content:space-between;align-items:center;gap:10px;background:#ffffff;border:1px solid #005BAA29;border-left:4px solid {O};border-radius:12px;padding:16px 20px;color:{B};font-weight:700;text-decoration:none;">{t}<span style="color:{O};">→</span></a>'
services = section(f'''{eyebrow("Dịch vụ", True)}
{h2("Dịch vụ của chúng&nbsp;tôi", True)}
<div style="display:flex;flex-wrap:wrap;gap:14px;">
{chr(10).join(pill(u,t) for u,t in svc)}
</div>''', bg="#f5f8fc", id_="dich-vu")

promo = lambda img, alt, text, href, cta: f'''<div style="flex:1 1 300px;min-width:0;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 6px 20px #005BAA14;display:flex;flex-direction:column;">
<img src="{UP}{img}?w=700" alt="{alt}" style="width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;display:block;" />
<div style="padding:22px 22px 24px;display:flex;flex-direction:column;gap:16px;flex:1 1 auto;">
<p style="margin:0;color:#2d3748;font-size:16px;flex:1 1 auto;">{text}</p>
<a href="{href}"{EXT} style="display:block;text-align:center;background:{O};color:#ffffff;text-decoration:none;font-weight:800;padding:13px 18px;border-radius:999px;">{cta}</a>
</div>
</div>'''
promos = section(f'''{eyebrow("Ưu đãi", True)}
{h2("Ưu đãi nổi&nbsp;bật", True)}
<div style="display:flex;flex-wrap:wrap;gap:24px;">
{promo("3-1.webp","Ưu đãi mời bạn kích hoạt Tài khoản Siêu Lợi Suất trên MyVIB","Khi mời bạn mới kích hoạt Tài khoản Siêu Lợi Suất trên MyVIB",M+"/vn/promotion/detail?promotionId=4398667&amp;name=Nhan-thuong-khi-moi-ban-moi-kich-hoat-tinh-nang-Tai-khoan-Sieu-Loi-Suat-tren-MyVIB","Nhận đến 100.000 VNĐ/lượt")}
{promo("4.webp","Gói giải pháp nâng hạng tài chính VIB Up","Cùng gói giải pháp nâng hạng tài chính VIB Up",M+"/vn/promotion/details/goi-vib-up-giai-phap-chon-goi-nang-hang-tai-chinh-nhan-tong-quyen-loi-hon-610-trieu","Nhận quyền lợi hơn 610 triệu")}
{promo("5.webp","Ưu đãi giảm 20% khi mua sắm trên Shopee bằng thẻ tín dụng VIB","Khi mua sắm trên Shopee bằng thẻ tín dụng VIB",M+"/vn/promotion/details/giam-20-phan-tram-khi-mua-sam-tren-shopee-2026-bang-the-tin-dung-vib","Giảm 20%")}
</div>''', id_="uu-dai")

def html_block(x): return "<!-- wp:html -->\n" + x + "<!-- /wp:html -->\n"
def full_group(x):
    return ('<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"0","bottom":"0","left":"0","right":"0"},"blockGap":"0"}},"layout":{"type":"default"}} -->\n'
            '<div class="wp-block-group alignfull" style="padding-top:0;padding-right:0;padding-bottom:0;padding-left:0">' + x + '</div>\n<!-- /wp:group -->\n')

home_inner = f'<div style="{F}color:#1a202c;line-height:1.65;background:#ffffff;margin:0;">\n' + header(True) + hero + stats + about + eco + cards + services + promos + footer() + "</div>\n"
(D / "HTML-TRANG-CHU.txt").write_text(full_group(html_block(home_inner)), encoding="utf-8")

news_top = f'''<div style="background:{B};color:#ffffff;padding:clamp(44px,7vw,80px) 20px;{F}">
<div style="max-width:1200px;margin:0 auto;">
<p style="margin:0 0 10px;color:{Y};font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;">Tin tức &amp; Ưu đãi</p>
<h1 style="margin:0 0 12px;color:#ffffff;font-size:clamp(30px,4.4vw,46px);line-height:1.15;font-weight:800;">Tin tức VIB</h1>
<p style="margin:0;color:#ffffffd9;font-size:17px;max-width:640px;">Cập nhật tin tức, ưu đãi và kiến thức tài chính từ Ngân hàng Thương mại Cổ phần Quốc tế Việt&nbsp;Nam&nbsp;(VIB).</p>
</div>
</div>
'''
query = (D / "C-NOI-DUNG-TRANG-TIN-TUC.txt").read_text(encoding="utf-8")
q0 = query.index('<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"56px"')
q1 = query.index("<!-- /wp:group --></div>\n<!-- /wp:group -->") + len("<!-- /wp:group -->")
news_query = query[q0:q1] + "\n"
news = html_block(header(False) + news_top) + "\n" + news_query + "\n" + html_block(footer())
(D / "HTML-TRANG-TIN-TUC.txt").write_text(full_group(news), encoding="utf-8")

(D / "xem-truoc-trang-chu.html").write_text('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VIB – Xem trước</title></head><body style="margin:0;">' + home_inner + "</body></html>", encoding="utf-8")
print("xong")
