#!/usr/bin/env bash
# HTTP wrapper for share-bai-webflow. Webflow API calls target a hardcoded host
# (api.webflow.com) so the Bash permission allowlist can scope to this script's
# invocation prefix instead of matching arbitrary curl commands.
#
# fetch-source/download-image take the SOURCE URL as user input (the whole point
# of this skill is rewriting articles from whatever URL the user gives at
# /share-bai-webflow time) — so they are NOT domain-restricted, only blocked
# from obvious SSRF targets (loopback/private/link-local addresses, non-http(s)
# schemes).
set -euo pipefail

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
BLOCKED_HOST_REGEX='^https?://(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2[0-9]|3[01])\.|\[::1\]|\[fe80|\[fc|\[fd)'
API='https://api.webflow.com/v2'

require_public_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https?:// ]]; then
    echo "webflow-http.sh: only http/https URLs are allowed: $url" >&2
    exit 1
  fi
  if [[ "$url" =~ $BLOCKED_HOST_REGEX ]]; then
    echo "webflow-http.sh: URL targets a local/private address, not allowed: $url" >&2
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
  list-sites)
    # list-sites <token> <out-file>  -- GET /v2/sites, also doubles as token/plan-access check
    token="$1"; out="$2"
    curl -s -H "Authorization: Bearer $token" "$API/sites" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  list-collections)
    # list-collections <site_id> <token> <out-file>
    site_id="$1"; token="$2"; out="$3"
    curl -s -H "Authorization: Bearer $token" "$API/sites/$site_id/collections" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-collection)
    # get-collection <collection_id> <token> <out-file>  -- fetch field schema (slugs + types)
    collection_id="$1"; token="$2"; out="$3"
    curl -s -H "Authorization: Bearer $token" "$API/collections/$collection_id" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-asset)
    # create-asset <site_id> <token> <file-name> <file-hash-md5-hex> <out-file>
    site_id="$1"; token="$2"; file_name="$3"; file_hash="$4"; out="$5"
    curl -s -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data "{\"fileName\":\"$file_name\",\"fileHash\":\"$file_hash\"}" \
      "$API/sites/$site_id/assets" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  upload-asset)
    # upload-asset <upload-url> <upload-details-json-file> <local-file> <out-file>
    # uploadDetails is treated as a flat {field: value} map of S3 POST-policy form
    # fields (standard S3 presigned-POST shape) — read dynamically instead of
    # hardcoding field names, since Webflow's exact keys aren't pinned down here.
    # See references/webflow-cms-api-steps.md "Known limits" — verify live before relying on this.
    upload_url="$1"; details_file="$2"; local_file="$3"; out="$4"
    form_args=()
    while IFS=$'\t' read -r key value; do
      [ -z "$key" ] && continue
      form_args+=(-F "$key=$value")
    done < <(node -e "
      const r = require(process.argv[1]);
      const d = r.uploadDetails || r;
      for (const [k, v] of Object.entries(d)) console.log(k + '\t' + v);
    " "$details_file")
    curl -s "${form_args[@]}" -F "file=@$local_file" "$upload_url" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  create-item)
    # create-item <collection_id> <token> <payload-json-file> <out-file>
    collection_id="$1"; token="$2"; payload="$3"; out="$4"
    curl -s -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      "$API/collections/$collection_id/items" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  publish-item)
    # publish-item <collection_id> <token> <item_id> <out-file>
    collection_id="$1"; token="$2"; item_id="$3"; out="$4"
    curl -s -X POST -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
      --data "{\"itemIds\":[\"$item_id\"]}" \
      "$API/collections/$collection_id/items/publish" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-item)
    # get-item <collection_id> <item_id> <token> <out-file>  -- verify after publish
    collection_id="$1"; item_id="$2"; token="$3"; out="$4"
    curl -s -H "Authorization: Bearer $token" "$API/collections/$collection_id/items/$item_id" -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "webflow-http.sh: unknown subcommand '$cmd' (expected: fetch-source|download-image|list-sites|list-collections|get-collection|create-asset|upload-asset|create-item|publish-item|get-item)" >&2
    exit 1
    ;;
esac
