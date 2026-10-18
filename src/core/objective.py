from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .constraints import check_state
from .models import Problem, State

OBJECTIVES = ("default", "alt")
ALT_UTILIZATION_WEIGHT = 0.05


@dataclass(frozen=True)
class Evaluation:
    objective: float
    total_value: float
    feasible: bool
    violations: dict
    value_per_truck: list
    weight_per_truck: list


@dataclass(frozen=True)
class _Scoring:
    scores: tuple[float, ...]
    unit: float
    rho: float
    utilization_bonus: float


def _scoring(problem: Problem, name: str) -> _Scoring:
    key = ("scoring", name)
    cached = problem.cache.get(key)
    if cached is not None:
        return cached
    if name == "default":
        scores = tuple(float(v) for v in problem.values)
        bonus = 0.0
    elif name == "alt":
        etas = [p.eta for p in problem.packages]
        lo, hi = min(etas, default=0), max(etas, default=0)
        span = hi - lo
        scores = tuple(p.value * (1 + ((hi - p.eta) / span if span else 0.0)) for p in problem.packages)
        bonus = ALT_UTILIZATION_WEIGHT * sum(scores)
    else:
        raise ValueError(f"objective tidak dikenal: {name!r}; pilihan: {OBJECTIVES}")
    unit = max(scores, default=1.0) or 1.0
    rho = max((s / w for s, w in zip(scores, problem.weights) if w > 0), default=1.0)
    result = problem.cache[key] = _Scoring(scores, unit, rho, bonus)
    return result


def _assess(problem: Problem, state: State, name: str):
    scoring = _scoring(problem, name)
    report = check_state(problem, state)
    value_per_truck = [0.0] * len(problem.trucks)
    volume_per_truck = [0] * len(problem.trucks)
    score = 0.0
    for t, members in enumerate(report.inside):
        for i in members:
            score += scoring.scores[i]
            value_per_truck[t] += problem.values[i]
            volume_per_truck[t] += problem.volumes[i]

    penalty = scoring.unit * (report.overlap + report.out_of_bounds
                              + report.floating + report.fragile_support)
    if report.overweight_trucks:
        penalty += scoring.rho * report.overweight + scoring.unit * report.overweight_trucks
    objective = score - penalty

    if scoring.utilization_bonus:
        used = 0.0
        for t, truck in enumerate(problem.trucks):
            used += (min(1.0, volume_per_truck[t] / truck.volume)
                     + min(1.0, report.weight_per_truck[t] / truck.max_capacity)) / 2
        objective += scoring.utilization_bonus * used / len(problem.trucks)
    return objective, report, value_per_truck


def evaluate(problem: Problem, state: State, objective: str = "default") -> Evaluation:
    value, report, value_per_truck = _assess(problem, state, objective)
    return Evaluation(
        objective=float(value),
        total_value=float(sum(value_per_truck)),
        feasible=report.feasible,
        violations=report.violations,
        value_per_truck=value_per_truck,
        weight_per_truck=list(report.weight_per_truck),
    )


def get_objective(name: str = "default") -> Callable[[Problem, State], float]:
    if name not in OBJECTIVES:
        raise ValueError(f"objective tidak dikenal: {name!r}; pilihan: {OBJECTIVES}")

    def objective(problem: Problem, state: State) -> float:
        return float(_assess(problem, state, name)[0])

    objective.__name__ = f"objective_{name}"
    return objective
