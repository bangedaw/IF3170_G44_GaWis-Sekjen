from __future__ import annotations

import random
from typing import Iterator

import numpy as np

from .candidates import TruckBoxes, candidate_positions, has_dependents, settle
from .models import Placement, Problem, State
from .orientation import AXES, dims_for, rotate

Move = dict

KIND_WEIGHTS = {"swap": 0.25, "move": 0.55, "rotate": 0.20}
FREE_MOVE_P = 0.10
REMOVE_P = 0.15
MAX_TRIES = 30
DEFAULT_PER_MOVE = 4


def _where(p: Placement):
    return None if p.truck is None else [p.truck, p.x, p.y, p.z]


def _lift(problem: Problem, placements: list[Placement], i: int) -> None:
    p = placements[i]
    dependents = p.truck is not None and has_dependents(placements, i)
    placements[i] = problem.outside(i, p.orientation)
    if dependents:
        settle(placements, p.truck)


def _pick(cands: np.ndarray, rng: random.Random | None, count: int) -> list[tuple[int, int, int]]:
    if len(cands) == 0:
        return []
    if rng is not None:
        order = rng.sample(range(len(cands)), min(count, len(cands)))
    else:
        order = np.lexsort((cands[:, 0], cands[:, 1], cands[:, 2]))[:count]
    return [(int(cands[k, 0]), int(cands[k, 1]), int(cands[k, 2])) for k in order]


def _moves_to(problem: Problem, state: State, i: int, target: int | None,
              rng: random.Random | None, count: int) -> list[tuple[State, Move]]:
    before = state.placements[i]
    base = list(state.placements)
    _lift(problem, base, i)
    if target is None:
        if before.truck is None:
            return []
        move = {"type": "move", "package": problem.ids[i], "mode": "remove", "from": _where(before), "to": None}
        return [(State(state.ids, tuple(base)), move)]

    truck, pkg = problem.trucks[target], problem.packages[i]
    load = sum(problem.weights[j] for j, p in enumerate(base) if p.truck == target)
    if load + pkg.weight > truck.max_capacity:
        return []
    cands = candidate_positions(TruckBoxes(problem, base, target), truck, before.dims, pkg.is_fragile)
    if before.truck == target and len(cands):
        keep = ~((cands[:, 0] == before.x) & (cands[:, 1] == before.y) & (cands[:, 2] == before.z))
        cands = cands[keep]

    out = []
    for x, y, z in _pick(cands, rng, count):
        items = list(base)
        items[i] = problem.place(i, target, x, y, z, before.orientation)
        move = {"type": "move", "package": problem.ids[i], "mode": "candidate",
                "from": _where(before), "to": [target, x, y, z]}
        out.append((State(state.ids, tuple(items)), move))
    return out


def _free_move(problem: Problem, state: State, i: int, rng: random.Random) -> tuple[State, Move]:
    before = state.placements[i]
    target = rng.randrange(len(problem.trucks))
    truck = problem.trucks[target]
    dx, dy, dz = before.dims
    x, y = rng.randint(0, max(0, truck.w - dx)), rng.randint(0, max(0, truck.l - dy))
    z = rng.randint(0, max(0, truck.h - dz))
    items = list(state.placements)
    _lift(problem, items, i)
    items[i] = problem.place(i, target, x, y, z, before.orientation)
    move = {"type": "move", "package": problem.ids[i], "mode": "free",
            "from": _where(before), "to": [target, x, y, z]}
    return State(state.ids, tuple(items)), move


def _land(problem: Problem, items: list[Placement], i: int, slot: Placement, rng: random.Random | None) -> bool:
    pkg, t = problem.packages[i], slot.truck
    dx, dy = items[i].dims[0], items[i].dims[1]
    xs = {slot.x, slot.x + slot.dims[0] - dx}
    ys = {slot.y, slot.y + slot.dims[1] - dy}
    ax = [x for x in sorted(xs) for _ in ys]
    ay = [y for _ in xs for y in sorted(ys)]
    boxes = TruckBoxes(problem, items, t)
    spots = candidate_positions(boxes, problem.trucks[t], items[i].dims, pkg.is_fragile, anchors=(ax, ay))
    if len(spots) == 0:
        return False
    row = spots[rng.randrange(len(spots)) if rng is not None else 0]
    items[i] = problem.place(i, t, int(row[0]), int(row[1]), int(row[2]), items[i].orientation)
    return True


def _swap(problem: Problem, state: State, a: int, b: int, rng: random.Random | None) -> tuple[State, Move] | None:
    pa, pb = state.placements[a], state.placements[b]
    if pa.truck is None and pb.truck is None:
        return None
    items = list(state.placements)
    _lift(problem, items, a)
    _lift(problem, items, b)
    for i, slot in ((a, pb), (b, pa)):
        if slot.truck is not None and not _land(problem, items, i, slot, rng):
            return None
    result = State(state.ids, tuple(items))
    if result == state:
        return None
    return result, {"type": "swap", "a": problem.ids[a], "b": problem.ids[b]}


