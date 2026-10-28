#!/usr/bin/env python3
"""Tạo danh-sach.json + lich.json cho đợt GP 28/10. Chạy lại sẽ ghi đè lịch (chỉ chạy trước khi đăng)."""
import json, os, random
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
VN = timezone(timedelta(hours=7))
random.seed(2810)

URLS = """https://topkinhdoanh.net/ban-lai-ngoai-te-con-du/
https://tophaiphongaz.com/lap-du-toan-chi-phi-cho-chuyen-du-lich-nuoc-ngoai-theo-tien-viet/
https://tophaiphongaz.com/cach-hinh-thanh-so-tien-viet-thuc-tra-khi-thanh-toan-the-bang-ngoai-te/
https://bentretoplist.com/nhung-thong-tin-tren-bang-ty-gia-ngan-hang-khi-doi-ngoai-te-lan-dau/
https://megacar.vn/tin-tuc/chuan-bi-thanh-toan-hoc-phi-khoa-hoc-truc-tuyen-dinh-gia-bang-do-la-my
https://tophaiduongaz.com/quan-ly-cac-khoan-thue-bao-dich-vu-so-tra-bang-ngoai-te-trong-ngan-sach-hang-thang/
https://tiepthisaigon.com.vn/chuan-bi-tai-chinh-cho-chuyen-du-lich-nhat-ban-voi-yen-nhat-va-cac-phuong-thuc-thanh-toan-13-5053.html
https://tiepthisaigon.com.vn/lua-chon-ngoai-te-mang-theo-cho-chuyen-du-lich-qua-nhieu-quoc-gia-chau-au-13-5054.html
https://tophungyenaz.com/len-ke-hoach-gui-sinh-hoat-phi-dinh-ky-cho-nguoi-than-dang-song-o-nuoc-ngoai/
https://meohayaz.com/mua-ngoai-te-theo-nhieu-dot-cho-mot-khoan-chi-lon-da-len-ke-hoach-tu-truoc.html
https://vntime.org/phan-bo-hop-ly-giua-tien-mat-ngoai-te-va-the-khi-chi-tieu-o-nuoc-ngoai.html
https://topthaibinhaz.com/quan-ly-thu-nhap-bang-do-la-my-tu-cong-viec-lam-tu-xa-cho-doi-tac-nuoc-ngoai/
https://daklak24h.com.vn/van-hoa-du-lich/119228/chon-dong-tien-thanh-toan-khi-dat-phong-khach-san-nuoc-ngoai-qua-mang.html
https://dongnaireview.vn/tai-chinh-cho-chuyen-du-lich-uc-thanh-toan-khong-tiep-xuc-7688.html
https://baotuyenquang.com.vn/thong-tin-quang-cao/202610/y-nghia-cua-ty-gia-trung-tam-va-bien-do-tran-san-voi-giao-dich-ngoai-te-cua-ca-nhan-0992e0c/
https://baophutho.vn/chon-loc-thong-tin-ty-gia-hang-ngay-phu-hop-voi-khoan-chi-ngoai-te-cua-gia-dinh-262905.htm
https://baotayninh.vn/ly-do-so-tien-hoan-ve-the-khac-voi-so-da-thanh-toan-trong-cac-giao-dich-ngoai-te-350944.html
https://baothainguyen.vn/han-che-chi-phi-chenh-lech-khi-doi-ngoai-te-qua-lai-nhieu-lan
https://binhduongreview.vn/ghi-chep-cac-khoan-chi-tieu-bang-ngoai-te-trong-so-ngan-sach-gia-dinh-8222.html
https://dongnaireview.vn/chia-se-chi-phi-bang-ngoai-te-khi-di-du-lich-nuoc-ngoai-7769.html
https://hanoireview.vn/doc-dung-tong-gia-ve-may-bay-quoc-te-niem-yet-bang-ngoai-te-truoc-khi-thanh-toan-21212.html
https://langvanhoavietnam.vn/chuan-bi-do-la-my-cho-chuyen-du-lich-my/
https://saigonreview.vn/chuan-bi-tai-chinh-cho-chuyen-di-tham-con-dang-hoc-tap-hoac-lam-viec-o-nuoc-ngoai-33586.html
https://topaz.vn/thanh-toan-bang-ma-qr-khi-du-lich-cac-nuoc-trong-khu-vuc-69670.html
https://congngheaz.com/doi-tien-du-lich-chau-a/
https://congngheaz.com/phi-ung-tuyen-du-hoc/
https://topshare.vn/dung-cong-cu-chuyen-doi-tien-te-truc-tuyen-de-co-con-so-quy-doi-sat-voi-giao-dich-thuc-te/""".split()

ds = [{"so": i + 1, "dong_sheet": 9 + i, "url": u} for i, u in enumerate(URLS)]
json.dump(ds, open(os.path.join(HERE, "danh-sach.json"), "w"), ensure_ascii=False, indent=1)


def trong_gio(t, tu=7, den=23):
    """Đẩy giờ đêm (23h–7h) sang sáng hôm sau, lệch ngẫu nhiên."""
    if t.hour >= den:
        t = (t + timedelta(days=1)).replace(hour=tu, minute=random.randint(5, 40))
    elif t.hour < tu:
        t = t.replace(hour=tu, minute=random.randint(5, 40))
    return t


def chuoi(start, n, lo, hi, dem=True):
    out, t = [], start
    for _ in range(n):
        if dem: t = trong_gio(t)
        out.append(t)
        t = t + timedelta(minutes=random.randint(lo, hi))
    return out


bat_dau = datetime(2026, 10, 29, 9, 0, tzinfo=VN)
lich = []
# WordPress: ~5 tiếng/bài (4h50–5h25), chạy cả ngày lẫn đêm nhưng né 0h–6h
wp, t = [], bat_dau + timedelta(minutes=random.randint(0, 15))
for _ in ds:
    if t.hour < 6: t = t.replace(hour=6, minute=random.randint(10, 50))
    wp.append(t); t += timedelta(minutes=random.randint(290, 325))
wix = chuoi(bat_dau + timedelta(minutes=random.randint(20, 30)), len(ds), 52, 72)
ma = chuoi(bat_dau + timedelta(minutes=random.randint(45, 55)), len(ds), 52, 72)
for i, x in enumerate(ds):
    for nen, g in (("wp", wp[i]), ("wix", wix[i]), ("ma", ma[i])):
        lich.append({"so": x["so"], "nen": nen, "gio": g.isoformat(timespec="minutes")})
lich.sort(key=lambda e: e["gio"])
json.dump(lich, open(os.path.join(HERE, "lich.json"), "w"), ensure_ascii=False, indent=1)
print(len(ds), "bài,", len(lich), "lượt đăng")
for nen in ("wp", "wix", "ma"):
    g = [e["gio"] for e in lich if e["nen"] == nen]
    print(nen, g[0], "→", g[-1])
