"""Тесты парсера командной строки (этап 1)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from parser import parse_command


class TestParser(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(parse_command("ls"), ["ls"])

    def test_args(self):
        self.assertEqual(parse_command("cd /home user"), ["cd", "/home", "user"])

    def test_double_quotes(self):
        self.assertEqual(parse_command('ls "my dir"'), ["ls", "my dir"])

    def test_single_quotes(self):
        self.assertEqual(parse_command("echo 'a b' c"), ["echo", "a b", "c"])

    def test_empty(self):
        self.assertEqual(parse_command(""), [])

    def test_unclosed_quote_raises(self):
        with self.assertRaises(ValueError):
            parse_command('ls "oops')


if __name__ == "__main__":
    unittest.main()
