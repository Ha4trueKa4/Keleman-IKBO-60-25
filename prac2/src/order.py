"""Порядок загрузки зависимостей (этап 4)."""


def load_order(edges, root):
    """Вернуть порядок загрузки: зависимости раньше зависящих пакетов.

    Пакет добавляется после всех своих зависимостей (обход в глубину,
    post-order). Ребро в пакет, который ещё обрабатывается, замыкает
    цикл и пропускается.

    Args:
        edges: список смежности графа.
        root: анализируемый пакет; в порядке он будет последним.

    Returns:
        list: имена пакетов в порядке загрузки.
    """
    order = []
    _place(root, edges, {}, order)
    return order


def _place(node, edges, state, order):
    """Добавить пакет в порядок после всех его зависимостей."""
    state[node] = "active"
    for dep in edges.get(node, []):
        if dep not in state:
            _place(dep, edges, state, order)
    state[node] = "done"
    order.append(node)
