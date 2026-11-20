"""Визуализация графа: язык диаграмм PlantUML и ASCII-дерево (этап 5)."""

ROOT_COLOR = "#LightBlue"
LIMIT_COLOR = "#LightGray"
CYCLE_ARROW = "-[#Red]->"
ARROW = "-->"


def to_plantuml(graph, cycles=()):
    """Сформировать описание графа на языке диаграмм PlantUML.

    Пакеты получают псевдонимы ``P0``, ``P1``, ..., так как в именах
    пакетов встречаются символы, недопустимые в идентификаторах
    PlantUML. Корень выделяется голубым, не раскрытые из-за глубины
    пакеты — серым, рёбра, замыкающие циклы, — красным.

    Args:
        graph: граф зависимостей (:class:`graph.DependencyGraph`).
        cycles: циклы, найденные :func:`graph.find_cycles`.

    Returns:
        list: строки диаграммы от ``@startuml`` до ``@enduml``.
    """
    aliases = {name: f"P{index}" for index, name in enumerate(graph.edges)}
    closing = {(cycle[-2], cycle[-1]) for cycle in cycles}
    lines = ["@startuml", f"title Зависимости пакета {graph.root}"]
    for name, alias in aliases.items():
        lines.append(f'rectangle "{name}" as {alias}{_color(graph, name)}')
    for name, deps in graph.edges.items():
        for dep in deps:
            arrow = CYCLE_ARROW if (name, dep) in closing else ARROW
            lines.append(f"{aliases[name]} {arrow} {aliases[dep]}")
    lines.append("@enduml")
    return lines


def _color(graph, name):
    """Вернуть цвет элемента пакета на диаграмме или пустую строку."""
    if name == graph.root:
        return f" {ROOT_COLOR}"
    if not graph.expanded(name):
        return f" {LIMIT_COLOR}"
    return ""


def to_ascii_tree(graph):
    """Сформировать ASCII-дерево зависимостей от корня графа.

    Каждый пакет раскрывается один раз. Повтор помечается ``(*)``,
    цикл — ``(цикл)``, не раскрытый из-за глубины пакет — ``...``.

    Args:
        graph: граф зависимостей (:class:`graph.DependencyGraph`).

    Returns:
        list: строки дерева.
    """
    return AsciiTree(graph).render()


class AsciiTree:
    """Построитель ASCII-дерева, помнящий уже показанные пакеты."""

    def __init__(self, graph):
        """Подготовить построитель для графа ``graph``."""
        self.graph = graph
        self.lines = []
        self.shown = set()

    def render(self):
        """Вернуть строки дерева, начиная с корня."""
        root = self.graph.root
        self.lines.append(root)
        self.shown.add(root)
        self._children(root, "", {root})
        return self.lines

    def _children(self, name, prefix, path):
        """Добавить зависимости пакета ``name`` с отступом ``prefix``."""
        deps = self.graph.edges.get(name, [])
        for index, dep in enumerate(deps):
            last = index == len(deps) - 1
            branch = "`-- " if last else "|-- "
            self.lines.append(prefix + branch + dep + self._mark(dep, path))
            if dep in path or dep in self.shown:
                continue
            self.shown.add(dep)
            child_prefix = prefix + ("    " if last else "|   ")
            self._children(dep, child_prefix, path | {dep})

    def _mark(self, dep, path):
        """Вернуть пометку пакета: цикл, повтор или предел глубины."""
        if dep in path:
            return " (цикл)"
        if dep in self.shown:
            return " (*)"
        if not self.graph.expanded(dep):
            return " ..."
        return ""
