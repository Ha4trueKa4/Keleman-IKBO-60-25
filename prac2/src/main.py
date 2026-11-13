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

DEFAULT_CONFIG = "config.example.ini"


def parse_args(argv):
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
    for line in lines:
        print(line)


def run(args):
    config = load_config(args.config)
    if args.show_config:
        _print(format_params(args.config, config))
        return
    resolve = open_repository(config)
    graph = build_graph(
        config.package, resolve, config.max_depth, config.filter_substring
    )
    _print(format_graph(graph))
    _print(format_cycles(find_cycles(graph.edges)))
    if config.load_order:
        _print(format_order(graph.root, load_order(graph.edges, graph.root)))


def main(argv=None):
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
