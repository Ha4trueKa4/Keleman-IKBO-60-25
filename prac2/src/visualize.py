ROOT_COLOR = "#LightBlue"
LIMIT_COLOR = "#LightGray"
CYCLE_ARROW = "-[#Red]->"
ARROW = "-->"


def to_plantuml(graph, cycles=()):
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
    if name == graph.root:
        return f" {ROOT_COLOR}"
    if not graph.expanded(name):
        return f" {LIMIT_COLOR}"
    return ""


def to_ascii_tree(graph):
    return _AsciiTree(graph).render()


class _AsciiTree:

    def __init__(self, graph):
        self.graph = graph
        self.lines = []
        self.shown = set()

    def render(self):
        root = self.graph.root
        self.lines.append(root)
        self.shown.add(root)
        self._children(root, "", {root})
        return self.lines

    def _children(self, name, prefix, path):
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
        if dep in path:
            return " (цикл)"
        if dep in self.shown:
            return " (*)"
        if not self.graph.expanded(dep):
            return " ..."
        return ""
