"""Constraint checker.

Setiap truk diperiksa terpisah dengan operasi matriks numpy (n x n) di atas kotak-kotak
yang ada di dalamnya, jadi biayanya hampir tidak bergantung pada ukuran truk.

Jenis pelanggaran yang dihitung:
  overlap          jumlah pasangan paket yang volumenya saling tumpang-tindih
  out_of_bounds    jumlah paket yang tidak seluruhnya berada di dalam peti kemas
  floating         jumlah paket yang melayang: z > 0 dan tidak ada satu pun paket lain yang
                   sisi atasnya tepat di z paket tersebut dengan luas irisan alas > 0
                   (cukup satu titik alas yang tersangga agar tidak dihitung melayang)
  fragile_support  jumlah pasangan (pecah-belah j, paket i) dengan i bertumpu langsung di atas j
  overweight       total kelebihan berat di atas max_capacity, dijumlahkan seluruh truk
"""
from __future__ import annotations

import numpy as np

from .models import Problem, State

VIOLATION_KEYS = ("overlap", "out_of_bounds", "floating", "fragile_support", "overweight")


class Report:
    """Hasil pemeriksaan satu State."""
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

        # xy[i, j]: alas i dan alas j beririsan dengan luas > 0
        xy = ((x[:, None] < x2[None, :]) & (x[None, :] < x2[:, None])
              & (y[:, None] < y2[None, :]) & (y[None, :] < y2[:, None]))
        np.fill_diagonal(xy, False)
        zo = (z[:, None] < z2[None, :]) & (z[None, :] < z2[:, None])
        report.overlap += int((xy & zo).sum()) // 2

        # beneath[i, j]: paket j tepat di bawah paket i (i bertumpu pada j)
        beneath = xy & (z2[None, :] == z[:, None])
        report.floating += int(((z > 0) & ~beneath.any(axis=1)).sum())
        frag = np.fromiter((fragile[i] for i in members), dtype=bool, count=len(members))
        if frag.any():
            report.fragile_support += int(beneath[:, frag].sum())
    return report
