#!/usr/bin/env node
// JSON helpers for share-bai-pinterest: credentials, payload building, result
// reading. Fixed script so the Bash allowlist can scope to it instead of `node -e`.
const fs = require('fs');

const [, , cmd, ...args] = process.argv;
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const writeJson = (p, v) => fs.writeFileSync(p, JSON.stringify(v, null, 2));
const loadAccounts = (p) => (fs.existsSync(p) ? readJson(p) : {});

// Pinterest field limits (API v5)
const LIMITS = { title: 100, description: 500, alt_text: 500 };

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-file> <account-key> <field>
    const [file, key, field] = args;
    const acc = loadAccounts(file)[key] || {};
    console.log(acc[field] === undefined || acc[field] === null ? '' : acc[field]);
    break;
  }
  case 'set-app': {
    // set-app <accounts-file> <account-key> <app_id> <app_secret> <redirect_uri> <env: prod|sandbox>
    const [file, key, appId, appSecret, redirectUri, env] = args;
    if (!['prod', 'sandbox'].includes(env)) { console.error('set-app: env must be prod or sandbox'); process.exit(1); }
    const all = loadAccounts(file);
    all[key] = { ...(all[key] || {}), app_id: appId, app_secret: appSecret, redirect_uri: redirectUri, env };
    writeJson(file, all);
    console.log('saved app for', key, '(env:', env + ')');
    break;
  }
  case 'set-field': {
    // set-field <accounts-file> <account-key> <field> <value>   (e.g. env, board_id)
    const [file, key, field, value] = args;
    const all = loadAccounts(file);
    if (!all[key]) { console.error('set-field: no account', key); process.exit(1); }
    all[key][field] = value;
    writeJson(file, all);
    console.log('set', field, 'for', key);
    break;
  }
  case 'save-tokens': {
    // save-tokens <accounts-file> <account-key> <token-response-file>
    // Works for both the first code exchange and later refreshes.
    const [file, key, respFile] = args;
    const resp = readJson(respFile);
    if (!resp.access_token) { console.error('save-tokens: no access_token in response:', JSON.stringify(resp).slice(0, 300)); process.exit(1); }
    const all = loadAccounts(file);
    const acc = all[key] || {};
    acc.access_token = resp.access_token;
    if (resp.refresh_token) acc.refresh_token = resp.refresh_token;
    acc.scope = resp.scope || acc.scope;
    acc.expires_in_seconds = resp.expires_in;
    if (resp.refresh_token_expires_in) acc.refresh_token_expires_in_seconds = resp.refresh_token_expires_in;
    acc.obtained_at = new Date().toISOString();
    all[key] = acc;
    writeJson(file, all);
    console.log('saved tokens for', key, '- access expires in', resp.expires_in, 's', resp.refresh_token ? '(refresh token updated)' : '');
    break;
  }
  case 'show-user': {
    // show-user <get-user-response-file>
    const r = readJson(args[0]);
    if (r.code || r.message && !r.username) { console.error('API error:', r.code, r.message); process.exit(1); }
    console.log(JSON.stringify({ username: r.username, account_type: r.account_type, business_name: r.business_name }));
    break;
  }
  case 'show-boards': {
    // show-boards <list-boards-response-file>
    const r = readJson(args[0]);
    if (!r.items) { console.error('API error:', r.code, r.message); process.exit(1); }
    r.items.forEach((b) => console.log(b.id + '\t' + b.name + '\t' + (b.privacy || '')));
    if (!r.items.length) console.log('(no boards)');
    break;
  }
  case 'build-board-payload': {
    // build-board-payload <name> <description> <out-file>
    const [name, description, out] = args;
    writeJson(out, { name, description, privacy: 'PUBLIC' });
    console.log('written', out);
    break;
  }
  case 'build-pin-payload': {
    // build-pin-payload <board_id> <title> <description> <link> <alt_text> <image-file> <mime> <out-file>
    const [boardId, title, description, link, altText, imageFile, mime, out] = args;
    const errs = [];
    if (title.length > LIMITS.title) errs.push(`title ${title.length}/${LIMITS.title} chars`);
    if (description.length > LIMITS.description) errs.push(`description ${description.length}/${LIMITS.description} chars`);
    if (altText.length > LIMITS.alt_text) errs.push(`alt_text ${altText.length}/${LIMITS.alt_text} chars`);
    if (!/^https?:\/\//.test(link)) errs.push('link must be http(s)');
    if (!/^image\/(jpeg|png)$/.test(mime)) errs.push('image must be image/jpeg or image/png');
    if (errs.length) { console.error('build-pin-payload: ' + errs.join('; ')); process.exit(1); }
    const data = fs.readFileSync(imageFile).toString('base64');
    writeJson(out, {
      board_id: boardId, title, description, link, alt_text: altText,
      media_source: { source_type: 'image_base64', content_type: mime, data },
    });
    console.log('written', out, '(image', Math.round(data.length / 1024), 'KB base64)');
    break;
  }
  case 'show-pin-result': {
    // show-pin-result <create-pin-response-file>
    const r = readJson(args[0]);
    if (!r.id) { console.error('API error:', r.code, r.message); process.exit(1); }
    console.log(JSON.stringify({ id: r.id, url: `https://www.pinterest.com/pin/${r.id}/`, title: r.title, link: r.link, board_id: r.board_id }, null, 2));
    break;
  }
  case 'char-count': {
    // char-count <text-file>
    console.log([...fs.readFileSync(args[0], 'utf8').trim()].length);
    break;
  }
  default:
    console.error('pinterest-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-app|set-field|save-tokens|show-user|show-boards|build-board-payload|build-pin-payload|show-pin-result|char-count)');
    process.exit(1);
}
