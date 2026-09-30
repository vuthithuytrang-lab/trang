#!/usr/bin/env bash
# HTTP wrapper for share-bai-mastodon. Mastodon instance host is a runtime
# argument (not hardcoded) since different accounts can live on different
# instances (mastodon.social, a self-hosted instance, etc.) — the Bash
# permission allowlist scopes to this script's invocation prefix instead of
# matching arbitrary curl commands.
#
# fetch-source/download-image take the SOURCE URL as user input (the whole
# point of this skill is rewriting articles from whatever URL the user gives
# at /share-bai-mastodon time) — so they are NOT domain-restricted, only
# blocked from obvious SSRF targets (loopback/private/link-local addresses,
# non-http(s) schemes).
#
# No refresh-token subcommand: Mastodon access tokens created via
# Preferences > Development > New application don't expire, unlike the
# OAuth access_token/refresh_token flow used by share-bai-wp/blogger/ggr/tumblr.
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "mastodon-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "mastodon-http.sh: URL targets a local/private address, not allowed: $url" >&2
    exit 1
  fi
}

strip_slash() {
  echo "${1%/}"
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
  verify-token)
    # verify-token <instance_url> <access_token> <out-file>
    instance="$(strip_slash "$1")"; token="$2"; out="$3"
    curl -s -H "Authorization: Bearer $token" "$instance/api/v1/accounts/verify_credentials" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  upload-media)
    # upload-media <instance_url> <access_token> <local-file> <mime-type> <description> <out-file>
    instance="$(strip_slash "$1")"; token="$2"; file="$3"; mime="$4"; desc="$5"; out="$6"
    curl -s -X POST "$instance/api/v2/media" \
      -H "Authorization: Bearer $token" \
      -F "file=@$file;type=$mime" \
      -F "description=$desc" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-media)
    # get-media <instance_url> <access_token> <media-id> <out-file>
    # Only needed if upload-media returns 202 (async processing, normally video-only —
    # images process synchronously with 200). Poll this once if url is still null.
    instance="$(strip_slash "$1")"; token="$2"; media_id="$3"; out="$4"
    curl -s -H "Authorization: Bearer $token" "$instance/api/v1/media/$media_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-status)
    # create-status <instance_url> <access_token> <payload-json-file> <out-file>
    instance="$(strip_slash "$1")"; token="$2"; payload="$3"; out="$4"
    curl -s -X POST "$instance/api/v1/statuses" \
      -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "mastodon-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|verify-token|upload-media|get-media|create-status)" >&2
    exit 1
    ;;
esac
