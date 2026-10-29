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


def resolve(root, cwd_parts, path):
    """Найти узел по пути ``path`` относительно текущего каталога.

    Поддерживает абсолютные и относительные пути, "." и "..".
    Возвращает (узел, части_пути). Бросает VfsError, если пути нет.
    """
    parts = [] if path.startswith("/") else list(cwd_parts)
    for token in path.split("/"):
        if token in ("", "."):
            continue
        if token == "..":
            if parts:
                parts.pop()
            continue
        parts.append(token)
    return _node_at(root, parts), parts


def _node_at(root, parts):
    """Вернуть узел по списку имён от корня или бросить VfsError."""
    node = root
    for part in parts:
        child = node.children.get(part) if node.is_dir else None
        if child is None:
            raise VfsError(f"нет такого пути: /{'/'.join(parts)}")
        node = child
    return node


def walk_paths(node, base):
    """Вернуть полные пути узла ``node`` и всех вложенных элементов."""
    result = []
    stack = [(node, base)]
    while stack:
        cur, path = stack.pop()
        result.append(path)
        if not cur.is_dir:
            continue
        for name in sorted(cur.children, reverse=True):
            stack.append((cur.children[name], path.rstrip("/") + "/" + name))
    return result


def tree_lines(node):
    """Вернуть строки дерева с отступами, начиная с узла ``node``."""
    lines = []
    _tree_into(node, 0, lines)
    return lines


def _tree_into(node, depth, lines):
    """Добавить в ``lines`` узел и его детей с отступом по глубине."""
    name = node.name
    if node.is_dir and not name.endswith("/"):
        name += "/"
    lines.append("  " * depth + name)
    if not node.is_dir:
        return
    for child_name in sorted(node.children):
        _tree_into(node.children[child_name], depth + 1, lines)
