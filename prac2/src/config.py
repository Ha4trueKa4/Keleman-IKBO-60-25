"""Конфигурация инструмента анализа зависимостей. Этап 1.

Единственный источник настраиваемых пользователем параметров —
конфигурационный файл формата INI (секция ``[analyzer]``). Модуль
читает файл, проверяет значения и возвращает объект :class:`Config`.
"""

import configparser
from dataclasses import dataclass

SECTION = "analyzer"
MIN_DEPTH = 0


class ConfigError(Exception):
    """Ошибка чтения или валидации конфигурации."""


@dataclass
class Config:
    """Набор настраиваемых пользователем параметров анализа."""

    package: str
    repo_url: str
    test_mode: bool
    version: str
    ascii_tree: bool
    max_depth: int
    filter_substring: str


def load_config(path):
    """Прочитать INI-файл и вернуть проверенный :class:`Config`.

    Бросает :class:`ConfigError` при отсутствии файла, отсутствии
    обязательных параметров или неверном формате значений.
    """
    parser = configparser.ConfigParser()
    section = _read_section(parser, path)
    return Config(
        package=_require(section, "package"),
        repo_url=_require(section, "repo_url"),
        test_mode=_get_bool(section, "test_mode"),
        version=section.get("version", "").strip(),
        ascii_tree=_get_bool(section, "ascii_tree"),
        max_depth=_get_depth(section),
        filter_substring=section.get("filter", "").strip(),
    )


def _read_section(parser, path):
    """Загрузить файл и вернуть секцию ``[analyzer]`` или бросить ошибку."""
    try:
        with open(path, encoding="utf-8") as handle:
            parser.read_file(handle)
    except OSError as exc:
        raise ConfigError(f"не удалось открыть конфиг '{path}': {exc}") from exc
    except configparser.Error as exc:
        raise ConfigError(f"неверный формат INI: {exc}") from exc
    if not parser.has_section(SECTION):
        raise ConfigError(f"нет секции [{SECTION}] в конфиге")
    return parser[SECTION]


def _require(section, key):
    """Вернуть непустое значение ключа или бросить :class:`ConfigError`."""
    value = section.get(key, "").strip()
    if not value:
        raise ConfigError(f"не задан обязательный параметр '{key}'")
    return value


def _get_bool(section, key):
    """Прочитать булев параметр (по умолчанию False)."""
    try:
        return section.getboolean(key, fallback=False)
    except ValueError as exc:
        raise ConfigError(f"параметр '{key}' должен быть true/false") from exc


def _get_depth(section):
    """Прочитать и проверить максимальную глубину анализа."""
    raw = section.get("max_depth", "").strip()
    if not raw:
        raise ConfigError("не задан обязательный параметр 'max_depth'")
    try:
        depth = int(raw)
    except ValueError as exc:
        raise ConfigError("параметр 'max_depth' должен быть целым") from exc
    if depth < MIN_DEPTH:
        raise ConfigError("глубина 'max_depth' не может быть отрицательной")
    return depth
