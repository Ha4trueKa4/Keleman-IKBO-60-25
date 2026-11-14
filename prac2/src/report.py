"""Текстовый вывод параметров, графа, циклов и порядка загрузки."""


def format_params(path, config):
    """Сформировать строки «ключ = значение» для всех параметров.

    Args:
        path: путь к конфигурационному файлу.
        config: параметры анализа (:class:`config.Config`).

    Returns:
        list: строки вывода с выровненными ключами.
    """
    rows = [
        ("package", config.package),
        ("repo_url", config.repo_url),
        ("test_mode", _as_bool(config.test_mode)),
        ("version", config.version or "(любая)"),
        ("ascii_tree", _as_bool(config.ascii_tree)),
        ("max_depth", config.max_depth),
        ("filter", config.filter_substring or "(нет)"),
        ("load_order", _as_bool(config.load_order)),
    ]
    width = max(len(key) for key, _ in rows)
    lines = [f"Параметры анализа (из {path}):"]
    lines += [f"  {key.ljust(width)} = {value}" for key, value in rows]
    return lines


def _as_bool(flag):
    """Представить булево значение строкой true/false."""
    return "true" if flag else "false"


def format_graph(graph):
    """Сформировать список пакетов графа по уровням BFS.

    Args:
        graph: граф зависимостей (:class:`graph.DependencyGraph`).

    Returns:
        list: строки вида ``[уровень] пакет -> зависимости``.
    """
    lines = [
        f"Граф зависимостей {graph.root} (BFS, max_depth = "
        f"{graph.max_depth}, фильтр: {graph.exclude or 'нет'}):"
    ]
    for name in graph.edges:
        level = graph.depths[name]
        lines.append(f"  [{level}] {name} -> {_targets(graph, name)}")
    lines.append(
        f"Пакетов: {len(graph.edges)}, связей: {graph.edge_count()}"
    )
    return lines


def _targets(graph, name):
    """Описать зависимости пакета с учётом ограничения глубины."""
    if not graph.expanded(name):
        return "... (не раскрыт: достигнута максимальная глубина)"
    return ", ".join(graph.edges[name]) or "(нет зависимостей)"


def format_order(root, order):
    """Сформировать нумерованный порядок загрузки зависимостей.

    Args:
        root: анализируемый пакет.
        order: имена пакетов в порядке загрузки.

    Returns:
        list: строки вывода.
    """
    lines = [f"Порядок загрузки зависимостей для {root}:"]
    width = len(str(len(order)))
    for number, name in enumerate(order, start=1):
        lines.append(f"  {str(number).rjust(width)}. {name}")
    return lines


def format_cycles(cycles):
    """Сформировать описание найденных циклических зависимостей.

    Args:
        cycles: циклы в виде путей ``[A, B, ..., A]``.

    Returns:
        list: строки вывода.
    """
    if not cycles:
        return ["Циклические зависимости: не обнаружены"]
    lines = ["Циклические зависимости:"]
    lines += ["  " + " -> ".join(cycle) for cycle in cycles]
    return lines
