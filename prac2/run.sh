#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$#" -eq 0 ]; then
    python3 "$ROOT/src/main.py" --config "$ROOT/config.example.ini"
else
    python3 "$ROOT/src/main.py" "$@"
fi
