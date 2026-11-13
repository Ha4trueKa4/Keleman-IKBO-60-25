#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN="$ROOT/src/main.py"
if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi

for cfg in test_diamond test_cycle test_filter test_complex order_bash; do
    echo
    echo "== $cfg =="
    "$PY" "$MAIN" --config "$ROOT/examples/$cfg.ini" \
        | sed -n '/^Порядок загрузки/,$p'
done
