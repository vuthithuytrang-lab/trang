// Kho dữ liệu: Workers KV. Mỗi người dùng một vùng riêng (khóa bắt đầu bằng u:<mã người dùng>:).
// Ngữ cảnh (env + người dùng) giữ trong AsyncLocalStorage để các yêu cầu chạy song song không lẫn dữ liệu.
import { AsyncLocalStorage } from 'node:async_hooks';
import { rnd } from './util.js';

const als = new AsyncLocalStorage();
export const withCtx = (env, uid, fn) => als.run({ env, uid }, fn);
const ctx = () => { const c = als.getStore(); if (!c) throw new Error('Thiếu ngữ cảnh'); return c; };
const kv = () => ctx().env.KV;
export const uid = () => ctx().uid;
const uk = (k) => `u:${ctx().uid}:${k}`;

async function get(key, def) { const v = await kv().get(key, 'json'); return v === null ? def : v; }
const put = (key, v) => kv().put(key, JSON.stringify(v));

export const getJSON = (k, def) => get(uk(k), def);
export const setJSON = (k, v) => put(uk(k), v);
export const getSys = (k, def) => get('sys:' + k, def);         // dùng chung cả app (chìa ứng dụng, danh sách người dùng)
export const setSys = (k, v) => put('sys:' + k, v);

export const DEFAULT_SETTINGS = {
  gio_bat_dau: 7, gio_ket_thuc: 23, cach_nhau_phut: 120, toi_da_moi_ngay: 6,
  sheet: { id: '', tab: '', cot_url_goc: 'B', cot_link: 'D', cot_gio: 'E' },
  tu_dong: true,
};
export async function settings() {
  const s = await getJSON('settings', {});
  return { ...DEFAULT_SETTINGS, ...s, sheet: { ...DEFAULT_SETTINGS.sheet, ...(s.sheet || {}) } };
}
export const conns = () => getJSON('conns', {});
export const saveConns = (c) => setJSON('conns', c);

// Bài đợi: 1 tài liệu/người (KV gói Free giới hạn số lần liệt kê, nên không tách mỗi bài 1 khóa)
const itemsMap = () => getJSON('items', {});
export async function listItems() { return Object.values(await itemsMap()).sort((a, b) => (a.created || '').localeCompare(b.created || '')); }
export async function getItem(id) { return (await itemsMap())[id] || null; }
export async function saveItem(it) { const m = await itemsMap(); m[it.id] = it; await setJSON('items', m); }
export async function saveItems(list) { const m = await itemsMap(); for (const it of list) m[it.id] = it; await setJSON('items', m); }
export async function delItem(id) { const m = await itemsMap(); delete m[id]; await setJSON('items', m); }

export async function log(viec, chi_tiet) {
  const l = await getJSON('log', []);
  l.unshift({ t: new Date().toISOString(), viec, chi_tiet: String(chi_tiet || '').slice(0, 500) });
  await setJSON('log', l.slice(0, 300));
}
export const id = () => rnd(6);

// Ảnh đại diện: khóa chung img:<mã> (đường link công khai để nền tảng tải về)
export const putImg = (env, key, bytes) => env.KV.put('img:' + key, bytes, { metadata: { type: 'image/png' } });
export const getImg = (env, key) => env.KV.get('img:' + key, 'arrayBuffer');

const VN = 7 * 3600e3;
export const vnHour = (d = new Date()) => new Date(d.getTime() + VN).getUTCHours();
export const vnDay = (d = new Date()) => new Date(new Date(d).getTime() + VN).toISOString().slice(0, 10);
export function fmtVN(d = new Date()) {
  const x = new Date(new Date(d).getTime() + VN), p = (n) => String(n).padStart(2, '0');
  return `${p(x.getUTCHours())}:${p(x.getUTCMinutes())} ${p(x.getUTCDate())}/${p(x.getUTCMonth() + 1)}/${x.getUTCFullYear()}`;
}
