import argparse
import sys

from config import ConfigError, load_config

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


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1
    print(f"Параметры анализа (из {args.config}):")
    for line in format_params(config):
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
