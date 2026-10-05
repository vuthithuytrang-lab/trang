"""Theo dõi ngày publish/cập nhật các URL techcombank.com — chạy lúc 08:00 và 20:00.

Cách chạy:
  python theo_doi.py                      chạy đầy đủ: lấy ngày, ghi sheet, gửi báo cáo
  python theo_doi.py --khong-gui          chạy đầy đủ nhưng không gửi báo cáo
  python theo_doi.py --buoi 20:00         ép tính là lần chạy 20:00
  python theo_doi.py --thu-lay-ngay       chỉ lấy ngày và in ra màn hình (không đụng sheet)
  python theo_doi.py --thu-lay-ngay URL1 URL2 ...
  python theo_doi.py --thu-lay-ngay --ngau-nhien 5
  python theo_doi.py --gui-thu            gửi 1 tin thử qua kênh báo cáo
  python theo_doi.py --bao-cao-tuan       gửi kèm báo cáo tuần ngay lần này (không cần đợi tối CN)
"""

import argparse
import json
import logging
import random
import sys
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bao_cao
import lay_ngay

THU_MUC = Path(__file__).resolve().parent
GIO_VN = timezone(timedelta(hours=7))  # Việt Nam không đổi giờ theo mùa
log = logging.getLogger("theo_doi")


def cai_log():
    thu_muc_log = THU_MUC / "logs"
    thu_muc_log.mkdir(exist_ok=True)
    dinh_dang = logging.Formatter("%(asctime)s  %(levelname)-7s %(message)s", "%Y-%m-%d %H:%M:%S")
    file = logging.FileHandler(thu_muc_log / f"{datetime.now(GIO_VN):%Y-%m}.log", encoding="utf-8")
    file.setFormatter(dinh_dang)
    log.addHandler(file)
    if sys.stdout is not None:  # pythonw (chạy ngầm) không có màn hình
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")  # để cửa sổ Windows hiện đúng dấu
        man_hinh = logging.StreamHandler(sys.stdout)
        man_hinh.setFormatter(dinh_dang)
        log.addHandler(man_hinh)
    log.setLevel(logging.INFO)


def doc_cau_hinh():
    return json.loads((THU_MUC / "cau-hinh.json").read_text(encoding="utf-8"))


def duong_dan(p):
    p = Path(p)
    return p if p.is_absolute() else THU_MUC / p


def in_tien_do(i, tong, kq):
    log.info(f"[{i}/{tong}] {kq.hien_thi:<16} {kq.url}")


def thu_lay_ngay(urls, ngau_nhien):
    if not urls:
        urls = [d.strip() for d in (THU_MUC / "danh-sach-url-mac-dinh.txt").read_text(encoding="utf-8").splitlines()
                if d.strip()]
        if ngau_nhien:
            urls = random.sample(urls, min(ngau_nhien, len(urls)))
    hom_nay = datetime.now(GIO_VN).date()
    ket_qua = lay_ngay.lay_nhieu(urls, in_tien_do)
    print(f"\nHôm nay: {hom_nay:%d/%m/%Y}")
    for kq in ket_qua:
        dau = "✔" if kq.ngay == hom_nay else "✘"
        print(f"  {dau} {kq.hien_thi:<16} {kq.url}")


