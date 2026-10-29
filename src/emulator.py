"""Эмулятор командной оболочки ОС (UNIX-подобной).

Этап 1. REPL — минимальный прототип с графическим интерфейсом (GUI).
Команды пока являются заглушками, но диалог с пользователем уже поддерживается.
"""

import os
import sys
import tkinter as tk
from tkinter import scrolledtext

from parser import parse_command

# Максимальное число аргументов команды cd (имя целевого каталога).
MAX_CD_ARGS = 1


class ShellEmulator:
    """Эмулятор оболочки с графическим интерфейсом на основе tkinter."""

    def __init__(self, vfs_name: str = "vfs"):
        """Создать окно эмулятора для VFS с именем ``vfs_name``."""
        self.vfs_name = vfs_name
        self.running = True

        self.root = tk.Tk()
        # Требование: заголовок окна должен содержать имя VFS.
        self.root.title(f"Эмулятор - [{self.vfs_name}]")
        self.root.geometry("800x500")

        self._build_ui()

        # Таблица команд: имя -> обработчик.
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

        self._write(f"Эмулятор оболочки. VFS: {self.vfs_name}\n")
        self._write("Введите команду (ls, cd, exit).\n\n")

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

    def execute(self, line: str) -> None:
        """Разобрать и выполнить одну строку ввода."""
        self._write(f"{self._prompt()}{line}\n")

        if not line.strip():
            return

        try:
            tokens = self.parse(line)
        except ValueError as exc:
            self._write(f"ошибка разбора: {exc}\n")
            return

        if not tokens:
            return

        name, args = tokens[0], tokens[1:]
        handler = self.commands.get(name)
        if handler is None:
            # Требование: сообщить об ошибке (неизвестная команда).
            self._write(f"{name}: команда не найдена\n")
            return

        handler(args)

    # ------------------------------------------------------------------ #
    # Команды (пока заглушки)
    # ------------------------------------------------------------------ #
    def cmd_ls(self, args) -> None:
        """Заглушка команды ls: выводит имя команды и аргументы."""
        self._write(f"ls {args}\n")

    def cmd_cd(self, args) -> None:
        """Заглушка команды cd: выводит имя команды и аргументы."""
        # Требование: сообщить о неверных аргументах.
        if len(args) > MAX_CD_ARGS:
            self._write("cd: слишком много аргументов\n")
            return
        self._write(f"cd {args}\n")

    def cmd_exit(self, args) -> None:
        """Завершить работу эмулятора."""
        self.running = False
        self.root.destroy()

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
    """Точка входа: имя VFS из аргумента или переменной окружения."""
    default = os.environ.get("VFS_NAME", "vfs")
    vfs_name = sys.argv[1] if len(sys.argv) > 1 else default
    ShellEmulator(vfs_name=vfs_name).run()


if __name__ == "__main__":
    main()
