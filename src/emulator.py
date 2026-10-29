"""Эмулятор командной оболочки ОС (UNIX-подобной).

Этап 1. REPL — минимальный прототип с графическим интерфейсом (GUI).
Этап 2. Конфигурация — параметры командной строки и TOML-файл, стартовый
скрипт и служебная команда conf-dump.
"""

import os
import sys
import tkinter as tk
from tkinter import scrolledtext

from config import Config, build_config
from parser import parse_command

# Максимальное число аргументов команды cd (имя целевого каталога).
MAX_CD_ARGS = 1


class ShellEmulator:
    """Эмулятор оболочки с графическим интерфейсом на основе tkinter."""

    def __init__(self, config: Config = None, config_error: str = None):
        """Создать окно эмулятора по конфигурации ``config``."""
        self.config = config or Config()
        self.running = True
        self.vfs_name = self._vfs_name_from(self.config.vfs_path)

        self.root = tk.Tk()
        # Требование: заголовок окна должен содержать имя VFS.
        self.root.title(f"Эмулятор - [{self.vfs_name}]")
        self.root.geometry("800x500")

        self._build_ui()

        # Таблица команд: имя -> обработчик.
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "conf-dump": self.cmd_conf_dump,
            "exit": self.cmd_exit,
        }

        self._print_startup(config_error)

    @staticmethod
    def _vfs_name_from(path: str) -> str:
        """Вернуть имя VFS для заголовка окна по пути к VFS."""
        name = os.path.basename(path.rstrip("/\\")) if path else ""
        return name or "vfs"

    def _build_ui(self) -> None:
        """Создать виджеты окна: область вывода и строку ввода."""
        # Область вывода (только для чтения).
        self.output = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state=tk.DISABLED,
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            font=("Consolas", 11),
        )
        self.output.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 0))

        # Нижняя полоса: приглашение и поле ввода.
        bottom = tk.Frame(self.root, bg="#1e1e1e")
        bottom.pack(fill=tk.X, padx=4, pady=4)

        self.prompt_label = tk.Label(
            bottom, text=self._prompt(), bg="#1e1e1e", fg="#4ec9b0",
            font=("Consolas", 11),
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            bottom, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            font=("Consolas", 11), relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus_set()

    def _print_startup(self, config_error: str) -> None:
        """Вывести приветствие, параметры запуска и ошибку конфига."""
        self._write(f"Эмулятор оболочки. VFS: {self.vfs_name}\n")
        if config_error:
            # Требование: сообщить об ошибке чтения конфигурации.
            self._write(f"ошибка конфигурации: {config_error}\n")
        # Отладочный вывод всех заданных параметров при запуске.
        self._write("Параметры запуска:\n")
        for key, value in self.config_items():
            self._write(f"  {key} = {value}\n")
        self._write("\n")

    def config_items(self):
        """Вернуть параметры эмулятора как пары (ключ, значение)."""
        return [
            ("vfs", self.config.vfs_path),
            ("script", self.config.script_path),
            ("config", self.config.config_path),
        ]

    # ------------------------------------------------------------------ #
    # Служебные методы
    # ------------------------------------------------------------------ #
    def _prompt(self) -> str:
        """Вернуть строку приглашения командной строки."""
        return f"{self.vfs_name}$ "

    def _write(self, text: str) -> None:
        """Вывести текст в область вывода."""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    # ------------------------------------------------------------------ #
    # Разбор и выполнение
    # ------------------------------------------------------------------ #
    def parse(self, line: str):
        """Разобрать строку на команду и аргументы.

        Корректно обрабатывает аргументы в кавычках (одинарных и двойных).
        Возвращает список токенов. Бросает ValueError при незакрытой кавычке.
        """
        return parse_command(line)

    def execute(self, line: str) -> bool:
        """Разобрать и выполнить одну строку ввода.

        Возвращает True при успехе и False при ошибке (нужно для останова
        стартового скрипта на первой ошибке).
        """
        self._write(f"{self._prompt()}{line}\n")

        if not line.strip():
            return True

        try:
            tokens = self.parse(line)
        except ValueError as exc:
            self._write(f"ошибка разбора: {exc}\n")
            return False

        if not tokens:
            return True

        name, args = tokens[0], tokens[1:]
        handler = self.commands.get(name)
        if handler is None:
            # Требование: сообщить об ошибке (неизвестная команда).
            self._write(f"{name}: команда не найдена\n")
            return False

        return handler(args)

    def run_script(self, path: str) -> None:
        """Выполнить стартовый скрипт эмулятора.

        На экране отображается и ввод, и вывод; выполнение
        останавливается при первой ошибке команды.
        """
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except OSError as exc:
            # Требование: сообщить об ошибке исполнения скрипта.
            self._write(f"ошибка скрипта: {exc}\n")
            return
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not self.execute(line):
                self._write("скрипт остановлен из-за ошибки\n")
                return

    # ------------------------------------------------------------------ #
    # Команды
    # ------------------------------------------------------------------ #
    def cmd_ls(self, args) -> bool:
        """Заглушка команды ls: выводит имя команды и аргументы."""
        self._write(f"ls {args}\n")
        return True

    def cmd_cd(self, args) -> bool:
        """Заглушка команды cd: выводит имя команды и аргументы."""
        # Требование: сообщить о неверных аргументах.
        if len(args) > MAX_CD_ARGS:
            self._write("cd: слишком много аргументов\n")
            return False
        self._write(f"cd {args}\n")
        return True

    def cmd_conf_dump(self, args) -> bool:
        """Служебная команда: вывести параметры в формате ключ-значение."""
        for key, value in self.config_items():
            self._write(f"{key} = {value}\n")
        return True

    def cmd_exit(self, args) -> bool:
        """Завершить работу эмулятора."""
        self.running = False
        self.root.destroy()
        return True

    # ------------------------------------------------------------------ #
    # GUI-обработчики
    # ------------------------------------------------------------------ #
    def _on_enter(self, _event) -> None:
        """Обработать нажатие Enter в поле ввода."""
        line = self.entry.get()
        self.entry.delete(0, tk.END)
        self.execute(line)

    def run(self) -> None:
        """Запустить главный цикл обработки событий окна."""
        self.root.mainloop()


def main() -> None:
    """Точка входа: собрать конфигурацию и запустить эмулятор."""
    config, error = build_config(sys.argv[1:])
    app = ShellEmulator(config, config_error=error)
    if config.script_path:
        app.run_script(config.script_path)
    app.run()


if __name__ == "__main__":
    main()
