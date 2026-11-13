@echo off
chcp 65001 >nul
setlocal
set ROOT=%~dp0..
set MAIN=%ROOT%\src\main.py

for %%c in (test_diamond test_cycle test_filter test_complex order_bash) do (
  echo.
  echo == %%c ==
  python "%MAIN%" --config "%ROOT%\examples\%%c.ini"
)
