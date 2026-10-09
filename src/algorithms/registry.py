from __future__ import annotations

import inspect
from importlib import import_module
from pathlib import Path

from algorithms.base import LocalSearch

ALGORITHMS_DIR = Path(__file__).resolve().parent
_SKIP_MODULES = {"algorithms.base", "algorithms.registry"}

_classes: dict[str, type[LocalSearch]] = {}
_import_errors: dict[str, str] = {}
_discovered = False


def _key(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def register(cls: type[LocalSearch]) -> type[LocalSearch]:
    _classes[_key(cls.name)] = cls
    return cls


def discover() -> None:
    global _discovered
    if _discovered:
        return
    _discovered = True
    for path in sorted(ALGORITHMS_DIR.rglob("*.py")):
        module_name = ".".join(path.relative_to(ALGORITHMS_DIR.parent).with_suffix("").parts)
        if module_name in _SKIP_MODULES:
            continue
        try:
            module = import_module(module_name)
        except Exception as exc:
            _import_errors[module_name] = f"{type(exc).__name__}: {exc}"
            continue
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, LocalSearch) and obj.__module__ == module_name and not inspect.isabstract(obj):
                register(obj)


def algorithms() -> dict[str, type[LocalSearch]]:
    discover()
    return dict(_classes)


def import_errors() -> dict[str, str]:
    discover()
    return dict(_import_errors)


def canonical_name(name: str) -> str:
    discover()
    key = _key(name)
    if key in _classes:
        return key
    for canonical, cls in _classes.items():
        if key in (_key(alias) for alias in cls.aliases):
            return canonical
    available = ", ".join(sorted(_classes)) or "(belum ada)"
    raise KeyError(f"Algoritma '{name}' tidak dikenal. Tersedia: {available}")


def get_algorithm(name: str) -> type[LocalSearch]:
    return _classes[canonical_name(name)]


def create(name: str, problem, objective: str = "default", seed: int | None = None,
           params: dict | None = None) -> LocalSearch:
    return get_algorithm(name)(problem, objective=objective, seed=seed, **(params or {}))
