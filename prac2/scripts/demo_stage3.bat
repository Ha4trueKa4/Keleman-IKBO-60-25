@echo off
setlocal
set ROOT=%~dp0..
set MAIN=%ROOT%\src\main.py

for %%c in (test_diamond test_cycle test_depth test_filter test_complex test_broken test_missing_root apt_curl) do (
  echo.
  echo == %%c ==
  python "%MAIN%" --config "%ROOT%\examples\%%c.ini"
)
