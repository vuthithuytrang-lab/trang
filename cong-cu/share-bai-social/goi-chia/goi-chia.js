#!/usr/bin/env node
// Gói / mở gói chìa kết nối của agent share-bai-social.
// Mục đích: chuyển sang tài khoản Claude khác hoặc máy mới mà KHÔNG phải kết nối lại từ đầu.
//
//   node cong-cu/share-bai-social/goi-chia/goi-chia.js dong-goi <file-ra.json>
//       Gom mọi file .claude/skills/*/*-accounts.local.json thành 1 file gói.
//   node cong-cu/share-bai-social/goi-chia/goi-chia.js mo-goi <file-goi.json>
//       Trả từng phần về đúng chỗ (ghi đè), quyền file 600.
//   node cong-cu/share-bai-social/goi-chia/goi-chia.js kiem-tra [file-goi.json]
//       Liệt kê nền tảng + tài khoản có trong gói (hoặc trên máy) — KHÔNG in chìa.
//
// Bảo mật: file gói chứa chìa thật. Không commit (đuôi .local.json đã chặn trong .gitignore),
// không in ra màn hình, không dán vào chat — chỉ gửi qua tệp đính kèm.
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..', '..');
const SKILLS = path.join(ROOT, '.claude', 'skills');
const TOKEN_KEYS = ['refresh_token', 'access_token', 'client_secret', 'app_secret'];

function findLocal() {
  const out = {};
  if (!fs.existsSync(SKILLS)) return out;
  for (const dir of fs.readdirSync(SKILLS)) {
    const d = path.join(SKILLS, dir);
    if (!fs.statSync(d).isDirectory()) continue;
    for (const f of fs.readdirSync(d)) {
      if (/-accounts\.local\.json$/.test(f) && !/example/.test(f)) {
        out[`${dir}/${f}`] = JSON.parse(fs.readFileSync(path.join(d, f), 'utf8'));
      }
    }
  }
  return out;
}

function summary(files) {
  const rows = [];
  for (const [rel, accounts] of Object.entries(files)) {
    for (const [acc, v] of Object.entries(accounts || {})) {
      const has = TOKEN_KEYS.filter(k => v && typeof v[k] === 'string' && v[k] && !/^TU_DONG|^DIEN|^OAUTH_|^WP_APP|^APP_SECRET/.test(v[k]));
      rows.push(`${rel.split('/')[0].padEnd(22)} ${acc.padEnd(42)} có: ${has.join(', ') || '(trống)'}`);
    }
  }
  return rows.length ? rows.join('\n') : '(không có kết nối nào)';
}

const [cmd, file] = process.argv.slice(2);
if (cmd === 'dong-goi') {
  if (!file) throw new Error('Thiếu tên file ra');
  const files = findLocal();
  if (!Object.keys(files).length) { console.error('Không có file *-accounts.local.json nào để gói.'); process.exit(1); }
  const goi = { loai: 'goi-chia-share-bai-social', tao_luc: new Date().toISOString(), files };
  fs.writeFileSync(file, JSON.stringify(goi, null, 2), { mode: 0o600 });
  console.log(`Đã gói ${Object.keys(files).length} file vào ${file}\n` + summary(files));
} else if (cmd === 'mo-goi') {
  if (!file) throw new Error('Thiếu file gói');
  const goi = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (goi.loai !== 'goi-chia-share-bai-social') throw new Error('Không phải file gói chìa share-bai-social');
  for (const [rel, data] of Object.entries(goi.files)) {
    if (!/^[a-z0-9-]+\/[a-z0-9-]+-accounts\.local\.json$/.test(rel)) throw new Error(`Đường dẫn lạ trong gói: ${rel}`);
    const dest = path.join(SKILLS, rel);
    if (!fs.existsSync(path.dirname(dest))) { console.error(`Bỏ qua ${rel}: không có skill này trong repo`); continue; }
    fs.writeFileSync(dest, JSON.stringify(data, null, 2) + '\n', { mode: 0o600 });
  }
  console.log(`Đã trả chìa về chỗ (gói tạo lúc ${goi.tao_luc})\n` + summary(goi.files));
} else if (cmd === 'kiem-tra') {
  const files = file ? JSON.parse(fs.readFileSync(file, 'utf8')).files : findLocal();
  console.log(summary(files));
} else {
  console.log('Dùng: dong-goi <file-ra> | mo-goi <file-goi> | kiem-tra [file-goi]');
  process.exit(1);
}
