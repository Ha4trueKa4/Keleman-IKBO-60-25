import gzip
import os
import tempfile
import unittest

from apt_repo import (
    direct_dependencies,
    find_package,
    load_index,
    parse_index,
)
from errors import RepoError

SAMPLE = (
    "Package: bash\n"
    "Version: 5.2.21-2ubuntu4\n"
    "Pre-Depends: libc6 (>= 2.38), libtinfo6 (>= 6)\n"
    "Depends: base-files (>= 2.1.12), debianutils (>= 5.6-0.1)\n"
    "Description: GNU Bourne Again SHell\n"
    " Bash is an sh-compatible command language interpreter.\n"
    "\n"
    "Package: tool\n"
    "Version: 1.0\n"
    "Depends: python3:any, mail-transport-agent | postfix,"
    " libx (>= 1), libx (<< 2)\n"
    "\n"
    "Package: tool\n"
    "Version: 2.0\n"
    "Depends: libc6\n"
    "\n"
    "Package: libc6\n"
    "Version: 2.39-0ubuntu8\n"
)


def _temp_file(data, suffix):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    return path


class TestParseIndex(unittest.TestCase):

    def setUp(self):
        self.index = parse_index(SAMPLE)

    def test_packages_and_versions(self):
        self.assertEqual(set(self.index), {"bash", "tool", "libc6"})
        self.assertEqual(len(self.index["tool"]), 2)

    def test_continuation_line(self):
        bash = self.index["bash"][0]
        self.assertIn("interpreter", bash["Description"])
        self.assertEqual(bash["Version"], "5.2.21-2ubuntu4")

    def test_pre_depends_and_depends(self):
        deps = direct_dependencies(self.index["bash"][0])
        expected = ["libc6", "libtinfo6", "base-files", "debianutils"]
        self.assertEqual(deps, expected)

    def test_alternatives_arch_duplicates(self):
        deps = direct_dependencies(self.index["tool"][0])
        self.assertEqual(deps, ["python3", "mail-transport-agent", "libx"])

    def test_no_dependencies(self):
        self.assertEqual(direct_dependencies(self.index["libc6"][0]), [])


class TestFindPackage(unittest.TestCase):

    def setUp(self):
        self.index = parse_index(SAMPLE)

    def test_exact_version(self):
        stanza = find_package(self.index, "tool", "1.0")
        self.assertEqual(stanza["Version"], "1.0")

    def test_default_version_is_last(self):
        stanza = find_package(self.index, "tool")
        self.assertEqual(stanza["Version"], "2.0")

    def test_unknown_version(self):
        with self.assertRaises(RepoError):
            find_package(self.index, "tool", "9.9")

    def test_unknown_package(self):
        with self.assertRaises(RepoError):
            find_package(self.index, "nothing")


class TestLoadIndex(unittest.TestCase):

    def _path(self, data, suffix):
        path = _temp_file(data, suffix)
        self.addCleanup(os.remove, path)
        return path

    def test_plain_file(self):
        path = self._path(SAMPLE.encode("utf-8"), "")
        self.assertIn("bash", load_index(path))

    def test_gzip_file(self):
        path = self._path(gzip.compress(SAMPLE.encode("utf-8")), ".gz")
        self.assertIn("tool", load_index(path))

    def test_broken_gzip(self):
        path = self._path(b"not a gzip archive", ".gz")
        with self.assertRaises(RepoError):
            load_index(path)

    def test_empty_index(self):
        path = self._path(b"<html>not an index</html>", "")
        with self.assertRaises(RepoError):
            load_index(path)

    def test_missing_file(self):
        missing = os.path.join(tempfile.gettempdir(), "no_such_index")
        with self.assertRaises(RepoError):
            load_index(missing)


if __name__ == "__main__":
    unittest.main()
