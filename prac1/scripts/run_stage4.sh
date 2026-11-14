#!/usr/bin/env bash
# Демонстрация команд этапа 4 (ls, cd, uptime, find, tree).
# Открывает окно эмулятора; закройте его, чтобы продолжить.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1] Все команды этапа 4 на многофайловой VFS"
python3 "$ROOT/src/emulator.py" --vfs "$ROOT/vfs/multi.csv" \
    --script "$ROOT/scripts/stage4_all.esh"

echo "[2] Интерактивный режим на многофайловой VFS"
python3 "$ROOT/src/emulator.py" --vfs "$ROOT/vfs/multi.csv"
