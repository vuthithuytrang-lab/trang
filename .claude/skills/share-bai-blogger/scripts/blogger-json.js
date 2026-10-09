#!/usr/bin/env node
// JSON/text helpers for share-bai-blogger. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
const fs = require('fs');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function writeAccounts(path, acc) {
  fs.writeFileSync(path, JSON.stringify(acc, null, 2) + '\n');
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <blog-key> <field>
    const [file, blogKey, field] = args;
    const acc = readJson(file);
    const value = acc[blogKey] ? acc[blogKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'set-client': {
    // set-client <accounts-json-file> <blog-key> <client_id> <client_secret> <blog-url>
    const [file, blogKey, clientId, clientSecret, blogUrl] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[blogKey] = {
      ...acc[blogKey],
      client_id: clientId,
      client_secret: clientSecret,
      blog_url: blogUrl,
    };
    writeAccounts(file, acc);
    console.log('saved client for', blogKey);
    break;
  }
  case 'save-tokens': {
    // save-tokens <accounts-json-file> <blog-key> <token-response-json-file>
    // Used once after the initial authorization_code exchange (google-oauth-server.js).
    const [file, blogKey, tokenRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(tokenRespFile);
    if (!resp.access_token) {
      console.error('save-tokens: response has no access_token');
      process.exit(1);
    }
    if (!resp.refresh_token && !(acc[blogKey] && acc[blogKey].refresh_token)) {
      console.error('save-tokens: response has no refresh_token and none stored yet — re-run OAuth with access_type=offline&prompt=consent');
      process.exit(1);
    }
    acc[blogKey] = {
      ...acc[blogKey],
      access_token: resp.access_token,
      refresh_token: resp.refresh_token || acc[blogKey].refresh_token,
      token_type: resp.token_type || 'Bearer',
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('saved tokens for', blogKey, 'has refresh_token:', !!acc[blogKey].refresh_token);
    break;
  }
  case 'save-refreshed-access-token': {
    // save-refreshed-access-token <accounts-json-file> <blog-key> <refresh-response-json-file>
    // Google refresh responses normally do NOT include a new refresh_token — keep the stored one.
    const [file, blogKey, refreshRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(refreshRespFile);
    if (!resp.access_token) {
      console.error('save-refreshed-access-token: response has no access_token (refresh_token may be revoked)');
      process.exit(1);
    }
    acc[blogKey] = {
      ...acc[blogKey],
      access_token: resp.access_token,
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('refreshed access_token for', blogKey);
    break;
  }
  case 'save-blog-id': {
    // save-blog-id <accounts-json-file> <blog-key> <blog-byurl-response-json-file>
    const [file, blogKey, blogRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(blogRespFile);
    if (!resp.id) {
      console.error('save-blog-id: response has no blog id (check blog_url is correct and access_token is valid)');
      process.exit(1);
    }
    acc[blogKey] = { ...acc[blogKey], blog_id: resp.id };
    writeAccounts(file, acc);
    console.log('saved blog_id', resp.id, 'for', blogKey);
    break;
  }
  case 'build-post-payload': {
    // build-post-payload <content-html-file> <title> <out-file>
    const [contentFile, title, outFile] = args;
    const content = fs.readFileSync(contentFile, 'utf8');
    const payload = { title, content };
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes');
    break;
  }
  case 'embed-image-datauri': {
    // embed-image-datauri <content-html-file> <image-file> <mime-type> <out-file>
    // Replaces the first <img ... src="..."> in content with a base64 data URI built
    // from the local image file. Use this instead of linking straight to the source
    // site's image URL — many sites (WAF/hotlink protection) block direct <img> loads
    // from other domains even though the page itself is publicly readable.
    const [contentFile, imageFile, mime, outFile] = args;
    const content = fs.readFileSync(contentFile, 'utf8');
    const b64 = fs.readFileSync(imageFile).toString('base64');
    const dataUri = `data:${mime};base64,${b64}`;
    const replaced = content.replace(/(<img[^>]*\ssrc=")[^"]*(")/, `$1${dataUri}$2`);
    if (replaced === content) {
      console.error('embed-image-datauri: no <img src="..."> tag found in content — nothing replaced');
      process.exit(1);
    }
    fs.writeFileSync(outFile, replaced);
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes (image', Math.round(b64.length / 1024), 'KB base64)');
    break;
  }
  case 'word-count': {
    // word-count <html-file>
    const [file] = args;
    const html = fs.readFileSync(file, 'utf8');
    const text = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<[^>]+>/g, ' ');
    console.log(text.trim().split(/\s+/).filter(Boolean).length);
    break;
  }
  case 'show-post-result': {
    // show-post-result <post-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({
      id: r.id, url: r.url, title: r.title, status: r.status,
    }, null, 2));
    break;
  }
  default:
    console.error('blogger-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-client|save-tokens|save-refreshed-access-token|save-blog-id|build-post-payload|embed-image-datauri|word-count|show-post-result)');
    process.exit(1);
}
