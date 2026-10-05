"""Soạn và gửi báo cáo qua Telegram hoặc Gmail."""

import smtplib
from email.mime.text import MIMEText
from pathlib import Path

import requests

GIOI_HAN_TELEGRAM = 4000  # Telegram cho tối đa 4096 ký tự / tin


def soan_bao_cao_ngay(buoi, hom_nay, tong_hop, link):
    da = [h for h in tong_hop if h["da_cap_nhat"]]
    loi = [h for h in tong_hop if h["loi"]]
    chua = [h for h in tong_hop if not h["da_cap_nhat"] and not h["loi"]]
    dong = [f"Check publish {buoi} {hom_nay:%d/%m/%Y} – Đã cập nhật: {len(da)}/{len(tong_hop)} "
            f"| Chưa cập nhật: {len(chua)} | Lỗi: {len(loi)}"]
    if chua:
        dong += ["", "Chưa cập nhật:"] + [f"{h['stt']} – {h['url']} – {h['hien_thi']}" for h in chua]
    if loi:
        dong += ["", "Lỗi truy cập:"] + [f"{h['stt']} – {h['url']} – {h['hien_thi']}" for h in loi]
    dong += ["", f"Xem sheet: {link}"]
    return "\n".join(dong)


def soan_bao_cao_tuan(ten_tab, hang_tuan, link):
    """hang_tuan: các hàng của tab tuần (chỉ URL còn trong danh sách), mỗi hàng có 7 ô ngày."""
    tong_luot = len(hang_tuan) * 7
    da_tick = sum(sum(h["ngay"]) for h in hang_tuan)
    ty_le = da_tick / tong_luot if tong_luot else 0
    duoi = [h for h in hang_tuan if sum(h["ngay"]) < 7]
    dong = [f"BÁO CÁO TUẦN – {ten_tab}",
            f"Tỷ lệ cập nhật cả tuần: {ty_le:.0%} ({da_tick}/{tong_luot} lượt ngày)",
            f"Số URL đạt 100%: {len(hang_tuan) - len(duoi)}/{len(hang_tuan)}"]
    if duoi:
        dong += ["", "URL dưới 100%:"]
        for h in sorted(duoi, key=lambda h: sum(h["ngay"])):
            so = sum(h["ngay"])
            dong.append(f"{h['stt']} – {h['url']} – lỡ {7 - so} ngày ({so / 7:.0%})")
    dong += ["", f"Xem tab tuần: {link}"]
    return "\n".join(dong)


def _cat_tin(van_ban, gioi_han=GIOI_HAN_TELEGRAM):
    """Cắt tin dài theo dòng để không vượt giới hạn Telegram."""
    phan, hien_tai = [], ""
    for dong in van_ban.split("\n"):
        if len(hien_tai) + len(dong) + 1 > gioi_han and hien_tai:
            phan.append(hien_tai)
            hien_tai = ""
        hien_tai += dong + "\n"
    if hien_tai.strip():
        phan.append(hien_tai)
    return phan


def _doc_bi_mat(thu_muc: Path, duong_dan: str) -> str:
    p = Path(duong_dan)
    if not p.is_absolute():
        p = thu_muc / p
    return p.read_text(encoding="utf-8").strip()


def _goi_telegram(token, phuong_thuc, **kw):
    """Gọi API Telegram. Lỗi mạng chỉ báo tên lỗi — thông báo gốc có chứa token trong đường dẫn."""
    try:
        tl = requests.post(f"https://api.telegram.org/bot{token}/{phuong_thuc}", timeout=30, **kw)
    except requests.RequestException as e:
        raise RuntimeError(f"Không kết nối được Telegram ({type(e).__name__})") from None
    if not tl.ok:
        raise RuntimeError(f"Telegram từ chối ({tl.status_code}): {tl.json().get('description', '')}")
    return tl.json()


def tim_chat_id(cau_hinh: dict, thu_muc: Path) -> str | None:
    """Lấy chat id từ tin nhắn gần nhất người dùng gửi cho bot (cần bấm START trước)."""
    token = _doc_bi_mat(thu_muc, cau_hinh["telegram"]["file_token"])
    for cap_nhat in reversed(_goi_telegram(token, "getUpdates").get("result", [])):
        tin = cap_nhat.get("message") or cap_nhat.get("my_chat_member") or {}
        if tin.get("chat", {}).get("id"):
            return str(tin["chat"]["id"])
    return None


def gui(cau_hinh: dict, thu_muc: Path, tieu_de: str, van_ban: str):
    kenh = cau_hinh.get("kenh_bao_cao", "khong").lower()
    if kenh == "telegram":
        tg = cau_hinh["telegram"]
        token = _doc_bi_mat(thu_muc, tg["file_token"])
        for phan in _cat_tin(van_ban):
            _goi_telegram(token, "sendMessage", data={"chat_id": tg["chat_id"], "text": phan,
                                                      "disable_web_page_preview": "true"})
    elif kenh == "gmail":
        gm = cau_hinh["gmail"]
        mat_khau = _doc_bi_mat(thu_muc, gm["file_mat_khau_ung_dung"])
        thu = MIMEText(van_ban, "plain", "utf-8")
        thu["Subject"] = tieu_de
        thu["From"] = gm["gui_tu"]
        thu["To"] = gm["gui_den"]
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as may:
            may.login(gm["gui_tu"], mat_khau.replace(" ", ""))
            may.send_message(thu)
    elif kenh != "khong":
        raise ValueError(f'kenh_bao_cao "{kenh}" không hợp lệ (chọn telegram / gmail / khong)')
