#!/usr/bin/env bash
# HTTP wrapper for share-bai-wix. Wix API calls target a hardcoded host
# (www.wixapis.com) so the Bash permission allowlist can scope to this
# script's invocation prefix instead of matching arbitrary curl commands.
#
# fetch-source takes the SOURCE URL as user input (the whole point of this
# skill is rewriting articles from whatever URL the user gives at
# /share-bai-wix time) — so it is NOT domain-restricted, only blocked from
# obvious SSRF targets (loopback/private/link-local addresses, non-http(s) schemes).
# Source images are handled the same way via import-media below — Wix fetches
# the bytes itself from the source URL, so this script never downloads image
# bytes locally.
#
# No refresh-token subcommand: Wix API keys don't expire, unlike the OAuth
# access_token flow used by share-bai-wp/blogger/ggr/tumblr.
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "wix-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "wix-http.sh: URL targets a local/private address, not allowed: $url" >&2
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
  query-sites)
    # query-sites <api_key> <account_id> <out-file>
    # Account-level call — lists sites in the account so the user can find the right site_id
    # when they can't read it off the dashboard URL themselves.
    api_key="$1"; account_id="$2"; out="$3"
    curl -s -X POST "https://www.wixapis.com/site-list/v2/sites/query" \
      -H "Authorization: $api_key" -H "wix-account-id: $account_id" -H "Content-Type: application/json" \
      -d '{}' \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-members)
    # get-members <api_key> <site_id> <out-file>
    # Site-level call — used once during setup to find a memberId to attribute posts to.
    api_key="$1"; site_id="$2"; out="$3"
    curl -s "https://www.wixapis.com/members/v1/members" \
      -H "Authorization: $api_key" -H "wix-site-id: $site_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  import-media)
    # import-media <api_key> <site_id> <image-url> <mime-type> <display-name> <out-file>
    # Wix fetches and hosts the image itself — no local download/upload step needed here.
    api_key="$1"; site_id="$2"; image_url="$3"; mime="$4"; display_name="$5"; out="$6"
    curl -s -X POST "https://www.wixapis.com/site-media/v1/files/import" \
      -H "Authorization: $api_key" -H "wix-site-id: $site_id" -H "Content-Type: application/json" \
      -d "$(printf '{"url":"%s","mimeType":"%s","displayName":"%s"}' "$image_url" "$mime" "$display_name")" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-draft-post)
    # create-draft-post <api_key> <site_id> <payload-json-file> <out-file>
    # fieldsets=URL is required in the query string, else the response omits the
    # "url" field entirely (base fields alone don't include it) — confirmed in docs.
    api_key="$1"; site_id="$2"; payload="$3"; out="$4"
    curl -s -X POST "https://www.wixapis.com/blog/v3/draft-posts?fieldsets=URL" \
      -H "Authorization: $api_key" -H "wix-site-id: $site_id" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-draft-post)
    # get-draft-post <api_key> <site_id> <post-id> <out-file>
    # Used to verify what's actually saved (title/richContent) after create/update calls.
    api_key="$1"; site_id="$2"; post_id="$3"; out="$4"
    curl -s "https://www.wixapis.com/blog/v3/draft-posts/$post_id?fieldsets=URL&fieldsets=RICH_CONTENT" \
      -H "Authorization: $api_key" -H "wix-site-id: $site_id" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  update-draft-post)
    # update-draft-post <api_key> <site_id> <post-id> <payload-json-file> <out-file>
    # CreateDraftPost does NOT accept a custom seoSlug — Wix auto-generates one from the
    # title, percent-encoding Vietnamese diacritics into an unreadable URL. This PATCH call
    # (with action:"UPDATE_PUBLICATION" in the payload, since the post is already published)
    # fixes the slug to a clean ASCII one after creation. fieldsets=URL again required to
    # get the updated "url" back in the response.
    api_key="$1"; site_id="$2"; post_id="$3"; payload="$4"; out="$5"
    curl -s -X PATCH "https://www.wixapis.com/blog/v3/draft-posts/$post_id?fieldsets=URL" \
      -H "Authorization: $api_key" -H "wix-site-id: $site_id" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "wix-http.sh: unknown subcommand '$cmd' (expected: fetch-source|query-sites|get-members|import-media|create-draft-post|get-draft-post|update-draft-post)" >&2
    exit 1
    ;;
esac
