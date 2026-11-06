# fetch.sh <url> <outfile> — tải trang Okamura, UA trình duyệt, thử lại 3 lần
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
u="${1%%\?*}"; [ -s "$2" ] && { echo "cache $2"; exit 0; }
for n in 1 2 3; do c=$(curl -sS -L -o "$2" -w "%{http_code}" -A "$UA" -H "Accept-Language: vi-VN,vi;q=0.9" "$u"); [ "$c" = 200 ] && break; sleep $((n*3)); done
echo "$c $(stat -c%s "$2") $u"; sleep 1
