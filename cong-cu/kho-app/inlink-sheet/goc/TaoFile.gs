/**
 * TaoFile.gs — tạo file Docs từ URL bài và chèn đủ anchor theo sheet.
 * Thứ tự cho mỗi anchor: cột Demo "Sau khi chèn" (tỷ giá) → link có sẵn đúng anchor → cụm có sẵn → AI viết 1 câu / dòng Xem thêm.
 * Không chèn được thì để thiếu và ghi rõ lý do (không ép câu gượng — bài học từ góp ý chị Lộc).
 */

function taiTrang(url) {
  var r = UrlFetchApp.fetch(url, {
    muteHttpExceptions: true, followRedirects: true,
    headers: { 'User-Agent': UA, 'Accept': 'text/html', 'Accept-Language': 'vi-VN,vi;q=0.9' }
  });
  return { ma: r.getResponseCode(), html: r.getContentText('UTF-8') };
}

/** Bước 1: tải bài, dựng HTML, tải lên Drive thành Google Docs. */
function taoDocTuUrl(pj, url) {
  var t = taiTrang(url.split('#')[0]);
  if (t.ma !== 200) return { loi: 'không tải được bài (mã ' + t.ma + ')' + (t.ma === 403 ? ' — website chặn máy chủ Google, cần làm tay' : '') };
  var info = layThongTinTrang(t.html);
  if (/Không tìm thấy|404|Not Found/i.test(info.title)) return { loi: 'bài đã bị gỡ (Không tìm thấy trang)' };
  var than = timThanBai(t.html);
  if (!than) return { loi: 'không tìm thấy thân bài (trang dựng bằng JavaScript hoặc là trang sản phẩm) — cần làm tay' };
  var goc = (url.match(/^https?:\/\/[^\/]+/) || [''])[0];
  than = lamSachThanBai(than, goc);
  var chu = than.replace(/<[^>]+>/g, ' ');
  var ten = tuKhoaTuSlug(url, [info.h1, info.title, info.meta, chu]);
  var html = dungHtmlDoc(url, info, than);
  var f = taoDocTuHtml(ten, html, pj.thuMuc);
  return { id: f.id, ten: ten, chuBai: chuanHoa(chu) };
}

/* ------------------------- đọc cấu trúc file Docs ------------------------- */

function linkTrongDoan(el) {
  var out = [];
  var tx = el.editAsText(), s = tx.getText();
  if (!s.length) return out;
  var idx = tx.getTextAttributeIndices(), cur = null;
  for (var i = 0; i < idx.length; i++) {
    var a = idx[i], b = i + 1 < idx.length ? idx[i + 1] : s.length;
    var u = tx.getLinkUrl(a);
    if (u && cur && cur.url === u && cur.end === a) { cur.end = b; continue; }
    if (cur) out.push(cur);
    cur = u ? { url: u, start: a, end: b } : null;
  }
  if (cur) out.push(cur);
  out.forEach(function (l) { l.text = s.slice(l.start, l.end); });
  return out;
}

/** Danh sách đoạn thân bài (bỏ 6 đoạn đầu: URL, title, meta). */
function docDoan(body, tu) {
  var ds = [];
  for (var i = (tu === undefined ? 6 : tu); i < body.getNumChildren(); i++) {
    var el = body.getChild(i), ty = el.getType();
    if (ty === DocumentApp.ElementType.PARAGRAPH || ty === DocumentApp.ElementType.LIST_ITEM) {
      var p = ty === DocumentApp.ElementType.PARAGRAPH ? el.asParagraph() : el.asListItem();
      var links = linkTrongDoan(p);
      ds.push({ el: p, text: p.getText(), heading: p.getHeading() !== DocumentApp.ParagraphHeading.NORMAL,
        list: ty === DocumentApp.ElementType.LIST_ITEM, table: false, link: links.map(function (l) { return l.url; }), links: links });
    } else if (ty === DocumentApp.ElementType.TABLE) {
      ds.push({ el: el, text: el.asTable().getText(), heading: false, list: false, table: true, link: [], links: [] });
    }
  }
  return ds;
}

function chenGhiChu(body, el, noiDung) {
  var i = body.getChildIndex(el);
  var p = body.insertParagraph(i + 1, noiDung);
  p.setHeading(DocumentApp.ParagraphHeading.NORMAL).setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
  p.editAsText().setLinkUrl(null).setBackgroundColor(null).setBold(false).setItalic(true).setForegroundColor(RED);
  return p;
}

