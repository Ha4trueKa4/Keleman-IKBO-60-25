"""Единый интерфейс получения зависимостей (этап 3).

Анализ графа не зависит от источника данных: он получает функцию
``resolve(name)``, возвращающую прямые зависимости пакета. Функция
строится либо для индекса apt, либо для тестового репозитория.
"""

from apt_repo import (
    direct_dependencies,
    find_package,
    load_index,
    virtual_providers,
)
from errors import RepoError
from test_repo import load_test_repo


def open_repository(config):
    """Создать функцию получения прямых зависимостей пакета.

    Args:
        config: параметры анализа (:class:`config.Config`).

    Returns:
        Callable[[str], list]: функция ``resolve(name)``.

    Raises:
        RepoError: репозиторий недоступен или в нём нет пакета.
    """
    if config.test_mode:
        return _test_resolver(config.repo_url, config.package)
    return _apt_resolver(config.repo_url, config.package, config.version)


def _test_resolver(path, root):
    """Построить ``resolve`` для тестового репозитория из файла.

    Raises:
        RepoError: файл некорректен или в нём нет пакета ``root``.
    """
    repo = load_test_repo(path)
    if root not in repo:
        raise RepoError(f"пакет '{root}' не найден в тестовом репозитории")
    return lambda name: list(repo.get(name, []))


def _apt_resolver(source, root, version):
    """Построить ``resolve`` для индекса apt.

    Для анализируемого пакета берётся заданная версия, для остальных —
    последняя в индексе. Виртуальный пакет разрешается в поставщика с
    наивысшим приоритетом.

    Raises:
        RepoError: индекс недоступен или нет пакета нужной версии.
    """
    index = load_index(source)
    root_stanza = find_package(index, root, version)
    providers = virtual_providers(index)

    def resolve(name):
        """Вернуть прямые зависимости пакета ``name``."""
        if name == root:
            return direct_dependencies(root_stanza)
        stanzas = index.get(name)
        if stanzas:
            return direct_dependencies(stanzas[-1])
        return providers.get(name, [])[:1]

    return resolve
