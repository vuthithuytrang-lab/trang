// APP SHARE BÀI trên Cloudflare Workers — giao diện (public/) + cổng /api + lịch tự đăng 10 phút/lần.
// Tài khoản riêng cho từng người; người đầu tiên đăng ký là quản trị (duyệt thành viên mới).
import { withCtx, getJSON, setJSON, getSys, setSys, settings, conns, saveConns, listItems, getItem, saveItem, saveItems, delItem, log, id, putImg, getImg } from './store.js';
import { PLATFORMS, OAUTH } from './platforms.js';
import { runOnce } from './runner.js';
import { apps, saveApps, quickStart, quickCallback, addByUrl } from './quick.js';
import { rnd, hashPw, hmac, safeEq, b64ToBytes } from './util.js';

const VERSION = '2026-11-11b';
const SECRET = new Set(['api_key', 'client_secret', 'access_token', 'refresh_token', 'token', 'bot_token']);
const json = (d, s = 200) => new Response(JSON.stringify(d), { status: s, headers: { 'Content-Type': 'application/json' } });
const mask = (c) => ({ ...c, data: Object.fromEntries(Object.entries(c.data || {}).map(([k, v]) => [k, SECRET.has(k) && v ? '••••••' : v])) });
const normEmail = (e) => String(e || '').trim().toLowerCase();

async function sysSecret(env) {
  let s = await env.KV.get('sys:secret'); if (!s) { s = rnd(24); await env.KV.put('sys:secret', s); } return s;
}
async function makeToken(env, uid) { const exp = Date.now() + 30 * 864e5; return `${uid}.${exp}.${await hmac(await sysSecret(env), uid + '.' + exp)}`; }
async function readToken(env, tok) {
  const [uid, exp, sig] = String(tok || '').split('.'); if (!uid || !sig || +exp < Date.now()) return null;
  return safeEq(await hmac(await sysSecret(env), uid + '.' + exp), sig) ? uid : null;
}
const users = (env) => env.KV.get('sys:users', 'json').then((v) => v || {});      // email -> {uid,name,salt,hash,role,approved,created}
const saveUsers = (env, u) => env.KV.put('sys:users', JSON.stringify(u));

