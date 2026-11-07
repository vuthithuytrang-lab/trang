// Kho dữ liệu: Netlify Blobs (miễn phí, đi kèm trang). Không có cơ sở dữ liệu ngoài.
import { getStore } from '@netlify/blobs';
import crypto from 'node:crypto';

export const db = () => getStore({ name: 'app-share', consistency: 'strong' });

export async function getJSON(key, def) {
  const v = await db().get(key, { type: 'json' });
  return v === null || v === undefined ? def : v;
}
export const setJSON = (key, v) => db().setJSON(key, v);

export const DEFAULT_SETTINGS = {
  gio_bat_dau: 7, gio_ket_thuc: 23, cach_nhau_phut: 120, toi_da_moi_ngay: 6,
  sheet: { id: '', tab: '', cot_url_goc: 'B', cot_link: 'D', cot_gio: 'E' },
  tu_dong: true,
};
export async function settings() {
  const s = await getJSON('settings', {});
  return { ...DEFAULT_SETTINGS, ...s, sheet: { ...DEFAULT_SETTINGS.sheet, ...(s.sheet || {}) } };
}

export const conns = () => getJSON('conns', {});          // id -> {id, type, name, data:{...chìa}, paused, created}
export const saveConns = (c) => setJSON('conns', c);

export async function listItems() {
  const { blobs } = await db().list({ prefix: 'item/' });
  const out = await Promise.all(blobs.map((b) => db().get(b.key, { type: 'json' })));
  return out.filter(Boolean).sort((a, b) => (a.created || '').localeCompare(b.created || ''));
}
export const getItem = (id) => getJSON('item/' + id, null);
export const saveItem = (it) => setJSON('item/' + it.id, it);
export const delItem = (id) => db().delete('item/' + id);

export async function log(viec, chi_tiet) {
  const l = await getJSON('log', []);
  l.unshift({ t: new Date().toISOString(), viec, chi_tiet: String(chi_tiet || '').slice(0, 500) });
  await setJSON('log', l.slice(0, 400));
}

export const id = () => crypto.randomBytes(6).toString('hex');

// ---- giờ Việt Nam ----
const VN = 7 * 3600e3;
export const vnHour = (d = new Date()) => new Date(d.getTime() + VN).getUTCHours();
export const vnDay = (d = new Date()) => new Date(new Date(d).getTime() + VN).toISOString().slice(0, 10);
export function fmtVN(d = new Date()) {
  const x = new Date(new Date(d).getTime() + VN), p = (n) => String(n).padStart(2, '0');
  return `${p(x.getUTCHours())}:${p(x.getUTCMinutes())} ${p(x.getUTCDate())}/${p(x.getUTCMonth() + 1)}/${x.getUTCFullYear()}`;
}
