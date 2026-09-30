#!/usr/bin/env bash
# HTTP wrapper for share-bai-pinterest. Pinterest API calls target hardcoded
# hosts (api.pinterest.com, or api-sandbox.pinterest.com while the app only has
# Trial access) so the Bash permission allowlist can scope to this script.
#
# fetch-source/download-image take the SOURCE URL as user input, so they are
# not domain-restricted, only blocked from local/private addresses.
#
# Every Pinterest call takes <env>: "prod" or "sandbox". Trial-access apps can
# only create Pins in the sandbox (visible to the creator only); after Standard
# access is granted, use "prod".
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "pinterest-http.sh: only http/https URLs are allowed: $url" >&2; exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "pinterest-http.sh: URL targets a local/private address, not allowed: $url" >&2; exit 1
  fi
}

api_base() {
  case "$1" in
    prod) echo "https://api.pinterest.com/v5" ;;
    sandbox) echo "https://api-sandbox.pinterest.com/v5" ;;
    *) echo "pinterest-http.sh: env must be prod or sandbox, got: $1" >&2; exit 1 ;;
  esac
}

cmd="${1:-}"; shift || true

case "$cmd" in
  fetch-source)
    # fetch-source <url> <out-file> [cookie]
    url="$1"; out="$2"; cookie="${3:-}"
    require_public_url "$url"
    curl -s -L -A "$UA" ${cookie:+-H "Cookie: $cookie"} "$url" -o "$out" \
      -w "HTTP_STATUS:%{http_code} SIZE:%{size_download}\n"
    ;;
  download-image)
    # download-image <url> <out-file> [cookie]
    url="$1"; out="$2"; cookie="${3:-}"
    require_public_url "$url"
    curl -s -L -A "$UA" ${cookie:+-H "Cookie: $cookie"} "$url" -o "$out" \
      -w "HTTP_STATUS:%{http_code} SIZE:%{size_download} TYPE:%{content_type}\n"
    ;;
  oauth-token)
    # oauth-token <app_id> <app_secret> <redirect_uri> <code> <out-file>
    app_id="$1"; app_secret="$2"; redirect_uri="$3"; code="$4"; out="$5"
    curl -s -X POST "https://api.pinterest.com/v5/oauth/token" \
      -u "$app_id:$app_secret" \
      --data-urlencode "grant_type=authorization_code" \
      --data-urlencode "code=$code" \
      --data-urlencode "redirect_uri=$redirect_uri" \
      --data-urlencode "continuous_refresh=true" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  refresh-token)
    # refresh-token <app_id> <app_secret> <refresh_token> <out-file>
    app_id="$1"; app_secret="$2"; refresh_token="$3"; out="$4"
    curl -s -X POST "https://api.pinterest.com/v5/oauth/token" \
      -u "$app_id:$app_secret" \
      --data-urlencode "grant_type=refresh_token" \
      --data-urlencode "refresh_token=$refresh_token" \
      --data-urlencode "continuous_refresh=true" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-user)
    # get-user <env> <access_token> <out-file>
    base="$(api_base "$1")"; token="$2"; out="$3"
    curl -s -H "Authorization: Bearer $token" "$base/user_account" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  list-boards)
    # list-boards <env> <access_token> <out-file>
    base="$(api_base "$1")"; token="$2"; out="$3"
    curl -s -H "Authorization: Bearer $token" "$base/boards?page_size=100" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-board)
    # create-board <env> <access_token> <payload-json-file> <out-file>
    base="$(api_base "$1")"; token="$2"; payload="$3"; out="$4"
    curl -s -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" "$base/boards" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-pin)
    # create-pin <env> <access_token> <payload-json-file> <out-file>
    base="$(api_base "$1")"; token="$2"; payload="$3"; out="$4"
    curl -s -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" "$base/pins" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-pin)
    # get-pin <env> <access_token> <pin_id> <out-file>
    base="$(api_base "$1")"; token="$2"; pin_id="$3"; out="$4"
    curl -s -H "Authorization: Bearer $token" "$base/pins/$pin_id" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "pinterest-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|oauth-token|refresh-token|get-user|list-boards|create-board|create-pin|get-pin)" >&2
    exit 1
    ;;
esac
