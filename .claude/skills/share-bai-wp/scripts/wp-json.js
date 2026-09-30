#!/usr/bin/env node
// JSON/text helpers for share-bai-wp. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
const fs = require('fs');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <site-domain> <field>
    const [file, site, field] = args;
    const acc = readJson(file);
    const value = acc[site] ? acc[site][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'decode-implicit-fragment': {
    // decode-implicit-fragment <fragment-string>  (legacy response_type=token flow)
    const [frag] = args;
    const params = new URLSearchParams(frag);
    console.log(JSON.stringify({
      access_token: params.get('access_token'),
      expires_in: params.get('expires_in'),
      token_type: params.get('token_type'),
      scope: params.get('scope'),
    }));
    break;
  }
  case 'save-oauth-token': {
    // save-oauth-token <accounts-json-file> <site-domain> <token-exchange-response-json-file>
    const [accountsFile, site, tokenRespFile] = args;
    const acc = readJson(accountsFile);
    const resp = readJson(tokenRespFile);
    if (!resp.access_token) {
      console.error('save-oauth-token: response has no access_token');
      process.exit(1);
    }
    acc[site] = {
      ...acc[site],
      access_token: resp.access_token,
      token_type: resp.token_type || 'bearer',
      token_scope: resp.scope || 'global',
      token_expires: 'expires_in' in resp,
      obtained_at: new Date().toISOString(),
    };
    fs.writeFileSync(accountsFile, JSON.stringify(acc, null, 2) + '\n');
    console.log('saved token for', site, 'expires:', 'expires_in' in resp);
    break;
  }
  case 'build-post-payload': {
    // build-post-payload <content-html-file> <title> <slug> <featured-media-id-or-empty> <out-file>
    const [contentFile, title, slug, mediaId, outFile] = args;
    const content = fs.readFileSync(contentFile, 'utf8');
    const payload = { title, content, slug, status: 'publish' };
    if (mediaId) payload.featured_image = mediaId;
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes');
    break;
  }
  case 'word-count': {
    // word-count <gutenberg-block-html-file>
    const [file] = args;
    const html = fs.readFileSync(file, 'utf8');
    const text = html.replace(/<!--[\s\S]*?-->/g, '').replace(/<[^>]+>/g, ' ');
    console.log(text.trim().split(/\s+/).filter(Boolean).length);
    break;
  }
  case 'show-media-id': {
    // show-media-id <media-upload-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(r.media && r.media[0] ? r.media[0].ID : '');
    break;
  }
  case 'show-post-result': {
    // show-post-result <post-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({
      ID: r.ID, status: r.status, URL: r.URL, title: r.title,
      slug: r.slug, featured_image: r.featured_image,
    }, null, 2));
    break;
  }
  default:
    console.error('wp-json.js: unknown subcommand', cmd, '(expected: get-account-field|decode-implicit-fragment|save-oauth-token|build-post-payload|word-count|show-media-id|show-post-result)');
    process.exit(1);
}
