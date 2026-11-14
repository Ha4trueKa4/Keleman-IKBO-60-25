"""Тесты построения графа обходом BFS и поиска циклов (этап 3)."""

import unittest

from graph import build_graph, find_cycles

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
CHAIN = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}


def resolver(repo):
    """Вернуть resolve по словарю, запоминающий запрошенные пакеты."""
    calls = []

    def resolve(name):
        """Вернуть зависимости пакета и записать запрос."""
        calls.append(name)
        return list(repo.get(name, []))

    resolve.calls = calls
    return resolve


class TestBuildGraph(unittest.TestCase):
    """Обход BFS с глубиной, фильтром и циклами."""

    def test_diamond_full(self):
        """Ромб строится полностью, уровни BFS верные."""
        graph = build_graph("A", resolver(DIAMOND), 10)
        self.assertEqual(graph.edges, DIAMOND)
        self.assertEqual(graph.depths, {"A": 0, "B": 1, "C": 1, "D": 2})

    def test_bfs_order(self):
        """Пакеты добавляются в порядке обхода в ширину."""
        graph = build_graph("A", resolver(DIAMOND), 10)
        self.assertEqual(list(graph.edges), ["A", "B", "C", "D"])

    def test_each_package_resolved_once(self):
        """Зависимости каждого пакета запрашиваются один раз."""
        resolve = resolver(DIAMOND)
        build_graph("A", resolve, 10)
        self.assertEqual(sorted(resolve.calls), ["A", "B", "C", "D"])

    def test_depth_limit(self):
        """Пакеты на глубине max_depth не раскрываются."""
        graph = build_graph("A", resolver(CHAIN), 2)
        self.assertEqual(list(graph.edges), ["A", "B", "C"])
        self.assertEqual(graph.edges["C"], [])
        self.assertTrue(graph.expanded("B"))
        self.assertFalse(graph.expanded("C"))

    def test_depth_zero(self):
        """При max_depth = 0 в графе только сам пакет."""
        graph = build_graph("A", resolver(CHAIN), 0)
        self.assertEqual(graph.edges, {"A": []})

    def test_filter(self):
        """Пакеты с подстрокой фильтра исключаются."""
        graph = build_graph("A", resolver(DIAMOND), 10, exclude="C")
        self.assertEqual(graph.edges, {"A": ["B"], "B": ["D"], "D": []})

    def test_cycle_terminates(self):
        """Цикл не приводит к бесконечному обходу."""
        graph = build_graph("A", resolver(CYCLE), 100)
        self.assertEqual(graph.edges, CYCLE)
        self.assertEqual(graph.edge_count(), 4)


class TestFindCycles(unittest.TestCase):
    """Поиск циклических зависимостей."""

    def test_no_cycles(self):
        """В ромбе циклов нет."""
        self.assertEqual(find_cycles(DIAMOND), [])

    def test_simple_cycle(self):
        """Простой цикл возвращается как путь."""
        self.assertEqual(find_cycles(CYCLE), [["A", "B", "C", "A"]])

    def test_self_loop(self):
        """Зависимость пакета от себя — цикл длины один."""
        self.assertEqual(find_cycles({"A": ["A"]}), [["A", "A"]])

    def test_several_cycles(self):
        """Находятся все независимые циклы."""
        edges = {"A": ["B", "C"], "B": ["A"], "C": ["D"], "D": ["C"]}
        cycles = find_cycles(edges)
        self.assertIn(["A", "B", "A"], cycles)
        self.assertIn(["C", "D", "C"], cycles)


if __name__ == "__main__":
    unittest.main()
