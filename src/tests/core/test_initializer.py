import random
from pathlib import Path

import pytest

from core import evaluate, load_problem, random_state

DATA = Path(__file__).resolve().parents[2] / "data"


@pytest.mark.parametrize("name", ["small", "medium", "large", "multi_truck"])
def test_feasible_mode_gives_valid_mixed_state(name):
    problem = load_problem(DATA / f"{name}.json")
    for seed in range(5):
        state = random_state(problem, random.Random(seed))
        assert evaluate(problem, state).feasible
        inside = sum(p.truck is not None for p in state.placements)
        assert 0 < inside < len(state)


def test_same_seed_same_state_different_seed_different_state():
    problem = load_problem(DATA / "medium.json")
    assert random_state(problem, random.Random(4)) == random_state(problem, random.Random(4))
    assert random_state(problem, random.Random(4)) != random_state(problem, random.Random(5))


def test_orientations_are_randomized():
    problem = load_problem(DATA / "medium.json")
    state = random_state(problem, random.Random(2))
    assert len({p.orientation for p in state.placements}) > 1


def test_uniform_mode_ignores_constraints_but_stays_in_bounds_coordinates():
    problem = load_problem(DATA / "medium.json")
    infeasible = 0
    for seed in range(5):
        state = random_state(problem, random.Random(seed), mode="uniform")
        infeasible += not evaluate(problem, state).feasible
        assert all(p.x >= 0 and p.y >= 0 and p.z >= 0 for p in state.placements)
    assert infeasible >= 4


def test_p_inside_extremes():
    problem = load_problem(DATA / "medium.json")
    none_in = random_state(problem, random.Random(1), p_inside=0.0)
    assert all(p.truck is None for p in none_in.placements)
    assert any(p.truck is not None for p in random_state(problem, random.Random(1), p_inside=1.0).placements)


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        random_state(load_problem(DATA / "small.json"), random.Random(1), mode="x")
