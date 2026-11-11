// Cổng dữ liệu cho trang web. Mọi đường /api/* trừ ảnh công khai và trả về OAuth đều cần mật khẩu.
import crypto from 'node:crypto';
import { db, getJSON, setJSON, settings, conns, saveConns, listItems, getItem, saveItem, delItem, log, id } from './lib/store.mjs';
import { PLATFORMS, OAUTH } from './lib/platforms.mjs';
import { runOnce } from './lib/runner.mjs';
import { apps, saveApps, quickStart, quickCallback, addByUrl } from './lib/quick.mjs';

const SECRET = new Set(['api_key', 'client_secret', 'access_token', 'refresh_token', 'token', 'bot_token']);
const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: { 'Content-Type': 'application/json' } });
const hash = (pw, salt) => crypto.scryptSync(pw, salt, 32).toString('hex');
const sign = (secret, exp) => exp + '.' + crypto.createHmac('sha256', secret).update(String(exp)).digest('hex');
async function authed(req, url) {
  const a = await getJSON('auth', null); if (!a) return false;
  const tok = req.headers.get('x-token') || url.searchParams.get('t') || '';
  const [exp] = tok.split('.');
  return +exp > Date.now() && tok.length > 20 && crypto.timingSafeEqual(Buffer.from(sign(a.secret, exp)), Buffer.from(tok.padEnd(sign(a.secret, exp).length).slice(0, sign(a.secret, exp).length)));
}
const mask = (c) => ({ ...c, data: Object.fromEntries(Object.entries(c.data || {}).map(([k, v]) => [k, SECRET.has(k) && v ? '••••••' : v])) });

