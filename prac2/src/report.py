def format_params(path, config):
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
    return "true" if flag else "false"


def format_graph(graph):
    lines = [
        f"Граф зависимостей {graph.root} (BFS, max_depth = "
        f"{graph.max_depth}, фильтр: {graph.exclude or 'нет'}):"
    ]
    for name, deps in graph.edges.items():
        level = graph.depths[name]
        lines.append(f"  [{level}] {name} -> {_targets(graph, name)}")
    lines.append(
        f"Пакетов: {len(graph.edges)}, связей: {graph.edge_count()}"
    )
    return lines


def _targets(graph, name):
    if not graph.expanded(name):
        return "... (не раскрыт: достигнута максимальная глубина)"
    return ", ".join(graph.edges[name]) or "(нет зависимостей)"


def format_order(root, order):
    lines = [f"Порядок загрузки зависимостей для {root}:"]
    width = len(str(len(order)))
    for number, name in enumerate(order, start=1):
        lines.append(f"  {str(number).rjust(width)}. {name}")
    return lines


def format_cycles(cycles):
    if not cycles:
        return ["Циклические зависимости: не обнаружены"]
    lines = ["Циклические зависимости:"]
    lines += ["  " + " -> ".join(cycle) for cycle in cycles]
    return lines
