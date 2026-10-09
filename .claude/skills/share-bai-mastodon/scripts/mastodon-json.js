#!/usr/bin/env node
// JSON helpers for share-bai-mastodon. Consolidates the JSON parsing/building
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

// Mirrors Mastodon's own status-length algorithm closely enough for this
// skill's purposes: any http(s) URL counts as a fixed 23 characters
// (configuration.statuses.characters_reserved_per_url on the instance)
// regardless of its real length, everything else counts as written.
// Length is measured in Unicode codepoints (Array.from), not UTF-16 units,
// so Vietnamese diacritics (precomposed) count correctly as 1 char each.
const URL_RESERVED_LENGTH = 23;
function weightedLength(text) {
  const withPlaceholders = text.replace(/https?:\/\/\S+/g, 'x'.repeat(URL_RESERVED_LENGTH));
  return Array.from(withPlaceholders).length;
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <account-key> <field>
    const [file, accountKey, field] = args;
    const acc = readJson(file);
    const value = acc[accountKey] ? acc[accountKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'set-credentials': {
    // set-credentials <accounts-json-file> <account-key> <access_token> <instance_url> [account_handle]
    const [file, accountKey, accessToken, instanceUrl, accountHandle] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[accountKey] = {
      ...acc[accountKey],
      access_token: accessToken,
      instance_url: instanceUrl.replace(/\/$/, ''),
      ...(accountHandle ? { account_handle: accountHandle } : {}),
    };
    writeAccounts(file, acc);
    console.log('saved credentials for', accountKey);
    break;
  }
  case 'char-count': {
    // char-count <status-text-file>
    // Prints the weighted length Mastodon uses against max_characters (500 on
    // mastodon.social) — trailing newline from the file is stripped first.
    const [file] = args;
    const text = fs.readFileSync(file, 'utf8').replace(/\n$/, '');
    console.log(weightedLength(text));
    break;
  }
  case 'build-status-payload': {
    // build-status-payload <status-text-file> <visibility> <out-file> [media_id...]
    // visibility: public|unlisted|private|direct. Trailing args (0-4) are media_ids.
    const [textFile, visibility, outFile, ...mediaIds] = args;
    const status = fs.readFileSync(textFile, 'utf8').replace(/\n$/, '');
    const payload = { status, visibility: visibility || 'public' };
    if (mediaIds.length > 0) payload.media_ids = mediaIds;
    fs.writeFileSync(outFile, JSON.stringify(payload));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes', '(media_ids:', mediaIds.length, ')');
    break;
  }
  case 'show-media-result': {
    // show-media-result <media-upload-response-json-file>
    // url is null while still processing (rare for images — normally synchronous 200).
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({ id: r.id, type: r.type, url: r.url, preview_url: r.preview_url }, null, 2));
    break;
  }
  case 'show-post-result': {
    // show-post-result <status-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({
      id: r.id,
      url: r.url,
      uri: r.uri,
      created_at: r.created_at,
      visibility: r.visibility,
      error: r.error,
    }, null, 2));
    break;
  }
  default:
    console.error('mastodon-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-credentials|char-count|build-status-payload|show-media-result|show-post-result)');
    process.exit(1);
}