export default async (req) => {
  const url = new URL(req.url), path = url.pathname.replace(/^\/api\/?/, ''), origin = process.env.URL || url.origin;
  const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {};
  try {
    // ---- công khai ----
    if (path.startsWith('img/')) {
      const b = await db().get('img/' + path.slice(4).replace(/\.png$/, ''), { type: 'arrayBuffer' });
      return b ? new Response(b, { headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=31536000' } }) : new Response('not found', { status: 404 });
    }
    if (path === 'status') return json({ setup: !!(await getJSON('auth', null)) });
    if (path === 'setup') {
      if (await getJSON('auth', null)) return json({ error: 'Đã đặt mật khẩu rồi' }, 400);
      if (!body.password || body.password.length < 6) return json({ error: 'Mật khẩu ít nhất 6 ký tự' }, 400);
      const salt = crypto.randomBytes(8).toString('hex');
      await setJSON('auth', { salt, hash: hash(body.password, salt), secret: crypto.randomBytes(24).toString('hex') });
      body.password_ok = true;
    }
    if (path === 'login' || path === 'setup') {
      const a = await getJSON('auth', null);
      if (!a || hash(body.password || '', a.salt) !== a.hash) return json({ error: 'Sai mật khẩu' }, 401);
      return json({ token: sign(a.secret, Date.now() + 30 * 864e5) });
    }
    if (path === 'oauth/cb' && String(url.searchParams.get('state') || '').startsWith('q.')) {
      if (url.searchParams.get('error')) return Response.redirect(origin + '/#nhanh=huy', 302);
      try { await quickCallback(url.searchParams.get('state'), url.searchParams.get('code'), origin); }
      catch (e) { await setJSON('quick_result', { t: Date.now(), out: ['Lỗi: ' + e.message] }); }
      return Response.redirect(origin + '/#nhanh', 302);
    }
    if (path === 'oauth/cb') {
      const [cid, nonce] = String(url.searchParams.get('state') || '').split('.');
      const C = await conns(), c = C[cid];
      if (!c || c.nonce !== nonce) return new Response('Liên kết hết hạn, quay lại trang và bấm Kết nối lại.', { status: 400 });
      if (url.searchParams.get('error')) return Response.redirect(origin + '/#ketnoi=huy', 302);
      await OAUTH[c.type].exchange(c, url.searchParams.get('code'), origin + '/api/oauth/cb');
      delete c.nonce; c.ok = false;
      try { c.test = await PLATFORMS[c.type].test(c, () => saveConns(C)); c.ok = true; } catch (e) { c.test = e.message; }
      await saveConns(C); await log('KẾT NỐI ' + c.name, c.test);
      return Response.redirect(origin + '/#ketnoi=' + cid, 302);
    }
    // ---- cần đăng nhập ----
    if (!(await authed(req, url))) return json({ error: 'Cần đăng nhập' }, 401);

    if (path === 'state') {
      const C = await conns();
      const A = await apps(), G = await getJSON('gacc', {});
      const appsMask = Object.fromEntries(Object.entries(A).map(([k, v]) => [k, { client_id: v.client_id, has_secret: !!v.client_secret }]));
      return json({ apps: appsMask, gaccounts: Object.keys(G), quick: await getJSON('quick_result', null), settings: await settings(), conns: Object.values(C).map(mask), items: await listItems(), log: (await getJSON('log', [])).slice(0, 150), redirect: origin + '/api/oauth/cb', origin });
    }
    if (path === 'quick/start') return Response.redirect(await quickStart(url.searchParams.get('kind'), origin), 302);
    if (path === 'apps') {
      const A = await apps(), k = body.kind; A[k] = { ...(A[k] || {}) };
      if (body.client_id) A[k].client_id = String(body.client_id).trim();
      if (body.client_secret && body.client_secret !== '••••••') A[k].client_secret = String(body.client_secret).trim();
      await saveApps(A); return json({ ok: true });
    }
    if (path === 'quick/url') { const out = []; for (const u of body.urls || []) { const r = await addByUrl(u, body.email); if (r) out.push(r); } return json({ out }); }
    if (path === 'quick/clear') { await setJSON('quick_result', null); return json({ ok: true }); }
    if (path === 'oauth/start') {
      const C = await conns(), c = C[url.searchParams.get('id')];
      if (!c || !OAUTH[c.type]) return json({ error: 'Không có kết nối' }, 404);
      c.nonce = crypto.randomBytes(8).toString('hex'); await saveConns(C);
      return Response.redirect(OAUTH[c.type].url(c, origin + '/api/oauth/cb', c.id + '.' + c.nonce), 302);
    }
    if (path === 'conn') {
      const C = await conns(), cid = body.id || id(), old = C[cid] || { id: cid, created: new Date().toISOString(), data: {} };
      const data = { ...old.data };
      for (const [k, v] of Object.entries(body.data || {})) if (!(SECRET.has(k) && (v === '' || v === '••••••'))) data[k] = typeof v === 'string' ? v.trim() : v;
      C[cid] = { ...old, type: body.type || old.type, name: body.name || old.name, data };
      await saveConns(C); return json({ ok: true, id: cid });
    }
    if (path === 'conn/test') {
      const C = await conns(), c = C[body.id]; if (!c) return json({ error: 'Không có kết nối' }, 404);
      try { c.test = await PLATFORMS[c.type].test(c, () => saveConns(C)); c.ok = true; } catch (e) { c.test = e.message; c.ok = false; }
      c.tested = new Date().toISOString(); await saveConns(C); return json({ ok: c.ok, msg: c.test });
    }
    if (path === 'conn/delete') { const C = await conns(); delete C[body.id]; await saveConns(C); return json({ ok: true }); }
    if (path === 'conn/pause') { const C = await conns(); if (C[body.id]) { C[body.id].paused = !!body.paused; if (!body.paused) C[body.id].pause_reason = ''; } await saveConns(C); return json({ ok: true }); }

    if (path === 'image') {   // ảnh đại diện vẽ sẵn trên trình duyệt → lưu, trả link công khai
      const b64 = String(body.data || '').replace(/^data:image\/png;base64,/, '');
      const key = id() + id(); await db().set('img/' + key, Buffer.from(b64, 'base64'));
      return json({ url: origin + '/api/img/' + key + '.png' });
    }
    if (path === 'item') {
      const old = body.id ? await getItem(body.id) : null;
      const it = { ...(old || { id: id(), created: new Date().toISOString() }), ...body };
      it.jobs = (body.jobs || []).map((j) => { const o = (old?.jobs || []).find((x) => x.conn === j.conn); return o && ['da_dang', 'dang'].includes(o.status) ? o : { ...o, ...j }; });
      await saveItem(it); return json({ ok: true, id: it.id });
    }
    if (path === 'items/import') {
      let n = 0; for (const x of body.items || []) { await saveItem({ id: id(), created: new Date().toISOString(), ...x }); n++; }
      await log('NHẬP HÀNG LOẠT', n + ' bài'); return json({ ok: true, n });
    }
    if (path === 'item/delete') { await delItem(body.id); return json({ ok: true }); }
    if (path === 'job') {   // đổi trạng thái 1 việc đăng: cho / tam_giu / đặt lại sau lỗi
      const it = await getItem(body.item); const j = it?.jobs.find((x) => x.conn === body.conn);
      if (!j) return json({ error: 'Không thấy' }, 404);
      if (j.status === 'da_dang') return json({ error: 'Bài đã đăng, không đổi được' }, 400);
      j.status = body.status; if (body.at) j.at = body.at; j.err = ''; await saveItem(it); return json({ ok: true });
    }
    if (path === 'settings') { await setJSON('settings', { ...(await settings()), ...body }); return json({ ok: true }); }
    if (path === 'run') return json({ out: await runOnce({ force: true, maxPublish: 1 }) });
    return json({ error: 'Không có đường này' }, 404);
  } catch (e) {
    return json({ error: e.message }, 500);
  }
};
export const config = { path: '/api/*' };
