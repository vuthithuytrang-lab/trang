// Cửa sổ điều khiển: kiểm tra Last crawl từng URL, bỏ qua URL Google đã đọc sau mốc giờ,
// ép phần còn lại đến khi thành công. Logic bấm/đọc giữ nguyên skill gốc (mac/request.sh, mac/inspect.sh):
// chỉ tính OK khi thấy "Testing if live URL" rồi hộp thoại "Indexing requested" MỚI.
const WAIT_RETRY = 60, WAIT_REJECTED = 15, WAIT_QUOTA = 30 * 60;
const $ = (id) => document.getElementById(id);

// ---------- Đồng hồ không bị làm chậm ----------
const timer = new Worker('timer.js');
const waits = {}; let waitId = 0;
timer.onmessage = (e) => { waits[e.data](); delete waits[e.data]; };
const sleep = (sec) => new Promise((r) => { const id = ++waitId; waits[id] = r; timer.postMessage({ id, ms: sec * 1000 }); });

// ---------- Nhật ký + kết quả ----------
let stopFlag = false, results = {};
function log(s) {
  const d = new Date(), t = d.toLocaleTimeString('vi-VN', { hour12: false });
  const box = $('nhatky');
  box.textContent += `[${t}] ${s}\n`;
  box.scrollTop = box.scrollHeight;
}
function status(s) { $('trangthai').textContent = s; }
async function saveResult(u, kq, note) {
  results[u] = { kq, note, moc: $('moc').value };
  await chrome.storage.local.set({ results });
  showCount();
}
function showCount() {
  const v = Object.values(results), c = (k) => v.filter((x) => x.kq === k).length;
  $('dem').textContent = `Đã đọc: ${c('DA-DOC')} · Ép OK: ${c('OK')} · Bỏ qua: ${c('SKIP')}`;
}

// ---------- Các hàm chạy bên trong tab GSC ----------
const P = {
  // Chặn Chrome tự dịch trang (bản dịch làm hỏng việc nhận diện chữ tiếng Anh)
  notranslate() {
    document.documentElement.setAttribute('translate', 'no');
    document.documentElement.classList.add('notranslate');
    if (!document.querySelector('meta[name=google][content=notranslate]')) {
      const m = document.createElement('meta'); m.name = 'google'; m.content = 'notranslate'; document.head.appendChild(m);
    }
    return document.documentElement.classList.contains('translated-ltr') || document.documentElement.classList.contains('translated-rtl') ? 'TRANSLATED' : 'OK';
  },
  async fill(u) {
    const find = () => [...document.querySelectorAll('input')].find((x) => /Inspect any URL/.test(x.getAttribute('aria-label') || '') && x.offsetParent);
    let i = find();
    if (!i) {
      // cửa sổ hẹp: ô tìm kiếm thu thành kính lúp → bấm để mở ra
      const b = [...document.querySelectorAll('[role=button],button')].find((x) => /Inspect|Search/i.test(x.getAttribute('aria-label') || '') && x.offsetParent);
      if (b) { b.click(); await new Promise((r) => setTimeout(r, 1000)); i = find(); }
    }
    if (!i) return 0;
    i.focus(); i.value = u; i.dispatchEvent(new Event('input', { bubbles: true }));
    const o = { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true };
    ['keydown', 'keypress', 'keyup'].forEach((t) => i.dispatchEvent(new KeyboardEvent(t, o)));
    return 1;
  },
  read(u) {
    const t = document.body.innerText;
    if (!location.pathname.includes('inspect') || !t.includes(u) || /Retrieving data/i.test(t) ||
        !/URL is (not )?on Google|unknown to Google|not in (the current )?property/i.test(t)) return 'loading';
    const m = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && e.textContent.trim() === 'Last crawl');
    const lc = m.map((x) => x.parentElement.parentElement.textContent.replace('Last crawl', '').replace(/Crawled as.*/, '').trim()).join(' || ');
    const st = (t.match(/URL is (not )?on Google|URL is unknown to Google|not in (the current )?property/i) || [''])[0];
    return { st, lc, href: location.href };
  },
  ready(u) {
    const t = document.body.innerText;
    if (/not in (the current )?property/i.test(t)) return 'NOTPROP';
    if (!location.pathname.includes('inspect') || !t.includes(u) || /Retrieving data/i.test(t)) return 'loading';
    return /REQUEST INDEXING/i.test(t) ? 'READY' : 'loading';
  },
  click(src) {
    const lbl = new RegExp(src, 'i');
    const bs = [...document.querySelectorAll('[role=button]')].filter((e) => lbl.test((e.innerText || '').trim()) && e.offsetParent);
    bs.forEach((b) => {
      const r = b.getBoundingClientRect(), o = { bubbles: true, cancelable: true, view: window, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2, button: 0 };
      ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach((t) => b.dispatchEvent(new (t.startsWith('pointer') ? PointerEvent : MouseEvent)(t, o)));
    });
    return bs.length;
  },
  dismiss() {
    const bs = [...document.querySelectorAll('button')].filter((b) => /^Dismiss$/i.test((b.innerText || '').trim()) && b.offsetParent);
    bs.forEach((b) => b.click());
    return bs.length;
  },
  vis() {
    return [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && /Indexing requested/.test(e.textContent) && e.offsetParent).length;
  },
  watch() {
    const t = document.body.innerText;
    if (/Indexing request rejected/i.test(t)) return 'rejected';
    const m = t.match(/Quota exceeded|Something went wrong|not a robot|recaptcha/i);
    if (m) return m[0];
    const vis = [...document.querySelectorAll('*')].filter((e) => e.children.length === 0 && /Indexing requested/.test(e.textContent) && e.offsetParent).length;
    if (vis > 0 && /added to a priority crawl queue/i.test(t)) return 'requested';
    return /Testing if live URL/i.test(t) ? 'testing' : 'none';
  },
};