def chay(cau_hinh, buoi, gui_bao_cao, ep_bao_cao_tuan):
    import google_sheet as gs  # chỉ cần khi chạy với sheet

    bay_gio = datetime.now(GIO_VN)
    hom_nay = bay_gio.date()
    buoi = buoi or ("08:00" if bay_gio.hour < 14 else "20:00")
    log.info(f"=== Bắt đầu lần chạy {buoi} ngày {hom_nay:%d/%m/%Y} ===")

    sh = gs.mo_sheet(cau_hinh["link_google_sheet"], str(duong_dan(cau_hinh["file_service_account"])))
    urls = gs.doc_danh_sach_url(sh, THU_MUC / "danh-sach-url-mac-dinh.txt")
    log.info(f"Đọc được {len(urls)} URL từ tab \"{gs.TAB_DANH_SACH}\"")
    if not urls:
        raise RuntimeError(f'Tab "{gs.TAB_DANH_SACH}" không có URL nào ở cột B')

    ket_qua = lay_ngay.lay_nhieu(urls, in_tien_do)

    thu_hai = gs.thu_hai_cua_tuan(hom_nay)
    ws = gs.lay_tab_tuan(sh, thu_hai, urls)
    tong_hop = gs.ghi_ket_qua(sh, ws, hom_nay, buoi, ket_qua, set(urls))
    link = gs.link_tab(sh, ws)
    so_da = sum(h["da_cap_nhat"] for h in tong_hop)
    log.info(f"Đã ghi vào tab \"{ws.title}\": {so_da}/{len(tong_hop)} URL đã cập nhật hôm nay")

    tin = [(f"Check publish {buoi} {hom_nay:%d/%m/%Y}",
            bao_cao.soan_bao_cao_ngay(buoi, hom_nay, tong_hop, link))]
    if ep_bao_cao_tuan or (buoi == "20:00" and hom_nay.weekday() == 6):
        hang_tuan = [h for h in gs.doc_tab_tuan(sh, ws) if h["url"] in set(urls)]
        tin.append((f"Báo cáo tuần {ws.title}", bao_cao.soan_bao_cao_tuan(ws.title, hang_tuan, link)))

    for tieu_de, van_ban in tin:
        log.info("Nội dung báo cáo:\n" + van_ban)
        if gui_bao_cao:
            bao_cao.gui(cau_hinh, THU_MUC, tieu_de, van_ban)
            log.info(f"Đã gửi: {tieu_de}")
    log.info("=== Xong ===")


def main():
    p = argparse.ArgumentParser(description="Theo dõi ngày publish URL techcombank.com")
    p.add_argument("--thu-lay-ngay", nargs="*", metavar="URL")
    p.add_argument("--ngau-nhien", type=int, default=0)
    p.add_argument("--buoi", choices=["08:00", "20:00"])
    p.add_argument("--khong-gui", action="store_true")
    p.add_argument("--gui-thu", action="store_true")
    p.add_argument("--bao-cao-tuan", action="store_true")
    a = p.parse_args()
    cai_log()

    if a.thu_lay_ngay is not None:
        thu_lay_ngay(a.thu_lay_ngay, a.ngau_nhien)
        return

    cau_hinh = doc_cau_hinh()
    if a.gui_thu:
        tg = cau_hinh.get("telegram", {})
        if cau_hinh.get("kenh_bao_cao") == "telegram" and not str(tg.get("chat_id", "")).strip():
            chat_id = bao_cao.tim_chat_id(cau_hinh, THU_MUC)
            if not chat_id:
                log.error("Chưa thấy tin nhắn nào gửi cho bot. Mở bot trên Telegram, bấm START rồi chạy lại.")
                sys.exit(1)
            tg["chat_id"] = chat_id
            (THU_MUC / "cau-hinh.json").write_text(json.dumps(cau_hinh, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
            log.info("Đã tự lấy chat id Telegram và lưu vào cau-hinh.json")
        bao_cao.gui(cau_hinh, THU_MUC, "Tin thử – Theo dõi publish Techcombank",
                    "Tin thử: hệ thống theo dõi publish Techcombank đã kết nối kênh báo cáo thành công.")
        log.info("Đã gửi tin thử")
        return

    try:
        chay(cau_hinh, a.buoi, not a.khong_gui, a.bao_cao_tuan)
    except Exception as e:
        log.error("Lần chạy bị lỗi:\n" + traceback.format_exc())
        if not a.khong_gui:
            try:
                bao_cao.gui(cau_hinh, THU_MUC, "LỖI – Theo dõi publish Techcombank",
                            f"⚠️ Lần chạy theo dõi publish bị lỗi: {type(e).__name__}: {e}\n"
                            f"Xem chi tiết trong thư mục logs/.")
            except Exception:
                log.error("Không gửi được tin báo lỗi:\n" + traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
