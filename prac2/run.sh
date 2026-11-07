#!/usr/bin/env bash
# Запуск анализатора зависимостей. Без аргументов используется
# config.example.ini; иначе аргументы передаются напрямую.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -eq 0 ]; then
    python3 "$ROOT/src/main.py" --config "$ROOT/config.example.ini"
else
    python3 "$ROOT/src/main.py" "$@"
fi
