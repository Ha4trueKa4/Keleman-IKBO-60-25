#!/usr/bin/env bash
# Запуск эмулятора оболочки (этап 1).
# Необязательный аргумент: имя VFS.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$DIR/src/emulator.py" "$@"
