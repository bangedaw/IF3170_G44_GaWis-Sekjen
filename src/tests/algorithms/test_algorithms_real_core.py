import json
from pathlib import Path

import pytest

from algorithms import registry
from algorithms.base import load_core

DATA = Path(__file__).resolve().parents[2] / "data"

QUICK_PARAMS = {
    "steepest_ascent_hc": {"neighbor_limit": 40, "max_iterations": 4},
    "stochastic_hc": {"neighbor_limit": 40, "max_iterations": 4},
    "sideways_move_hc": {"max_sideways": 2, "neighbor_limit": 40, "max_iterations": 4},
    "random_restart_hc": {"max_restart": 2, "base_params": {"neighbor_limit": 30, "max_iterations": 2}},
    "simulated_annealing": {"t0": 50, "cooling": 0.99, "max_iterations": 300, "stuck_patience": 50},
}
HILL_CLIMBING = [name for name in QUICK_PARAMS if name.endswith("_hc")]
CASES = [("small", "default"), ("medium", "alt"), ("multi_truck", "default"), ("multi_truck", "alt")]


@pytest.fixture(scope="module")
def problems():
    core = load_core()
    return {name: core.load_problem(DATA / f"{name}.json") for name in ("small", "medium", "multi_truck")}


def test_all_miguel_algorithms_are_registered():
    assert set(QUICK_PARAMS) <= set(registry.algorithms())
    assert registry.import_errors() == {}


@pytest.mark.parametrize("problem_name, objective", CASES)
@pytest.mark.parametrize("algorithm", QUICK_PARAMS)
def test_runs_on_real_core(problems, algorithm, problem_name, objective):
    problem = problems[problem_name]
    result = registry.create(algorithm, problem, objective=objective, seed=1, params=QUICK_PARAMS[algorithm]).run()
    data = json.loads(result.to_json())

    assert data["objective_name"] == objective
    assert len(data["history"]["objective"]) == data["iterations"] + 1
    assert set(data["final_state"]["placements"]) == set(problem.ids)
    assert len(data["extra"]["value_per_truck"]) == len(problem.trucks)
    assert sum(data["extra"]["value_per_truck"]) == pytest.approx(data["final_value"])
    evaluation = load_core().evaluate(problem, load_core().state_from_dict(data["final_state"], problem), objective)
    assert evaluation.objective == pytest.approx(data["final_objective"])
    if algorithm in HILL_CLIMBING:
        assert data["final_objective"] >= data["initial_objective"]
