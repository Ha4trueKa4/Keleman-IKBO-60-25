"""Виртуальная файловая система (VFS) в памяти. Этап 3.

Источник VFS — CSV-файл. Двоичное содержимое файлов хранится в base64.
Вложенность задаётся полным путём в колонке ``path``. Все операции
выполняются в памяти; исходные данные VFS не модифицируются.
"""

import base64
import binascii
import csv
from dataclasses import dataclass, field


@dataclass
class VfsNode:
    """Узел VFS: файл или каталог."""

    name: str
    is_dir: bool
    children: dict = field(default_factory=dict)
    data: bytes = b""


class VfsError(Exception):
    """Ошибка загрузки или формата VFS."""


def load_vfs(path):
    """Загрузить VFS из CSV-файла в память.

    Возвращает корневой узел (каталог "/"). Бросает VfsError при ошибке
    загрузки: файл не найден, неверный формат, некорректный base64.
    """
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        raise VfsError(f"не удалось открыть VFS '{path}': {exc}") from exc
    root = VfsNode(name="/", is_dir=True)
    for row in rows:
        _add_row(root, row)
    return root


def _add_row(root, row):
    """Добавить одну строку CSV (узел) в дерево VFS."""
    path = (row.get("path") or "").strip()
    node_type = (row.get("type") or "").strip()
    if not path or node_type not in ("dir", "file"):
        raise VfsError(f"неверная строка VFS: {row}")
    if path == "/":
        return
    parts = path.strip("/").split("/")
    parent = _descend(root, parts[:-1])
    is_dir = node_type == "dir"
    data = b"" if is_dir else _decode(row.get("content", ""))
    parent.children[parts[-1]] = VfsNode(
        name=parts[-1], is_dir=is_dir, data=data,
    )


def _descend(root, parts):
    """Спуститься к родителю, создавая промежуточные каталоги."""
    node = root
    for part in parts:
        child = node.children.get(part)
        if child is None:
            child = VfsNode(name=part, is_dir=True)
            node.children[part] = child
        node = child
    return node


def _decode(text):
    """Декодировать base64-содержимое файла (пустая строка -> b'')."""
    text = (text or "").strip()
    if not text:
        return b""
    try:
        return base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise VfsError(f"неверный base64: {exc}") from exc


def vfs_stats(root):
    """Вернуть кортеж (число файлов, число каталогов, макс. глубина)."""
    files = 0
    dirs = 0
    max_depth = 0
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        max_depth = max(max_depth, depth)
        if not node.is_dir:
            files += 1
            continue
        if node is not root:
            dirs += 1
        for child in node.children.values():
            stack.append((child, depth + 1))
    return files, dirs, max_depth
