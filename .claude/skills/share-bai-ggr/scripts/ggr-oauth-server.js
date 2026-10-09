#!/usr/bin/env node
// One-time Google OAuth flow for share-bai-ggr. Starts a short-lived local
// HTTP server as the redirect_uri, prints the authorize URL for the user to
// open manually (no Claude in Chrome / browser automation involved), captures
// the ?code= Google sends back, exchanges it for tokens, and writes the raw
// token response to <out-file>. Caller then runs
// `node ggr-json.js save-tokens <accounts-file> <group-key> <out-file>`.
//
// Scope is gmail.send + gmail.metadata. gmail.send alone is not enough:
// Gmail does NOT reliably keep a caller-supplied Message-ID header when
// sending via the API (confirmed in production — a permalink built from a
// self-generated Message-ID pointed at the wrong/non-existent thread).
// gmail.metadata lets Step 8 read back the REAL Message-Id Gmail assigned
// (headers only, no body access) so the Google Groups permalink is built
// from the value Gmail actually used, not a guess.
//
// Usage: node ggr-oauth-server.js <client_id> <client_secret> <out-file> [port]
const http = require('http');
const https = require('https');
const querystring = require('querystring');

const [, , clientId, clientSecret, outFile, portArg] = process.argv;
if (!clientId || !clientSecret || !outFile) {
  console.error('Usage: node ggr-oauth-server.js <client_id> <client_secret> <out-file> [port]');
  process.exit(1);
}
const port = Number(portArg) || 8766;
const redirectUri = `http://127.0.0.1:${port}`;
const SCOPE = 'https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.metadata';
const TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes to click Allow

const authorizeUrl =
  'https://accounts.google.com/o/oauth2/v2/auth?' +
  querystring.stringify({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code',
    scope: SCOPE,
    access_type: 'offline', // required to receive a refresh_token
    prompt: 'consent', // forces refresh_token on repeat authorizations too
  });

function exchangeCode(code) {
  const body = querystring.stringify({
    client_id: clientId,
    client_secret: clientSecret,
    code,
    grant_type: 'authorization_code',
    redirect_uri: redirectUri,
  });
  const req = https.request(
    {
      hostname: 'oauth2.googleapis.com',
      path: '/token',
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
