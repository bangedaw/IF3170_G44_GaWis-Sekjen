import json
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
for path in (TESTS_DIR / "helpers", TESTS_DIR.parent):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import fake_core as _fake
from algorithms.base import CORE_API
from dummy_algorithm import RandomWalk


@pytest.fixture
def fake_core(monkeypatch):
    for module in {"core", *CORE_API.values()}:
        monkeypatch.setitem(sys.modules, module, _fake)
    return _fake


@pytest.fixture
def knapsack(fake_core):
    return fake_core.make_problem(
        values=[60, 50, 40, 35, 30, 25, 20, 10],
        weights=[40, 35, 30, 25, 20, 15, 10, 5],
        capacities=(100,),
    )


@pytest.fixture
def problem_file(tmp_path, fake_core):
    problem = fake_core.make_problem(
        values=[60, 50, 40, 35, 30, 25, 20, 10],
        weights=[40, 35, 30, 25, 20, 15, 10, 5],
        capacities=(80, 60),
    )
    path = tmp_path / "problem.json"
    path.write_text(json.dumps(fake_core.problem_dict(problem)), encoding="utf-8")
    return path


@pytest.fixture
def dummy_algorithm(monkeypatch, fake_core):
    from algorithms import registry

    monkeypatch.setitem(registry.ALGORITHMS, RandomWalk.name, RandomWalk)
    return RandomWalk
