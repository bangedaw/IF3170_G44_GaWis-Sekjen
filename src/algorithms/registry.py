from __future__ import annotations

from algorithms.base import LocalSearch
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.hill_climbing.random_restart import RandomRestartHC
from algorithms.hill_climbing.sideways import SidewaysMoveHC
from algorithms.hill_climbing.steepest_ascent import SteepestAscentHC
from algorithms.hill_climbing.stochastic import StochasticHC
from algorithms.simulated_annealing import SimulatedAnnealing

ALGORITHMS: dict[str, type[LocalSearch]] = {
    cls.name: cls
    for cls in (SteepestAscentHC, StochasticHC, SidewaysMoveHC, RandomRestartHC,
                SimulatedAnnealing, GeneticAlgorithm)
}


def algorithms() -> dict[str, type[LocalSearch]]:
    return dict(ALGORITHMS)


def canonical_name(name: str) -> str:
    key = name.strip().lower().replace("-", "_")
    for canonical, cls in ALGORITHMS.items():
        if key == canonical or key in cls.aliases:
            return canonical
    raise KeyError(f"Algoritma '{name}' tidak dikenal. Tersedia: {', '.join(sorted(ALGORITHMS))}")


def get_algorithm(name: str) -> type[LocalSearch]:
    return ALGORITHMS[canonical_name(name)]


def create(name: str, problem, objective: str = "default", seed: int | None = None,
           params: dict | None = None) -> LocalSearch:
    return get_algorithm(name)(problem, objective=objective, seed=seed, **(params or {}))
