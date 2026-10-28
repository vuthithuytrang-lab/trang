#!/usr/bin/env bash
# Chạy trọn công thức của 1 bài TCB không cần Claude: tải bài + lấy giá + sửa số + tô vàng -> <ra>/<mã>/bai1.min.html
# Dùng: bash chay.sh <mã công thức> <thư mục ra>     (mã = tên thư mục trong skill-cap-nhat-bai-tcb/cong-thuc/)
set -uo pipefail
MA=$1; RA=$(realpath -m "$2")
GOC=$(cd "$(dirname "$0")/../skill-cap-nhat-bai-tcb" && pwd)
SKILL=$GOC/cap-nhat-bai-tcb/scripts/cap_nhat.py; CT=$GOC/cong-thuc/$MA
W=$RA/$MA; rm -rf "$W"; mkdir -p "$W/cap-nhat"; cd "$W"
cp "$CT/cau-hinh.json" cap-nhat/
N=$(TZ=Asia/Ho_Chi_Minh date -d "+1 day" +%d/%m/%Y)     # luôn ghi ngày hôm sau (Trang chốt 21/10/2026)
P="python3 -I"; X=cap-nhat/xem.txt; X2=cap-nhat/xem2.txt
buoc(){ echo "▶ $*"; "$@"; }
case $MA in
  lai-suat-1|lai-suat-2)                                  # 2 bài lãi suất: công cụ riêng cong-cu/cap-nhat-lai-suat
    SO=${MA#lai-suat-}; cp "$GOC/../cap-nhat-lai-suat/cap-nhat.py" .
    buoc $P cap-nhat.py lay && buoc $P cap-nhat.py dung $N || { echo "LỖI công cụ lãi suất"; exit 1; }
    [ $SO = 1 ] && TEN="Lãi suất tiết kiệm Techcombank" || TEN="Cách tính lãi suất tiền gửi tiết kiệm Techcombank"
    python3 -I - "$SO" <<'PY'
import json, sys
k = json.load(open('tam/ket-qua.json')); b = k['bai'].get('bai' + sys.argv[1], {})
if b.get('loi'):
    print('LỖI:', b['loi']); sys.exit(1)
for x in [f'Chưa cập nhật được từ {n} do không truy cập được' for n in k.get('loi_nguon', [])] + b.get('can_duyet', []):
    print('  cần duyệt:', x)
PY
    [ $? = 0 ] || exit 1
    echo "bai1 $TEN – $N: 0 bảng lãi suất"                # dòng tên file cho tong_hop.py
    cp tam/bai$SO.min.html "$W/bai.html"
    echo "XONG $MA ngày $N"; exit 0 ;;
esac
buoc $P $SKILL lay cap-nhat/cau-hinh.json
case $MA in
  gia-ca-phe)
    buoc $P $SKILL dung cap-nhat/cau-hinh.json $N
    buoc node $CT/lay_gia_the_gioi.js cap-nhat/gia-the-gioi.json
    $P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X
    buoc $P $CT/tao_sua.py --xem $X --nha-be cap-nhat/tam/thamkhao1.goc --the-gioi cap-nhat/gia-the-gioi.json --ra cap-nhat/sua.json
    KIEM=(--nha-be cap-nhat/tam/thamkhao1.goc --the-gioi cap-nhat/gia-the-gioi.json) ;;
  gia-xang-dau)
    buoc $P $CT/lay_gia.py cap-nhat
    buoc $P $SKILL dung cap-nhat/cau-hinh.json $N
    $P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X
    buoc $P $CT/tao_sua.py --xem $X --gia cap-nhat/gia.json --ra cap-nhat/sua.json
    KIEM=(--gia cap-nhat/gia.json) ;;
  1-chi-vang)
    buoc node $CT/lay_bang.js cap-nhat/bang-nguon.json
    buoc $P $SKILL dung cap-nhat/cau-hinh.json $N
    $P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X
    buoc $P $CT/tao_sua.py --xem $X --nguon cap-nhat/bang-nguon.json --ra cap-nhat/sua.json
    KIEM=(--nguon cap-nhat/bang-nguon.json) ;;
  vang-*)
    JS=$(ls $CT/lay_*.js | head -1); G=cap-nhat/gia.json
    buoc node $JS $G
    buoc $P $SKILL dung cap-nhat/cau-hinh.json $N
    $P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X
    THEM=(); [ $MA = vang-14k ] && THEM=(--goc cap-nhat/tam/bai1.html)
    buoc $P $CT/tao_sua.py --xem $X --gia $G "${THEM[@]}" --ra cap-nhat/sua.json
    KIEM=(--gia $G "${THEM[@]}") ;;
  *) echo "Chưa có công thức cho $MA"; exit 2 ;;
esac
buoc $P $SKILL sua cap-nhat/cau-hinh.json cap-nhat/sua.json
[ $MA = vang-14k ] && buoc $P $CT/tao_sua.py --xem - --gia - --goc cap-nhat/tam/bai1.html --bo-to-ngay-xu-huong cap-nhat/tam/bai1.min.html
$P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X2
$P $CT/tao_sua.py --kiem --xem $X2 "${KIEM[@]}" | tee cap-nhat/kiem.txt
cp cap-nhat/tam/bai1.min.html "$W/bai.html"
echo "XONG $MA ngày $N"
