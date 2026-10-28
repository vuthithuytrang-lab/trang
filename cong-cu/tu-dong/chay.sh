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
[ $MA = vang-14k ] && buoc $P $CT/tao_sua.py --xem - --gia - --bo-to-ngay-xu-huong cap-nhat/tam/bai1.min.html
$P $SKILL xem cap-nhat/cau-hinh.json bai1 > $X2
$P $CT/tao_sua.py --kiem --xem $X2 "${KIEM[@]}" | tee cap-nhat/kiem.txt
cp cap-nhat/tam/bai1.min.html "$W/bai.html"
echo "XONG $MA ngày $N"
