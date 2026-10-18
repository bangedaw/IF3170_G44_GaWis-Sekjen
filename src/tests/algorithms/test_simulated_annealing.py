import math

import pytest

from algorithms.simulated_annealing import SimulatedAnnealing


def test_history_is_complete(knapsack):
    result = SimulatedAnnealing(knapsack, seed=1, t0=50, cooling=0.99, max_iterations=300).run()
    n = result.iterations
    assert n == 300
    assert len(result.history["objective"]) == n + 1
    assert len(result.history["acceptance_prob"]) == n
    assert len(result.history["temperature"]) == n
    assert all(0.0 <= p <= 1.0 for p in result.history["acceptance_prob"])
    assert any(p < 1.0 for p in result.history["acceptance_prob"])
    temperatures = result.history["temperature"]
    assert temperatures[0] == 50 and all(b < a for a, b in zip(temperatures, temperatures[1:]))
    assert result.final_objective == result.history["objective"][-1]
    assert result.extra["stop_reason"] == "max_iterations"


def test_stops_when_temperature_reaches_t_min(knapsack):
    result = SimulatedAnnealing(knapsack, seed=1, t0=10, cooling=0.9, t_min=1, max_iterations=10_000).run()
    assert result.iterations == math.ceil(math.log(1 / 10) / math.log(0.9))
    assert result.extra["stop_reason"] == "t_min"


def test_counts_stuck_events(knapsack):
    result = SimulatedAnnealing(knapsack, seed=1, t0=0.01, cooling=0.999, t_min=1e-9,
                                max_iterations=400, stuck_patience=20).run()
    extra = result.extra
    assert extra["stuck_count"] >= 1
    assert extra["stuck_count"] == len(extra["stuck_iterations"])
    assert "20 iterasi" in extra["stuck_definition"]


def test_accepts_worse_moves_when_hot(knapsack):
    result = SimulatedAnnealing(knapsack, seed=1, t0=1e6, cooling=0.999, max_iterations=200).run()
    assert result.extra["accepted_worse_moves"] > 0
    history = result.history["objective"]
    assert any(b < a for a, b in zip(history, history[1:]))


def test_return_best(knapsack):
    result = SimulatedAnnealing(knapsack, seed=2, t0=1e4, cooling=0.99, max_iterations=200, return_best=True).run()
    assert result.final_objective == max(result.history["objective"]) == result.extra["best_objective_seen"]


def test_rejects_invalid_schedule(knapsack):
    with pytest.raises(ValueError):
        SimulatedAnnealing(knapsack, cooling=1.5)
    with pytest.raises(ValueError):
        SimulatedAnnealing(knapsack, t0=0)


def test_reproducible(knapsack):
    a = SimulatedAnnealing(knapsack, seed=9, max_iterations=300).run()
    b = SimulatedAnnealing(knapsack, seed=9, max_iterations=300).run()
    assert a.history == b.history and a.final_state == b.final_state