// ---------- Điều khiển tab ----------
let tabId = null, rid = '';
async function findTab(domain) {
  // phóng to cửa sổ GSC để ô "Kiểm tra URL" hiện đầy đủ
  const tabs = await chrome.tabs.query({ url: 'https://search.google.com/search-console*' });
  const t = tabs.find((x) => x.url.includes(domain) && /[?&]resource_id=/.test(x.url));
  if (!t) throw new Error(`Không thấy tab Search Console của ${domain}. Hãy mở trang Tổng quan của ${domain} trong Chrome này.`);
  tabId = t.id;
  rid = t.url.match(/[?&]resource_id=([^&#]*)/)[1];
  await chrome.tabs.update(tabId, { active: true });
  await chrome.windows.update(t.windowId, { state: 'maximized' }).catch(() => {});
}
async function run(fn, ...args) {
  try {
    const [r] = await chrome.scripting.executeScript({ target: { tabId }, func: fn, args });
    return r ? r.result : null;
  } catch (e) {
    if (/No tab with id/i.test(e.message)) throw new Error('Tab Search Console đã bị đóng. Hãy mở lại rồi bấm Bắt đầu.');
    return null; // tab đang tải trang
  }
}
async function nav(url) {
  await chrome.tabs.update(tabId, { url });
  for (let i = 0; i < 30; i++) {
    await sleep(1);
    const t = await chrome.tabs.get(tabId);
    if (t.status === 'complete') break;
  }
}
let warnedTranslate = false;
async function home() {
  await nav(`https://search.google.com/search-console?resource_id=${rid}&hl=en`);
  await sleep(1);
  if ((await run(P.notranslate)) === 'TRANSLATED' && !warnedTranslate) {
    warnedTranslate = true;
    log('⚠️ Chrome đang tự dịch trang GSC — hãy tắt dịch cho trang này (xem hướng dẫn của Claude)');
  }
}
const CLOSE = '^(Dismiss|GOT IT)$';

// ---------- Đọc Last crawl ----------
async function inspect(u) {
  await home(); await sleep(6);
  let r = null;
  for (let k = 0; k < 3 && !(r && r.st !== undefined); k++) {
    if (!(await run(P.fill, u))) log('  Chưa thấy ô Kiểm tra URL, đang thử lại...');
    for (let i = 0; i < 15; i++) { await sleep(3); r = await run(P.read, u); if (r && r.st !== undefined) break; }
    if (!(r && r.st !== undefined)) await sleep(3);
  }
  if (!(r && r.st !== undefined)) return null;
  // tải lại đúng trang kết quả cho sạch rồi đọc lại
  await nav(r.href); await sleep(5);
  for (let i = 0; i < 20; i++) { r = await run(P.read, u); if (r && r.st !== undefined) return r; await sleep(3); }
  return null;
}

// "Oct 30, 2026, 9:15:23 PM" → Date (giờ máy, cũng là giờ GSC hiển thị); không đọc được → null
const MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11 };
function parseCrawl(s) {
  if (!s) return null;
  s = s.split(' || ')[0].replace(/[  ]/g, ' ');
  const m = s.match(/([A-Z][a-z]{2}) (\d{1,2}), (\d{4}),? (\d{1,2}):(\d{2})(?::(\d{2}))? ?([AP]M)/);
  if (!m || !(m[1] in MON)) return null;
  let h = +m[4] % 12; if (m[7] === 'PM') h += 12;
  return new Date(+m[3], MON[m[1]], +m[2], h, +m[5], +(m[6] || 0));
}
const fmt = (d) => d.toLocaleString('vi-VN', { hour12: false, day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

// Google đã đọc sau mốc chưa? → 'NOTPROP' | chữ giờ đọc | null (chưa)
async function freshSince(u, cut) {
  const r = await inspect(u);
  if (!r) { log('  Không đọc được trang kiểm tra — coi như chưa đọc'); return null; }
  if (/not in/i.test(r.st)) return 'NOTPROP';
  const d = parseCrawl(r.lc);
  if (d && d >= cut) return fmt(d);
  log(`  Last crawl: ${r.lc || '(không có)'}`);
  return null;
}

// ---------- Một lần Request indexing ----------
// → OK | SKIP | REJECTED | QUOTA | ROBOT | FAIL:<lý do>
async function request(u) {
  await home(); await sleep(7);
  let st = '';
  for (let k = 0; k < 3; k++) {
    await run(P.click, CLOSE); await sleep(1);
    if (!(await run(P.fill, u))) log('  Chưa thấy ô Kiểm tra URL, đang thử lại...');
    for (let i = 0; i < 15; i++) { await sleep(3); st = await run(P.ready, u); if (st === 'READY' || st === 'NOTPROP') break; }
    if (st === 'READY' || st === 'NOTPROP') break;
  }
  if (st === 'NOTPROP') return 'SKIP';
  if (st !== 'READY') return 'FAIL:không mở được trang kiểm tra';
  await run(P.click, CLOSE); await sleep(1);
  if ((await run(P.vis)) !== 0) return 'FAIL:hộp thoại cũ chưa đóng';
  await run(P.click, '^REQUEST INDEXING$');
  let seen = false, r = 'none';
  for (let i = 0; i < 200; i++) {
    await sleep(3);
    r = (await run(P.watch)) || 'none';
    if (r === 'testing') seen = true;
    if (r !== 'none' && r !== 'testing') break;
  }
  let res;
  if (r === 'requested' && seen) res = 'OK';
  else if (r === 'rejected') { await run(P.dismiss); res = 'REJECTED'; }
  else if (/Quota/i.test(r)) res = 'QUOTA';
  else if (/robot|recaptcha/i.test(r)) res = 'ROBOT';
  else res = `FAIL:${r} (testing_seen=${seen})`;
  await run(P.click, CLOSE);
  return res;
}

// ---------- Chạy cả danh sách ----------
async function main() {
  const domain = $('domain').value.trim();
  const cut = new Date($('moc').value);
  if (isNaN(cut)) throw new Error('Chưa nhập giờ publish.');
  const urls = [...new Set($('urls').value.split(/\s+/).filter((x) => /^https?:\/\//.test(x)))];
  await findTab(domain);
  log(`Bắt đầu: ${urls.length} link, mốc ${fmt(cut)}`);

  // Link đã xong ở lần chạy trước (cùng mốc giờ) thì không làm lại
  const done = (u) => results[u] && results[u].moc === $('moc').value && ['OK', 'DA-DOC', 'SKIP'].includes(results[u].kq);

  status('Bước 1: kiểm tra Google đã đọc link nào');
  const todo = [];
  for (const [i, u] of urls.entries()) {
    if (stopFlag) return;
    if (done(u)) { log(`[${i + 1}] đã xong từ trước: ${u}`); continue; }
    status(`Bước 1: kiểm tra ${i + 1}/${urls.length}`);
    const f = await freshSince(u, cut);
    if (f === 'NOTPROP') { await saveResult(u, 'SKIP', 'không thuộc property'); log(`[${i + 1}] BỎ QUA (không thuộc website): ${u}`); }
    else if (f) { await saveResult(u, 'DA-DOC', `Google đọc lúc ${f}`); log(`[${i + 1}] ĐÃ ĐỌC lúc ${f}: ${u}`); }
    else { todo.push(u); log(`[${i + 1}] CẦN ÉP: ${u}`); }
  }

  log(`=== Cần ép ${todo.length} link`);
  for (const [i, u] of todo.entries()) {
    let n = 0;
    while (!stopFlag) {
      n++;
      status(`Bước 2: ép ${i + 1}/${todo.length} — lần ${n}`);
      const r = await request(u);
      if (r === 'OK') { await saveResult(u, 'OK', `ép lúc ${fmt(new Date())}`); log(`[${i + 1}/${todo.length}] OK sau ${n} lần: ${u}`); break; }
      if (r === 'SKIP') { await saveResult(u, 'SKIP', 'không thuộc property'); log(`[${i + 1}/${todo.length}] BỎ QUA: ${u}`); break; }
      if (r === 'ROBOT') {
        status('⚠️ Google hiện ô "Tôi không phải robot" — hãy bấm ô đó trong tab GSC, rồi bấm Bắt đầu lại');
        log('DỪNG: gặp ô "Tôi không phải robot"');
        alert('Google hiện ô "Tôi không phải robot". Bạn bấm ô đó trong tab Search Console, rồi bấm Bắt đầu lại.');
        return;
      }
      log(`  lần ${n} chưa được (${r})`);
      if (r === 'QUOTA') {
        status(`Hết lượt ép trong ngày — chờ 30 phút rồi thử lại (link ${i + 1}/${todo.length})`);
        log('  Hết lượt ép của Google — chờ 30 phút');
        await sleep(WAIT_QUOTA);
        if (stopFlag) return;
        const f = await freshSince(u, cut);
        if (f && f !== 'NOTPROP') { await saveResult(u, 'DA-DOC', `Google đọc lúc ${f}`); log(`  Google đã tự đọc lúc ${f} — thôi ép`); break; }
      } else await sleep(r === 'REJECTED' ? WAIT_REJECTED : WAIT_RETRY);
    }
  }
  if (!stopFlag) { status('✅ Xong. Bấm "Sao chép kết quả" rồi dán vào chat cho Claude.'); log('=== XONG'); }
}

// ---------- Nút bấm ----------
$('batdau').onclick = async () => {
  stopFlag = false;
  $('batdau').disabled = true; $('dung').disabled = false;
  try { await main(); }
  catch (e) { status('⚠️ ' + e.message); log('DỪNG: ' + e.message); }
  $('batdau').disabled = false; $('dung').disabled = true;
  if (stopFlag) status('Đã dừng. Bấm Bắt đầu để chạy tiếp, link đã xong sẽ không làm lại.');
};
$('dung').onclick = () => { stopFlag = true; status('Đang dừng sau bước hiện tại...'); };
$('xoa').onclick = async () => {
  if (!confirm('Xoá hết kết quả đã lưu?')) return;
  results = {}; await chrome.storage.local.set({ results }); showCount();
};
$('saochep').onclick = async () => {
  const rows = Object.entries(results).map(([u, r]) => `${u}\t${r.kq}\t${r.note}`);
  await navigator.clipboard.writeText(['URL\tKết quả\tGhi chú', ...rows].join('\n'));
  status(`Đã sao chép ${rows.length} dòng — dán vào chat cho Claude.`);
};
chrome.storage.local.get('results').then((s) => { results = s.results || {}; showCount(); });
