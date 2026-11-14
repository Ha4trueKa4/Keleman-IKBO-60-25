@echo off
rem Запуск эмулятора оболочки (этап 1).
rem Необязательный аргумент: имя VFS.
python "%~dp0src\emulator.py" %*
