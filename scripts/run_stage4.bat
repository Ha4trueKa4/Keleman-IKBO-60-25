@echo off
rem Демонстрация команд этапа 4 (ls, cd, uptime, find, tree).
rem Открывает окно эмулятора; закройте его, чтобы продолжить.
setlocal
set ROOT=%~dp0..

echo [1] Все команды этапа 4 на многофайловой VFS
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv" --script "%ROOT%\scripts\stage4_all.esh"

echo [2] Интерактивный режим на многофайловой VFS
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv"

endlocal
