"""Конфигурация эмулятора: параметры командной строки и TOML-файл.

Этап 2. Значения из конфигурационного файла имеют приоритет над
значениями, заданными в командной строке.
"""

import argparse
import tomllib
from dataclasses import dataclass


@dataclass
class Config:
    """Итоговые параметры запуска эмулятора."""

    vfs_path: str = ""
    script_path: str = ""
    config_path: str = ""


def parse_args(argv):
    """Разобрать параметры командной строки эмулятора."""
    parser = argparse.ArgumentParser(description="Эмулятор оболочки ОС")
    parser.add_argument("--vfs", default="", help="путь к VFS")
    parser.add_argument("--script", default="", help="стартовый скрипт")
    parser.add_argument("--config", default="", help="TOML-конфиг")
    return parser.parse_args(argv)


def load_config(path):
    """Загрузить параметры из TOML-файла.

    Возвращает словарь. Бросает ValueError при ошибке чтения или разбора.
    """
    try:
        with open(path, "rb") as handle:
            return tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        message = f"не удалось прочитать конфиг '{path}': {exc}"
        raise ValueError(message) from exc


def build_config(argv):
    """Собрать конфигурацию из CLI и TOML (файл имеет приоритет).

    Возвращает пару (Config, текст_ошибки|None). Ошибка заполняется,
    если конфигурационный файл задан, но не прочитан.
    """
    args = parse_args(argv)
    config = Config(
        vfs_path=args.vfs,
        script_path=args.script,
        config_path=args.config,
    )
    if not args.config:
        return config, None
    try:
        data = load_config(args.config)
    except ValueError as exc:
        return config, str(exc)
    # Значения из файла имеют приоритет над командной строкой.
    if "vfs" in data:
        config.vfs_path = str(data["vfs"])
    if "script" in data:
        config.script_path = str(data["script"])
    return config, None
