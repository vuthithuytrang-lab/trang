#!/usr/bin/env bash
# Usage (chạy trong thư mục chứa skill): bash scripts/install.sh
set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== /inlink-generator — Installer ==="
echo "Thư mục skill: $SKILL_DIR"
mkdir -p "$SKILL_DIR/credentials" "$SKILL_DIR/oauth_clients" "$SKILL_DIR/runs"

for py in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$py" >/dev/null 2>&1; then
    PYBIN="$py"; break
  fi
done
if [ -z "$PYBIN" ]; then
  echo "ERROR: Python 3.10+ required."; exit 1
fi

echo "Using: $($PYBIN --version)"
[ ! -d "$SKILL_DIR/.venv" ] && "$PYBIN" -m venv "$SKILL_DIR/.venv"

"$SKILL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SKILL_DIR/.venv/bin/pip" install --quiet -r "$SKILL_DIR/scripts/requirements.txt"

echo "=== Done ==="
