#!/usr/bin/env bash
# Демонстрация этапа 1: вывод параметров и обработка ошибок.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAIN="$ROOT/src/main.py"

echo "== Корректный конфиг =="
python3 "$MAIN" --config "$ROOT/config.example.ini"

for cfg in err_no_package err_bad_depth err_bad_bool; do
    echo
    echo "== Ошибка: $cfg =="
    python3 "$MAIN" --config "$ROOT/examples/$cfg.ini"
done
