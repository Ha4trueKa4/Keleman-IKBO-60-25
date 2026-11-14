"""Парсер командной строки.

Корректно обрабатывает аргументы в кавычках (одинарных и двойных).
Вынесен в отдельный модуль, чтобы его можно было тестировать без GUI.
"""

import shlex
from typing import List


def parse_command(line: str) -> List[str]:
    """Разобрать строку на токены (команда + аргументы).

    Аргументы в кавычках сохраняются как единый токен.
    Бросает ValueError при незакрытой кавычке.

    >>> parse_command('ls -l "my dir"')
    ['ls', '-l', 'my dir']
    >>> parse_command("echo 'a b' c")
    ['echo', 'a b', 'c']
    """
    return shlex.split(line, posix=True)
