@echo off
rem Проверка загрузки различных вариантов VFS (этап 3).
rem Каждый вызов открывает окно эмулятора; закройте его, чтобы продолжить.
setlocal
set ROOT=%~dp0..

echo [1] Минимальная VFS (только корень)
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\minimal.csv"

echo [2] Многофайловая VFS (>=3 уровней, двоичный файл)
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv"

echo [3] Битая VFS (неверный base64 -> ошибка загрузки)
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\broken.csv"

echo [4] Несуществующая VFS (файл не найден -> ошибка загрузки)
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\nope.csv"

echo [5] VFS + стартовый скрипт со всеми командами
python "%ROOT%\src\emulator.py" --vfs "%ROOT%\vfs\multi.csv" --script "%ROOT%\scripts\stage3_all.esh"

endlocal
