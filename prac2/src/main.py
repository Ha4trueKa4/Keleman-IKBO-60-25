"""CLI-инструмент визуализации графа зависимостей (apt, PlantUML).

Вариант 15. На этапе 1 приложение читает INI-конфигурацию и выводит
все настраиваемые пользователем параметры в формате «ключ-значение».
"""

import argparse
import sys

from config import ConfigError, load_config


def parse_args(argv):
    """Разобрать аргументы командной строки (путь к INI-конфигу)."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов apt.",
    )
    parser.add_argument(
        "--config", required=True, help="путь к INI-файлу конфигурации",
    )
    return parser.parse_args(argv)


def format_params(config):
    """Вернуть строки «ключ = значение» для всех параметров анализа."""
    return [
        f"package      = {config.package}",
        f"repo_url     = {config.repo_url}",
        f"test_mode    = {config.test_mode}",
        f"version      = {config.version or '(любая)'}",
        f"ascii_tree   = {config.ascii_tree}",
        f"max_depth    = {config.max_depth}",
        f"filter       = {config.filter_substring or '(нет)'}",
    ]


def main(argv=None):
    """Точка входа: прочитать конфиг и вывести параметры."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1
    print("Параметры анализа:")
    for line in format_params(config):
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
