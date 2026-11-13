import argparse
import sys

from apt_repo import direct_dependencies, find_package, load_index
from config import load_config
from errors import ConfigError, RepoError

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


def format_params(config):
    rows = [
        ("package", config.package),
        ("repo_url", config.repo_url),
        ("test_mode", _as_bool(config.test_mode)),
        ("version", config.version or "(любая)"),
        ("ascii_tree", _as_bool(config.ascii_tree)),
        ("max_depth", config.max_depth),
        ("filter", config.filter_substring or "(нет)"),
    ]
    width = max(len(key) for key, _ in rows)
    return [f"{key.ljust(width)} = {value}" for key, value in rows]


def _as_bool(flag):
    return "true" if flag else "false"


def print_params(path, config):
    print(f"Параметры анализа (из {path}):")
    for line in format_params(config):
        print(f"  {line}")


def print_direct(name, stanza):
    deps = direct_dependencies(stanza)
    print(f"Прямые зависимости {name} {stanza.get('Version', '?')}:")
    for dep in deps:
        print(f"  {dep}")
    if not deps:
        print("  (нет)")


def run(args):
    config = load_config(args.config)
    if args.show_config:
        print_params(args.config, config)
        return
    index = load_index(config.repo_url)
    stanza = find_package(index, config.package, config.version)
    print_direct(config.package, stanza)


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
