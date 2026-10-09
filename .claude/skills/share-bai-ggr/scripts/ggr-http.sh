#!/usr/bin/env bash
# HTTP wrapper for share-bai-ggr. Google API calls target hardcoded hosts
# (oauth2.googleapis.com, gmail.googleapis.com) so the Bash permission
# allowlist can scope to this script's invocation prefix instead of matching
# arbitrary curl commands.
#
# fetch-source/download-image take the SOURCE URL as user input (the whole point
# of this skill is rewriting articles from whatever URL the user gives at
# /share-bai-ggr time) — so they are NOT domain-restricted, only blocked from
# obvious SSRF targets (loopback/private/link-local addresses, non-http(s) schemes).
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "ggr-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "ggr-http.sh: URL targets a local/private address, not allowed: $url" >&2
    exit 1
  fi
}

cmd="${1:-}"; shift || true

case "$cmd" in
  fetch-source)
    # fetch-source <url> <out-file> [cookie]  -- url is the user-supplied source article URL
    url="$1"; out="$2"; cookie="${3:-}"
    require_public_url "$url"
    if [ -n "$cookie" ]; then
      curl -s -A "$UA" -b "$cookie" "$url" -o "$out" -w "HTTP_STATUS:%{http_code} SIZE:%{size_download}\n"
    else
      curl -s -A "$UA" "$url" -o "$out" -w "HTTP_STATUS:%{http_code} SIZE:%{size_download}\n"
    fi
    ;;
  download-image)
    # download-image <url> <out-file> <cookie>  -- url comes from the source article (og:image/img src)
    url="$1"; out="$2"; cookie="$3"
    require_public_url "$url"
    curl -s -A "$UA" -b "$cookie" "$url" -o "$out" -w "HTTP_STATUS:%{http_code} SIZE:%{size_download} TYPE:%{content_type}\n"
    ;;
  refresh-token)
    # refresh-token <client_id> <client_secret> <refresh_token> <out-file>
    # Google access tokens live ~1h — call this before every Gmail API call, no user interaction needed.
    client_id="$1"; client_secret="$2"; refresh_token="$3"; out="$4"
    curl -s -X POST "https://oauth2.googleapis.com/token" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "refresh_token=$refresh_token" \
      --data-urlencode "grant_type=refresh_token" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  gmail-send)
    # gmail-send <access_token> <raw-payload-json-file> <out-file>
    # payload file is {"raw": "<base64url RFC 2822 message>"} built by ggr-json.js build-mime-message
    access_token="$1"; payload="$2"; out="$3"
    curl -s -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://gmail.googleapis.com/gmail/v1/users/me/messages/send" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  gmail-get-message)
    # gmail-get-message <access_token> <message-id> <out-file>
    # Headers-only fetch (format=metadata) of the just-sent message, to read back
    # the REAL Message-Id Gmail assigned — needed because Gmail does not reliably
    # keep a caller-supplied Message-ID header, so the Google Groups permalink
    # must be built from this value, not from an ID generated before sending.
    access_token="$1"; message_id="$2"; out="$3"
    curl -s -G -H "Authorization: Bearer $access_token" \
      --data-urlencode "format=metadata" \
      --data-urlencode "metadataHeaders=Message-Id" \
      "https://gmail.googleapis.com/gmail/v1/users/me/messages/$message_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "ggr-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|refresh-token|gmail-send|gmail-get-message)" >&2
    exit 1
    ;;
esac
