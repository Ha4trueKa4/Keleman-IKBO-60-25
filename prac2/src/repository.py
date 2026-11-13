from apt_repo import (
    direct_dependencies,
    find_package,
    load_index,
    virtual_providers,
)
from errors import RepoError
from test_repo import load_test_repo


def open_repository(config):
    if config.test_mode:
        return _test_resolver(config.repo_url, config.package)
    return _apt_resolver(config.repo_url, config.package, config.version)


def _test_resolver(path, root):
    repo = load_test_repo(path)
    if root not in repo:
        raise RepoError(f"пакет '{root}' не найден в тестовом репозитории")
    return lambda name: list(repo.get(name, []))


def _apt_resolver(source, root, version):
    index = load_index(source)
    root_stanza = find_package(index, root, version)
    providers = virtual_providers(index)

    def resolve(name):
        if name == root:
            return direct_dependencies(root_stanza)
        stanzas = index.get(name)
        if stanzas:
            return direct_dependencies(stanzas[-1])
        return providers.get(name, [])[:1]

    return resolve
