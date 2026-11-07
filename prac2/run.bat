@echo off
setlocal
if "%~1"=="" (
  python "%~dp0src\main.py" --config "%~dp0config.example.ini"
) else (
  python "%~dp0src\main.py" %*
)
