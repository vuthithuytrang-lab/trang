#!/usr/bin/env node
// One-time Tumblr OAuth2 flow for share-bai-tumblr. Starts a short-lived local
// HTTP server as the redirect_uri, prints the authorize URL for the user to
// open manually (no Claude in Chrome / browser automation involved), captures
// the ?code= Tumblr sends back, exchanges it for tokens, and writes the raw
// token response to <out-file>. Caller then runs
// `node tumblr-json.js save-tokens <accounts-file> <blog-key> <out-file>`.
//
// Tumblr rejects raw-IP redirect URIs at app-registration time ("This url's
// domain is not valid") — the app must be registered with an `http://localhost:PORT/`
// callback, not `http://127.0.0.1:PORT/`. The local server still binds to
// 127.0.0.1 (loopback resolves the same), only the URL text differs.
//
// Scope is write + offline_access. offline_access is required to receive a
// refresh_token (confirmed in Tumblr API docs) — without it, Tumblr issues an
// access_token only, which expires and forces re-authorization every time.
//
// Usage: node tumblr-oauth-server.js <client_id> <client_secret> <out-file> [port]
const http = require('http');
const https = require('https');
const crypto = require('crypto');
const querystring = require('querystring');

const [, , clientId, clientSecret, outFile, portArg] = process.argv;
if (!clientId || !clientSecret || !outFile) {
  console.error('Usage: node tumblr-oauth-server.js <client_id> <client_secret> <out-file> [port]');
  process.exit(1);
}
const port = Number(portArg) || 8767;
const redirectUri = `http://localhost:${port}/`;
const SCOPE = 'write offline_access';
// OAUTH_STATE lets a remote/cloud session print the authorize URL first and
// replay the pasted redirect later with the same state (browser and server on
// different machines); default stays a fresh random state per run.
const state = process.env.OAUTH_STATE || crypto.randomBytes(16).toString('hex');
const TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes to click Allow

const authorizeUrl =
  'https://www.tumblr.com/oauth2/authorize?' +
  querystring.stringify({
    client_id: clientId,
    response_type: 'code',
    scope: SCOPE,
    state,
    redirect_uri: redirectUri,
  });

function exchangeCode(code) {
  const body = querystring.stringify({
    grant_type: 'authorization_code',
    code,
    client_id: clientId,
    client_secret: clientSecret,
    redirect_uri: redirectUri,
  });
  const req = https.request(
    {
      hostname: 'api.tumblr.com',
      path: '/v2/oauth2/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(body),
      },
    },
    (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        require('fs').writeFileSync(outFile, data);
        console.log('HTTP_STATUS:' + res.statusCode);
        process.exit(res.statusCode === 200 ? 0 : 1);
      });
    }
  );
  req.on('error', (err) => {
    console.error('token exchange request failed:', err.message);
    process.exit(1);
  });
  req.write(body);
  req.end();
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, redirectUri);
  const code = url.searchParams.get('code');
  const returnedState = url.searchParams.get('state');
  const error = url.searchParams.get('error');

  if (error) {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end('<html><body>Đã từ chối cấp quyền. Có thể đóng tab này.</body></html>');
    server.close();
    require('fs').writeFileSync(outFile, JSON.stringify({ error }));
    console.error('User denied consent:', error);
    process.exit(1);
  }
  if (!code) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('missing code');
    return;
  }
  if (returnedState !== state) {
    res.writeHead(400, { 'Content-Type': 'text/plain' });
    res.end('state mismatch');
    server.close();
    console.error('state mismatch — possible CSRF, aborting');
    process.exit(1);
  }

  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end('<html><body>Đã nhận quyền truy cập. Có thể đóng tab này và quay lại Claude Code.</body></html>');
  server.close();
  exchangeCode(code);
});

server.listen(port, '127.0.0.1', () => {
  console.log('Mở link này trong trình duyệt để cấp quyền (chỉ cần làm 1 lần):');
  console.log(authorizeUrl);
});

setTimeout(() => {
  console.error(`Hết thời gian chờ (${TIMEOUT_MS / 1000}s) — không nhận được phản hồi. Thử lại.`);
  server.close();
  process.exit(1);
}, TIMEOUT_MS);
