#!/usr/bin/env node
// JSON/MIME helpers for share-bai-ggr. Consolidates the JSON parsing/building
// this skill needs into a fixed script, so the Bash permission allowlist can
// scope to this script's invocation prefix instead of matching arbitrary `node -e`.
const fs = require('fs');
const crypto = require('crypto');

const [, , cmd, ...args] = process.argv;

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}

function writeAccounts(path, acc) {
  fs.writeFileSync(path, JSON.stringify(acc, null, 2) + '\n');
}

function base64url(buf) {
  return buf.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function wrap76(b64) {
  return b64.replace(/(.{76})/g, '$1\r\n');
}

function encodeHeaderValue(value) {
  // RFC 2047 encode Subject/etc when it contains non-ASCII (Vietnamese diacritics).
  if (/^[\x00-\x7F]*$/.test(value)) return value;
  return '=?UTF-8?B?' + Buffer.from(value, 'utf8').toString('base64') + '?=';
}

switch (cmd) {
  case 'get-account-field': {
    // get-account-field <accounts-json-file> <group-key> <field>
    const [file, groupKey, field] = args;
    const acc = readJson(file);
    const value = acc[groupKey] ? acc[groupKey][field] : undefined;
    console.log(value === undefined || value === null ? '' : value);
    break;
  }
  case 'set-client': {
    // set-client <accounts-json-file> <group-key> <client_id> <client_secret> <group-email>
    const [file, groupKey, clientId, clientSecret, groupEmail] = args;
    let acc = {};
    if (fs.existsSync(file)) acc = readJson(file);
    acc[groupKey] = {
      ...acc[groupKey],
      client_id: clientId,
      client_secret: clientSecret,
      group_email: groupEmail,
    };
    writeAccounts(file, acc);
    console.log('saved client for', groupKey);
    break;
  }
  case 'save-tokens': {
    // save-tokens <accounts-json-file> <group-key> <token-response-json-file>
    // Used once after the initial authorization_code exchange (ggr-oauth-server.js).
    const [file, groupKey, tokenRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(tokenRespFile);
    if (!resp.access_token) {
      console.error('save-tokens: response has no access_token');
      process.exit(1);
    }
    if (!resp.refresh_token && !(acc[groupKey] && acc[groupKey].refresh_token)) {
      console.error('save-tokens: response has no refresh_token and none stored yet — re-run OAuth with access_type=offline&prompt=consent');
      process.exit(1);
    }
    acc[groupKey] = {
      ...acc[groupKey],
      access_token: resp.access_token,
      refresh_token: resp.refresh_token || acc[groupKey].refresh_token,
      token_type: resp.token_type || 'Bearer',
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('saved tokens for', groupKey, 'has refresh_token:', !!acc[groupKey].refresh_token);
    break;
  }
  case 'save-refreshed-access-token': {
    // save-refreshed-access-token <accounts-json-file> <group-key> <refresh-response-json-file>
    // Google refresh responses normally do NOT include a new refresh_token — keep the stored one.
    const [file, groupKey, refreshRespFile] = args;
    const acc = readJson(file);
    const resp = readJson(refreshRespFile);
    if (!resp.access_token) {
      console.error('save-refreshed-access-token: response has no access_token (refresh_token may be revoked)');
      process.exit(1);
    }
    acc[groupKey] = {
      ...acc[groupKey],
      access_token: resp.access_token,
      expires_in_seconds: resp.expires_in || 3600,
      obtained_at: new Date().toISOString(),
    };
    writeAccounts(file, acc);
    console.log('refreshed access_token for', groupKey);
    break;
  }
  case 'build-mime-message': {
    // build-mime-message <content-html-file> <subject> <to-email> <out-file> [image-file] [image-mime]
    // Writes {"raw": "<base64url RFC 2822 message>"} to <out-file>, ready for gmail-send.
    // No Message-ID header is set here — Gmail does NOT reliably keep a
    // caller-supplied one when sending via the API (confirmed in production: a
    // permalink built from a self-generated Message-ID pointed at the wrong
    // thread), so it's pointless to set one. Gmail assigns its own; Step 8 reads
    // it back via gmail-get-message + extract-message-id before building the
    // Google Groups permalink.
    // Images MUST go in as a multipart/related inline part with Content-ID (cid:) —
    // NOT as a data: URI <img src="data:...">. Gmail and most mail clients strip
    // data: URIs from *received* HTML email for security, unlike a browser
    // rendering a normal web page (see references/google-groups-api-steps.md).
    const [contentFile, subject, to, outFile, imageFile, imageMime] = args;
    const html = fs.readFileSync(contentFile, 'utf8');
    const encodedSubject = encodeHeaderValue(subject);
    let mime;
    if (imageFile) {
      const boundary = 'ggr_' + crypto.randomBytes(12).toString('hex');
      const imgB64 = wrap76(fs.readFileSync(imageFile).toString('base64'));
      const htmlB64 = wrap76(Buffer.from(html, 'utf8').toString('base64'));
      mime = [
        'MIME-Version: 1.0',
        `To: ${to}`,
        `Subject: ${encodedSubject}`,
        `Content-Type: multipart/related; boundary="${boundary}"`,
        '',
        `--${boundary}`,
        'Content-Type: text/html; charset="UTF-8"',
        'Content-Transfer-Encoding: base64',
        '',
        htmlB64,
        '',
        `--${boundary}`,
        `Content-Type: ${imageMime || 'image/jpeg'}`,
        'Content-Transfer-Encoding: base64',
        'Content-ID: <ggr-inline-image>',
        'Content-Disposition: inline; filename="image"',
        '',
        imgB64,
        '',
        `--${boundary}--`,
        '',
      ].join('\r\n');
    } else {
      const htmlB64 = wrap76(Buffer.from(html, 'utf8').toString('base64'));
      mime = [
        'MIME-Version: 1.0',
        `To: ${to}`,
        `Subject: ${encodedSubject}`,
        'Content-Type: text/html; charset="UTF-8"',
        'Content-Transfer-Encoding: base64',
        '',
        htmlB64,
        '',
      ].join('\r\n');
    }
    const raw = base64url(Buffer.from(mime, 'utf8'));
    fs.writeFileSync(outFile, JSON.stringify({ raw }));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes (mime', mime.length, 'chars, image:', !!imageFile, ')');
    break;
  }
  case 'build-reply-mime-message': {
    // build-reply-mime-message <content-html-file> <subject> <to-email> <in-reply-to-message-id> <out-file> [image-file] [image-mime]
    // Same as build-mime-message but threads as a reply: sets In-Reply-To and
    // References to the ORIGINAL message's real Message-Id (the value
    // extract-message-id returned for the original send, e.g. "<xxx@mail.gmail.com>",
    // angle brackets included) so Gmail/Google Groups renders this as a reply in
    // the same topic instead of starting a new one. Subject should keep the
    // original subject verbatim (no "Re:" needed, but harmless if added).
    const [contentFile, subject, to, inReplyTo, outFile, imageFile, imageMime] = args;
    const html = fs.readFileSync(contentFile, 'utf8');
    const encodedSubject = encodeHeaderValue(subject);
    const threadHeaders = [`In-Reply-To: ${inReplyTo}`, `References: ${inReplyTo}`];
    let mime;
    if (imageFile) {
      const boundary = 'ggr_' + crypto.randomBytes(12).toString('hex');
      const imgB64 = wrap76(fs.readFileSync(imageFile).toString('base64'));
      const htmlB64 = wrap76(Buffer.from(html, 'utf8').toString('base64'));
      mime = [
        'MIME-Version: 1.0',
        `To: ${to}`,
        `Subject: ${encodedSubject}`,
        ...threadHeaders,
        `Content-Type: multipart/related; boundary="${boundary}"`,
        '',
        `--${boundary}`,
        'Content-Type: text/html; charset="UTF-8"',
        'Content-Transfer-Encoding: base64',
        '',
        htmlB64,
        '',
        `--${boundary}`,
        `Content-Type: ${imageMime || 'image/jpeg'}`,
        'Content-Transfer-Encoding: base64',
        'Content-ID: <ggr-inline-image>',
        'Content-Disposition: inline; filename="image"',
        '',
        imgB64,
        '',
        `--${boundary}--`,
        '',
      ].join('\r\n');
    } else {
      const htmlB64 = wrap76(Buffer.from(html, 'utf8').toString('base64'));
      mime = [
        'MIME-Version: 1.0',
        `To: ${to}`,
        `Subject: ${encodedSubject}`,
        ...threadHeaders,
        'Content-Type: text/html; charset="UTF-8"',
        'Content-Transfer-Encoding: base64',
        '',
        htmlB64,
        '',
      ].join('\r\n');
    }
    const raw = base64url(Buffer.from(mime, 'utf8'));
    fs.writeFileSync(outFile, JSON.stringify({ raw }));
    console.log('written', outFile, fs.statSync(outFile).size, 'bytes (mime', mime.length, 'chars, image:', !!imageFile, ', reply-to:', inReplyTo, ')');
    break;
  }
  case 'extract-message-id': {
    // extract-message-id <messages-get-response-json-file>
    // Reads the Message-Id header Gmail actually assigned (from a format=metadata
    // response) — this is the value that must feed build-permalink, NOT the
    // Message-ID generated before sending (Gmail may replace it).
    const [file] = args;
    const r = readJson(file);
    const headers = (r.payload && r.payload.headers) || [];
    const h = headers.find((x) => x.name && x.name.toLowerCase() === 'message-id');
    if (!h || !h.value) {
      console.error('extract-message-id: no Message-Id header found in response');
      process.exit(1);
    }
    console.log(h.value);
    break;
  }
  case 'build-permalink': {
    // build-permalink <group-email> <message-id>
    // Google Groups resolves https://groups.google.com/d/msgid/<group>/<message-id>
    // to the actual topic — this is a documented, stable permalink format that
    // works without needing to read the message back from the Gmail API.
    const [groupEmail, messageId] = args;
    const groupName = groupEmail.split('@')[0];
    const stripped = messageId.replace(/^</, '').replace(/>$/, '');
    console.log(`https://groups.google.com/d/msgid/${groupName}/${encodeURIComponent(stripped)}`);
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
  case 'show-send-result': {
    // show-send-result <send-response-json-file>
    const [file] = args;
    const r = readJson(file);
    console.log(JSON.stringify({ id: r.id, threadId: r.threadId }, null, 2));
    break;
  }
  default:
    console.error('ggr-json.js: unknown subcommand', cmd, '(expected: get-account-field|set-client|save-tokens|save-refreshed-access-token|build-mime-message|build-reply-mime-message|extract-message-id|build-permalink|word-count|show-send-result)');
    process.exit(1);
}
