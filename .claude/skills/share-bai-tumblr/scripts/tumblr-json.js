#!/usr/bin/env node
// JSON/NPF helpers for share-bai-tumblr. Consolidates the JSON parsing/building
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
    // set-client <accounts-json-file> <blog-key> <client_id> <client_secret> <blog_identifier>
    const [file, blogKey, clientId, clientSecret, blogIdentifier] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[blogKey] = {
      ...acc[blogKey],
      client_id: clientId,
      client_secret: clientSecret,
      blog_identifier: blogIdentifier,
    };
    writeAccounts(file, acc);
    console.log('saved client for', blogKey);
    break;
  }
  case 'save-tokens': {
    // save-tokens <accounts-json-file> <blog-key> <token-response-json-file>
    // Used once after the initial authorization_code exchange (tumblr-oauth-server.js).
    const [file, blogKey, tokenRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(tokenRespFile);
    if (!resp.access_token) {
      console.error('save-tokens: response has no access_token');
      process.exit(1);
    }
    if (!resp.refresh_token && !(acc[blogKey] && acc[blogKey].refresh_token)) {
      console.error('save-tokens: response has no refresh_token and none stored yet — re-run OAuth, make sure scope includes offline_access');
      process.exit(1);
    }
    acc[blogKey] = {
      ...acc[blogKey],
      access_token: resp.access_token,
      refresh_token: resp.refresh_token || acc[blogKey].refresh_token,
      token_type: resp.token_type || 'bearer',
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('saved tokens for', blogKey, 'has refresh_token:', !!acc[blogKey].refresh_token);
    break;
  }
  case 'save-refreshed-access-token': {
    // save-refreshed-access-token <accounts-json-file> <blog-key> <refresh-response-json-file>
    // Tumblr refresh responses may include a new refresh_token (rotating) — keep it if present, else keep stored one.
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
      refresh_token: resp.refresh_token || acc[blogKey].refresh_token,
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('refreshed access_token for', blogKey);
    break;
  }
  case 'add-link-formatting': {
    // add-link-formatting <content-blocks-json-file> <block-index> <link-text> <url> <out-file>
    // NPF text blocks need char-offset "formatting" entries for inline links, not <a href>.
    // Computing offsets by hand is error-prone, so this finds <link-text> inside the block's
    // "text" field and injects {"type":"link","url":...,"start":N,"end":M}. Errors (instead of
    // guessing) if the phrase is missing or ambiguous (appears more than once in that block).
    const [file, blockIndexArg, linkText, url, outFile] = args;
    const blocks = readJson(file);
    const idx = Number(blockIndexArg);
    const block = blocks[idx];
    if (!block || block.type !== 'text') {
      console.error('add-link-formatting: block', idx, 'is not a text block');
      process.exit(1);
    }
    const text = block.text;
    const first = text.indexOf(linkText);
    if (first === -1) {
      console.error('add-link-formatting: link text not found in block', idx, '—', JSON.stringify(linkText));
      process.exit(1);
    }
    if (text.indexOf(linkText, first + 1) !== -1) {
      console.error('add-link-formatting: link text appears more than once in block', idx, '— use a longer, unique phrase');
      process.exit(1);
    }
    const start = first;
    const end = first + linkText.length;
    block.formatting = [...(block.formatting || []), { type: 'link', url, start, end }];
    fs.writeFileSync(outFile, JSON.stringify(blocks, null, 2));
    console.log('written', outFile, '- link added at offset', start, '-', end);
    break;
  }
  case 'build-post-payload': {
    // build-post-payload <content-blocks-json-file> <tags-comma-separated-or-empty> <out-file> [slug]
    // NOTE: confirmed against the live API — Tumblr's /v2/blog/{id}/posts endpoint rejects
    // "tags" as a JSON array (400 "Posting failed. Please try again.", code 8001, no field
    // named in the error) even though the general NPF spec examples show an array. The
    // working shape is a single comma-separated STRING, same as the legacy endpoint.
    //
    // "slug" (optional): confirmed accepted by the same endpoint — without it, Tumblr
    // auto-generates the URL slug from the post title, percent-encoding Vietnamese
    // diacritics (e.g. "d%E1%BB%8Bch-vu-..."). Pass an ASCII kebab-case slug to get a
    // clean URL instead, same convention as the WordPress/Blogger sibling skills.
    const [contentFile, tagsArg, outFile, slugArg] = args;
    const content = readJson(contentFile);
    const tags = (tagsArg || '').split(',').map((t) => t.trim()).filter(Boolean);
    const payload = { content, state: 'published' };
    if (tags.length) payload.tags = tags.join(',');
    if (slugArg) payload.slug = slugArg;
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes', '(blocks:', content.length, ')');
    break;
  }
  case 'word-count': {
    // word-count <content-blocks-json-file>
    // Sums words across every text block's "text" field; image/other blocks are ignored.
    const [file] = args;
    const blocks = readJson(file);
    const words = blocks
      .filter((b) => b.type === 'text' && b.text)
      .map((b) => b.text.trim())
      .join(' ')
      .split(/\s+/)
      .filter(Boolean);
    console.log(words.length);
    break;
  }
  case 'show-post-result': {
    // show-post-result <post-response-json-file> <blog_identifier>
    // Tumblr wraps the real payload in {"meta":{...},"response":{...}}.
    // Confirmed against the live API — the create-post response does NOT include
    // "post_url" or "blog_name" (only id/state/display_text), unlike some NPF doc
    // examples. Build the permalink ourselves from blog_identifier + id instead.
    const [file, blogIdentifier] = args;
    const r = readJson(file);
    const resp = r.response || {};
    const id = resp.id_string || resp.id;
    console.log(JSON.stringify({
      id,
      state: resp.state,
      post_url: resp.post_url || (blogIdentifier && id ? `https://${blogIdentifier}/post/${id}` : undefined),
      meta: r.meta,
    }, null, 2));
    break;
  }
  default:
    console.error('tumblr-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-client|save-tokens|save-refreshed-access-token|add-link-formatting|build-post-payload|word-count|show-post-result)');
    process.exit(1);
}
