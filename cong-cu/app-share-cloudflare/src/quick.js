// KẾT NỐI NHANH: đăng nhập 1 lần (Google / WordPress.com) + dán link tài khoản → app tự tạo kết nối.
// Chìa "ứng dụng" (client ID/secret) chỉ khai 1 lần trong Cài đặt; mật khẩu tài khoản KHÔNG bao giờ đi qua app.
import { rnd } from './util.js';
import { getJSON, setJSON, getSys, setSys, conns, saveConns, log, id, uid } from './store.js';
import { PLATFORMS } from './platforms.js';

async function http(method, url, { headers = {}, json, form } = {}) {
  const opt = { method, headers: { ...headers } };
  if (json !== undefined) { opt.body = JSON.stringify(json); opt.headers['Content-Type'] = 'application/json'; }
  if (form) { opt.body = new URLSearchParams(form).toString(); opt.headers['Content-Type'] = 'application/x-www-form-urlencoded'; }
  const r = await fetch(url, opt); const t = await r.text(); let d = {}; try { d = JSON.parse(t); } catch { d = { raw: t.slice(0, 300) }; }
  return { code: r.status, data: d };
}
const GSCOPE = 'openid email https://www.googleapis.com/auth/blogger https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.metadata';

export const apps = () => getSys('apps', {});
export const saveApps = (a) => setSys('apps', a);

export async function quickStart(kind, origin) {
  const A = await apps(), app = A[kind];
  if (!app?.client_id || !app?.client_secret) throw new Error('Chưa cài chìa ứng dụng ' + (kind === 'google' ? 'Google' : 'WordPress') + ' (làm 1 lần trong mục "Cài đặt 1 lần" ở trên).');
  const nonce = rnd(8); await setJSON('oauth_nonce', { kind, nonce, t: Date.now() });
  const redir = encodeURIComponent(origin + '/api/oauth/cb'), state = `q.${kind}.${uid()}.${nonce}`;
  if (kind === 'google') return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(app.client_id)}&redirect_uri=${redir}&response_type=code&access_type=offline&prompt=consent&include_granted_scopes=true&scope=${encodeURIComponent(GSCOPE)}&state=${state}`;
  return `https://public-api.wordpress.com/oauth2/authorize?client_id=${encodeURIComponent(app.client_id)}&redirect_uri=${redir}&response_type=code&scope=global&state=${state}`;
}

async function upsert(C, type, key, name, data) {
  let c = Object.values(C).find((x) => x.type === type && x.key === key);
  if (!c) { const cid = id(); c = C[cid] = { id: cid, type, key, name, created: new Date().toISOString(), data: {} }; }
  c.data = { ...c.data, ...data }; c.name = c.name || name;
  try { c.test = await PLATFORMS[type].test(c, () => saveConns(C)); c.ok = true; } catch (e) { c.test = e.message; c.ok = false; }
  c.tested = new Date().toISOString();
  return c;
}

