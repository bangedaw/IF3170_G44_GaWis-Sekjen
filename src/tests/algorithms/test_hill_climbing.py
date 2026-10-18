import pytest

from algorithms.hill_climbing.common import EPS
from algorithms.hill_climbing.first_choice import FirstChoiceHC
from algorithms.hill_climbing.random_restart import RandomRestartHC
from algorithms.hill_climbing.sideways import SidewaysMoveHC
from algorithms.hill_climbing.steepest_ascent import SteepestAscentHC
from algorithms.hill_climbing.stochastic import StochasticHC

SINGLE_CLIMB = [
    (SteepestAscentHC, {}),
    (SidewaysMoveHC, {"max_sideways": 5}),
    (StochasticHC, {}),
    (StochasticHC, {"weighted": True}),
    (StochasticHC, {"mode": "random", "max_iterations": 50}),
    (FirstChoiceHC, {"max_tries": 50}),
]


def has_better_neighbor(fake_core, problem, state_dict, value):
    state = fake_core.state_from_dict(state_dict)
    objective = fake_core.get_objective("default")
    return any(objective(problem, neighbor) > value + EPS for neighbor, _ in fake_core.neighbors(problem, state))


@pytest.fixture
def plateau(fake_core):
    return fake_core.make_problem([10] * 8, [5] * 8, capacities=(20,))


@pytest.mark.parametrize("cls, params", SINGLE_CLIMB)
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_hill_climbing_never_goes_down(knapsack, cls, params, seed):
    result = cls(knapsack, seed=seed, **params).run()
    history = result.history["objective"]
    assert len(history) == result.iterations + 1
    assert all(b >= a - EPS for a, b in zip(history, history[1:]))
    assert history[0] == result.initial_objective
    assert history[-1] == result.final_objective
    assert "stop_reason" in result.extra


@pytest.mark.parametrize("cls, params", [(SteepestAscentHC, {}), (StochasticHC, {}), (StochasticHC, {"weighted": True})])
@pytest.mark.parametrize("seed", [1, 2, 3])
def test_full_neighborhood_climbers_stop_at_local_optimum(fake_core, knapsack, cls, params, seed):
    result = cls(knapsack, seed=seed, **params).run()
    assert result.extra["stop_reason"] == "local_optimum"
    assert not has_better_neighbor(fake_core, knapsack, result.final_state, result.final_objective)


def test_steepest_ascent_takes_best_neighbor(fake_core, knapsack):
    result = SteepestAscentHC(knapsack, seed=4).run()
    start = fake_core.state_from_dict(result.initial_state)
    objective = fake_core.get_objective("default")
    best_first_step = max(objective(knapsack, neighbor) for neighbor, _ in fake_core.neighbors(knapsack, start))
    assert result.history["objective"][1] == best_first_step


def test_max_iterations_respected(knapsack):
    result = SteepestAscentHC(knapsack, seed=1, max_iterations=1).run()
    assert result.iterations <= 1


def test_stochastic_random_mode_runs_exactly_nmax(knapsack):
    result = StochasticHC(knapsack, seed=1, mode="random", max_iterations=40).run()
    assert result.iterations == 40
    assert result.extra["evaluations"] == 41


def test_stochastic_rejects_invalid_params(knapsack):
    with pytest.raises(ValueError):
        StochasticHC(knapsack, mode="greedy")
    with pytest.raises(ValueError):
        StochasticHC(knapsack, mode="random", max_iterations=None)


@pytest.mark.parametrize("max_sideways", [0, 1, 7])
def test_sideways_stops_when_limit_reached(plateau, max_sideways):
    result = SidewaysMoveHC(plateau, seed=1, max_sideways=max_sideways).run()
    assert result.extra["max_sideways"] == max_sideways
    assert result.extra["sideways_used"] == max_sideways
    assert result.extra["stop_reason"] == "max_sideways"
    assert result.final_objective == 40
    history = result.history["objective"]
    assert sum(b == a for a, b in zip(history, history[1:])) == max_sideways


def test_first_choice_stops_without_better_neighbor(knapsack):
    result = FirstChoiceHC(knapsack, seed=1, max_tries=500).run()
    assert result.extra["stop_reason"] == "no_better_neighbor"


def test_random_restart_records_each_climb(knapsack):
    result = RandomRestartHC(knapsack, seed=1, max_restart=4).run()
    extra = result.extra
    assert extra["max_restart"] == 4 and extra["restarts"] == 4
    assert len(extra["iterations_per_restart"]) == 5
    assert sum(extra["iterations_per_restart"]) == result.iterations
    assert len(result.history["objective"]) == result.iterations + 1
    assert result.history["objective"][0] == result.initial_objective
    assert extra["start_objective_per_restart"][0] == result.initial_objective
    assert result.final_objective == max(extra["objective_per_restart"])
    assert extra["objective_per_restart"][extra["best_restart"]] == result.final_objective


def test_random_restart_history_marks_restart_edges(knapsack):
    result = RandomRestartHC(knapsack, seed=2, max_restart=3).run()
    history, extra = result.history["objective"], result.extra
    edge = 0
    for count, final in zip(extra["iterations_per_restart"], extra["objective_per_restart"]):
        edge += count
        assert history[edge] == final


def test_random_restart_with_sideways_base(plateau):
    result = RandomRestartHC(plateau, seed=2, max_restart=2, base_algorithm="sideways",
                             base_params={"max_sideways": 3}).run()
    assert result.extra["base_extra"]["sideways_used"] == 9


def test_random_restart_rejects_invalid_base(knapsack):
    with pytest.raises(ValueError):
        RandomRestartHC(knapsack, base_algorithm="sa")
    with pytest.raises(ValueError):
        RandomRestartHC(knapsack, base_params={"unknown": 1})


@pytest.mark.parametrize("cls", [SteepestAscentHC, SidewaysMoveHC, StochasticHC, FirstChoiceHC, RandomRestartHC])
def test_reproducible(knapsack, cls):
    a, b = cls(knapsack, seed=5).run(), cls(knapsack, seed=5).run()
    assert a.history == b.history and a.final_state == b.final_state
