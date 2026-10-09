from __future__ import annotations

import json
from dataclasses import dataclass
from types import SimpleNamespace

PENALTY = 10.0
API = ("load_problem", "random_state", "evaluate", "get_objective",
       "random_neighbor", "neighbors", "state_to_dict", "state_from_dict")


@dataclass(frozen=True)
class Problem:
    ids: tuple[str, ...]
    values: tuple[float, ...]
    weights: tuple[float, ...]
    capacities: tuple[float, ...]


def make_problem(values, weights, capacities=(100,)) -> Problem:
    ids = tuple(f"P{i}" for i in range(len(values)))
    return Problem(ids, tuple(values), tuple(weights), tuple(capacities))


def problem_dict(problem: Problem) -> dict:
    dims = {"w": 1, "l": 1, "h": 1}
    return {
        "trucks": [{"id": f"T{t + 1}", "dimensions": dims, "max_capacity": c}
                   for t, c in enumerate(problem.capacities)],
        "packages": [{"id": pid, "dimensions": dims, "value": v, "weight": w, "is_fragile": False, "eta": 1}
                     for pid, v, w in zip(problem.ids, problem.values, problem.weights)],
    }


def load_problem(path) -> Problem:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    packages = raw["packages"]
    return Problem(
        tuple(p["id"] for p in packages),
        tuple(p["value"] for p in packages),
        tuple(p["weight"] for p in packages),
        tuple(t["max_capacity"] for t in raw["trucks"]),
    )


def random_state(problem, rng):
    options = [None, *range(len(problem.capacities))]
    return tuple((pid, rng.choice(options)) for pid in problem.ids)


def _loads(problem, state):
    value = [0.0] * len(problem.capacities)
    weight = [0.0] * len(problem.capacities)
    for i, (_, truck) in enumerate(state):
        if truck is not None:
            value[truck] += problem.values[i]
            weight[truck] += problem.weights[i]
    overweight = sum(max(0.0, w - c) for w, c in zip(weight, problem.capacities))
    return value, overweight


def _default(problem, state):
    value, overweight = _loads(problem, state)
    return sum(value) - PENALTY * overweight


def _alt(problem, state):
    value, overweight = _loads(problem, state)
    return 2 * sum(value) - PENALTY * overweight


OBJECTIVES = {"default": _default, "alt": _alt}


def get_objective(name):
    if name not in OBJECTIVES:
        raise ValueError(f"objective tidak dikenal: {name}")
    return OBJECTIVES[name]


def evaluate(problem, state, objective="default"):
    value, overweight = _loads(problem, state)
    return SimpleNamespace(
        objective=get_objective(objective)(problem, state),
        total_value=sum(value),
        feasible=overweight == 0,
        violations={"overlap": 0, "out_of_bounds": 0, "floating": 0, "fragile_support": 0, "overweight": overweight},
        value_per_truck=value,
    )


def _moves(problem, state):
    options = [None, *range(len(problem.capacities))]
    for i, (_, truck) in enumerate(state):
        for target in options:
            if target != truck:
                yield {"type": "move", "package": i, "truck": target}
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i][1] != state[j][1]:
                yield {"type": "swap", "a": i, "b": j}


def _apply(state, move):
    trucks = [truck for _, truck in state]
    if move["type"] == "move":
        trucks[move["package"]] = move["truck"]
    else:
        trucks[move["a"]], trucks[move["b"]] = trucks[move["b"]], trucks[move["a"]]
    return tuple((pid, truck) for (pid, _), truck in zip(state, trucks)), move


def neighbors(problem, state, rng=None, limit=None):
    moves = list(_moves(problem, state))
    if rng is not None:
        rng.shuffle(moves)
    if limit is not None:
        moves = moves[:limit]
    for move in moves:
        yield _apply(state, move)


def random_neighbor(problem, state, rng):
    return _apply(state, rng.choice(list(_moves(problem, state))))


def state_to_dict(state):
    placements = {}
    for pid, truck in state:
        if truck is None:
            placements[pid] = {"truck": None, "orientation": "xyz"}
        else:
            placements[pid] = {"truck": truck, "x": 0, "y": 0, "z": 0, "orientation": "xyz", "dims": [1, 1, 1]}
    return {"placements": placements}


def state_from_dict(data):
    return tuple((pid, p["truck"]) for pid, p in data["placements"].items())
