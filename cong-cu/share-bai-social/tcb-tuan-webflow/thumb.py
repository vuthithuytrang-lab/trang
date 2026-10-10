#!/usr/bin/env python3
"""Tạo ảnh bìa 1200x675 cho bài Wix từ meta.json (trường 'thumb').
Usage: thumb.py <row> <out.png>   — dùng Chromium có sẵn, không thư viện ngoài."""
import html, json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
# 5 bộ màu xoay vòng theo row để các ảnh không giống hệt nhau
THEMES = [('#0B2545', '#13315C', '#8DA9C4'), ('#1B4332', '#2D6A4F', '#95D5B2'), ('#3C096C', '#5A189A', '#C77DFF'),
          ('#7F4F24', '#936639', '#E6CCB2'), ('#023E8A', '#0077B6', '#90E0EF')]

def main(row, out):
    meta = json.load(open(os.path.join(HERE, 'bai', str(row), 'meta.json'), encoding='utf-8'))
    a, b, c = THEMES[(int(row) // 11 + 2) % len(THEMES)]
    page = f'''<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:675px;overflow:hidden}}
body{{background:linear-gradient(135deg,{a} 0%,{b} 100%);font-family:"Inter","Noto Sans",sans-serif;color:#fff;position:relative}}
.k{{position:absolute;left:80px;top:70px;font-size:26px;letter-spacing:3px;text-transform:uppercase;color:{c};font-weight:700}}
.t{{position:absolute;left:80px;right:80px;top:150px;font-size:72px;line-height:1.18;font-weight:800}}
.bar{{position:absolute;left:80px;bottom:90px;width:140px;height:10px;background:{c};border-radius:5px}}
.d{{position:absolute;left:80px;bottom:40px;font-size:24px;color:#ffffffcc}}
.o{{position:absolute;right:-140px;top:-140px;width:520px;height:520px;border-radius:50%;border:60px solid #ffffff14}}
</style><div class="o"></div><div class="k">Kiến thức tài chính doanh nghiệp</div>
<div class="t">{html.escape(meta['thumb'])}</div><div class="bar"></div><div class="d">Tổng hợp &amp; hướng dẫn thực tế</div>'''
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f: f.write(page)
    subprocess.run([CHROME, '--headless=new', '--no-sandbox', '--hide-scrollbars', f'--screenshot={out}', '--window-size=1200,800', 'file://' + f.name],
                   capture_output=True)
    os.unlink(f.name)
    if not os.path.exists(out): sys.exit('khong tao duoc anh')
    from PIL import Image  # cửa sổ headless hụt ~90px nên chụp dư rồi cắt đúng 1200x675
    Image.open(out).crop((0, 0, 1200, 675)).save(out)

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
