"""Тестовый репозиторий: граф пакетов из текстового файла (этап 3).

Каждая непустая строка описывает пакет и его прямые зависимости::

    A: B C

Имена пакетов состоят только из больших латинских букв.
"""

import re

from errors import RepoError

NAME_PATTERN = re.compile(r"[A-Z]+")


def load_test_repo(path):
    """Прочитать файл тестового репозитория.

    Args:
        path: путь к файлу описания графа.

    Returns:
        dict: имя пакета -> список его прямых зависимостей.

    Raises:
        RepoError: файл не читается или пуст, содержит ошибку формата,
            недопустимое имя или повторное описание пакета.
    """
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise RepoError(
            f"не удалось прочитать тестовый репозиторий '{path}': {exc}"
        ) from exc
    repo = {}
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        name, deps = _parse_line(line, number)
        if name in repo:
            raise RepoError(f"строка {number}: пакет '{name}' описан повторно")
        repo[name] = deps
    if not repo:
        raise RepoError(f"тестовый репозиторий '{path}' пуст")
    return repo


def _parse_line(line, number):
    """Разобрать строку ``ПАКЕТ: ЗАВИСИМОСТИ`` в имя и список зависимостей.

    Raises:
        RepoError: нет двоеточия или имя не из больших латинских букв.
    """
    head, colon, tail = line.partition(":")
    if not colon:
        raise RepoError(
            f"строка {number}: ожидается формат 'ПАКЕТ: ЗАВИСИМОСТИ'"
        )
    names = [head.strip()] + tail.split()
    for name in names:
        if not NAME_PATTERN.fullmatch(name):
            raise RepoError(
                f"строка {number}: недопустимое имя пакета '{name}' "
                "(допустимы только большие латинские буквы)"
            )
    return names[0], list(dict.fromkeys(names[1:]))
