import os
import tempfile
import unittest

from config import Config
from errors import RepoError
from repository import open_repository
from test_repo import load_test_repo


def _write(text):
    fd, path = tempfile.mkstemp(suffix=".graph")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def _config(path, package):
    return Config(
        package=package,
        repo_url=path,
        test_mode=True,
        version="",
        ascii_tree=False,
        max_depth=5,
        filter_substring="",
    )


class TestLoadTestRepo(unittest.TestCase):

    def _load(self, text):
        path = _write(text)
        self.addCleanup(os.remove, path)
        return load_test_repo(path)

    def test_valid(self):
        repo = self._load("A: B C\nB: C\n\nC:\n")
        self.assertEqual(repo, {"A": ["B", "C"], "B": ["C"], "C": []})

    def test_duplicate_dependency_removed(self):
        self.assertEqual(self._load("A: B B\n")["A"], ["B"])

    def test_lowercase_name(self):
        with self.assertRaises(RepoError):
            self._load("A: b\n")

    def test_digits_in_name(self):
        with self.assertRaises(RepoError):
            self._load("A1: B\n")

    def test_missing_colon(self):
        with self.assertRaises(RepoError):
            self._load("A B C\n")

    def test_duplicate_package(self):
        with self.assertRaises(RepoError):
            self._load("A: B\nA: C\n")

    def test_empty(self):
        with self.assertRaises(RepoError):
            self._load("\n\n")

    def test_missing_file(self):
        missing = os.path.join(tempfile.gettempdir(), "no_such.graph")
        with self.assertRaises(RepoError):
            load_test_repo(missing)


class TestOpenRepository(unittest.TestCase):

    def setUp(self):
        self.path = _write("A: B\nB:\n")
        self.addCleanup(os.remove, self.path)

    def test_resolver(self):
        resolve = open_repository(_config(self.path, "A"))
        self.assertEqual(resolve("A"), ["B"])
        self.assertEqual(resolve("B"), [])
        self.assertEqual(resolve("X"), [])

    def test_missing_root(self):
        with self.assertRaises(RepoError):
            open_repository(_config(self.path, "Z"))


if __name__ == "__main__":
    unittest.main()
