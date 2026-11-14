"""Тесты разбора индекса apt и функции resolve для apt (этапы 2–3)."""

import gzip
import os
import tempfile
import unittest

from apt_repo import (
    direct_dependencies,
    find_package,
    load_index,
    parse_index,
    virtual_providers,
)
from config import Config
from errors import RepoError
from repository import open_repository

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
    "\n"
    "Package: gawk\n"
    "Version: 5.2.1\n"
    "Priority: optional\n"
    "Provides: awk\n"
    "\n"
    "Package: mawk\n"
    "Version: 1.3.4\n"
    "Priority: required\n"
    "Provides: awk, libc6\n"
    "Depends: libc6\n"
)


def _temp_file(data, suffix):
    """Записать байты во временный файл и вернуть путь к нему."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    return path


class TestParseIndex(unittest.TestCase):
    """Разбор записей индекса и извлечение зависимостей."""

    def setUp(self):
        """Разобрать тестовый индекс."""
        self.index = parse_index(SAMPLE)

    def test_packages_and_versions(self):
        """Все пакеты найдены, у tool две версии."""
        expected = {"bash", "tool", "libc6", "gawk", "mawk"}
        self.assertEqual(set(self.index), expected)
        self.assertEqual(len(self.index["tool"]), 2)

    def test_virtual_providers_by_priority(self):
        """Поставщики виртуального пакета упорядочены по Priority."""
        providers = virtual_providers(self.index)
        self.assertEqual(providers, {"awk": ["mawk", "gawk"]})

    def test_continuation_line(self):
        """Строка-продолжение приклеивается к предыдущему полю."""
        bash = self.index["bash"][0]
        self.assertIn("interpreter", bash["Description"])
        self.assertEqual(bash["Version"], "5.2.21-2ubuntu4")

    def test_pre_depends_and_depends(self):
        """Зависимости берутся из Pre-Depends и Depends без версий."""
        deps = direct_dependencies(self.index["bash"][0])
        expected = ["libc6", "libtinfo6", "base-files", "debianutils"]
        self.assertEqual(deps, expected)

    def test_alternatives_arch_duplicates(self):
        """Архитектура отбрасывается, альтернатива первая, без повторов."""
        deps = direct_dependencies(self.index["tool"][0])
        self.assertEqual(deps, ["python3", "mail-transport-agent", "libx"])

    def test_no_dependencies(self):
        """Пакет без полей зависимостей даёт пустой список."""
        self.assertEqual(direct_dependencies(self.index["libc6"][0]), [])


class TestFindPackage(unittest.TestCase):
    """Выбор записи пакета по версии."""

    def setUp(self):
        """Разобрать тестовый индекс."""
        self.index = parse_index(SAMPLE)

    def test_exact_version(self):
        """Заданная версия находится точно."""
        stanza = find_package(self.index, "tool", "1.0")
        self.assertEqual(stanza["Version"], "1.0")

    def test_default_version_is_last(self):
        """Без версии берётся последняя запись в индексе."""
        stanza = find_package(self.index, "tool")
        self.assertEqual(stanza["Version"], "2.0")

    def test_unknown_version(self):
        """Отсутствующая версия — ошибка."""
        with self.assertRaises(RepoError):
            find_package(self.index, "tool", "9.9")

    def test_unknown_package(self):
        """Отсутствующий пакет — ошибка."""
        with self.assertRaises(RepoError):
            find_package(self.index, "nothing")


class TestLoadIndex(unittest.TestCase):
    """Загрузка индекса из файла и обработка ошибок."""

    def _path(self, data, suffix):
        """Создать временный файл индекса с автоудалением."""
        path = _temp_file(data, suffix)
        self.addCleanup(os.remove, path)
        return path

    def test_plain_file(self):
        """Несжатый индекс читается."""
        path = self._path(SAMPLE.encode("utf-8"), "")
        self.assertIn("bash", load_index(path))

    def test_gzip_file(self):
        """Индекс .gz распаковывается."""
        path = self._path(gzip.compress(SAMPLE.encode("utf-8")), ".gz")
        self.assertIn("tool", load_index(path))

    def test_broken_gzip(self):
        """Повреждённый архив — ошибка."""
        path = self._path(b"not a gzip archive", ".gz")
        with self.assertRaises(RepoError):
            load_index(path)

    def test_empty_index(self):
        """Файл без записей пакетов — ошибка."""
        path = self._path(b"<html>not an index</html>", "")
        with self.assertRaises(RepoError):
            load_index(path)

    def test_missing_file(self):
        """Несуществующий файл индекса — ошибка."""
        missing = os.path.join(tempfile.gettempdir(), "no_such_index")
        with self.assertRaises(RepoError):
            load_index(missing)


class TestAptResolver(unittest.TestCase):
    """Функция resolve для индекса apt."""

    def setUp(self):
        """Создать resolve для пакета tool версии 1.0."""
        path = _temp_file(SAMPLE.encode("utf-8"), "")
        self.addCleanup(os.remove, path)
        config = Config(
            package="tool",
            repo_url=path,
            test_mode=False,
            version="1.0",
            ascii_tree=False,
            max_depth=3,
            filter_substring="",
        )
        self.resolve = open_repository(config)

    def test_root_uses_requested_version(self):
        """Для корня используется заданная версия."""
        expected = ["python3", "mail-transport-agent", "libx"]
        self.assertEqual(self.resolve("tool"), expected)

    def test_other_package(self):
        """Для остальных пакетов используется запись из индекса."""
        self.assertEqual(self.resolve("mawk"), ["libc6"])

    def test_virtual_package(self):
        """Виртуальный пакет разрешается в лучшего поставщика."""
        self.assertEqual(self.resolve("awk"), ["mawk"])

    def test_unknown_package_is_leaf(self):
        """Неизвестный пакет считается пакетом без зависимостей."""
        self.assertEqual(self.resolve("python3"), [])


if __name__ == "__main__":
    unittest.main()
