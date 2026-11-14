"""Граф зависимостей: обход BFS с рекурсией и поиск циклов (этап 3)."""

from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    """Граф зависимостей пакета.

    Attributes:
        root: имя анализируемого пакета.
        max_depth: максимальная глубина анализа.
        exclude: подстрока для исключения пакетов.
        edges: список смежности: пакет -> его прямые зависимости.
        depths: уровень BFS, на котором найден каждый пакет.
    """

    root: str
    max_depth: int
    exclude: str = ""
    edges: dict = field(default_factory=dict)
    depths: dict = field(default_factory=dict)

    def expanded(self, name):
        """Проверить, раскрывались ли зависимости пакета ``name``."""
        return self.depths[name] < self.max_depth

    def edge_count(self):
        """Вернуть число рёбер графа."""
        return sum(len(deps) for deps in self.edges.values())


def build_graph(root, resolve, max_depth, exclude=""):
    """Построить граф зависимостей пакета обходом в ширину.

    Args:
        root: имя анализируемого пакета.
        resolve: функция ``resolve(name)`` -> прямые зависимости.
        max_depth: сколько уровней зависимостей раскрывать.
        exclude: подстрока; пакеты с ней в имени не анализируются.

    Returns:
        DependencyGraph: построенный граф.
    """
    graph = DependencyGraph(root, max_depth, exclude)
    graph.edges[root] = []
    graph.depths[root] = 0
    _bfs([root], 0, graph, resolve)
    return graph


def _bfs(level, depth, graph, resolve):
    """Обработать один уровень BFS и рекурсивно перейти к следующему.

    Каждый пакет раскрывается один раз, поэтому циклические
    зависимости не приводят к бесконечному обходу.
    """
    if not level or depth >= graph.max_depth:
        return
    next_level = []
    for name in level:
        for dep in resolve(name):
            if graph.exclude and graph.exclude in dep:
                continue
            graph.edges[name].append(dep)
            if dep not in graph.edges:
                graph.edges[dep] = []
                graph.depths[dep] = depth + 1
                next_level.append(dep)
    _bfs(next_level, depth + 1, graph, resolve)


def find_cycles(edges):
    """Найти циклические зависимости обходом в глубину.

    Args:
        edges: список смежности графа.

    Returns:
        list: циклы в виде путей ``[A, B, ..., A]``.
    """
    cycles = []
    state = {}
    for node in edges:
        if node not in state:
            _visit(node, edges, state, [], cycles)
    return cycles


def _visit(node, edges, state, path, cycles):
    """Обойти пакет в глубину и записать найденные циклы."""
    state[node] = "active"
    path.append(node)
    for dep in edges.get(node, []):
        if state.get(dep) == "active":
            cycles.append(path[path.index(dep):] + [dep])
        elif dep not in state:
            _visit(dep, edges, state, path, cycles)
    path.pop()
    state[node] = "done"
