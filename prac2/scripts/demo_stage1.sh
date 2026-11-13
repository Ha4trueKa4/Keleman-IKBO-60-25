#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN="$ROOT/src/main.py"
if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi

echo "== Корректный конфиг =="
"$PY" "$MAIN" --show-config --config "$ROOT/config.example.ini"

for cfg in err_no_section err_no_package err_no_repo \
           err_bad_bool err_bad_depth err_negative_depth; do
    echo
    echo "== Ошибка: $cfg =="
    "$PY" "$MAIN" --show-config --config "$ROOT/examples/$cfg.ini"
done
