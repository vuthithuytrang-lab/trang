#!/usr/bin/env bash
# HTTP wrapper for share-bai-tumblr. Tumblr API calls target hardcoded hosts
# (api.tumblr.com) so the Bash permission allowlist can scope to this script's
# invocation prefix instead of matching arbitrary curl commands.
#
# fetch-source takes the SOURCE URL as user input (the whole point of this
# skill is rewriting articles from whatever URL the user gives at
# /share-bai-tumblr time) — so it is NOT domain-restricted, only blocked from
# obvious SSRF targets (loopback/private/link-local addresses, non-http(s) schemes).
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "tumblr-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "tumblr-http.sh: URL targets a local/private address, not allowed: $url" >&2
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
  exchange-code)
    # exchange-code <client_id> <client_secret> <redirect_uri> <code> <out-file>
    # Manual fallback for when tumblr-oauth-server.js already exited (e.g. timed out)
    # but the user still has a valid ?code=... from the browser redirect URL.
    client_id="$1"; client_secret="$2"; redirect_uri="$3"; code="$4"; out="$5"
    curl -s -X POST "https://api.tumblr.com/v2/oauth2/token" \
      --data-urlencode "grant_type=authorization_code" \
      --data-urlencode "code=$code" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "redirect_uri=$redirect_uri" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  refresh-token)
    # refresh-token <client_id> <client_secret> <refresh_token> <out-file>
    # Tumblr OAuth2 access tokens are short-lived — call this before every API call.
    client_id="$1"; client_secret="$2"; refresh_token="$3"; out="$4"
    curl -s -X POST "https://api.tumblr.com/v2/oauth2/token" \
      --data-urlencode "grant_type=refresh_token" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "refresh_token=$refresh_token" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-post)
    # get-post <blog-identifier> <access_token> <post-id> <out-file>
    blog_identifier="$1"; access_token="$2"; post_id="$3"; out="$4"
    curl -s -G -H "Authorization: Bearer $access_token" \
      --data-urlencode "id=$post_id" \
      --data-urlencode "npf=true" \
      "https://api.tumblr.com/v2/blog/$blog_identifier/posts" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  delete-post)
    # delete-post <blog-identifier> <access_token> <post-id> <out-file>
    blog_identifier="$1"; access_token="$2"; post_id="$3"; out="$4"
    curl -s -X POST -H "Authorization: Bearer $access_token" \
      --data-urlencode "id=$post_id" \
      "https://api.tumblr.com/v2/blog/$blog_identifier/post/delete" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-post)
    # create-post <blog-identifier> <access_token> <payload-json-file> <out-file>
    # blog-identifier is "<name>.tumblr.com" or a custom domain, e.g. "myblog.tumblr.com"
    blog_identifier="$1"; access_token="$2"; payload="$3"; out="$4"
    curl -s -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://api.tumblr.com/v2/blog/$blog_identifier/posts" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  edit-post)
    # edit-post <blog-identifier> <access_token> <post_id> <payload-json-file> <out-file>
    # Tumblr NPF edit is PUT to the same posts collection with the post id appended.
    blog_identifier="$1"; access_token="$2"; post_id="$3"; payload="$4"; out="$5"
    curl -s -X PUT -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://api.tumblr.com/v2/blog/$blog_identifier/posts/$post_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "tumblr-http.sh: unknown subcommand '$cmd' (expected: fetch-source|exchange-code|refresh-token|create-post|edit-post|get-post|delete-post)" >&2
    exit 1
    ;;
esac
