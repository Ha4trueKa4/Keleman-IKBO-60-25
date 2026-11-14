"""Тесты визуализации: PlantUML и ASCII-дерево (этап 5)."""

import unittest

from graph import build_graph, find_cycles
from visualize import to_ascii_tree, to_plantuml

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["A"]}
CHAIN = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}


def graph_of(repo, root="A", depth=10):
    """Построить граф по словарю зависимостей."""
    return build_graph(root, lambda name: list(repo.get(name, [])), depth)


class TestPlantUml(unittest.TestCase):
    """Описание графа на языке PlantUML."""

    def test_structure(self):
        """Диаграмма обрамлена @startuml/@enduml, корень выделен."""
        lines = to_plantuml(graph_of(DIAMOND))
        self.assertEqual(lines[0], "@startuml")
        self.assertEqual(lines[-1], "@enduml")
        self.assertIn('rectangle "A" as P0 #LightBlue', lines)
        self.assertIn('rectangle "D" as P3', lines)

    def test_edges(self):
        """Каждое ребро графа превращается в стрелку."""
        lines = to_plantuml(graph_of(DIAMOND))
        edges = [line for line in lines if "-->" in line]
        self.assertEqual(edges, [
            "P0 --> P1", "P0 --> P2", "P1 --> P3", "P2 --> P3",
        ])

    def test_cycle_edge_is_red(self):
        """Ребро, замыкающее цикл, рисуется красным."""
        graph = graph_of(CYCLE)
        lines = to_plantuml(graph, find_cycles(graph.edges))
        self.assertIn("P0 --> P1", lines)
        self.assertIn("P1 -[#Red]-> P0", lines)

    def test_depth_limited_node_is_gray(self):
        """Не раскрытый из-за глубины пакет выделен серым."""
        lines = to_plantuml(graph_of(CHAIN, depth=1))
        self.assertIn('rectangle "B" as P1 #LightGray', lines)

    def test_names_with_symbols(self):
        """Имена с символами + и - выводятся в кавычках."""
        repo = {"libstdc++6": ["gcc-14-base"], "gcc-14-base": []}
        lines = to_plantuml(graph_of(repo, root="libstdc++6"))
        self.assertIn('rectangle "libstdc++6" as P0 #LightBlue', lines)


class TestAsciiTree(unittest.TestCase):
    """Вывод зависимостей в виде ASCII-дерева."""

    def test_diamond(self):
        """Повторно встреченный пакет помечается (*)."""
        self.assertEqual(to_ascii_tree(graph_of(DIAMOND)), [
            "A",
            "|-- B",
            "|   `-- D",
            "`-- C",
            "    `-- D (*)",
        ])

    def test_cycle(self):
        """Пакет из текущего пути помечается (цикл)."""
        self.assertEqual(to_ascii_tree(graph_of(CYCLE)), [
            "A",
            "`-- B",
            "    `-- A (цикл)",
        ])

    def test_depth_limit(self):
        """Не раскрытый из-за глубины пакет помечается многоточием."""
        self.assertEqual(to_ascii_tree(graph_of(CHAIN, depth=2)), [
            "A",
            "`-- B",
            "    `-- C ...",
        ])

    def test_single_package(self):
        """Дерево пакета без зависимостей — одна строка."""
        self.assertEqual(to_ascii_tree(graph_of({"A": []})), ["A"])


if __name__ == "__main__":
    unittest.main()
