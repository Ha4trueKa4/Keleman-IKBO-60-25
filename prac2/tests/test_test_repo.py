"""Тесты тестового репозитория и resolve для него (этап 3)."""

import os
import tempfile
import unittest

from config import Config
from errors import RepoError
from repository import open_repository
from test_repo import load_test_repo


def _write(text):
    """Записать текст во временный файл графа и вернуть путь к нему."""
    fd, path = tempfile.mkstemp(suffix=".graph")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def _config(path, package):
    """Создать конфигурацию тестового режима для пакета."""
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
    """Разбор файла тестового репозитория."""

    def _load(self, text):
        """Загрузить репозиторий из временного файла с автоудалением."""
        path = _write(text)
        self.addCleanup(os.remove, path)
        return load_test_repo(path)

    def test_valid(self):
        """Корректный файл разбирается, пустые строки пропускаются."""
        repo = self._load("A: B C\nB: C\n\nC:\n")
        self.assertEqual(repo, {"A": ["B", "C"], "B": ["C"], "C": []})

    def test_duplicate_dependency_removed(self):
        """Повторная зависимость в строке удаляется."""
        self.assertEqual(self._load("A: B B\n")["A"], ["B"])

    def test_lowercase_name(self):
        """Строчные буквы в имени — ошибка."""
        with self.assertRaises(RepoError):
            self._load("A: b\n")

    def test_digits_in_name(self):
        """Цифры в имени — ошибка."""
        with self.assertRaises(RepoError):
            self._load("A1: B\n")

    def test_missing_colon(self):
        """Строка без двоеточия — ошибка."""
        with self.assertRaises(RepoError):
            self._load("A B C\n")

    def test_duplicate_package(self):
        """Повторное описание пакета — ошибка."""
        with self.assertRaises(RepoError):
            self._load("A: B\nA: C\n")

    def test_empty(self):
        """Файл без пакетов — ошибка."""
        with self.assertRaises(RepoError):
            self._load("\n\n")

    def test_missing_file(self):
        """Несуществующий файл — ошибка."""
        missing = os.path.join(tempfile.gettempdir(), "no_such.graph")
        with self.assertRaises(RepoError):
            load_test_repo(missing)


class TestOpenRepository(unittest.TestCase):
    """Функция resolve в тестовом режиме."""

    def setUp(self):
        """Создать временный репозиторий A -> B."""
        self.path = _write("A: B\nB:\n")
        self.addCleanup(os.remove, self.path)

    def test_resolver(self):
        """resolve отдаёт зависимости, неизвестный пакет — лист."""
        resolve = open_repository(_config(self.path, "A"))
        self.assertEqual(resolve("A"), ["B"])
        self.assertEqual(resolve("B"), [])
        self.assertEqual(resolve("X"), [])

    def test_missing_root(self):
        """Отсутствующий анализируемый пакет — ошибка."""
        with self.assertRaises(RepoError):
            open_repository(_config(self.path, "Z"))


if __name__ == "__main__":
    unittest.main()
