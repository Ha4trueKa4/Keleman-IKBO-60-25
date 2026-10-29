"""Тесты навигации по VFS: resolve, walk_paths, tree_lines (этап 4)."""

import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import VfsError, load_vfs, resolve, tree_lines, walk_paths

CSV = (
    "path,type,content\n"
    "/,dir,\n"
    "/home,dir,\n"
    "/home/user,dir,\n"
    f"/home/user/f.txt,file,{base64.b64encode(b'hi').decode()}\n"
    "/bin,dir,\n"
)


class TestNav(unittest.TestCase):
    """Тесты разрешения путей и обхода дерева VFS."""

    def setUp(self):
        """Создать временную VFS из CSV перед каждым тестом."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(CSV)
        self.addCleanup(os.remove, path)
        self.root = load_vfs(path)

    def test_absolute(self):
        node, parts = resolve(self.root, [], "/home/user")
        self.assertEqual(node.name, "user")
        self.assertEqual(parts, ["home", "user"])

    def test_relative(self):
        node, parts = resolve(self.root, ["home"], "user")
        self.assertEqual(parts, ["home", "user"])

    def test_parent(self):
        node, parts = resolve(self.root, ["home", "user"], "..")
        self.assertEqual(parts, ["home"])

    def test_missing_raises(self):
        with self.assertRaises(VfsError):
            resolve(self.root, [], "/nope")

    def test_walk_paths(self):
        paths = walk_paths(self.root, "/")
        self.assertIn("/home/user/f.txt", paths)
        self.assertIn("/bin", paths)

    def test_tree_lines(self):
        lines = tree_lines(self.root)
        self.assertEqual(lines[0], "/")
        self.assertTrue(any("user/" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