export async function quickCallback(state, code, origin) {
  const [, kind, , nonce] = state.split('.'); const N = await getJSON('oauth_nonce', {});
  if (N.kind !== kind || N.nonce !== nonce || Date.now() - N.t > 15 * 60e3) throw new Error('Liên kết đăng nhập đã hết hạn, bấm đăng nhập lại.');
  const A = await apps(), app = A[kind], C = await conns(), out = [], redir = origin + '/api/oauth/cb';
  if (kind === 'google') {
    const r = await http('POST', 'https://oauth2.googleapis.com/token', { form: { client_id: app.client_id, client_secret: app.client_secret, redirect_uri: redir, code, grant_type: 'authorization_code' } });
    if (r.code !== 200) throw new Error('Google từ chối: ' + JSON.stringify(r.data).slice(0, 200));
    const H = { Authorization: 'Bearer ' + r.data.access_token };
    const me = (await http('GET', 'https://openidconnect.googleapis.com/v1/userinfo', { headers: H })).data;
    const email = me.email || 'google';
    const G = await getJSON('gacc', {}); G[email] = { refresh_token: r.data.refresh_token || G[email]?.refresh_token, scope: r.data.scope, at: new Date().toISOString() }; await setJSON('gacc', G);
    const base = { client_id: app.client_id, client_secret: app.client_secret, refresh_token: G[email].refresh_token, google_email: email };
    const b = await http('GET', 'https://www.googleapis.com/blogger/v3/users/self/blogs', { headers: H });
    for (const x of b.data.items || []) { const c = await upsert(C, 'blogger', 'blog:' + x.id, 'Blogger - ' + (x.url || '').replace(/^https?:\/\//, '').replace(/\/$/, ''), { ...base, blog_id: x.id, home: x.url }); out.push(c.name + ': ' + c.test); }
    for (const c of Object.values(C)) if (['blogger', 'ggroups'].includes(c.type) && c.data.google_email === email) c.data.refresh_token = base.refresh_token;   // làm mới chìa cho kết nối cũ
    if (!(b.data.items || []).length) out.push(`Gmail ${email} chưa có blog Blogger nào (vẫn dùng được cho Google Groups và ghi Sheet).`);
    out.unshift('Đã đăng nhập Google: ' + email);
  } else {
    const r = await http('POST', 'https://public-api.wordpress.com/oauth2/token', { form: { client_id: app.client_id, client_secret: app.client_secret, redirect_uri: redir, code, grant_type: 'authorization_code' } });
    if (r.code !== 200) throw new Error('WordPress từ chối: ' + JSON.stringify(r.data).slice(0, 200));
    const s = (await http('GET', `https://public-api.wordpress.com/rest/v1.1/sites/${r.data.blog_id}`, { headers: { Authorization: 'Bearer ' + r.data.access_token } })).data;
    const host = String(s.URL || r.data.blog_url || '').replace(/^https?:\/\//, '').replace(/\/$/, '');
    const c = await upsert(C, 'wordpress', 'wp:' + r.data.blog_id, 'WordPress - ' + host, { client_id: app.client_id, client_secret: app.client_secret, access_token: r.data.access_token, site_id: String(r.data.blog_id) });
    out.push(c.name + ': ' + c.test);
  }
  await setJSON('oauth_nonce', {}); await saveConns(C); await log('ĐĂNG NHẬP NHANH ' + kind, out.join(' | '));
  await setJSON('quick_result', { t: Date.now(), out });
}

// Dán link tài khoản social → nhận diện nền tảng → tự kết nối nếu đã đăng nhập, hoặc trả về form cần điền thêm
export async function addByUrl(raw, prefEmail) {
  const u = String(raw).trim(); if (!u) return null;
  const low = u.toLowerCase(), C = await conns(), G = await getJSON('gacc', {}), A = await apps();
  const gEmail = prefEmail && G[prefEmail] ? prefEmail : Object.keys(G)[0];
  const host = (low.match(/^(?:https?:\/\/)?([^/]+)/) || [])[1] || '';
  const grp = (low.match(/groups\.google\.com\/(?:a\/[^/]+\/)?g\/([\w.-]+)/) || low.match(/^([\w.-]+)@googlegroups\.com$/) || [])[1];
  if (grp) {
    if (!gEmail) return { url: u, ok: false, msg: 'Google Groups: bấm "Đăng nhập Google" trước (bằng Gmail là thành viên nhóm), rồi dán lại link.' };
    const c = await upsert(C, 'ggroups', 'grp:' + grp, 'GG Group - ' + grp, { client_id: A.google.client_id, client_secret: A.google.client_secret, refresh_token: G[gEmail].refresh_token, google_email: gEmail, group_email: grp + '@googlegroups.com' });
    await saveConns(C); return { url: u, ok: c.ok, msg: c.name + ': ' + c.test + (c.ok ? ' (Gmail ' + gEmail + ' phải là thành viên nhóm)' : '') };
  }
  if (host.endsWith('blogspot.com') || host.includes('blogger.com')) {
    const c = Object.values(C).find((x) => x.type === 'blogger' && String(x.data.home || '').toLowerCase().includes(host));
    if (c) return { url: u, ok: !!c.ok, msg: 'Blog này đã kết nối: ' + c.name };
    return { url: u, ok: false, msg: gEmail ? `Blog này không thuộc Gmail đã đăng nhập (${Object.keys(G).join(', ')}). Bấm "Đăng nhập Google" bằng Gmail sở hữu blog.` : 'Bấm "Đăng nhập Google" (bằng Gmail sở hữu blog) — app tự nhận mọi blog của Gmail đó.' };
  }
  if (host.endsWith('wordpress.com')) {
    const c = Object.values(C).find((x) => x.type === 'wordpress' && String(x.data.home || x.name).toLowerCase().includes(host));
    return c ? { url: u, ok: !!c.ok, msg: 'Blog này đã kết nối: ' + c.name } : { url: u, ok: false, msg: 'Bấm "Đăng nhập WordPress.com" rồi chọn blog này — app tự kết nối.' };
  }
  const pre = u.startsWith('http') ? u : 'https://' + u;
  if (host.includes('wixsite.com') || host.includes('wix')) return { url: u, ok: false, form: 'wix', prefill: { url_prefix: pre.replace(/\/?$/, '/') }, msg: 'Wix không có đăng nhập chung — cần 1 chìa API (mở form đã điền sẵn link).' };
  if (host.endsWith('webflow.io')) return { url: u, ok: false, form: 'webflow', prefill: { url_prefix: pre.replace(/\/?$/, '/') }, msg: 'Webflow cần 1 token của trang (mở form đã điền sẵn link).' };
  if (host.endsWith('tumblr.com')) return { url: u, ok: false, form: 'tumblr', prefill: { blog: (host.split('.')[0] === 'www' ? (low.split('/')[3] || '') : host.split('.')[0]) }, msg: 'Tumblr: mở form đã điền sẵn tên blog.' };
  if (host === 't.me') return { url: u, ok: false, form: 'telegram', prefill: { chat_id: '@' + (low.split('/')[3] || '') }, msg: 'Telegram: mở form đã điền sẵn kênh.' };
  if (/\/@[\w.]+/.test(low)) return { url: u, ok: false, form: 'mastodon', prefill: { instance: host }, msg: 'Mastodon: mở form đã điền sẵn máy chủ.' };
  return { url: u, ok: false, msg: 'Chưa nhận ra nền tảng của link này.' };
}
