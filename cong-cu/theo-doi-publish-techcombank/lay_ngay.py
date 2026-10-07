"""Lấy ngày publish/cập nhật của một trang techcombank.com.

Quy tắc:
- URL có "/thong-tin/blog/": đọc thẻ <div class="article-header-body--date"> nằm ngay
  sau H1 và sapo. Thẻ chứa ngày ISO, ví dụ 2026-10-05T00:00:00.000+07:00.
- URL khác: tìm ngày dd/mm/yyyy trong thẻ <title>.
"""

import random
import re
import time
from dataclasses import dataclass
from datetime import date

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
TIMEOUT = 20
SO_LAN_THU_LAI = 2  # thử lại 2 lần sau lần đầu => tối đa 3 lần gọi

THE_NGAY_BLOG = "div.article-header-body--date"
MAU_ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
MAU_DMY = re.compile(r"(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)")


@dataclass
class KetQua:
    url: str
    ngay: date | None = None  # ngày tìm thấy
    loi: str | None = None  # mã lỗi nếu không truy cập được

    @property
    def hien_thi(self) -> str:
        """Chữ ghi vào sheet / báo cáo."""
        if self.loi:
            return f"Lỗi: {self.loi}"
        if self.ngay is None:
            return "Không có ngày"
        return self.ngay.strftime("%d/%m/%Y")


def tao_phien() -> requests.Session:
    phien = requests.Session()
    phien.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        # Xin bản mới nhất, không lấy bản lưu tạm (cache) — khách vừa đăng là thấy ngay
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })
    return phien


def _tai_html(phien: requests.Session, url: str) -> tuple[str | None, str | None]:
    """Trả về (html, mã lỗi). Thử lại khi lỗi mạng hoặc lỗi máy chủ 5xx/429."""
    loi = None
    for lan in range(SO_LAN_THU_LAI + 1):
        if lan:
            time.sleep(random.uniform(1, 2) * lan)
        try:
            tl = phien.get(url, timeout=TIMEOUT)
        except requests.RequestException as e:
            loi = type(e).__name__
            continue
        if tl.status_code == 200:
            tl.encoding = "utf-8"
            return tl.text, None
        loi = str(tl.status_code)
        if tl.status_code not in (429, 500, 502, 503, 504):
            break  # 403/404... thử lại cũng vậy
    return None, loi


def tach_ngay(url: str, html: str) -> date | None:
    soup = BeautifulSoup(html, "html.parser")
    try:
        if "/thong-tin/blog/" in url:
            the = soup.select_one(THE_NGAY_BLOG)
            m = MAU_ISO.search(the.get_text()) if the else None
            if m:
                return date(int(m[1]), int(m[2]), int(m[3]))
        else:
            tieu_de = soup.title.get_text() if soup.title else ""
            m = MAU_DMY.search(tieu_de)
            if m:
                return date(int(m[3]), int(m[2]), int(m[1]))
    except ValueError:  # ngày vô lý, ví dụ 31/02
        pass
    return None


def lay_ngay(phien: requests.Session, url: str) -> KetQua:
    html, loi = _tai_html(phien, url)
    if loi:
        return KetQua(url, loi=loi)
    return KetQua(url, ngay=tach_ngay(url, html))


def lay_nhieu(urls: list[str], in_tien_do=None) -> list[KetQua]:
    phien = tao_phien()
    ket_qua = []
    for i, url in enumerate(urls):
        if i:
            time.sleep(random.uniform(1, 2))
        kq = lay_ngay(phien, url)
        ket_qua.append(kq)
        if in_tien_do:
            in_tien_do(i + 1, len(urls), kq)
    return ket_qua
