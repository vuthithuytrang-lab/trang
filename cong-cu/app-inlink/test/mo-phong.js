// Mô phỏng Google (DocumentApp, Drive, UrlFetchApp, Gemini) để chạy trọn xuLyDong() trên bài thật.
// node test/mo-phong.js <bai.html> <url> <rows.json> <row>
const fs = require('fs'), vm = require('vm'), cp = require('child_process');
const [,, fBai, URL_BAI, fRows, ROW, PJ = '0'] = process.argv;
const row = JSON.parse(fs.readFileSync(fRows, 'utf8')).find(r => String(r.row) === String(ROW));
const docs = {};
class Text { constructor(p) { this.p = p; }
  rng(a, b) { return b === undefined ? [0, this.p.ch.length - 1] : [a, b]; }
  getText() { return this.p.ch.map(c => c.c).join(''); }
  getTextAttributeIndices() { const r = []; let prev = null; this.p.ch.forEach((c, i) => { const k = (c.link||'')+'|'+(c.bg||''); if (k !== prev) r.push(i); prev = k; }); return r; }
  getLinkUrl(i) { return this.p.ch[i] ? this.p.ch[i].link || null : null; }
  getBackgroundColor(i) { return this.p.ch[i] ? this.p.ch[i].bg || null : null; }
  set(k, a, b, v) { if (b === undefined && a !== undefined && typeof a !== 'number') { v = a; a = 0; b = this.p.ch.length - 1; } if (a === undefined) { a = 0; b = this.p.ch.length - 1; } for (let i = a; i <= b; i++) if (this.p.ch[i]) this.p.ch[i][k] = v; return this; }
  setLinkUrl(a, b, v) { return arguments.length === 1 ? this.set('link', a) : this.set('link', a, b, v); }
  setBackgroundColor(a, b, v) { return arguments.length === 1 ? this.set('bg', a) : this.set('bg', a, b, v); }
  setForegroundColor(a, b, v) { return arguments.length === 1 ? this.set('fg', a) : this.set('fg', a, b, v); }
  setUnderline(a, b, v) { return this.set('u', a, b, v); }
  setBold(a, b, v) { return arguments.length === 1 ? this.set('b', a) : this.set('b', a, b, v); }
  setItalic(a, b, v) { return arguments.length === 1 ? this.set('it', a) : this.set('it', a, b, v); }
  insertText(i, s) { const base = this.p.ch[i - 1] || {}; this.p.ch.splice(i, 0, ...[...s].map(c => ({ c, link: base.link, bg: base.bg }))); return this; }
  deleteText(a, b) { this.p.ch.splice(a, b - a + 1); return this; } }
class Para { constructor(o) { this.type = o.type; this.heading = o.heading; this.ch = [...(o.text||'')].map(c => ({ c })); (o.links||[]).forEach(([a, b, u]) => { for (let i = a; i < b; i++) if (this.ch[i]) this.ch[i].link = u; }); }
  getType() { return this.type; } asParagraph() { return this; } asListItem() { return this; } asTable() { return this; }
  getText() { return this.ch.map(c => c.c).join(''); } editAsText() { return new Text(this); }
  getHeading() { return this.heading ? 'H2' : 'NORMAL'; } setHeading(h) { this.heading = h !== 'NORMAL'; return this; } setAlignment() { return this; } }
class Body { constructor(c) { this.c = c; } getNumChildren() { return this.c.length; } getChild(i) { return this.c[i]; }
  getChildIndex(e) { return this.c.indexOf(e); } insertParagraph(i, t) { const p = new Para({ type: 'PARAGRAPH', text: t }); this.c.splice(i, 0, p); return p; } }