function toLink(tx, a, b, url) {
  tx.setLinkUrl(a, b - 1, url).setUnderline(a, b - 1, true).setForegroundColor(a, b - 1, LINK_BLUE).setBackgroundColor(a, b - 1, YELLOW);
}

/** Phần tử cuối của danh sách chứa el (để chèn đoạn mới sau cả danh sách). */
function cuoiDanhSach(body, el) {
  var i = body.getChildIndex(el);
  while (i + 1 < body.getNumChildren() && body.getChild(i + 1).getType() === DocumentApp.ElementType.LIST_ITEM) i++;
  return body.getChild(i);
}

/* ------------------------------ các cách chèn ------------------------------ */

function chenTheoDemo(body, doan, a, demo) {
  var mT = demo.match(/Trước khi chèn:\s*([\s\S]*?)\s*Sau khi chèn:\s*([\s\S]*)$/i);
  if (!mT) return null;
  var boGach = function (x) { return chuanHoa(x).replace(/^[-•+*–]\s*/, ''); };
  var truoc0 = boGach(mT[1]).replace(/\.$/, ''), sau0 = boGach(mT[2]);
  if (sau0.indexOf(a.anchor) < 0) return null;
  // thử cả câu; nếu không khớp thì thử phần sau nhãn "...:" (nhãn in đậm đầu gạch đầu dòng)
  var thu = [[truoc0, sau0]];
  var c1 = truoc0.indexOf(': '), c2 = sau0.indexOf(': ');
  if (c1 > 0 && c2 > 0 && truoc0.slice(0, c1) === sau0.slice(0, c2)) thu.push([truoc0.slice(c1 + 2), sau0.slice(c2 + 2)]);
  for (var i = 0; i < doan.length; i++) {
    var d = doan[i];
    if (d.table || d.heading) continue;
    var s = d.text.replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').normalize('NFC');
    var k = -1, truoc = '', sau = '';
    for (var t = 0; t < thu.length && k < 0; t++) { k = s.indexOf(thu[t][0]); truoc = thu[t][0]; sau = thu[t][1]; }
    if (k < 0 || sau.indexOf(a.anchor) < 0) continue;
    if (s.length !== d.text.length) continue;   // văn bản có khoảng trắng lạ → vị trí lệch, để làm tay
    var goc = d.text, tx = d.el.editAsText();
    var het = k + truoc.length;
    if (s.charAt(het) === '.' && /\.$/.test(sau)) het++;
    tx.deleteText(k, het - 1);
    tx.insertText(k, sau);
    var kh = phanKhacNhau(truoc, sau);
    tx.setBackgroundColor(k + kh.start, k + kh.end - 1, YELLOW);
    var ai = sau.indexOf(a.anchor);
    toLink(tx, k + ai, k + ai + a.anchor.length, a.url);
    chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + chuanHoa(goc) + ']');
    return 'cột Demo';
  }
  return 'khong_thay';
}

function chenLinkCoSan(body, doan, a) {
  for (var i = 0; i < doan.length; i++) {
    var ls = doan[i].links;
    for (var j = 0; j < ls.length; j++) {
      if (slugCua(ls[j].url) === slugCua(a.url) && chuanHoa(ls[j].text) === a.anchor) {
        doan[i].el.editAsText().setBackgroundColor(ls[j].start, ls[j].end - 1, YELLOW);
        chenGhiChu(body, doan[i].el, '[Bài gốc đã có sẵn link đúng anchor và URL đích — giữ nguyên]');
        return 'có sẵn link đúng anchor';
      }
    }
  }
  return null;
}

function chenCumCoSan(body, doan, a) {
  var hit = timCumCoSan(doan, a.anchor);
  if (!hit) return null;
  var d = doan[hit.i], goc = chuanHoa(d.text);
  toLink(d.el.editAsText(), hit.offset, hit.offset + a.anchor.length, a.url);
  chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + goc + ']');
  return 'gắn cụm có sẵn';
}

