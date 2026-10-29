"""Тесты изменяющих команд VFS: mkdir и rm (этап 5)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import VfsError, load_vfs, make_dir, remove, resolve

CSV = (
    "path,type,content\n"
    "/,dir,\n"
    "/a,dir,\n"
    "/a/f.txt,file,aGk=\n"
)


class TestFsOps(unittest.TestCase):
    """Тесты создания и удаления элементов VFS в памяти."""

    def setUp(self):
        """Создать временную VFS из CSV перед каждым тестом."""
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(CSV)
        self.addCleanup(os.remove, path)
        self.root = load_vfs(path)

    def test_mkdir_creates(self):
        make_dir(self.root, [], "/a/new")
        node, _ = resolve(self.root, [], "/a/new")
        self.assertTrue(node.is_dir)

    def test_mkdir_existing_raises(self):
        with self.assertRaises(VfsError):
            make_dir(self.root, [], "/a")

    def test_mkdir_missing_parent_raises(self):
        with self.assertRaises(VfsError):
            make_dir(self.root, [], "/nope/child")

    def test_rm_removes_file(self):
        remove(self.root, [], "/a/f.txt")
        with self.assertRaises(VfsError):
            resolve(self.root, [], "/a/f.txt")

    def test_rm_missing_raises(self):
        with self.assertRaises(VfsError):
            remove(self.root, [], "/a/nope")

    def test_rm_root_raises(self):
        with self.assertRaises(VfsError):
            remove(self.root, [], "/")


if __name__ == "__main__":
    unittest.main()
