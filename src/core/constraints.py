from __future__ import annotations

import numpy as np

from .models import Problem, State

VIOLATION_KEYS = ("overlap", "out_of_bounds", "floating", "fragile_support", "overweight")


class Report:
    __slots__ = ("overlap", "out_of_bounds", "floating", "fragile_support", "overweight",
                 "overweight_trucks", "weight_per_truck", "inside")

    def __init__(self, n_trucks: int):
        self.overlap = self.out_of_bounds = self.floating = self.fragile_support = 0
        self.overweight = 0
        self.overweight_trucks = 0
        self.weight_per_truck = [0] * n_trucks
        self.inside: list[list[int]] = [[] for _ in range(n_trucks)]

    @property
    def violations(self) -> dict:
        return {key: getattr(self, key) for key in VIOLATION_KEYS}

    @property
    def feasible(self) -> bool:
        return not (self.overlap or self.out_of_bounds or self.floating
                    or self.fragile_support or self.overweight)


def check_state(problem: Problem, state: State) -> Report:
    report = Report(len(problem.trucks))
    placements = state.placements
    for i, p in enumerate(placements):
        if p.truck is not None:
            report.inside[p.truck].append(i)

    weights, fragile = problem.weights, problem.fragile
    for t, members in enumerate(report.inside):
        if not members:
            continue
        truck = problem.trucks[t]
        load = sum(weights[i] for i in members)
        report.weight_per_truck[t] = load
        if load > truck.max_capacity:
            report.overweight += load - truck.max_capacity
            report.overweight_trucks += 1

        boxes = np.array([(p.x, p.y, p.z, *p.dims) for p in (placements[i] for i in members)], dtype=np.int64)
        x, y, z, dx, dy, dz = boxes.T
        x2, y2, z2 = x + dx, y + dy, z + dz

        report.out_of_bounds += int(((x < 0) | (y < 0) | (z < 0)
                                     | (x2 > truck.w) | (y2 > truck.l) | (z2 > truck.h)).sum())
        if len(members) == 1:
            if z[0] > 0:
                report.floating += 1
            continue

        xy = ((x[:, None] < x2[None, :]) & (x[None, :] < x2[:, None])
              & (y[:, None] < y2[None, :]) & (y[None, :] < y2[:, None]))
        np.fill_diagonal(xy, False)
        zo = (z[:, None] < z2[None, :]) & (z[None, :] < z2[:, None])
        report.overlap += int((xy & zo).sum()) // 2

        beneath = xy & (z2[None, :] == z[:, None])
        report.floating += int(((z > 0) & ~beneath.any(axis=1)).sum())
        frag = np.fromiter((fragile[i] for i in members), dtype=bool, count=len(members))
        if frag.any():
            report.fragile_support += int(beneath[:, frag].sum())
    return report
