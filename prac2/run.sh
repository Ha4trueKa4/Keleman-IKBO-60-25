#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi
if [ "$#" -eq 0 ]; then
    "$PY" "$ROOT/src/main.py" --config "$ROOT/config.example.ini"
else
    "$PY" "$ROOT/src/main.py" "$@"
fi
