import unittest

from graph import build_graph, find_cycles

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
CHAIN = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}


def resolver(repo):
    calls = []

    def resolve(name):
        calls.append(name)
        return list(repo.get(name, []))

    resolve.calls = calls
    return resolve


class TestBuildGraph(unittest.TestCase):

    def test_diamond_full(self):
        graph = build_graph("A", resolver(DIAMOND), 10)
        self.assertEqual(graph.edges, DIAMOND)
        self.assertEqual(graph.depths, {"A": 0, "B": 1, "C": 1, "D": 2})

    def test_bfs_order(self):
        graph = build_graph("A", resolver(DIAMOND), 10)
        self.assertEqual(list(graph.edges), ["A", "B", "C", "D"])

    def test_each_package_resolved_once(self):
        resolve = resolver(DIAMOND)
        build_graph("A", resolve, 10)
        self.assertEqual(sorted(resolve.calls), ["A", "B", "C", "D"])

    def test_depth_limit(self):
        graph = build_graph("A", resolver(CHAIN), 2)
        self.assertEqual(list(graph.edges), ["A", "B", "C"])
        self.assertEqual(graph.edges["C"], [])
        self.assertTrue(graph.expanded("B"))
        self.assertFalse(graph.expanded("C"))

    def test_depth_zero(self):
        graph = build_graph("A", resolver(CHAIN), 0)
        self.assertEqual(graph.edges, {"A": []})

    def test_filter(self):
        graph = build_graph("A", resolver(DIAMOND), 10, exclude="C")
        self.assertEqual(graph.edges, {"A": ["B"], "B": ["D"], "D": []})

    def test_cycle_terminates(self):
        graph = build_graph("A", resolver(CYCLE), 100)
        self.assertEqual(graph.edges, CYCLE)
        self.assertEqual(graph.edge_count(), 4)


class TestFindCycles(unittest.TestCase):

    def test_no_cycles(self):
        self.assertEqual(find_cycles(DIAMOND), [])

    def test_simple_cycle(self):
        self.assertEqual(find_cycles(CYCLE), [["A", "B", "C", "A"]])

    def test_self_loop(self):
        self.assertEqual(find_cycles({"A": ["A"]}), [["A", "A"]])

    def test_several_cycles(self):
        edges = {"A": ["B", "C"], "B": ["A"], "C": ["D"], "D": ["C"]}
        cycles = find_cycles(edges)
        self.assertIn(["A", "B", "A"], cycles)
        self.assertIn(["C", "D", "C"], cycles)


if __name__ == "__main__":
    unittest.main()
