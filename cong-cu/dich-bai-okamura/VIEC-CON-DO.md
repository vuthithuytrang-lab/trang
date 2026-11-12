# Việc còn dở — dịch bài Okamura (12/11/2026)

Phiên Claude mới: đọc skill `.claude/skills/dich-bai-okamura/SKILL.md` rồi làm đúng các bước dưới.

## BV15 — nội thất phòng làm việc
- Doc: https://docs.google.com/document/d/1X3erMGH-OvdoG5uiYYqaF_n9GWQIg6uB3c67C5wDI9g — tab bản dịch `t.1gzlnawr2sbq`
- Cột phải (EN): XONG, verify khớp 100%.
- Cột trái (VN): còn thiếu 2 lô cuối (lô 5 và 6, chia `--chunk 45`): phần đầu bài + ảnh của cột Việt.
- Cách làm nốt:
  1. `read_doc` doc trên (lấy link ảnh mới — link chỉ sống ~15 phút), bóc `content` ra file JSON.
  2. `python3 cong-cu/dich-bai-okamura/build_requests.py fill <JSON> cong-cu/dich-bai-okamura/ban-dich/bv15_en.txt --tab t.1gzlnawr2sbq --cells 5,7 --out <scratch>/bv15.json --chunk 45`
  3. CHỈ gửi `bv15_5.json` rồi `bv15_6.json` (lô 1-4 đã ghi rồi, gửi lại sẽ bị nhân đôi).
  4. `read_doc` lại → `verify.py` phải ra "OK — khớp hoàn toàn".

## BV40 — tủ tài liệu
- Doc: https://docs.google.com/document/d/1FtxPeSpZ4T4a56StG7p2jErjprY2q59w8doPO3mhQdQ — tab `t.8atlqcdeyxfd`
- Trạng thái: xem dòng cập nhật cuối file này.

**Cập nhật:** BV40 XONG cả 2 cột, verify khớp 100% (95 đoạn, 8 ảnh). BV9 XONG. Chỉ còn BV15 lô 5-6 (cột trái).
