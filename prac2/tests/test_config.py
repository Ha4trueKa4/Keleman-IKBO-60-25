import os
import tempfile
import unittest

from config import ConfigError, load_config

VALID = (
    "[analyzer]\n"
    "package = bash\n"
    "repo_url = http://example/Packages.gz\n"
    "test_mode = false\n"
    "version = 5.1-6ubuntu1\n"
    "ascii_tree = true\n"
    "max_depth = 3\n"
    "filter = -dev\n"
)


def _write(text):
    fd, path = tempfile.mkstemp(suffix=".ini")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class TestConfig(unittest.TestCase):

    def _load(self, text):
        path = _write(text)
        self.addCleanup(os.remove, path)
        return load_config(path)

    def test_valid_all_fields(self):
        config = self._load(VALID)
        self.assertEqual(config.package, "bash")
        self.assertEqual(config.repo_url, "http://example/Packages.gz")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.version, "5.1-6ubuntu1")
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.filter_substring, "-dev")

    def test_optional_fields_default(self):
        text = (
            "[analyzer]\n"
            "package = A\n"
            "repo_url = repos/x.graph\n"
            "max_depth = 0\n"
        )
        config = self._load(text)
        self.assertEqual(config.version, "")
        self.assertEqual(config.filter_substring, "")
        self.assertFalse(config.test_mode)
        self.assertFalse(config.ascii_tree)
        self.assertEqual(config.max_depth, 0)

    def test_bool_synonyms(self):
        text = VALID.replace("test_mode = false", "test_mode = YES")
        self.assertTrue(self._load(text).test_mode)

    def test_missing_section(self):
        with self.assertRaises(ConfigError):
            self._load("package = x\n")

    def test_missing_package(self):
        text = VALID.replace("package = bash\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_repo_url(self):
        text = VALID.replace("repo_url = http://example/Packages.gz\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_bad_depth(self):
        text = VALID.replace("max_depth = 3", "max_depth = abc")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_negative_depth(self):
        text = VALID.replace("max_depth = 3", "max_depth = -1")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_depth(self):
        text = VALID.replace("max_depth = 3\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_bad_bool(self):
        text = VALID.replace("test_mode = false", "test_mode = maybe")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_file(self):
        missing = os.path.join(tempfile.gettempdir(), "no_such_cfg.ini")
        with self.assertRaises(ConfigError):
            load_config(missing)


if __name__ == "__main__":
    unittest.main()
