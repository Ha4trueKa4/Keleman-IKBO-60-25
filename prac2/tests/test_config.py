"""Тесты чтения и проверки INI-конфигурации (этап 1)."""

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
    """Записать текст во временный INI-файл и вернуть путь к нему."""
    fd, path = tempfile.mkstemp(suffix=".ini")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class TestConfig(unittest.TestCase):
    """Загрузка корректной конфигурации и обработка ошибок."""

    def _load(self, text):
        """Загрузить конфиг из временного файла с автоудалением."""
        path = _write(text)
        self.addCleanup(os.remove, path)
        return load_config(path)

    def test_valid_all_fields(self):
        """Корректный конфиг разбирается во все параметры."""
        config = self._load(VALID)
        self.assertEqual(config.package, "bash")
        self.assertEqual(config.repo_url, "http://example/Packages.gz")
        self.assertFalse(config.test_mode)
        self.assertEqual(config.version, "5.1-6ubuntu1")
        self.assertTrue(config.ascii_tree)
        self.assertEqual(config.max_depth, 3)
        self.assertEqual(config.filter_substring, "-dev")

    def test_optional_fields_default(self):
        """Необязательные параметры получают значения по умолчанию."""
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

    def test_relative_repo_path(self):
        """Относительный путь отсчитывается от папки конфига."""
        path = _write(VALID.replace(
            "http://example/Packages.gz", "repos/x.graph"
        ))
        self.addCleanup(os.remove, path)
        expected = os.path.join(os.path.dirname(path), "repos", "x.graph")
        self.assertEqual(load_config(path).repo_url, expected)

    def test_load_order_flag(self):
        """Параметр load_order по умолчанию выключен и включается."""
        self.assertFalse(self._load(VALID).load_order)
        text = VALID + "load_order = true\n"
        self.assertTrue(self._load(text).load_order)

    def test_bad_load_order(self):
        """Нераспознанное значение load_order — ошибка."""
        with self.assertRaises(ConfigError):
            self._load(VALID + "load_order = иногда\n")

    def test_bool_synonyms(self):
        """Булевы параметры понимают разные написания."""
        text = VALID.replace("test_mode = false", "test_mode = YES")
        self.assertTrue(self._load(text).test_mode)

    def test_missing_section(self):
        """Отсутствие секции [analyzer] — ошибка."""
        with self.assertRaises(ConfigError):
            self._load("package = x\n")

    def test_missing_package(self):
        """Отсутствие обязательного package — ошибка."""
        text = VALID.replace("package = bash\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_repo_url(self):
        """Отсутствие обязательного repo_url — ошибка."""
        text = VALID.replace("repo_url = http://example/Packages.gz\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_bad_depth(self):
        """Нечисловая глубина — ошибка."""
        text = VALID.replace("max_depth = 3", "max_depth = abc")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_negative_depth(self):
        """Отрицательная глубина — ошибка."""
        text = VALID.replace("max_depth = 3", "max_depth = -1")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_depth(self):
        """Отсутствие обязательного max_depth — ошибка."""
        text = VALID.replace("max_depth = 3\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_bad_bool(self):
        """Нераспознанное булево значение — ошибка."""
        text = VALID.replace("test_mode = false", "test_mode = maybe")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_file(self):
        """Несуществующий файл конфигурации — ошибка."""
        missing = os.path.join(tempfile.gettempdir(), "no_such_cfg.ini")
        with self.assertRaises(ConfigError):
            load_config(missing)


if __name__ == "__main__":
    unittest.main()
