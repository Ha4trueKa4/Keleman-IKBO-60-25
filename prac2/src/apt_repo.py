import gzip
import lzma
import re
import urllib.request

from errors import RepoError

DEPENDENCY_FIELDS = ("Pre-Depends", "Depends")
PRIORITIES = ("required", "important", "standard", "optional", "extra")
NAME_PATTERN = re.compile(r"[a-z0-9][a-z0-9+.-]*")
TIMEOUT = 60


def load_index(source):
    raw = _read_source(source)
    text = _decompress(source, raw).decode("utf-8", errors="replace")
    index = parse_index(text)
    if not index:
        raise RepoError(f"индекс '{source}' пуст или имеет неверный формат")
    return index


def _read_source(source):
    try:
        if "://" in source:
            with urllib.request.urlopen(source, timeout=TIMEOUT) as response:
                return response.read()
        with open(source, "rb") as handle:
            return handle.read()
    except (OSError, ValueError) as exc:
        raise RepoError(f"не удалось получить '{source}': {exc}") from exc


def _decompress(source, raw):
    try:
        if source.endswith(".gz"):
            return gzip.decompress(raw)
        if source.endswith(".xz"):
            return lzma.decompress(raw)
    except (OSError, EOFError, lzma.LZMAError) as exc:
        raise RepoError(f"повреждённый архив '{source}': {exc}") from exc
    return raw


def parse_index(text):
    index = {}
    for block in text.replace("\r\n", "\n").split("\n\n"):
        fields = _parse_stanza(block)
        if "Package" in fields:
            index.setdefault(fields["Package"], []).append(fields)
    return index


def _parse_stanza(block):
    fields = {}
    key = None
    for line in block.splitlines():
        if line[:1] in (" ", "\t"):
            if key:
                fields[key] += " " + line.strip()
        elif ":" in line:
            key, _, value = line.partition(":")
            fields[key] = value.strip()
    return fields


def find_package(index, name, version=""):
    stanzas = index.get(name)
    if not stanzas:
        raise RepoError(f"пакет '{name}' не найден в репозитории")
    if not version:
        return stanzas[-1]
    for stanza in stanzas:
        if stanza.get("Version") == version:
            return stanza
    known = ", ".join(stanza.get("Version", "?") for stanza in stanzas)
    raise RepoError(
        f"версия '{version}' пакета '{name}' не найдена (есть: {known})"
    )


def direct_dependencies(stanza):
    result = []
    for field in DEPENDENCY_FIELDS:
        for group in stanza.get(field, "").split(","):
            name = _first_alternative(group)
            if name and name not in result:
                result.append(name)
    return result


def virtual_providers(index):
    providers = {}
    for name, stanzas in index.items():
        for group in stanzas[-1].get("Provides", "").split(","):
            virtual = _first_alternative(group)
            if virtual and virtual not in index:
                providers.setdefault(virtual, []).append(name)
    for names in providers.values():
        names.sort(key=lambda name: _priority_rank(index[name][-1]))
    return providers


def _priority_rank(stanza):
    priority = stanza.get("Priority", "optional")
    if priority in PRIORITIES:
        return PRIORITIES.index(priority)
    return len(PRIORITIES)


def _first_alternative(group):
    match = NAME_PATTERN.match(group.split("|")[0].strip())
    return match.group(0) if match else ""
