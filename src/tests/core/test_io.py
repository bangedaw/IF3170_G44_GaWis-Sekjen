import json
from pathlib import Path

import pytest

from core import (load_problem, problem_from_dict, problem_to_dict, random_state, state_from_dict,
                  state_to_dict)

DATA = Path(__file__).resolve().parents[2] / "data"
RAW = {
    "trucks": [{"id": "T1", "dimensions": {"w": 10, "l": 20, "h": 5}, "max_capacity": 500}],
    "packages": [{"id": "RusdiPackage", "dimensions": {"w": 3, "l": 4, "h": 1}, "value": 60,
                  "weight": 5, "is_fragile": False, "eta": 3}],
}


def test_problem_roundtrip():
    problem = problem_from_dict(RAW)
    assert problem_to_dict(problem) == RAW
    assert problem.packages[0].dims == (3, 4, 1) and problem.trucks[0].volume == 1000


def test_load_problem_from_file(tmp_path):
    path = tmp_path / "p.json"
    path.write_text(json.dumps(RAW), encoding="utf-8")
    assert load_problem(path).ids == ("RusdiPackage",)


def test_rejects_duplicate_ids_and_bad_dims():
    dup = json.loads(json.dumps(RAW))
    dup["packages"].append(dup["packages"][0])
    with pytest.raises(ValueError):
        problem_from_dict(dup)
    bad = json.loads(json.dumps(RAW))
    bad["packages"][0]["dimensions"]["w"] = 2.5
    with pytest.raises(ValueError):
        problem_from_dict(bad)
    bad["packages"][0]["dimensions"]["w"] = 0
    with pytest.raises(ValueError):
        problem_from_dict(bad)


@pytest.mark.parametrize("name", ["small", "medium", "large", "multi_truck"])
def test_state_dict_roundtrip_is_json_serializable(name):
    import random
    problem = load_problem(DATA / f"{name}.json")
    state = random_state(problem, random.Random(3))
    data = state_to_dict(state)
    assert json.loads(json.dumps(data)) == data
    assert state_from_dict(data) == state
    assert state_from_dict(data, problem) == state


def test_state_dict_follows_contract(build):
    make_problem, make_state = build
    problem = make_problem([(10, 10, 5, 100)], [(3, 4, 1, 60, 5, False), (2, 2, 2, 1, 1, False)])
    data = state_to_dict(make_state(problem, [(0, 1, 2, 0, "yxz"), None]))
    assert data["placements"]["P0"] == {"truck": 0, "x": 1, "y": 2, "z": 0, "orientation": "yxz", "dims": [4, 3, 1]}
    assert data["placements"]["P1"]["truck"] is None and "x" not in data["placements"]["P1"]


def test_state_from_dict_accepts_outside_without_dims():
    data = {"placements": {"A": {"truck": None, "orientation": "xyz"}}}
    assert state_from_dict(data).placements[0].truck is None


def test_state_from_dict_rejects_bad_orientation():
    with pytest.raises(ValueError):
        state_from_dict({"placements": {"A": {"truck": None, "orientation": "xxx"}}})


@pytest.mark.parametrize("name", ["small", "medium", "large", "multi_truck"])
def test_generated_data_files_are_valid(name):
    problem = load_problem(DATA / f"{name}.json")
    assert len(problem.packages) >= 5
    assert any(p.is_fragile for p in problem.packages)
    assert sum(p.weight for p in problem.packages) > sum(t.max_capacity for t in problem.trucks)
    assert sum(p.volume for p in problem.packages) > sum(t.volume for t in problem.trucks)
    assert all(any(max(p.dims) <= max(t.dims) and min(p.dims) <= min(t.dims) for t in problem.trucks)
               for p in problem.packages)


def test_multi_truck_file_has_several_trucks():
    assert len(load_problem(DATA / "multi_truck.json").trucks) >= 2
