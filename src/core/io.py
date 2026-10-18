from __future__ import annotations

import json
from pathlib import Path

from .models import Package, Placement, Problem, State, Truck
from .orientation import ORIENTATIONS


def _int(value, what: str) -> int:
    if isinstance(value, bool) or int(value) != value:
        raise ValueError(f"{what} harus bilangan bulat, bukan {value!r}")
    return int(value)


def _positive_dims(raw: dict, what: str) -> tuple[int, int, int]:
    dims = tuple(_int(raw[k], f"{what}.{k}") for k in ("w", "l", "h"))
    if min(dims) <= 0:
        raise ValueError(f"dimensi {what} harus positif: {dims}")
    return dims


def problem_from_dict(raw: dict) -> Problem:
    trucks = []
    for t in raw["trucks"]:
        w, l, h = _positive_dims(t["dimensions"], f"truk {t['id']}")
        trucks.append(Truck(str(t["id"]), w, l, h, t["max_capacity"]))
    packages = []
    for p in raw["packages"]:
        w, l, h = _positive_dims(p["dimensions"], f"paket {p['id']}")
        packages.append(Package(str(p["id"]), w, l, h, p["value"], p["weight"],
                                bool(p.get("is_fragile", False)), _int(p.get("eta", 0), f"eta {p['id']}")))
    return Problem(tuple(trucks), tuple(packages))


def problem_to_dict(problem: Problem) -> dict:
    return {
        "trucks": [{"id": t.id, "dimensions": {"w": t.w, "l": t.l, "h": t.h}, "max_capacity": t.max_capacity}
                   for t in problem.trucks],
        "packages": [{"id": p.id, "dimensions": {"w": p.w, "l": p.l, "h": p.h}, "value": p.value,
                      "weight": p.weight, "is_fragile": p.is_fragile, "eta": p.eta}
                     for p in problem.packages],
    }


def load_problem(path) -> Problem:
    return problem_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def state_to_dict(state: State) -> dict:
    placements = {}
    for pid, p in zip(state.ids, state.placements):
        if p.truck is None:
            placements[pid] = {"truck": None, "orientation": p.orientation, "dims": list(p.dims)}
        else:
            placements[pid] = {"truck": p.truck, "x": p.x, "y": p.y, "z": p.z,
                               "orientation": p.orientation, "dims": list(p.dims)}
    return {"placements": placements}


def state_from_dict(data: dict, problem: Problem | None = None) -> State:
    raw = data["placements"]
    ids = problem.ids if problem is not None else tuple(raw)
    placements = []
    for index, pid in enumerate(ids):
        d = raw[pid]
        orientation = d.get("orientation", "xyz")
        if orientation not in ORIENTATIONS:
            raise ValueError(f"orientasi tidak valid untuk {pid}: {orientation!r}")
        if problem is not None:
            if d["truck"] is None:
                placements.append(problem.outside(index, orientation))
            else:
                placements.append(problem.place(index, d["truck"], d["x"], d["y"], d["z"], orientation))
            continue
        dims = tuple(int(v) for v in d.get("dims", (0, 0, 0)))
        if d["truck"] is None:
            placements.append(Placement(None, 0, 0, 0, orientation, dims))
        else:
            placements.append(Placement(int(d["truck"]), int(d["x"]), int(d["y"]), int(d["z"]), orientation, dims))
    return State(tuple(ids), tuple(placements))
