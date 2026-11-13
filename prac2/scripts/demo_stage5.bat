@echo off
chcp 65001 >nul
setlocal
set ROOT=%~dp0..
set MAIN=%ROOT%\src\main.py

for %%c in ("%ROOT%\config.example.ini" "%ROOT%\examples\apt_curl.ini" "%ROOT%\examples\apt_git.ini" "%ROOT%\examples\test_complex.ini") do (
  echo.
  echo == %%~nxc ==
  python "%MAIN%" --config %%c
)
