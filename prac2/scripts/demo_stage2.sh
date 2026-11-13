#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN="$ROOT/src/main.py"
if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi

for cfg in apt_curl apt_git apt_version \
           apt_bad_version apt_unknown apt_bad_url; do
    echo
    echo "== $cfg =="
    "$PY" "$MAIN" --config "$ROOT/examples/$cfg.ini"
done