async function api(req, env, url, origin) {
  const path = url.pathname.replace(/^\/api\/?/, '');
  const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {};

  // ---------- công khai ----------
  if (path.startsWith('img/')) {
    const b = await getImg(env, path.slice(4).replace(/\.png$/, ''));
    return b ? new Response(b, { headers: { 'Content-Type': 'image/png', 'Cache-Control': 'public, max-age=31536000' } }) : new Response('not found', { status: 404 });
  }
  if (path === 'status') { const U = await users(env); return json({ users: Object.keys(U).length, version: VERSION }); }
  if (path === 'register') {
    const U = await users(env), email = normEmail(body.email), first = !Object.keys(U).length;
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return json({ error: 'Email chưa đúng' }, 400);
    if (String(body.password || '').length < 6) return json({ error: 'Mật khẩu ít nhất 6 ký tự' }, 400);
    if (U[email]) return json({ error: 'Email này đã có tài khoản — bấm Đăng nhập' }, 400);
    const salt = rnd(8);
    U[email] = { uid: rnd(6), name: String(body.name || email.split('@')[0]).slice(0, 60), salt, hash: await hashPw(body.password, salt), role: first ? 'admin' : 'member', approved: first, created: new Date().toISOString() };
    await saveUsers(env, U);
    if (!first) return json({ pending: true, msg: 'Đã tạo tài khoản. Chờ quản trị duyệt rồi đăng nhập lại.' });
    return json({ token: await makeToken(env, U[email].uid) });
  }
  if (path === 'login') {
    const U = await users(env), u = U[normEmail(body.email)];
    if (!u || !safeEq(await hashPw(String(body.password || ''), u.salt), u.hash)) return json({ error: 'Sai email hoặc mật khẩu' }, 401);
    if (!u.approved) return json({ error: 'Tài khoản đang chờ quản trị duyệt' }, 403);
    return json({ token: await makeToken(env, u.uid) });
  }
  if (path === 'oauth/cb') {   // nền tảng trả về sau khi bấm "Cho phép" — trạng thái mang theo mã người dùng
    const st = String(url.searchParams.get('state') || '');
    if (st.startsWith('q.')) {
      const uidQ = st.split('.')[2];
      return withCtx(env, uidQ, async () => {
        if (url.searchParams.get('error')) return Response.redirect(origin + '/share/#nhanh=huy', 302);
        try { await quickCallback(st, url.searchParams.get('code'), origin); } catch (e) { await setJSON('quick_result', { t: Date.now(), out: ['Lỗi: ' + e.message] }); }
        return Response.redirect(origin + '/share/#nhanh', 302);
      });
    }
    const [, uidC, cid, nonce] = st.split('.');
    return withCtx(env, uidC, async () => {
      const C = await conns(), c = C[cid];
      if (!c || c.nonce !== nonce) return new Response('Liên kết hết hạn, quay lại app và bấm Kết nối lại.', { status: 400 });
      if (url.searchParams.get('error')) return Response.redirect(origin + '/share/#ketnoi=huy', 302);
      await OAUTH[c.type].exchange(c, url.searchParams.get('code'), origin + '/api/oauth/cb');
      delete c.nonce; c.ok = false;
      try { c.test = await PLATFORMS[c.type].test(c, () => saveConns(C)); c.ok = true; } catch (e) { c.test = e.message; }
      await saveConns(C); await log('KẾT NỐI ' + c.name, c.test);
      return Response.redirect(origin + '/share/#ketnoi=' + cid, 302);
    });
  }

  // ---------- cần đăng nhập ----------
  const uid = await readToken(env, req.headers.get('x-token') || url.searchParams.get('t'));
  if (!uid) return json({ error: 'Cần đăng nhập' }, 401);
  const U = await users(env), me = Object.entries(U).find(([, v]) => v.uid === uid);
  if (!me || !me[1].approved) return json({ error: 'Cần đăng nhập' }, 401);
  const isAdmin = me[1].role === 'admin';

  return withCtx(env, uid, async () => {
    if (path === 'state') {
      const C = await conns(), A = await apps(), G = await getJSON('gacc', {});
      const appsMask = Object.fromEntries(Object.entries(A).map(([k, v]) => [k, { client_id: v.client_id, has_secret: !!v.client_secret }]));
      return json({ me: { email: me[0], name: me[1].name, admin: isAdmin }, version: VERSION, apps: appsMask, gaccounts: Object.keys(G), quick: await getJSON('quick_result', null),
        settings: await settings(), conns: Object.values(C).map(mask), items: await listItems(), log: (await getJSON('log', [])).slice(0, 150), redirect: origin + '/api/oauth/cb', origin,
        members: isAdmin ? Object.entries(U).map(([e, v]) => ({ email: e, name: v.name, role: v.role, approved: v.approved, created: v.created })) : undefined });
    }
    if (path === 'members' && isAdmin) {      // duyệt / gỡ thành viên
      const t = U[normEmail(body.email)]; if (!t) return json({ error: 'Không thấy' }, 404);
      if (body.action === 'approve') t.approved = true;
      if (body.action === 'remove' && t.uid !== uid) delete U[normEmail(body.email)];
      await saveUsers(env, U); return json({ ok: true });
    }
    if (path === 'password') {
      if (!safeEq(await hashPw(String(body.old || ''), me[1].salt), me[1].hash)) return json({ error: 'Mật khẩu cũ chưa đúng' }, 400);
      if (String(body.new || '').length < 6) return json({ error: 'Mật khẩu mới ít nhất 6 ký tự' }, 400);
      me[1].salt = rnd(8); me[1].hash = await hashPw(body.new, me[1].salt); await saveUsers(env, U); return json({ ok: true });
    }
    if (path === 'quick/start') return Response.redirect(await quickStart(url.searchParams.get('kind'), origin), 302);
    if (path === 'apps') {
      if (!isAdmin) return json({ error: 'Chỉ quản trị khai chìa ứng dụng (dùng chung cả team)' }, 403);
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
      c.nonce = rnd(8); await saveConns(C);
      return Response.redirect(OAUTH[c.type].url(c, origin + '/api/oauth/cb', `c.${uid}.${c.id}.${c.nonce}`), 302);
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
    if (path === 'image') {
      const key = rnd(12); await putImg(env, key, b64ToBytes(String(body.data || '').replace(/^data:image\/png;base64,/, '')));
      return json({ url: origin + '/api/img/' + key + '.png' });
    }
    if (path === 'item') {
      const old = body.id ? await getItem(body.id) : null;
      const it = { ...(old || { id: id(), created: new Date().toISOString() }), ...body };
      it.jobs = (body.jobs || []).map((j) => { const o = (old?.jobs || []).find((x) => x.conn === j.conn); return o && ['da_dang', 'dang'].includes(o.status) ? o : { ...o, ...j }; });
      await saveItem(it); return json({ ok: true, id: it.id });
    }
    if (path === 'items/import') {
      const list = (body.items || []).map((x) => ({ id: id(), created: new Date().toISOString(), ...x }));
      await saveItems(list); await log('NHẬP HÀNG LOẠT', list.length + ' bài'); return json({ ok: true, n: list.length });
    }
    if (path === 'item/delete') { await delItem(body.id); return json({ ok: true }); }
    if (path === 'job') {
      const it = await getItem(body.item); const j = it?.jobs.find((x) => x.conn === body.conn);
      if (!j) return json({ error: 'Không thấy' }, 404);
      if (j.status === 'da_dang') return json({ error: 'Bài đã đăng, không đổi được' }, 400);
      j.status = body.status; if (body.at) j.at = body.at; j.err = ''; await saveItem(it); return json({ ok: true });
    }
    if (path === 'settings') { await setJSON('settings', { ...(await settings()), ...body }); return json({ ok: true }); }
    if (path === 'run') return json({ out: await runOnce({ force: true, maxPublish: 1 }) });
    return json({ error: 'Không có đường này' }, 404);
  });
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), origin = url.origin;
    if (url.pathname.startsWith('/api/')) {
      try { return await api(req, env, url, origin); } catch (e) { return json({ error: e.message }, 500); }
    }
    return env.ASSETS.fetch(req);
  },
  // Lịch tự đăng: mỗi 10 phút, lần lượt từng người dùng đã được duyệt (mỗi tài khoản tối đa 1 bài/lượt)
  async scheduled(_ev, env, ctx) {
    const U = await users(env);
    for (const u of Object.values(U)) {
      if (!u.approved) continue;
      ctx.waitUntil(withCtx(env, u.uid, async () => { try { await runOnce(); } catch (e) { await log('LỖI lượt tự động', e.message); } }));
    }
  },
};
