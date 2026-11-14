"""Тесты конфигурации эмулятора (этап 2)."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import build_config, load_config, parse_args


class TestArgs(unittest.TestCase):
    """Тесты разбора параметров командной строки."""

    def test_defaults(self):
        args = parse_args([])
        self.assertEqual(args.vfs, "")
        self.assertEqual(args.script, "")
        self.assertEqual(args.config, "")

    def test_values(self):
        args = parse_args(["--vfs", "fs.csv", "--script", "s.esh"])
        self.assertEqual(args.vfs, "fs.csv")
        self.assertEqual(args.script, "s.esh")


class TestConfigFile(unittest.TestCase):
    """Тесты чтения TOML-конфига и приоритета значений."""

    def _write_toml(self, text):
        """Создать временный TOML-файл и вернуть путь к нему."""
        fd, path = tempfile.mkstemp(suffix=".toml")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_missing_file_raises(self):
        with self.assertRaises(ValueError):
            load_config("no_such_file.toml")

    def test_file_overrides_cli(self):
        path = self._write_toml('vfs = "from_file"\n')
        argv = ["--vfs", "from_cli", "--config", path]
        config, error = build_config(argv)
        self.assertIsNone(error)
        self.assertEqual(config.vfs_path, "from_file")

    def test_bad_config_reports_error(self):
        path = self._write_toml("vfs = = =\n")
        config, error = build_config(["--config", path])
        self.assertIsNotNone(error)

    def test_cli_used_without_config(self):
        config, error = build_config(["--vfs", "only_cli"])
        self.assertIsNone(error)
        self.assertEqual(config.vfs_path, "only_cli")


if __name__ == "__main__":
    unittest.main()
