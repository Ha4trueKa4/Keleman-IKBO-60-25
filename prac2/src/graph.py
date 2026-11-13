from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    root: str
    max_depth: int
    exclude: str = ""
    edges: dict = field(default_factory=dict)
    depths: dict = field(default_factory=dict)

    def expanded(self, name):
        return self.depths[name] < self.max_depth

    def edge_count(self):
        return sum(len(deps) for deps in self.edges.values())


def build_graph(root, resolve, max_depth, exclude=""):
    graph = DependencyGraph(root, max_depth, exclude)
    graph.edges[root] = []
    graph.depths[root] = 0
    _bfs([root], 0, graph, resolve)
    return graph


def _bfs(level, depth, graph, resolve):
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
    cycles = []
    state = {}
    for node in edges:
        if node not in state:
            _visit(node, edges, state, [], cycles)
    return cycles


def _visit(node, edges, state, path, cycles):
    state[node] = "active"
    path.append(node)
    for dep in edges.get(node, []):
        if state.get(dep) == "active":
            cycles.append(path[path.index(dep):] + [dep])
        elif dep not in state:
            _visit(dep, edges, state, path, cycles)
    path.pop()
    state[node] = "done"
