import json

import pytest

from algorithms.base import CORE_API, RunResult, load_core
from dummy_algorithm import RandomWalk

CONTRACT_KEYS = {
    "algorithm", "objective_name", "problem", "problem_file", "seed", "params",
    "initial_state", "initial_objective", "final_state", "final_objective", "final_value",
    "feasible", "duration_sec", "iterations", "history", "extra",
}


def test_load_core_collects_contract_api(fake_core):
    core = load_core()
    assert set(vars(core)) == set(CORE_API) == set(fake_core.API)
    assert core.evaluate is fake_core.evaluate


def test_unknown_param_rejected(knapsack):
    with pytest.raises(ValueError, match="tidak dikenal"):
        RandomWalk(knapsack, stepz=3)


def test_result_follows_contract(knapsack):
    result = RandomWalk(knapsack, seed=1, steps=4).run()
    data = result.to_dict()
    assert CONTRACT_KEYS <= data.keys()
    assert data["algorithm"] == "random_walk"
    assert data["params"] == {"steps": 4}
    assert data["iterations"] == 4
    assert len(data["history"]["objective"]) == 5
    assert data["initial_objective"] == data["history"]["objective"][0]
    assert data["final_objective"] == data["history"]["objective"][-1]
    assert set(data["final_state"]["placements"]) == set(knapsack.ids)
    assert set(data["final_violations"]) == {"overlap", "out_of_bounds", "floating", "fragile_support", "overweight"}
    assert data["extra"]["evaluations"] == 5
    assert data["duration_sec"] >= 0


def test_objective_is_swappable(knapsack):
    default = RandomWalk(knapsack, seed=3).run()
    alt = RandomWalk(knapsack, objective="alt", seed=3).run()
    assert alt.objective_name == "alt"
    assert alt.final_state == default.final_state
    assert alt.final_objective != default.final_objective


def test_same_seed_same_result(knapsack):
    a, b = RandomWalk(knapsack, seed=7).run(), RandomWalk(knapsack, seed=7).run()
    assert a.history == b.history and a.final_state == b.final_state
    algo = RandomWalk(knapsack, seed=7)
    assert algo.run().history == algo.run().history


def test_value_per_truck_for_multi_truck(fake_core):
    problem = fake_core.make_problem([10, 20, 30], [1, 1, 1], capacities=(5, 5))
    result = RandomWalk(problem, seed=1).run()
    assert len(result.extra["value_per_truck"]) == 2
    assert sum(result.extra["value_per_truck"]) == result.final_value


def test_save_load_roundtrip(knapsack, tmp_path):
    result = RandomWalk(knapsack, seed=1).run()
    path = result.save(tmp_path / "nested" / "run.json")
    text = path.read_text(encoding="utf-8")
    objective_line = next(line for line in text.splitlines() if '"objective": [' in line)
    assert objective_line.rstrip().endswith("]")
    assert RunResult.load(path).to_dict() == json.loads(json.dumps(result.to_dict()))


def test_numpy_values_are_serialized():
    np = pytest.importorskip("numpy")
    result = RunResult(algorithm="x", iterations=np.int64(3), history={"objective": np.arange(3.0)},
                       extra={"flag": np.bool_(True)})
    data = json.loads(result.to_json())
    assert data["iterations"] == 3 and data["history"]["objective"] == [0.0, 1.0, 2.0]
    assert data["extra"]["flag"] is True
