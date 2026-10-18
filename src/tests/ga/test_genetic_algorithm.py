import json
from pathlib import Path

import pytest

from algorithms import registry
from algorithms.base import RunResult, load_core
from algorithms.genetic_algorithm import GeneticAlgorithm


def test_ga_is_registered():
    assert "genetic_algorithm" in registry.algorithms()
    assert registry.get_algorithm("genetic_algorithm") is GeneticAlgorithm
    assert registry.get_algorithm("ga") is GeneticAlgorithm
    assert registry.get_algorithm("genetic") is GeneticAlgorithm


def test_ga_params_validation(knapsack):
    algo = GeneticAlgorithm(knapsack, population_size=10, generations=5)
    assert algo.params["population_size"] == 10
    assert algo.params["generations"] == 5

    with pytest.raises(ValueError, match="parameter tidak dikenal"):
        GeneticAlgorithm(knapsack, unknown_param=123)


def test_ga_run_knapsack(knapsack):
    algo = GeneticAlgorithm(knapsack, seed=42, population_size=10, generations=8)
    result = algo.run()

    assert isinstance(result, RunResult)
    assert result.algorithm == "genetic_algorithm"
    assert result.iterations == 8
    assert len(result.history["objective"]) == 9
    assert len(result.history["max"]) == 9
    assert len(result.history["avg"]) == 9

    for m, a in zip(result.history["max"], result.history["avg"]):
        assert m >= a - 1e-6

    assert result.extra["population_size"] == 10
    assert result.extra["generations"] == 8
    assert result.duration_sec >= 0.0


def test_ga_run_real_core():
    core = load_core()
    problem_path = Path(__file__).resolve().parents[2] / "data" / "small.json"
    problem = core.load_problem(str(problem_path))

    algo = GeneticAlgorithm(problem, seed=123, population_size=8, generations=5)
    result = algo.run()

    assert result.iterations == 5
    assert len(result.history["objective"]) == 6
    assert result.final_state is not None
    assert "placements" in result.final_state
    assert len(result.final_state["placements"]) == len(problem.packages)


def test_ga_reproducibility():
    core = load_core()
    problem_path = Path(__file__).resolve().parents[2] / "data" / "small.json"
    problem = core.load_problem(str(problem_path))

    r1 = GeneticAlgorithm(problem, seed=99, population_size=6, generations=4).run()
    r2 = GeneticAlgorithm(problem, seed=99, population_size=6, generations=4).run()

    assert r1.final_objective == r2.final_objective
    assert r1.history["objective"] == r2.history["objective"]
    assert r1.history["max"] == r2.history["max"]


def test_ga_multi_truck_and_alt_objective():
    core = load_core()
    problem_path = Path(__file__).resolve().parents[2] / "data" / "multi_truck.json"
    problem = core.load_problem(str(problem_path))

    algo = GeneticAlgorithm(problem, objective="alt", seed=7, population_size=6, generations=3)
    result = algo.run()

    assert result.objective_name == "alt"
    assert "value_per_truck" in result.extra
    assert len(result.extra["value_per_truck"]) == len(problem.trucks)
