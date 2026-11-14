"""Чтение и проверка конфигурации анализатора (этап 1).

Единственный источник настраиваемых пользователем параметров —
INI-файл с секцией ``[analyzer]``. Модуль разбирает файл, проверяет
каждое значение и возвращает неизменяемый объект :class:`Config`.
"""

import configparser
import os
from dataclasses import dataclass

from errors import ConfigError

SECTION = "analyzer"
MIN_DEPTH = 0
TRUE_VALUES = ("true", "1", "yes", "on", "да")
FALSE_VALUES = ("false", "0", "no", "off", "нет")


@dataclass(frozen=True)
class Config:
    """Проверенные параметры анализа зависимостей.

    Attributes:
        package: имя анализируемого пакета.
        repo_url: URL индекса apt или путь к файлу репозитория.
        test_mode: работать с тестовым репозиторием вместо apt.
        version: версия пакета; пустая строка — последняя в индексе.
        ascii_tree: выводить зависимости в виде ASCII-дерева.
        max_depth: максимальная глубина анализа зависимостей.
        filter_substring: подстрока для исключения пакетов из анализа.
        load_order: выводить порядок загрузки зависимостей.
    """

    package: str
    repo_url: str
    test_mode: bool
    version: str
    ascii_tree: bool
    max_depth: int
    filter_substring: str
    load_order: bool = False


def load_config(path):
    """Прочитать INI-файл и вернуть проверенные параметры анализа.

    Args:
        path: путь к конфигурационному файлу.

    Returns:
        Config: неизменяемый объект с параметрами.

    Raises:
        ConfigError: файл недоступен, не является INI, не содержит
            секции ``[analyzer]`` или значение не прошло проверку.
    """
    section = _read_section(path)
    return Config(
        package=_text(section, "package", required=True),
        repo_url=_source(section, path),
        test_mode=_boolean(section, "test_mode"),
        version=_text(section, "version", required=False),
        ascii_tree=_boolean(section, "ascii_tree"),
        max_depth=_depth(section, "max_depth"),
        filter_substring=_text(section, "filter", required=False),
        load_order=_boolean(section, "load_order"),
    )


def _read_section(path):
    """Загрузить INI-файл и вернуть секцию ``[analyzer]``.

    Raises:
        ConfigError: файл не найден или не читается, имеет неверный
            формат INI или не содержит секции ``[analyzer]``.
    """
    parser = configparser.ConfigParser()
    try:
        with open(path, encoding="utf-8") as handle:
            parser.read_file(handle)
    except FileNotFoundError as exc:
        raise ConfigError(f"файл конфигурации не найден: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"не удалось прочитать '{path}': {exc}") from exc
    except configparser.MissingSectionHeaderError as exc:
        raise ConfigError(
            f"в конфиге нет обязательной секции [{SECTION}]"
        ) from exc
    except configparser.Error as exc:
        raise ConfigError(f"некорректный формат INI: {exc}") from exc
    if not parser.has_section(SECTION):
        raise ConfigError(f"в конфиге нет обязательной секции [{SECTION}]")
    return parser[SECTION]


def _text(section, key, required):
    """Вернуть строковое значение параметра без крайних пробелов.

    Raises:
        ConfigError: параметр обязательный, но не задан.
    """
    value = section.get(key, "").strip()
    if required and not value:
        raise ConfigError(f"не задан обязательный параметр '{key}'")
    return value


def _source(section, config_path):
    """Вернуть URL или путь к репозиторию из параметра ``repo_url``.

    Относительный путь отсчитывается от папки конфигурационного файла,
    URL и абсолютный путь возвращаются без изменений.
    """
    value = _text(section, "repo_url", required=True)
    if "://" in value or os.path.isabs(value):
        return value
    base = os.path.dirname(os.path.abspath(config_path))
    return os.path.normpath(os.path.join(base, value))


def _boolean(section, key):
    """Вернуть булев параметр; пустое значение означает ``False``.

    Raises:
        ConfigError: значение не распознано как true/false.
    """
    raw = section.get(key, "").strip().lower()
    if not raw:
        return False
    if raw in TRUE_VALUES:
        return True
    if raw in FALSE_VALUES:
        return False
    raise ConfigError(
        f"параметр '{key}' должен быть true/false, получено '{raw}'"
    )


def _depth(section, key):
    """Вернуть максимальную глубину анализа — целое не меньше нуля.

    Raises:
        ConfigError: параметр не задан, не является целым числом или
            отрицателен.
    """
    raw = section.get(key, "").strip()
    if not raw:
        raise ConfigError(f"не задан обязательный параметр '{key}'")
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(
            f"параметр '{key}' должен быть целым числом, получено '{raw}'"
        ) from exc
    if value < MIN_DEPTH:
        raise ConfigError(f"параметр '{key}' не может быть отрицательным")
    return value
