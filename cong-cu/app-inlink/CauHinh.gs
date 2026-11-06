/**
 * CauHinh.gs — mỗi dự án 1 mục. Thêm dự án mới: chép 1 mục, đổi sheet/tab/thư mục/tên cột.
 * Tên cột tìm theo CHỮ ở hàng 1 (không theo vị trí) → sheet có chèn/đổi cột vẫn chạy đúng.
 */
var DU_AN = [
  {
    ten: 'Techcombank',
    sheetId: '1KqFQ7DIRFM3vwozccCYZrlsRybOAsieAKm_MVsM2Lnc',
    tab: 'Plan internal links - Tổng',
    thuMuc: '1qLQU6FfkXcOvAsUvKZ-KsVeXWC5RLgHH',
    goc: 'https://techcombank.com',
    taiQua: function (u) { return u.replace('//techcombank.com', '//www.techcombank.com').split('?')[0]; },
    thanBai: /<div[^>]*class=["'][^"']*\barticle-text\b[^"']*["'][^>]*>/,
    boKhoi: [/<div[^>]*class=["'][^"']*\bcurrency-converter\b[^"']*["'][^>]*>/, /<div[^>]*class=["'][^"']*\blist-?tiles?\b[^"']*["'][^>]*>/],
    cot: {
      url: /^URL$/i, file: /^FILE BLOG$/i, ghiChu: /^Ghi chú$/i, duyet: /^Chị Lộc duyệt$/i,
      tyGiaAnchor: /^Anchor text \(Trang tỷ giá\)$/i, tyGiaUrl: /^URL đích \(Trang tỷ giá\)$/i,
      demo: /^Demo nội dung chèn ACT Tỷ giá$/i, xf: /^Chèn XF$/i,
      capAnchor: /^Anchor ?text ?(\d)$/i, capUrl: /^URL đích (\d)$/i
    },
    boQuaTyGia: function (h) { return /tiết kiệm/i.test(h.xf || '') || /XF Tiết kiệm/i.test(h.ghiChu || ''); },
    boQuaDong: function (h) { return false; },
    nguoiDuyet: 'Lộc',
    tuChay: true
  },
  {
    ten: 'Okamura',
    sheetId: '1xKnPX-uf7av3FpSocVjy9wKJiNeygrsZLVmdcMC7np8',
    tab: 'Trang tính146',
    thuMuc: '1dfPI34Qf5mFI1ALHl5vWU8MUKrqVnwiU',
    goc: 'https://www.okamura.com.vn',
    taiQua: function (u) { return u.split('?')[0]; },
    thanBai: /<(?:div|section)[^>]*data-hook=["']post-description["'][^>]*>/,
    boKhoi: [],
    cot: {
      url: /^Landingpage chính xác$/i, file: /^Fie Blog$|^File Blog$/i, ghiChu: null, duyet: null, tinhTrang: /^Tình trạng$/i,
      tyGiaAnchor: null, tyGiaUrl: null, demo: null, xf: null,
      capAnchor: /^Anchotext 0?(\d)/i, capUrl: /^URL 0?(\d)$/i
    },
    boQuaTyGia: function () { return true; },
    boQuaDong: function (h) { return /đã done|^-$/i.test(String(h.tinhTrang || '').trim()); },
    nguoiDuyet: 'Lộc',
    tuChay: false
  }
];

var UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36';
var GIOI_HAN_GIAY = 300;          // Apps Script cho tối đa 6 phút mỗi lần chạy; dừng ở 5 phút cho an toàn
var TAB_GOP_Y = 'Sổ góp ý';
var TAB_NHAT_KY = 'Nhật ký app';
