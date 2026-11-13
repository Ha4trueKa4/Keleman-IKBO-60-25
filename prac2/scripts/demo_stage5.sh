#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN="$ROOT/src/main.py"
if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi

for cfg in "$ROOT/config.example.ini" \
           "$ROOT/examples/apt_curl.ini" \
           "$ROOT/examples/apt_git.ini" \
           "$ROOT/examples/test_complex.ini"; do
    echo
    echo "== $(basename "$cfg") =="
    "$PY" "$MAIN" --config "$cfg" \
        | sed -n '/^Описание графа/,/^Порядок загрузки/p' \
        | sed '$d'
done
