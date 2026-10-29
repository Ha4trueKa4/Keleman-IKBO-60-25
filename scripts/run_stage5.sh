#!/usr/bin/env bash
# Демонстрация команд этапа 5 (mkdir, rm) — изменение VFS в памяти.
# Открывает окно эмулятора; закройте его, чтобы продолжить.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[1] Команды этапа 5 на многофайловой VFS"
python3 "$ROOT/src/emulator.py" --vfs "$ROOT/vfs/multi.csv" \
    --script "$ROOT/scripts/stage5_all.esh"

echo "[2] Интерактивный режим (попробуйте mkdir и rm вручную)"
python3 "$ROOT/src/emulator.py" --vfs "$ROOT/vfs/multi.csv"
