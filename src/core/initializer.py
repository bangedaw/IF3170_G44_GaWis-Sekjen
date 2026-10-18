from __future__ import annotations

import random

from .candidates import TruckBoxes, candidate_positions
from .models import Problem, State
from .orientation import ORIENTATIONS

DEFAULT_P_INSIDE = 0.5


def random_state(problem: Problem, rng: random.Random, mode: str = "feasible",
                 p_inside: float = DEFAULT_P_INSIDE) -> State:
    if mode not in ("feasible", "uniform"):
        raise ValueError(f"mode harus 'feasible' atau 'uniform', bukan {mode!r}")
    placements = [problem.outside(i, rng.choice(ORIENTATIONS)) for i in range(len(problem.packages))]
    order = list(range(len(placements)))
    rng.shuffle(order)
    trucks = range(len(problem.trucks))

    for i in order:
        if rng.random() >= p_inside:
            continue
        pkg, dims, orientation = problem.packages[i], placements[i].dims, placements[i].orientation
        if mode == "uniform":
            t = rng.choice(trucks)
            truck = problem.trucks[t]
            x, y, z = (rng.randint(0, max(0, lim - d)) for lim, d in zip(truck.dims, dims))
            placements[i] = problem.place(i, t, x, y, z, orientation)
            continue
        for t in rng.sample(trucks, len(trucks)):
            truck = problem.trucks[t]
            load = sum(problem.weights[j] for j, p in enumerate(placements) if p.truck == t)
            if load + pkg.weight > truck.max_capacity:
                continue
            cands = candidate_positions(TruckBoxes(problem, placements, t), truck, dims, pkg.is_fragile)
            if len(cands):
                x, y, z = (int(v) for v in cands[rng.randrange(len(cands))])
                placements[i] = problem.place(i, t, x, y, z, orientation)
                break
    return State(problem.ids, tuple(placements))
