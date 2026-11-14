"""Тесты виртуальной файловой системы (этап 3)."""

import base64
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import VfsError, load_vfs, vfs_stats

HEADER = "path,type,content\n"


def _b64(text):
    """Вернуть base64 строки в кодировке UTF-8."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


class TestVfs(unittest.TestCase):
    """Тесты загрузки VFS из CSV в память."""

    def _csv(self, body):
        """Создать временный CSV-файл VFS и вернуть путь."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(HEADER + body)
        self.addCleanup(os.remove, path)
        return path

    def test_minimal(self):
        root = load_vfs(self._csv("/,dir,\n"))
        self.assertEqual(vfs_stats(root), (0, 0, 0))

    def test_depth_and_content(self):
        body = (
            "/a,dir,\n"
            "/a/b,dir,\n"
            f"/a/b/f.txt,file,{_b64('hi')}\n"
        )
        root = load_vfs(self._csv(body))
        files, dirs, depth = vfs_stats(root)
        self.assertEqual(files, 1)
        self.assertEqual(dirs, 2)
        self.assertGreaterEqual(depth, 3)
        node = root.children["a"].children["b"].children["f.txt"]
        self.assertEqual(node.data, b"hi")

    def test_missing_file(self):
        with self.assertRaises(VfsError):
            load_vfs("no_such_vfs.csv")

    def test_bad_base64(self):
        with self.assertRaises(VfsError):
            load_vfs(self._csv("/f,file,!!!bad!!!\n"))

    def test_bad_type(self):
        with self.assertRaises(VfsError):
            load_vfs(self._csv("/x,folder,\n"))


if __name__ == "__main__":
    unittest.main()
