import unittest

from order import load_order

DIAMOND = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
CYCLE = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": []}
COMPLEX = {
    "APP": ["CORE", "UI"],
    "CORE": ["LIBC"],
    "UI": ["CORE", "GFX"],
    "GFX": ["LIBC"],
    "LIBC": [],
}


class TestLoadOrder(unittest.TestCase):

    def test_diamond(self):
        self.assertEqual(load_order(DIAMOND, "A"), ["D", "B", "C", "A"])

    def test_dependencies_first(self):
        order = load_order(COMPLEX, "APP")
        position = {name: index for index, name in enumerate(order)}
        for name, deps in COMPLEX.items():
            for dep in deps:
                self.assertLess(position[dep], position[name])

    def test_each_package_once(self):
        order = load_order(COMPLEX, "APP")
        self.assertEqual(sorted(order), sorted(COMPLEX))

    def test_cycle(self):
        order = load_order(CYCLE, "A")
        self.assertEqual(order, ["D", "C", "B", "A"])

    def test_single_package(self):
        self.assertEqual(load_order({"A": []}, "A"), ["A"])


if __name__ == "__main__":
    unittest.main()
