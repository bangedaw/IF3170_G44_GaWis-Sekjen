import json
from pathlib import Path

import pytest

from algorithms.base import RunResult

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
MOCK_RUNS = sorted(p for p in FIXTURES.glob("mock_*.json") if not p.name.startswith("mock_problem"))
CONTRACT_KEYS = {
    "algorithm", "objective_name", "problem", "problem_file", "seed", "params",
    "initial_state", "initial_objective", "final_state", "final_objective", "final_value",
    "feasible", "duration_sec", "iterations", "history", "extra",
}


def effective_dims(package, orientation):
    dims = [0, 0, 0]
    for side, axis in zip("wlh", orientation):
        dims["xyz".index(axis)] = package["dimensions"][side]
    return dims


def test_all_mock_kinds_exist():
    names = {p.stem for p in MOCK_RUNS}
    assert {"mock_steepest_ascent_hc", "mock_simulated_annealing", "mock_genetic_algorithm",
            "mock_multi_truck_simulated_annealing"} <= names


@pytest.mark.parametrize("path", MOCK_RUNS, ids=lambda p: p.stem)
def test_mock_follows_contract(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert CONTRACT_KEYS <= data.keys()
    assert RunResult.load(path).to_dict() == data
    assert (FIXTURES.parents[2] / data["problem_file"]).exists()

    problem = data["problem"]
    packages = {p["id"]: p for p in problem["packages"]}
    for key in ("initial_state", "final_state"):
        placements = data[key]["placements"]
        assert set(placements) == set(packages)
        for pid, pl in placements.items():
            assert sorted(pl["orientation"]) == ["x", "y", "z"]
            if pl["truck"] is None:
                continue
            assert 0 <= pl["truck"] < len(problem["trucks"])
            assert pl["dims"] == effective_dims(packages[pid], pl["orientation"])
            assert all(isinstance(pl[k], int) for k in "xyz")

    assert data["feasible"] and not any(data["final_violations"].values())
    inside = [pid for pid, pl in data["final_state"]["placements"].items() if pl["truck"] is not None]
    assert data["final_value"] == sum(packages[pid]["value"] for pid in inside)
    assert sum(data["extra"]["value_per_truck"]) == data["final_value"]
    assert len(data["extra"]["value_per_truck"]) == len(problem["trucks"])
    assert data["history"]["objective"][0] == data["initial_objective"]


@pytest.mark.parametrize("path", [p for p in MOCK_RUNS if "simulated_annealing" in p.stem], ids=lambda p: p.stem)
def test_sa_mock_history(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    n = data["iterations"]
    assert len(data["history"]["acceptance_prob"]) == len(data["history"]["temperature"]) == n
    assert len(data["history"]["objective"]) == n + 1
    assert {"stuck_count", "stuck_definition"} <= data["extra"].keys()


def test_ga_mock_history():
    data = json.loads((FIXTURES / "mock_genetic_algorithm.json").read_text(encoding="utf-8"))
    best, avg = data["history"]["max"], data["history"]["avg"]
    assert len(best) == len(avg) == data["extra"]["generations"] + 1
    assert all(a <= b for a, b in zip(avg, best))
    assert best[-1] == data["final_objective"]


def test_random_restart_mock_extra():
    data = json.loads((FIXTURES / "mock_random_restart_hc.json").read_text(encoding="utf-8"))
    extra = data["extra"]
    assert extra["restarts"] == extra["max_restart"] == len(extra["iterations_per_restart"]) - 1
    assert sum(extra["iterations_per_restart"]) == data["iterations"]
    assert max(extra["objective_per_restart"]) == data["final_objective"]
