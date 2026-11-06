// Chạy thử phần lõi trên bài thật: node test/chay-thu.js <file.html> <url> <tcb|oka>
const fs = require('fs'); const C = require('../Core.gs.js');
const [,, f, url, kieu] = process.argv;
const html = fs.readFileSync(f, 'utf8');
const SEL = { tcb: /<div[^>]*class=["'][^"']*\barticle-text\b[^"']*["'][^>]*>/, oka: /<(?:div|section)[^>]*data-hook=["']post-description["'][^>]*>/ };
const BASE = { tcb: 'https://techcombank.com', oka: 'https://www.okamura.com.vn' };
const info = C.layThongTinTrang(html);
let k = C.catKhoi(html, SEL[kieu]);
if (!k) { console.log('KHÔNG TÌM THẤY THÂN BÀI'); process.exit(1); }
let than = k.inner;
if (kieu === 'tcb') [/<div[^>]*class=["'][^"']*\bcurrency-converter\b[^"']*["'][^>]*>/, /<div[^>]*class=["'][^"']*\blist-?tiles?\b[^"']*["'][^>]*>/].forEach(r => than = C.xoaKhoi(than, r));
than = C.lamSachThanBai(than, BASE[kieu]);
const doc = C.dungHtmlDoc(url, info, than);
const txt = than.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ');
console.log(JSON.stringify({ title: info.title, kw: C.tuKhoaTuSlug(url, [info.h1, info.title, info.meta, txt]), len: doc.length,
  p: (than.match(/<p\b/g)||[]).length, h2: (than.match(/<h2\b/g)||[]).length, li: (than.match(/<li\b/g)||[]).length,
  img: (than.match(/<img\b/g)||[]).length, a: (than.match(/<a\b/g)||[]).length, words: txt.split(' ').length }));
fs.writeFileSync(process.argv[5] || '/dev/null', doc);
