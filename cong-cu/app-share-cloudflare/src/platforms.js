// Các nền tảng: mỗi loại có test() (kiểm tra kết nối, chỉ đọc) và publish() (đăng thẳng, không tạo nháp).
import { rnd, b64utf8, b64url } from './util.js';

async function http(method, url, { headers = {}, json, form, raw } = {}) {
  const opt = { method, headers: { ...headers } };
  if (json !== undefined) { opt.body = JSON.stringify(json); opt.headers['Content-Type'] = 'application/json'; }
  if (form) { opt.body = new URLSearchParams(form).toString(); opt.headers['Content-Type'] = 'application/x-www-form-urlencoded'; }
  if (raw) opt.body = raw;
  const r = await fetch(url, opt);
  const text = await r.text();
  let data = {}; try { data = JSON.parse(text); } catch { data = { raw: text.slice(0, 300) }; }
  return { code: r.status, data };
}
const fail = (where, r) => { throw new Error(`${where} lỗi ${r.code}: ${JSON.stringify(r.data).slice(0, 250)}`); };

// ---------- chuyển HTML đơn giản (p, h2, h3, ul/ol/li, strong, a) ----------
const decode = (t) => t.replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
export const strip = (h) => decode(String(h).replace(/<[^>]+>/g, '')).trim();
function blocks(html) {   // -> [{tag, inner}] ; tag: p|h2|h3|ul-li|ol-li
  const out = []; const s = String(html).replace(/\r/g, '');
  const re = /<(p|h2|h3|ul|ol)[^>]*>([\s\S]*?)<\/\1>/gi; let m;
  while ((m = re.exec(s))) {
    const tag = m[1].toLowerCase();
    if (tag === 'ul' || tag === 'ol') {
      const li = /<li[^>]*>([\s\S]*?)<\/li>/gi; let x;
      while ((x = li.exec(m[2]))) out.push({ tag: tag + '-li', inner: x[1].trim() });
    } else out.push({ tag, inner: m[2].trim() });
  }
  if (!out.length && strip(s)) strip(s).split(/\n\s*\n/).forEach((p) => out.push({ tag: 'p', inner: p }));
  return out;
}
function runs(inner) {     // -> [{text, bold, link}]
  const res = []; const re = /<(\/?)(strong|b|a)([^>]*)>/gi; let pos = 0, bold = false, link = null, m;
  const push = (t) => { t = decode(t.replace(/<[^>]+>/g, '')); if (t) res.push({ text: t, bold, link }); };
  while ((m = re.exec(inner))) {
    push(inner.slice(pos, m.index)); const close = m[1] === '/';
    if (m[2].toLowerCase() !== 'a') bold = !close; else link = close ? null : ((m[3].match(/href="([^"]+)"/) || [])[1] || null);
    pos = re.lastIndex;
  }
  push(inner.slice(pos)); return res;
}
const nid = () => rnd(4);
export function toRicos(html) {
  const out = []; let list = null, listTag = null;
  const para = (inner) => ({ type: 'PARAGRAPH', id: nid(), paragraphData: {}, nodes: runs(inner).map((r) => ({
    type: 'TEXT', id: '', nodes: [], textData: { text: r.text, decorations: [
      ...(r.bold ? [{ type: 'BOLD', fontWeightValue: 700 }] : []),
      ...(r.link ? [{ type: 'LINK', linkData: { link: { url: r.link, target: 'BLANK', rel: { noreferrer: true } } } }] : [])] } })) });
  for (const b of blocks(html)) {
    if (b.tag.endsWith('-li')) {
      if (listTag !== b.tag) { list = b.tag === 'ul-li' ? { type: 'BULLETED_LIST', id: nid(), nodes: [], bulletedListData: { indentation: 0 } } : { type: 'ORDERED_LIST', id: nid(), nodes: [], orderedListData: { indentation: 0 } }; out.push(list); listTag = b.tag; }
      list.nodes.push({ type: 'LIST_ITEM', id: nid(), nodes: [para(b.inner)] });
      continue;
    }
    listTag = null;
    if (b.tag === 'p') out.push(para(b.inner));
    else out.push({ ...para(b.inner), type: 'HEADING', paragraphData: undefined, headingData: { level: +b.tag[1] } });
  }
  return out;
}
function toGutenberg(html) {
  const out = []; let open = null;
  const close = () => { if (open) { out.push(open === 'ul-li' ? '</ul>\n<!-- /wp:list -->' : '</ol>\n<!-- /wp:list -->'); open = null; } };
  for (const b of blocks(html)) {
    if (b.tag.endsWith('-li')) {
      if (open !== b.tag) { close(); out.push(b.tag === 'ul-li' ? '<!-- wp:list -->\n<ul class="wp-block-list">' : '<!-- wp:list {"ordered":true} -->\n<ol class="wp-block-list">'); open = b.tag; }
      out.push(`<!-- wp:list-item -->\n<li>${b.inner}</li>\n<!-- /wp:list-item -->`); continue;
    }
    close();
    if (b.tag === 'p') out.push(`<!-- wp:paragraph -->\n<p>${b.inner}</p>\n<!-- /wp:paragraph -->`);
    else if (b.tag === 'h2') out.push(`<!-- wp:heading -->\n<h2 class="wp-block-heading">${b.inner}</h2>\n<!-- /wp:heading -->`);
    else out.push(`<!-- wp:heading {"level":3} -->\n<h3 class="wp-block-heading">${b.inner}</h3>\n<!-- /wp:heading -->`);
  }
  close(); return out.join('\n\n');
}
function toNPF(html) {      // Tumblr
  return blocks(html).map((b) => {
    let text = '', fmt = [];
    for (const r of runs(b.inner)) {
      const s = [...text].length, e = s + [...r.text].length;
      if (r.bold) fmt.push({ start: s, end: e, type: 'bold' });
      if (r.link) fmt.push({ start: s, end: e, type: 'link', url: r.link });
      text += r.text;
    }
    const blk = { type: 'text', text };
    if (b.tag === 'h2') blk.subtype = 'heading1'; else if (b.tag === 'h3') blk.subtype = 'heading2';
    else if (b.tag === 'ul-li') blk.subtype = 'unordered-list-item'; else if (b.tag === 'ol-li') blk.subtype = 'ordered-list-item';
    if (fmt.length) blk.formatting = fmt;
    return blk;
  });
}
export const shortText = (item, n = 280) => {
  const t = item.short || strip((String(item.html).match(/<p[^>]*>([\s\S]*?)<\/p>/i) || [, item.html])[1]);
  return t.length > n ? t.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : t;
};
const escT = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ---------- Google (Blogger + ghi Sheet) ----------
export async function googleToken(c) {
  const r = await http('POST', 'https://oauth2.googleapis.com/token', { form: {
    client_id: c.data.client_id, client_secret: c.data.client_secret, refresh_token: c.data.refresh_token, grant_type: 'refresh_token' } });
  if (r.code !== 200) fail('Google cấp quyền (có thể chìa hết hạn — bấm Kết nối lại)', r);
  return r.data.access_token;
}
// ---------- Tumblr (chìa hết hạn ~40 phút, tự làm mới) ----------
async function tumblrToken(c, save) {
  if (c.data.access_token && c.data.expires_at > Date.now() + 60e3) return c.data.access_token;
  const r = await http('POST', 'https://api.tumblr.com/v2/oauth2/token', { form: {
    grant_type: 'refresh_token', refresh_token: c.data.refresh_token, client_id: c.data.client_id, client_secret: c.data.client_secret } });
  if (r.code !== 200) fail('Tumblr làm mới chìa (bấm Kết nối lại)', r);
  c.data.access_token = r.data.access_token; c.data.refresh_token = r.data.refresh_token || c.data.refresh_token;
  c.data.expires_at = Date.now() + (r.data.expires_in || 2400) * 1000; await save();
  return c.data.access_token;
}
// ---------- Wix ----------
const wixH = (c) => ({ Authorization: c.data.api_key, 'wix-site-id': c.data.site_id });
const wixTotal = async (c) => (await http('GET', 'https://www.wixapis.com/blog/v3/posts?paging.limit=1', { headers: wixH(c) })).data?.metaData?.total;

// ================== ĐỊNH NGHĨA NỀN TẢNG ==================
export const PLATFORMS = {
  wix: {
    async test(c) {
      let r = await http('POST', 'https://www.wixapis.com/blog/v3/posts/query', { headers: wixH(c), json: { paging: { limit: 1 } } });
      if (r.code === 401 || r.code === 403 || r.code === 404) {
        // Có thể Site ID chưa đúng → dùng chìa tự lấy danh sách trang của tài khoản (quyền "Lấy danh sách trang web")
        const acc = c.data.account_id || c.data.member_id;
        const s = acc ? await http('POST', 'https://www.wixapis.com/site-list/v2/sites/query', { headers: { Authorization: c.data.api_key, 'wix-account-id': acc }, json: { query: { cursorPaging: { limit: 50 } } } }) : { code: 0, data: {} };
        const sites = s.data?.sites || [];
        if (s.code === 401 || s.code === 403) throw new Error('Wix từ chối chìa (lỗi ' + r.code + '). Thường do chép thiếu chìa: chìa đầy đủ rất dài và bắt đầu bằng "IST." — tạo chìa mới, bấm Copy ngay khi hiện ra rồi dán lại.');
        const pick = sites.find((x) => (c.data.url_prefix || '').includes(String(x.viewUrl || '').replace(/^https?:\/\//, '').replace(/\/$/, ''))) || (sites.length === 1 ? sites[0] : null);
        if (pick && pick.id !== c.data.site_id) {
          c.data.site_id = pick.id;
          r = await http('POST', 'https://www.wixapis.com/blog/v3/posts/query', { headers: wixH(c), json: { paging: { limit: 1 } } });
        }
        if (r.code !== 200) {
          const g = await http('GET', 'https://www.wixapis.com/blog/v3/posts?paging.limit=1', { headers: wixH(c) });
          const d = await http('POST', 'https://www.wixapis.com/blog/v3/draft-posts/query', { headers: wixH(c), json: { paging: { limit: 1 } } });
          const ct = await http('GET', 'https://www.wixapis.com/blog/v3/categories?paging.limit=1', { headers: wixH(c) });
          c.data.diag = `posts.query ${r.code} · posts.list ${g.code} · drafts.query ${d.code} · categories ${ct.code}`;
          if (g.code === 200 && d.code === 200) { c.data.list_ok = true; return `Kết nối được (đọc bằng danh sách). Trang đang có ${g.data?.metaData?.total ?? '?'} bài.`; }
        }
        if (r.code !== 200) throw new Error(`Wix lỗi ${r.code} [${c.data.diag || ''}]. Chìa thấy ${sites.length} trang: ${sites.map((x) => x.displayName + ' = ' + x.id).join('; ') || '(không đọc được)'}. Kiểm tra chìa đã tích quyền "Wix Blog" và chọn đúng trang, rồi bấm Kiểm tra lại.`);
      }
      if (r.code !== 200) fail('Wix', r);
      if (!c.data.member_id) {
        const m = await http('POST', 'https://www.wixapis.com/members/v1/members/query', { headers: wixH(c), json: { query: { paging: { limit: 1 } } } });
        const mem = m.data?.members?.[0]; if (mem) c.data.member_id = mem.id;
      }
      if (!c.data.member_id) throw new Error('Chưa tìm được tác giả (Member ID) — dán Member ID vào ô tương ứng');
      return `Kết nối được. Trang đang có ${r.data?.metaData?.total ?? '?'} bài.`;
    },
    async publish(c, it) {
      const draft = { title: it.title, memberId: c.data.member_id, richContent: { nodes: toRicos(it.html) }, seoSlug: it.slug };
      if (it.image) {
        const im = await http('POST', 'https://www.wixapis.com/site-media/v1/files/import', { headers: wixH(c), json: { url: it.image, mediaType: 'IMAGE', mimeType: 'image/png', displayName: (it.slug || 'anh') + '.png' } });
        const fid = im.data?.file?.id; if (fid) draft.media = { wixMedia: { image: { id: fid } }, displayed: true, custom: true };
      }
      const before = await wixTotal(c);
      const r = await http('POST', 'https://www.wixapis.com/blog/v3/draft-posts', { headers: wixH(c), json: { draftPost: draft, publish: true } });
      if (r.code !== 200) {
        await new Promise((s) => setTimeout(s, 8000));
        if ((await wixTotal(c)) > before) throw Object.assign(new Error('Wix báo lỗi nhưng số bài đã tăng — có thể bài đã lên. Kiểm tra tay, KHÔNG đăng lại.'), { noRetry: true });
        fail('Wix', r);
      }
      const pid = r.data.draftPost.id;
      const g = await http('GET', `https://www.wixapis.com/blog/v3/posts/${pid}?fieldsets=URL`, { headers: wixH(c) });
      const u = g.data?.post?.url; return { url: u?.base && u?.path ? u.base + u.path : (c.data.url_prefix || '') + it.slug };
    },
  },
  wordpress: {
    async test(c) {
      const r = await http('GET', `https://public-api.wordpress.com/rest/v1.1/sites/${c.data.site_id}`, { headers: { Authorization: 'Bearer ' + c.data.access_token } });
      if (r.code !== 200) fail('WordPress', r);
      c.data.home = r.data.URL;
      return `Kết nối được blog "${r.data.name}" (${r.data.URL}), đang có ${r.data.post_count ?? '?'} bài.`;
    },
    async publish(c, it) {
      const H = { Authorization: 'Bearer ' + c.data.access_token }, base = `https://public-api.wordpress.com/rest/v1.1/sites/${c.data.site_id}`;
      const body = { title: it.title, content: toGutenberg(it.html), slug: it.slug, status: 'publish' };
      if (it.image) { const m = await http('POST', base + '/media/new', { headers: H, form: { 'media_urls[]': it.image } }); const mid = m.data?.media?.[0]?.ID; if (mid) body.featured_image = mid; }
      const r = await http('POST', base + '/posts/new', { headers: H, json: body });
      if (r.code !== 200) fail('WordPress', r);
      return { url: r.data.URL };
    },
  },
  blogger: {
    async test(c) {
      const t = await googleToken(c);
      const r = await http('GET', `https://www.googleapis.com/blogger/v3/blogs/${c.data.blog_id}`, { headers: { Authorization: 'Bearer ' + t } });
      if (r.code !== 200) fail('Blogger', r);
      c.data.home = r.data.url;
      return `Kết nối được blog "${r.data.name}" (${r.data.url}), đang có ${r.data.posts?.totalItems ?? '?'} bài.`;
    },
    async publish(c, it) {
      const t = await googleToken(c);
      const img = it.image ? `<p><img src="${it.image}" alt="${escT(it.title)}" style="max-width:100%"></p>\n` : '';
      const r = await http('POST', `https://www.googleapis.com/blogger/v3/blogs/${c.data.blog_id}/posts/`, { headers: { Authorization: 'Bearer ' + t }, json: { title: it.title, content: img + it.html } });
      if (r.code !== 200) fail('Blogger', r);
      return { url: r.data.url };
    },
  },
  webflow: {
    async test(c) {
      const r = await http('GET', `https://api.webflow.com/v2/collections/${c.data.collection_id}`, { headers: { Authorization: 'Bearer ' + c.data.token } });
      if (r.code !== 200) fail('Webflow', r);
      const f = r.data.fields || [];
      c.data.f_body = (f.find((x) => x.type === 'RichText') || {}).slug;
      c.data.f_image = (f.find((x) => x.type === 'Image') || {}).slug;
      c.data.f_summary = (f.find((x) => x.type === 'PlainText' && !['name', 'slug'].includes(x.slug)) || {}).slug;
      if (!c.data.f_body) throw new Error('Bộ sưu tập này không có ô nội dung dạng Rich Text');
      const n = await http('GET', `https://api.webflow.com/v2/collections/${c.data.collection_id}/items?limit=1`, { headers: { Authorization: 'Bearer ' + c.data.token } });
      return `Kết nối được bộ sưu tập "${r.data.displayName}", đang có ${n.data?.pagination?.total ?? '?'} bài (gói miễn phí tối đa 50).`;
    },
    async publish(c, it) {
      const fd = { name: it.title, slug: it.slug, [c.data.f_body]: it.html };
      if (c.data.f_image && it.image) fd[c.data.f_image] = { url: it.image };
      if (c.data.f_summary) fd[c.data.f_summary] = shortText(it, 250);
      const r = await http('POST', `https://api.webflow.com/v2/collections/${c.data.collection_id}/items/live`, { headers: { Authorization: 'Bearer ' + c.data.token }, json: { isDraft: false, fieldData: fd } });
      if (r.code !== 200 && r.code !== 202) fail('Webflow', r);
      return { url: (c.data.url_prefix || '') + (r.data.fieldData?.slug || it.slug) };
    },
  },
  tumblr: {
    async test(c, save) {
      const t = await tumblrToken(c, save);
      const r = await http('GET', `https://api.tumblr.com/v2/blog/${c.data.blog}/info`, { headers: { Authorization: 'Bearer ' + t } });
      if (r.code !== 200) fail('Tumblr', r);
      c.data.home = r.data.response?.blog?.url;
      return `Kết nối được blog "${r.data.response?.blog?.title}", đang có ${r.data.response?.blog?.posts ?? '?'} bài.`;
    },
    async publish(c, it, save) {
      const t = await tumblrToken(c, save);
      const content = [...(it.image ? [{ type: 'image', media: [{ url: it.image, type: 'image/png' }] }] : []), { type: 'text', subtype: 'heading1', text: it.title }, ...toNPF(it.html)];
      const r = await http('POST', `https://api.tumblr.com/v2/blog/${c.data.blog}/posts`, { headers: { Authorization: 'Bearer ' + t }, json: { content, state: 'published', slug: it.slug } });
      if (r.code !== 201 && r.code !== 200) fail('Tumblr', r);
      const pid = r.data.response?.id_string || r.data.response?.id;
      return { url: `https://${String(c.data.blog).replace(/\.tumblr\.com$/, '')}.tumblr.com/post/${pid}` };
    },
  },
  mastodon: {
    async test(c) {
      const r = await http('GET', `https://${c.data.instance}/api/v1/accounts/verify_credentials`, { headers: { Authorization: 'Bearer ' + c.data.token } });
      if (r.code !== 200) fail('Mastodon', r);
      c.data.home = r.data.url;
      return `Kết nối được tài khoản @${r.data.acct}, đã đăng ${r.data.statuses_count} tút.`;
    },
    async publish(c, it) {
      const status = `${it.title}\n\n${shortText(it, 380 - it.title.length - it.source.length)}\n\n${it.source}`.slice(0, 495);
      const r = await http('POST', `https://${c.data.instance}/api/v1/statuses`, { headers: { Authorization: 'Bearer ' + c.data.token, 'Idempotency-Key': it.id + c.id }, json: { status, visibility: 'public' } });
      if (r.code !== 200) fail('Mastodon', r);
      return { url: r.data.url };
    },
  },
  telegram: {
    async test(c) {
      const r = await http('GET', `https://api.telegram.org/bot${c.data.bot_token}/getChat?chat_id=${encodeURIComponent(c.data.chat_id)}`);
      if (!r.data.ok) fail('Telegram', r);
      return `Kết nối được kênh/nhóm "${r.data.result.title || r.data.result.username}".`;
    },
    async publish(c, it) {
      const text = `<b>${escT(it.title)}</b>\n\n${escT(shortText(it, 700))}\n\n<a href="${escT(it.source)}">${escT(it.source)}</a>`;
      const r = await http('POST', `https://api.telegram.org/bot${c.data.bot_token}/sendMessage`, { json: { chat_id: c.data.chat_id, text, parse_mode: 'HTML' } });
      if (!r.data.ok) fail('Telegram', r);
      const u = r.data.result.chat?.username;
      return { url: u ? `https://t.me/${u}/${r.data.result.message_id}` : `telegram:${r.data.result.chat?.id}/${r.data.result.message_id}` };
    },
  },
  ggroups: {
    async test(c) {
      const t = await googleToken(c);
      const r = await http('GET', 'https://gmail.googleapis.com/gmail/v1/users/me/profile', { headers: { Authorization: 'Bearer ' + t } });
      if (r.code !== 200) fail('Gmail', r);
      c.data.from = r.data.emailAddress;
      c.data.home = 'https://groups.google.com/g/' + String(c.data.group_email).split('@')[0];
      return `Kết nối được Gmail ${r.data.emailAddress}. Bài sẽ gửi tới ${c.data.group_email} (tài khoản này phải là thành viên nhóm và được đăng bài).`;
    },
    async publish(c, it) {
      const t = await googleToken(c), H = { Authorization: 'Bearer ' + t };
      const b64 = b64utf8;
      const img = it.image ? `<p><img src="${it.image}" alt="${escT(it.title)}" style="max-width:100%"></p>\n` : '';
      const mime = [`From: ${c.data.from || 'me'}`, `To: ${c.data.group_email}`, `Subject: =?UTF-8?B?${b64(it.title)}?=`, 'MIME-Version: 1.0',
        'Content-Type: text/html; charset=UTF-8', 'Content-Transfer-Encoding: base64', '', b64(img + it.html).replace(/.{76}/g, '$&\r\n')].join('\r\n');
      const raw = b64url(mime);
      const r = await http('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/messages/send', { headers: H, json: { raw } });
      if (r.code !== 200) fail('Gmail gửi bài', r);
      const m = await http('GET', `https://gmail.googleapis.com/gmail/v1/users/me/messages/${r.data.id}?format=metadata&metadataHeaders=Message-Id`, { headers: H });
      const mid = ((m.data.payload?.headers || []).find((h) => /^message-id$/i.test(h.name))?.value || '').replace(/^<|>$/g, '');
      const g = String(c.data.group_email).split('@')[0];
      return { url: mid ? `https://groups.google.com/d/msgid/${g}/${encodeURIComponent(mid)}` : `https://groups.google.com/g/${g}` };
    },
  },
};

// Trang còn sống không? 410/404/451 = bị khóa
export async function siteAlive(c) {
  const home = c.data.home || (c.type === 'wix' ? c.data.url_prefix : '') || '';
  if (!/^https?:\/\//.test(home)) return true;
  try { const r = await fetch(home, { redirect: 'follow' }); return ![404, 410, 451].includes(r.status); } catch { return true; }
}

// ---------- OAuth: tạo link đăng nhập + đổi mã ----------
export const OAUTH = {
  wordpress: {
    url: (c, redir, state) => `https://public-api.wordpress.com/oauth2/authorize?client_id=${encodeURIComponent(c.data.client_id)}&redirect_uri=${encodeURIComponent(redir)}&response_type=code&scope=global&state=${state}`,
    async exchange(c, code, redir) {
      const r = await http('POST', 'https://public-api.wordpress.com/oauth2/token', { form: { client_id: c.data.client_id, client_secret: c.data.client_secret, redirect_uri: redir, code, grant_type: 'authorization_code' } });
      if (r.code !== 200) fail('WordPress', r);
      c.data.access_token = r.data.access_token; if (!c.data.site_id) c.data.site_id = r.data.blog_id;
    },
  },
  blogger: {
    url: (c, redir, state) => `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(c.data.client_id)}&redirect_uri=${encodeURIComponent(redir)}&response_type=code&access_type=offline&prompt=consent&scope=${encodeURIComponent('https://www.googleapis.com/auth/blogger https://www.googleapis.com/auth/spreadsheets')}&state=${state}`,
    async exchange(c, code, redir) {
      const r = await http('POST', 'https://oauth2.googleapis.com/token', { form: { client_id: c.data.client_id, client_secret: c.data.client_secret, redirect_uri: redir, code, grant_type: 'authorization_code' } });
      if (r.code !== 200) fail('Google', r);
      c.data.refresh_token = r.data.refresh_token || c.data.refresh_token;
      if (!c.data.blog_id) {
        const b = await http('GET', 'https://www.googleapis.com/blogger/v3/users/self/blogs', { headers: { Authorization: 'Bearer ' + r.data.access_token } });
        c.data.blogs = (b.data.items || []).map((x) => ({ id: x.id, name: x.name, url: x.url }));
        if (c.data.blogs.length) c.data.blog_id = c.data.blogs[0].id;
      }
    },
  },
  ggroups: {
    url: (c, redir, state) => `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(c.data.client_id)}&redirect_uri=${encodeURIComponent(redir)}&response_type=code&access_type=offline&prompt=consent&scope=${encodeURIComponent('https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.metadata')}&state=${state}`,
    async exchange(c, code, redir) {
      const r = await http('POST', 'https://oauth2.googleapis.com/token', { form: { client_id: c.data.client_id, client_secret: c.data.client_secret, redirect_uri: redir, code, grant_type: 'authorization_code' } });
      if (r.code !== 200) fail('Google', r);
      c.data.refresh_token = r.data.refresh_token || c.data.refresh_token;
    },
  },
  tumblr: {
    url: (c, redir, state) => `https://www.tumblr.com/oauth2/authorize?client_id=${encodeURIComponent(c.data.client_id)}&response_type=code&scope=${encodeURIComponent('basic write offline_access')}&state=${state}&redirect_uri=${encodeURIComponent(redir)}`,
    async exchange(c, code, redir) {
      const r = await http('POST', 'https://api.tumblr.com/v2/oauth2/token', { form: { grant_type: 'authorization_code', code, client_id: c.data.client_id, client_secret: c.data.client_secret, redirect_uri: redir } });
      if (r.code !== 200) fail('Tumblr', r);
      c.data.access_token = r.data.access_token; c.data.refresh_token = r.data.refresh_token; c.data.expires_at = Date.now() + (r.data.expires_in || 2400) * 1000;
      if (!c.data.blog) {
        const u = await http('GET', 'https://api.tumblr.com/v2/user/info', { headers: { Authorization: 'Bearer ' + c.data.access_token } });
        c.data.blog = u.data.response?.user?.blogs?.[0]?.name;
      }
    },
  },
};

// ---------- Ghi link về Google Sheet (tìm lại dòng theo URL bài gốc) ----------
export async function writeBack(google, sheet, job, item, url, when) {
  if (!sheet.id || !sheet.tab || !job.sheet_row) return 'bỏ qua (không khai báo dòng sheet)';
  const t = await googleToken(google), H = { Authorization: 'Bearer ' + t };
  const base = `https://sheets.googleapis.com/v4/spreadsheets/${sheet.id}/values/`;
  const rng = (col, row) => encodeURIComponent(`'${sheet.tab}'!${col}${row}`);
  // Người khác hay chèn/xóa dòng → tìm dòng theo URL bài gốc gần dòng đã khai, rồi mới ghi
  let row = +job.sheet_row;
  const near = await http('GET', base + encodeURIComponent(`'${sheet.tab}'!${sheet.cot_url_goc}${Math.max(1, row - 30)}:${sheet.cot_url_goc}${row + 30}`), { headers: H });
  const vals = (near.data.values || []).map((v) => (v[0] || '').trim());
  const want = item.source.trim().split('?')[0];
  const at = vals.findIndex((v) => v.split('?')[0] === want);
  if (at >= 0 && job.sheet_offset !== undefined) row = Math.max(1, row - 30) + at + +job.sheet_offset;
  const cur = await http('GET', base + rng(sheet.cot_link, row), { headers: H });
  if ((cur.data.values || [[]])[0]?.[0]) return `dòng ${row} đã có link — không ghi đè`;
  for (const [col, v] of [[sheet.cot_link, url], [sheet.cot_gio, when]]) {
    const w = await http('PUT', base + rng(col, row) + '?valueInputOption=RAW', { headers: H, json: { values: [[v]] } });
    if (w.code !== 200) fail('Ghi Google Sheet', w);
  }
  return `đã ghi dòng ${row}`;
}
