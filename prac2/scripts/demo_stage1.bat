@echo off
setlocal
set ROOT=%~dp0..
set MAIN=%ROOT%\src\main.py

echo == Корректный конфиг ==
python "%MAIN%" --config "%ROOT%\config.example.ini"

for %%c in (err_no_package err_bad_depth err_bad_bool) do (
  echo.
  echo == Ошибка: %%c ==
  python "%MAIN%" --config "%ROOT%\examples\%%c.ini"
)