def _clear(problem: Problem, items: list[Placement], i: int) -> bool:
    p = items[i]
    truck = problem.trucks[p.truck]
    x2, y2, z2 = p.x + p.dims[0], p.y + p.dims[1], p.z + p.dims[2]
    if p.x < 0 or p.y < 0 or p.z < 0 or x2 > truck.w or y2 > truck.l or z2 > truck.h:
        return False
    boxes = TruckBoxes(problem, items, p.truck, exclude=(i,))
    if boxes.size == 0:
        return True
    hit = ((p.x < boxes.x2) & (boxes.x < x2) & (p.y < boxes.y2) & (boxes.y < y2)
           & (p.z < boxes.z2) & (boxes.z < z2))
    return not hit.any()


def _rotate(problem: Problem, state: State, i: int, axis: str) -> tuple[State, Move] | None:
    p = state.placements[i]
    orientation = rotate(p.orientation, axis)
    dims = dims_for(problem.packages[i].dims, orientation)
    if dims == p.dims:
        return None
    items = list(state.placements)
    x, y = p.x, p.y
    if p.truck is not None:
        truck = problem.trucks[p.truck]
        x, y = max(0, min(x, truck.w - dims[0])), max(0, min(y, truck.l - dims[1]))
    items[i] = p._replace(x=x, y=y, orientation=orientation, dims=dims)
    if p.truck is not None:
        settle(items, p.truck)
        if not _clear(problem, items, i):
            return None
    move = {"type": "rotate", "package": problem.ids[i], "axis": axis, "orientation": orientation}
    return State(state.ids, tuple(items)), move


def _specs(problem: Problem, state: State) -> list[tuple]:
    n, trucks = len(state), len(problem.trucks)
    inside = [p.truck is not None for p in state.placements]
    specs: list[tuple] = []
    for i in range(n):
        specs.extend(("move", i, t) for t in range(trucks))
        if inside[i]:
            specs.append(("move", i, None))
            specs.extend(("rotate", i, axis) for axis in AXES)
    for i in range(n):
        for j in range(i + 1, n):
            if inside[i] or inside[j]:
                specs.append(("swap", i, j))
    return specs


def neighbors(problem: Problem, state: State, rng: random.Random | None = None,
              limit: int | None = None, per_move: int = DEFAULT_PER_MOVE) -> Iterator[tuple[State, Move]]:
    specs = _specs(problem, state)
    if rng is not None:
        rng.shuffle(specs)
    produced = 0
    for kind, i, arg in specs:
        if kind == "move":
            found = _moves_to(problem, state, i, arg, rng, per_move)
        elif kind == "rotate":
            result = _rotate(problem, state, i, arg)
            found = [result] if result else []
        else:
            result = _swap(problem, state, i, arg, rng)
            found = [result] if result else []
        for neighbor in found:
            yield neighbor
            produced += 1
            if limit is not None and produced >= limit:
                return


def _random_swap(problem: Problem, state: State, rng: random.Random):
    n = len(state)
    inside = [i for i, p in enumerate(state.placements) if p.truck is not None]
    if n < 2 or not inside:
        return None
    a = rng.choice(inside)
    b = rng.randrange(n - 1)
    return _swap(problem, state, a, b + (b >= a), rng)


def _random_move(problem: Problem, state: State, rng: random.Random):
    if not len(state):
        return None
    i = rng.randrange(len(state))
    inside = state.placements[i].truck is not None
    if rng.random() < FREE_MOVE_P:
        return _free_move(problem, state, i, rng)
    if inside and rng.random() < REMOVE_P:
        target = None
    else:
        target = rng.randrange(len(problem.trucks))
    found = _moves_to(problem, state, i, target, rng, 1)
    return found[0] if found else None


def _random_rotate(problem: Problem, state: State, rng: random.Random):
    if not len(state):
        return None
    i = rng.randrange(len(state))
    axes = list(AXES)
    rng.shuffle(axes)
    for axis in axes:
        result = _rotate(problem, state, i, axis)
        if result:
            return result
    return None


_RANDOM = {"swap": _random_swap, "move": _random_move, "rotate": _random_rotate}


def random_neighbor(problem: Problem, state: State, rng: random.Random) -> tuple[State, Move]:
    kinds, weights = list(KIND_WEIGHTS), list(KIND_WEIGHTS.values())
    for _ in range(MAX_TRIES):
        result = _RANDOM[rng.choices(kinds, weights)[0]](problem, state, rng)
        if result is not None:
            return result
    if len(state):
        return _free_move(problem, state, rng.randrange(len(state)), rng)
    return state, {"type": "none"}
