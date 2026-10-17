"""Tes kontrak: core asli dipakai lewat LocalSearch (algorithms/base.py) seperti oleh Miguel dan Rere."""
import json
from pathlib import Path

import pytest

from algorithms.base import CORE_API, LocalSearch, load_core

DATA = Path(__file__).resolve().parents[2] / "data"


class Climb(LocalSearch):
    name = "climb"
    default_params = {"steps": 60}

    def _search(self):
        state = self.random_state()
        initial, best = state, self.objective(state)
        for _ in range(self.params["steps"]):
            candidate, _ = self.random_neighbor(state)
            value = self.objective(candidate)
            self.iterations += 1
            if value >= best:
                state, best = candidate, value
            self.record("objective", best)
        return initial, state


def test_core_exposes_the_whole_contract_api():
    core = load_core()
    assert set(vars(core)) == set(CORE_API)
    assert all(callable(fn) for fn in vars(core).values())


@pytest.mark.parametrize("name, objective", [("small", "default"), ("multi_truck", "default"), ("medium", "alt")])
def test_local_search_runs_end_to_end_on_real_core(name, objective):
    core = load_core()
    problem = core.load_problem(DATA / f"{name}.json")
    result = Climb(problem, objective=objective, seed=1).run()
    assert result.final_objective >= result.initial_objective
    assert result.final_state["placements"].keys() == initial_keys(result)
    assert len(result.history["objective"]) == 60
    assert set(result.final_violations) == {"overlap", "out_of_bounds", "floating", "fragile_support", "overweight"}
    json.loads(result.to_json())
    if name == "multi_truck":
        assert len(result.extra["value_per_truck"]) == 3


def initial_keys(result):
    return result.initial_state["placements"].keys()


def test_runs_are_reproducible_by_seed():
    core = load_core()
    problem = core.load_problem(DATA / "small.json")
    first = Climb(problem, seed=3).run()
    second = Climb(problem, seed=3).run()
    assert first.final_state == second.final_state and first.initial_state == second.initial_state
