#!/usr/bin/env bash
# Демонстрация параметров командной строки эмулятора (этап 2).
# Каждый вызов открывает окно эмулятора; закройте его, чтобы продолжить.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1] Без параметров (значения по умолчанию)"
python3 "$ROOT/src/emulator.py"

echo "[2] Только --vfs"
python3 "$ROOT/src/emulator.py" --vfs vfs/example.csv

echo "[3] --vfs и --script (успешный скрипт)"
python3 "$ROOT/src/emulator.py" --vfs vfs/example.csv \
    --script "$ROOT/scripts/demo_ok.esh"

echo "[4] --script с ошибкой (останов при первой ошибке)"
python3 "$ROOT/src/emulator.py" --script "$ROOT/scripts/demo_err.esh"

echo "[5] --config (TOML имеет приоритет над --vfs)"
python3 "$ROOT/src/emulator.py" --vfs ignored \
    --config "$ROOT/config.example.toml"