function chenCauAI(body, doan, a, ngCanh) {
  var pct = viTriPhanTram(doan), ung = [];
  for (var i = 0; i < doan.length; i++) if (duocChen(doan, pct, i) && !keLink(doan, i)) ung.push(i);
  if (!ung.length) return { ly_do: 'không còn đoạn hợp lệ (≥25%, không kề link)' };
  var g = aiChonCho(a, doan, pct, ung, ngCanh);
  if (!g.ok) return { ly_do: g.ly_do };
  var d = doan[g.i], goc = chuanHoa(d.text);
  if (g.cach === 'xemthem') {
    var sau = d.list ? cuoiDanhSach(body, d.el) : d.el;
    var ghi = chenGhiChu(body, sau, '[Đề xuất viết thêm đoạn mới]');
    var p = body.insertParagraph(body.getChildIndex(ghi) + 1, g.cau);
    p.setHeading(DocumentApp.ParagraphHeading.NORMAL).setAlignment(DocumentApp.HorizontalAlignment.JUSTIFY);
    var tx = p.editAsText();
    tx.setLinkUrl(null).setForegroundColor(null).setBold(true).setItalic(true).setBackgroundColor(YELLOW);
    var k = g.cau.indexOf(a.anchor);
    toLink(tx, k, k + a.anchor.length, a.url);
    return { cach: 'xem thêm' };
  }
  var tx2 = d.el.editAsText(), s = tx2.getText().replace(/\s+$/, '');
  var them = (/[.:;!?…]$/.test(s) ? '' : '.') + ' ' + g.cau;
  var bd = s.length;
  tx2.insertText(bd, them);
  tx2.setBackgroundColor(bd + 1, bd + them.length - 1, YELLOW).setLinkUrl(bd, bd + them.length - 1, null);
  var k2 = bd + them.indexOf(a.anchor);
  toLink(tx2, k2, k2 + a.anchor.length, a.url);
  chenGhiChu(body, d.el, '[Nội dung gốc trước khi chèn: ' + goc + ']');
  return { cach: 'viết thêm 1 câu' };
}

/* ------------------------------- soát cuối ------------------------------- */

function soatFile(body, ds, tu) {
  var doan = docDoan(body, tu), pct = viTriPhanTram(doan);
  return ds.map(function (a) {
    for (var i = 0; i < doan.length; i++) {
      var ls = doan[i].links;
      for (var j = 0; j < ls.length; j++) {
        if (slugCua(ls[j].url) === slugCua(a.url) && chuanHoa(ls[j].text) === a.anchor) {
          var vang = doan[i].el.editAsText().getBackgroundColor(ls[j].start) === YELLOW;
          return { anchor: a.anchor, ok: vang, vang: vang, pct: pct[i], heading: doan[i].heading };
        }
      }
    }
    return { anchor: a.anchor, ok: false };
  });
}

/** Xử lý trọn 1 dòng sheet. Trả về {id, ketQua, loi}. */
function xuLyDong(pj, url, ds, ghiChuDong, idCoSan) {
  var tao = idCoSan ? { id: idCoSan } : taoDocTuUrl(pj, url);
  if (tao.loi) return tao;
  var tu = idCoSan ? 0 : 6;
  var doc = DocumentApp.openById(tao.id), body = doc.getBody();
  if (idCoSan) { tao.ten = doc.getName(); tao.chuBai = chuanHoa(body.getText()).slice(0, 20000); }
  var ngCanh = { chuBai: tao.chuBai, tieuDe: tao.ten, luat: pj.luat, giongVan: pj.giongVan, ghiChuDong: ghiChuDong || '' };
  var ketQua = [];
  ds.forEach(function (a) {
    var doan = docDoan(body, tu), cach = null, lyDo = '';
    cach = chenLinkCoSan(body, doan, a);
    if (!cach) cach = chenCumCoSan(body, doan, a);
    if (!cach) {
      var r = chenCauAI(body, docDoan(body, tu), a, ngCanh);
      cach = r.cach || null; lyDo = r.ly_do || '';
    }
    ketQua.push({ anchor: a.anchor, ok: !!cach, cach: cach, ly_do: lyDo });
  });
  doc.saveAndClose();
  var soat = soatFile(DocumentApp.openById(tao.id).getBody(), ds, tu);
  soat.forEach(function (s, i) {
    if (ketQua[i].ok && !s.ok) { ketQua[i].ok = false; ketQua[i].ly_do = 'soát lại không thấy link/tô vàng'; }
  });
  return { id: tao.id, ketQua: ketQua };
}

