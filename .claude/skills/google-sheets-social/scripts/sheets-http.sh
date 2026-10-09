#!/usr/bin/env bash
# HTTP wrapper for google-sheets-social. Google Sheets API calls target hardcoded
# hosts (oauth2.googleapis.com, sheets.googleapis.com) so the Bash permission
# allowlist can scope to this script's invocation prefix instead of matching
# arbitrary curl commands. No source-URL fetching here — this skill is pure
# Sheets I/O, unlike the share-bai-* skills.
set -euo pipefail

cmd="${1:-}"; shift || true

case "$cmd" in
  refresh-token)
    # refresh-token <client_id> <client_secret> <refresh_token> <out-file>
    # Google access tokens live ~1h — call this before every Sheets API call.
    client_id="$1"; client_secret="$2"; refresh_token="$3"; out="$4"
    curl -s -X POST "https://oauth2.googleapis.com/token" \
      --data-urlencode "client_id=$client_id" \
      --data-urlencode "client_secret=$client_secret" \
      --data-urlencode "refresh_token=$refresh_token" \
      --data-urlencode "grant_type=refresh_token" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  list-sheet-tabs)
    # list-sheet-tabs <access_token> <spreadsheet_id> <out-file>
    # Lists real tab titles (properties.title) without guessing — a tab name that
    # LOOKS right in the browser can still mismatch (extra space, different Unicode
    # space char) and get-sheet-data's "Unable to parse range" error doesn't
    # distinguish a syntax error from a nonexistent sheet name.
    access_token="$1"; spreadsheet_id="$2"; out="$3"
    curl -s -G "https://sheets.googleapis.com/v4/spreadsheets/$spreadsheet_id" \
      -H "Authorization: Bearer $access_token" \
      --data-urlencode "fields=sheets.properties(sheetId,title)" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  get-sheet-data)
    # get-sheet-data <access_token> <spreadsheet_id> <sheet_name> <out-file>
    # Requests formattedValue (display text — checkbox cells read "TRUE"/"FALSE"),
    # hyperlink (the real link on a cell, independent of its display text — this is
    # what distinguishes platforms whose display names look alike), and
    # userEnteredValue (raw value, backup when formattedValue is empty).
    access_token="$1"; spreadsheet_id="$2"; sheet_name="$3"; out="$4"
    # A1-notation ranges require the sheet name single-quoted if it has any char
    # outside [A-Za-z0-9_] (space, dash, Vietnamese diacritics, emoji...) — a bare
    # "Share social" is rejected by the API as an unparsable range.
    #
    # CONFIRMED BUG on this Windows setup: curl's own --data-urlencode mangles
    # non-ASCII UTF-8 bytes (e.g. Vietnamese "í" became the U+FFFD replacement
    # char) even though the shell variable holds the correct string — curl's
    # encoder itself misreads the multi-byte sequence. Node's encodeURIComponent
    # handles UTF-8 correctly, so build the already-percent-encoded range in Node
    # and splice it into the URL directly instead of handing raw text to curl.
    if [[ "$sheet_name" =~ ^[A-Za-z0-9_]+$ ]]; then
      quoted_range="$sheet_name"
    else
      escaped_name="${sheet_name//\'/\'\'}"
      quoted_range="'$escaped_name'"
    fi
    encoded_ranges="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$quoted_range")"
    encoded_fields="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "sheets(properties(title),data(rowData(values(formattedValue,hyperlink,userEnteredValue))))")"
    curl -s "https://sheets.googleapis.com/v4/spreadsheets/$spreadsheet_id?ranges=$encoded_ranges&fields=$encoded_fields" \
      -H "Authorization: Bearer $access_token" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  update-cell)
    # update-cell <access_token> <spreadsheet_id> <a1_range> <payload-json-file> <out-file>
    # a1_range must already be A1-notation-escaped (build with sheets-json.js build-a1-range).
    # payload-json-file holds {"values":[["<value>"]]} (build with build-update-cell-body).
    access_token="$1"; spreadsheet_id="$2"; a1_range="$3"; payload="$4"; out="$5"
    encoded_range="$(node -e "console.log(encodeURIComponent(process.argv[1]))" "$a1_range")"
    curl -s -X PUT "https://sheets.googleapis.com/v4/spreadsheets/$spreadsheet_id/values/$encoded_range?valueInputOption=USER_ENTERED" \
      -H "Authorization: Bearer $access_token" -H "Content-Type: application/json" \
      --data-binary "@$payload" \
      -o "$out" -w "HTTP_STATUS:%{http_code}\n"
    ;;
  *)
    echo "sheets-http.sh: unknown subcommand '$cmd' (expected: refresh-token|list-sheet-tabs|get-sheet-data|update-cell)" >&2
    exit 1
    ;;
esac
