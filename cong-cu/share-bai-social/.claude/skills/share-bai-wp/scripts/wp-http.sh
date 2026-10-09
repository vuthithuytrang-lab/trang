#!/usr/bin/env bash
# HTTP wrapper for share-bai-wp. WordPress API calls target a hardcoded host
# (public-api.wordpress.com) so the Bash permission allowlist can scope to this
# script's invocation prefix instead of matching arbitrary curl commands.
#
# fetch-source/download-image take the SOURCE URL as user input (the whole point
# of this skill is rewriting articles from whatever URL the user gives at /share-bai-wp
# time) — so they are NOT domain-restricted, only blocked from obvious SSRF targets
# (loopback/private/link-local addresses, non-http(s) schemes).
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "wp-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "wp-http.sh: URL targets a local/private address, not allowed: $url" >&2
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
  check-site)
    # check-site <site-domain> <token>
    site="$1"; token="$2"
    curl -s -H "Authorization: Bearer $token" "https://public-api.wordpress.com/rest/v1.1/sites/$site" -o /dev/null -w "HTTP_STATUS:%{http_code}\n"
    ;;
  oauth-token)
    # oauth-token <client_id> <client_secret> <redirect_uri> <code> <out-file>
    client_id="$1"; client_secret="$2"; redirect_uri="$3"; code="$4"; out="$5"
    curl -s -X POST "https://public-api.wordpress.com/oauth2/token" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "redirect_uri=$redirect_uri" \
      --data-urlencode "code=$code" \
      --data-urlencode "grant_type=authorization_code" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  upload-media)
    # upload-media <site-domain> <token> <local-file> <mime-type> <out-file>
    site="$1"; token="$2"; file="$3"; mime="$4"; out="$5"
    curl -s -H "Authorization: Bearer $token" \
      -F "media[]=@$file;type=$mime" \
      "https://public-api.wordpress.com/rest/v1.1/sites/$site/media/new" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-post)
    # create-post <site-domain> <token> <payload-json-file> <out-file>
    site="$1"; token="$2"; payload="$3"; out="$4"
    curl -s -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://public-api.wordpress.com/rest/v1.1/sites/$site/posts/new" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  update-post)
    # update-post <site-domain> <token> <post_id> <payload-json-file> <out-file>
    # Same endpoint shape as create-post, just targeting an existing post ID
    # instead of "new" — WordPress.com REST API treats both as POST.
    site="$1"; token="$2"; post_id="$3"; payload="$4"; out="$5"
    curl -s -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://public-api.wordpress.com/rest/v1.1/sites/$site/posts/$post_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-post-by-slug)
    # get-post-by-slug <site-domain> <token> <slug> <out-file>
    # WordPress.com REST API convenience path — returns the post JSON (incl.
    # numeric "ID") for its slug, needed before update-post can target it.
    site="$1"; token="$2"; slug="$3"; out="$4"
    curl -s -H "Authorization: Bearer $token" \
      "https://public-api.wordpress.com/rest/v1.1/sites/$site/posts/slug:$slug" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "wp-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|check-site|oauth-token|upload-media|create-post|update-post|get-post-by-slug)" >&2
    exit 1
    ;;
esac
