@echo off
setlocal
set ROOT=%~dp0..
set MAIN=%ROOT%\src\main.py

for %%c in (apt_curl apt_git apt_version apt_bad_version apt_unknown apt_bad_url) do (
  echo.
  echo == %%c ==
  python "%MAIN%" --config "%ROOT%\examples\%%c.ini"
)
