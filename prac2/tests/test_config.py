"""Тесты чтения и валидации INI-конфигурации (этап 1)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import ConfigError, load_config

VALID = (
    "[analyzer]\n"
    "package = bash\n"
    "repo_url = http://example/Packages.gz\n"
    "test_mode = false\n"
    "version = 5.1\n"
    "ascii_tree = true\n"
    "max_depth = 3\n"
    "filter = -dev\n"
)


def _write(text):
    """Записать текст во временный INI-файл и вернуть путь."""
    fd, path = tempfile.mkstemp(suffix=".ini")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


class TestConfig(unittest.TestCase):
    """Проверки загрузки конфигурации и обработки ошибок."""

    def _load(self, text):
        """Загрузить конфиг из временного файла с автоудалением."""
        path = _write(text)
        self.addCleanup(os.remove, path)
        return load_config(path)

    def test_valid(self):
        """Корректный конфиг читается во все поля."""
        config = self._load(VALID)
        self.assertEqual(config.package, "bash")
        self.assertEqual(config.max_depth, 3)
        self.assertTrue(config.ascii_tree)
        self.assertFalse(config.test_mode)

    def test_missing_package(self):
        """Отсутствие обязательного package — ошибка."""
        text = VALID.replace("package = bash\n", "")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_section(self):
        """Отсутствие секции [analyzer] — ошибка."""
        with self.assertRaises(ConfigError):
            self._load("package = x\n")

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

    def test_bad_bool(self):
        """Нераспознанное булево значение — ошибка."""
        text = VALID.replace("test_mode = false", "test_mode = maybe")
        with self.assertRaises(ConfigError):
            self._load(text)

    def test_missing_file(self):
        """Несуществующий файл конфига — ошибка."""
        with self.assertRaises(ConfigError):
            load_config(os.path.join(tempfile.gettempdir(), "no_such.ini"))


if __name__ == "__main__":
    unittest.main()
