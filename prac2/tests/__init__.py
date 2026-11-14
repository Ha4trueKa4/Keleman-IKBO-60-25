"""Модульные тесты анализатора; каталог src добавляется в путь поиска."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