let gemCount = 0;
const ctx = {
  console, JSON, Math, Date, parseInt, String, Object, Array, RegExp, Error,
  DocumentApp: { ElementType: { PARAGRAPH: 'PARAGRAPH', LIST_ITEM: 'LIST_ITEM', TABLE: 'TABLE' }, ParagraphHeading: { NORMAL: 'NORMAL' }, HorizontalAlignment: { JUSTIFY: 'J' },
    openById: id => ({ getBody: () => docs[id], saveAndClose() {} }) },
  MimeType: { GOOGLE_DOCS: 'doc' },
  Utilities: { newBlob: (h) => ({ h }), base64EncodeWebSafe: s => Buffer.from(String(s)).toString('base64') },
  Drive: { Files: { create: (res, blob) => { const id = 'doc' + Object.keys(docs).length; const bl = JSON.parse(cp.execSync('python3 ' + __dirname + '/khoi.py', { input: blob.h }).toString());
    docs[id] = new Body(bl.map(o => new Para(o))); fs.writeFileSync('/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/rv2/mo-phong-goc.html', blob.h); return { id }; } } },
  CacheService: { getScriptCache: () => ({ get: () => null, put() {} }) },
  PropertiesService: { getUserProperties: () => ({ getProperty: k => k === 'GEMINI_KEY' ? 'gia' : null }) },
  UrlFetchApp: { fetch: (u, o) => {
    if (/generativelanguage/.test(u)) { gemCount++; const p = JSON.parse(o.payload).contents[0].parts[0].text;
      const anchor = p.match(/ANCHOR: "([^"]+)"/)[1]; const ids = [...p.matchAll(/^\[(\d+)\] \((\d+)%\)/gm)].map(m => +m[1]);
      const i = ids[Math.floor(ids.length / 2)];
      const ans = { i, cach: gemCount % 2 ? 'sentence' : 'xemthem', cau: gemCount % 2 ? 'Trước khi quyết định, bạn nên xem ' + anchor + ' để chọn phương án phù hợp với nhu cầu.' : '>>> Xem thêm: ' + anchor + ' cho người mới bắt đầu' };
      return { getResponseCode: () => 200, getContentText: () => JSON.stringify({ candidates: [{ content: { parts: [{ text: JSON.stringify(ans) }] } }] }) }; }
    if (/raw\.githubusercontent/.test(u)) return { getResponseCode: () => 200, getContentText: () => '# sổ bài học (giả lập)' };
    if (u.split('?')[0].replace('//www.', '//') === URL_BAI.split('?')[0].replace('//www.', '//')) return { getResponseCode: () => 200, getContentText: () => fs.readFileSync(fBai, 'utf8') };
    return { getResponseCode: () => 200, getContentText: () => '<title>Trang đích</title><h2>Mục 1</h2>' }; } }
};
vm.createContext(ctx);
fs.readdirSync(__dirname + '/..').filter(f => f.endsWith('.gs') && f !== 'Inlink-gop.gs').forEach(f => vm.runInContext(fs.readFileSync(__dirname + '/../' + f, 'utf8'), ctx, { filename: f }));
const ds = []; if (row.F && row.G) ds.push({ anchor: row.F, url: row.G, tyGia: true }); row.pairs.forEach(([a, u]) => ds.push({ anchor: a, url: u }));
ctx.ds = ds; ctx.URL_BAI = URL_BAI; ctx.DEMO = row.I || '';
const kq = vm.runInContext('xuLyDong(DU_AN[' + PJ + '], URL_BAI, ds, DEMO)', ctx);
console.log(JSON.stringify(kq.ketQua, null, 1)); console.log('Gemini gọi', gemCount, 'lần');
// xuất file kết quả ra HTML để soát bằng kiemtra-like
const b = docs[kq.id]; let h = '<html><body>';
b.c.forEach(p => { if (p.type === 'TABLE') { h += '<table><tr><td>' + p.getText() + '</td></tr></table>'; return; }
  let s = '', cur = null; p.ch.forEach(c => { const k = (c.link||'') + '|' + (c.bg||'') + '|' + (c.fg||''); if (k !== cur) { if (cur !== null) s += '</span>' + (cur.split('|')[0] ? '</a>' : ''); if (c.link) s += '<a href="' + c.link + '">'; s += '<span style="' + (c.bg ? 'background-color:' + c.bg + ';' : '') + (c.fg ? 'color:' + c.fg : '') + '">'; cur = k; } s += c.c.replace(/</g, '&lt;'); });
  if (cur !== null) s += '</span>' + (cur.split('|')[0] ? '</a>' : '');
  const tag = p.heading ? 'h2' : (p.type === 'LIST_ITEM' ? 'li' : 'p'); h += '<' + tag + '>' + s + '</' + tag + '>'; });
fs.writeFileSync('/tmp/claude-0/-home-user-trang/3ba9cdf0-f0cf-51c4-a48f-adbd1e263eb3/scratchpad/rv2/mo-phong-ket-qua.html', h + '</body></html>');
