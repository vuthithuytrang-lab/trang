#!/usr/bin/env bash
# HTTP wrapper for share-bai-blogger. Google/Blogger API calls target hardcoded
# hosts (oauth2.googleapis.com, www.googleapis.com) so the Bash permission
# allowlist can scope to this script's invocation prefix instead of matching
# arbitrary curl commands.
#
# fetch-source/download-image take the SOURCE URL as user input (the whole point
# of this skill is rewriting articles from whatever URL the user gives at
# /share-bai-blogger time) — so they are NOT domain-restricted, only blocked from
# obvious SSRF targets (loopback/private/link-local addresses, non-http(s) schemes).
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "blogger-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "blogger-http.sh: URL targets a local/private address, not allowed: $url" >&2
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
    # Google access tokens live ~1h — call this before every Blogger API call, no user interaction needed.
    client_id="$1"; client_secret="$2"; refresh_token="$3"; out="$4"
    curl -s -X POST "https://oauth2.googleapis.com/token" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "refresh_token=$refresh_token" \
      --data-urlencode "grant_type=refresh_token" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-blog-by-url)
    # get-blog-by-url <access_token> <blog-url> <out-file>
    access_token="$1"; blog_url="$2"; out="$3"
    curl -s -G -H "Authorization: Bearer $access_token" \
      --data-urlencode "url=$blog_url" \
      "https://www.googleapis.com/blogger/v3/blogs/byurl" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-post)
    # create-post <blog-id> <access_token> <payload-json-file> <out-file>
    blog_id="$1"; access_token="$2"; payload="$3"; out="$4"
    curl -s -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://www.googleapis.com/blogger/v3/blogs/$blog_id/posts/" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  update-post)
    # update-post <blog-id> <post-id> <access_token> <payload-json-file> <out-file>
    blog_id="$1"; post_id="$2"; access_token="$3"; payload="$4"; out="$5"
    curl -s -X PUT -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "https://www.googleapis.com/blogger/v3/blogs/$blog_id/posts/$post_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-post-by-url)
    # get-post-by-url <blog-id> <post-url> <access_token> <out-file>
    # Blogger API "bypath" lookup — returns the post JSON (incl. numeric "id")
    # for a live published post URL, needed before update-post can target it.
    #
    # A bare "path=/2026/09/..." argument gets mangled by Git-Bash/MSYS's
    # automatic POSIX-path conversion (it rewrites the leading "/2026/..." into
    # a Windows path like "C:/Program Files/Git/2026/..."), the same class of
    # bug as the Unicode --data-urlencode issue noted elsewhere in this project.
    # Fix: pre-encode the path in Node (percent-encoding removes every literal
    # "/" from the argv token, so MSYS has nothing path-shaped to rewrite) and
    # splice it into a single, already-complete URL instead of a separate
    # --data-urlencode argument.
    blog_id="$1"; post_url="$2"; access_token="$3"; out="$4"
    encoded_path=$(node -e "console.log(encodeURIComponent(new URL(process.argv[1]).pathname))" "$post_url")
    curl -s -H "Authorization: Bearer $access_token" \
      "https://www.googleapis.com/blogger/v3/blogs/$blog_id/posts/bypath?path=$encoded_path" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "blogger-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|refresh-token|get-blog-by-url|get-post-by-url|create-post|update-post)" >&2
    exit 1
    ;;
esac
