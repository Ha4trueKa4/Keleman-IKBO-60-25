"""CLI-инструмент визуализации графа зависимостей пакетов apt.

Вариант 15: конфигурация в формате INI, пакеты Ubuntu (apt), обход
графа алгоритмом BFS с рекурсией, визуализация на языке PlantUML.
"""

import argparse
import sys

from config import load_config
from errors import ConfigError, RepoError
from graph import build_graph, find_cycles
from order import load_order
from report import (
    format_cycles,
    format_graph,
    format_order,
    format_params,
)
from repository import open_repository
from visualize import to_ascii_tree, to_plantuml

DEFAULT_CONFIG = "config.example.ini"
TREE_LEGEND = (
    "(*) — уже показан выше, (цикл) — циклическая зависимость, "
    "... — не раскрыт из-за max_depth"
)


def parse_args(argv):
    """Разобрать аргументы командной строки.

    Args:
        argv: список аргументов без имени программы.

    Returns:
        argparse.Namespace: поля ``config`` и ``show_config``.
    """
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Визуализатор графа зависимостей пакетов apt.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help=f"путь к INI-файлу конфигурации (по умолчанию {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="вывести параметры конфигурации и завершить работу",
    )
    return parser.parse_args(argv)


def _print(lines):
    """Напечатать строки по одной."""
    for line in lines:
        print(line)


def _section(lines):
    """Напечатать блок вывода, отделив его пустой строкой."""
    print()
    _print(lines)


def report(config, graph):
    """Вывести граф, циклы, PlantUML, ASCII-дерево и порядок загрузки.

    Args:
        config: параметры анализа (:class:`config.Config`).
        graph: построенный граф зависимостей.
    """
    cycles = find_cycles(graph.edges)
    _print(format_graph(graph))
    _print(format_cycles(cycles))
    _section(
        ["Описание графа на языке PlantUML:"] + to_plantuml(graph, cycles)
    )
    if config.ascii_tree:
        _section(
            ["Зависимости в виде ASCII-дерева:"]
            + to_ascii_tree(graph)
            + [TREE_LEGEND]
        )
    if config.load_order:
        order = load_order(graph.edges, graph.root)
        _section(format_order(graph.root, order))


def run(args):
    """Выполнить анализ по параметрам из конфигурационного файла.

    Args:
        args: разобранные аргументы командной строки.

    Raises:
        ConfigError: ошибка в конфигурационном файле.
        RepoError: ошибка получения данных репозитория.
    """
    config = load_config(args.config)
    if args.show_config:
        _print(format_params(args.config, config))
        return
    resolve = open_repository(config)
    graph = build_graph(
        config.package, resolve, config.max_depth, config.filter_substring
    )
    report(config, graph)


def main(argv=None):
    """Запустить анализ и вернуть код завершения.

    Args:
        argv: аргументы командной строки; ``None`` — взять из sys.argv.

    Returns:
        int: 0 при успехе, 1 при ошибке конфигурации или репозитория.
    """
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        run(args)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1
    except RepoError as exc:
        print(f"Ошибка репозитория: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
