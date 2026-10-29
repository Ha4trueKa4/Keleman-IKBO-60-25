@echo off
rem Демонстрация команд этапа 5 (mkdir, rm) — изменение VFS в памяти.
rem Открывает окно эмулятора; закройте его, чтобы продолжить.
setlocal
set ROOT=%~dp0..

echo [1] Команды этапа 5 на многофайловой VFS
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv" --script "%ROOT%\scripts\stage5_all.esh"

echo [2] Интерактивный режим (попробуйте mkdir и rm вручную)
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv"

endlocal
