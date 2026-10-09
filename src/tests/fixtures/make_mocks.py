from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURES.parents[1]))

from algorithms.base import RunResult

AXES = "xyz"
ORIENTATIONS = ("xyz", "yxz", "xzy", "zyx", "yzx", "zxy")
VIOLATION_PENALTY = 100
OVERWEIGHT_PENALTY = 10


def effective_dims(package: dict, orientation: str) -> list[int]:
    dims = [0, 0, 0]
    for side, axis in zip("wlh", orientation):
        dims[AXES.index(axis)] = package["dimensions"][side]
    return dims


def truck_size(truck: dict) -> list[int]:
    return [truck["dimensions"][s] for s in "wlh"]


def make_problem(rng: random.Random, trucks: list[dict], n_packages: int) -> dict:
    packages = [
        {
            "id": f"P{i + 1:02d}",
            "dimensions": {"w": rng.randint(2, 5), "l": rng.randint(2, 6), "h": rng.randint(1, 3)},
            "value": rng.randint(10, 100),
            "weight": rng.randint(10, 70),
            "is_fragile": rng.random() < 0.2,
            "eta": rng.randint(1, 7),
        }
        for i in range(n_packages)
    ]
    assert sum(p["weight"] for p in packages) > sum(t["max_capacity"] for t in trucks)
    return {"trucks": trucks, "packages": packages}


def _box(package: dict, truck: int, pos, orientation: str) -> dict:
    return {"truck": truck, "x": pos[0], "y": pos[1], "z": pos[2],
            "orientation": orientation, "dims": effective_dims(package, orientation)}


def _overlap_1d(a0, a1, b0, b1) -> bool:
    return a0 < b1 and b0 < a1


def _overlaps(a: dict, b: dict) -> bool:
    return all(_overlap_1d(a[k], a[k] + a["dims"][i], b[k], b[k] + b["dims"][i]) for i, k in enumerate("xyz"))


def _rests_on(upper: dict, lower: dict) -> bool:
    return lower["z"] + lower["dims"][2] == upper["z"] and all(
        _overlap_1d(upper[k], upper[k] + upper["dims"][i], lower[k], lower[k] + lower["dims"][i])
        for i, k in enumerate("xy")
    )


def _inside(box: dict, size: list[int]) -> bool:
    return all(box[k] >= 0 and box[k] + box["dims"][i] <= size[i] for i, k in enumerate("xyz"))


def random_state(problem: dict, rng: random.Random, p_inside: float = 0.8) -> dict:
    placements = {}
    for p in problem["packages"]:
        placements[p["id"]] = {"truck": None, "orientation": "xyz"}
        if rng.random() >= p_inside:
            continue
        t = rng.randrange(len(problem["trucks"]))
        size = truck_size(problem["trucks"][t])
        orientation = rng.choice(ORIENTATIONS)
        dims = effective_dims(p, orientation)
        if any(d > s for d, s in zip(dims, size)):
            continue
        z = 0 if rng.random() < 0.5 else rng.randint(0, size[2] - dims[2])
        pos = (rng.randint(0, size[0] - dims[0]), rng.randint(0, size[1] - dims[1]), z)
        placements[p["id"]] = _box(p, t, pos, orientation)
    return {"placements": placements}


def pack(problem: dict) -> dict:
    packages = {p["id"]: p for p in problem["packages"]}
    placements = {pid: {"truck": None, "orientation": "xyz"} for pid in packages}
    placed = [[] for _ in problem["trucks"]]
    points = [{(0, 0, 0)} for _ in problem["trucks"]]
    load = [0] * len(problem["trucks"])

    for p in sorted(packages.values(), key=lambda p: p["value"] / p["weight"], reverse=True):
        for t, truck in enumerate(problem["trucks"]):
            if load[t] + p["weight"] > truck["max_capacity"]:
                continue
            box = _first_fit(p, t, truck, placed[t], points[t], packages)
            if box is None:
                continue
            placements[p["id"]] = box
            placed[t].append((p["id"], box))
            load[t] += p["weight"]
            dx, dy, dz = box["dims"]
            points[t] |= {(box["x"] + dx, box["y"], box["z"]), (box["x"], box["y"] + dy, box["z"])}
            if not p["is_fragile"]:
                points[t].add((box["x"], box["y"], box["z"] + dz))
            break
    return {"placements": placements}


def _first_fit(package, t, truck, placed, points, packages):
    size = truck_size(truck)
    for x, y, z in sorted(points, key=lambda pt: (pt[2], pt[1], pt[0])):
        for orientation in ("xyz", "yxz"):
            box = _box(package, t, (x, y, z), orientation)
            if not _inside(box, size) or any(_overlaps(box, other) for _, other in placed):
                continue
            below = [pid for pid, other in placed if _rests_on(box, other)]
            if z > 0 and (not below or any(packages[pid]["is_fragile"] for pid in below)):
                continue
            return box
    return None


def evaluate(problem: dict, state: dict) -> dict:
    packages = {p["id"]: p for p in problem["packages"]}
    violations = dict.fromkeys(("overlap", "out_of_bounds", "floating", "fragile_support", "overweight"), 0)
    value_per_truck = []
    for t, truck in enumerate(problem["trucks"]):
        boxes = [(pid, pl) for pid, pl in state["placements"].items() if pl["truck"] == t]
        size = truck_size(truck)
        for i, (pid, box) in enumerate(boxes):
            violations["out_of_bounds"] += not _inside(box, size)
            below = [other_id for other_id, other in boxes if other is not box and _rests_on(box, other)]
            violations["floating"] += box["z"] > 0 and not below
            violations["fragile_support"] += sum(packages[other_id]["is_fragile"] for other_id in below)
            violations["overlap"] += sum(_overlaps(box, other) for _, other in boxes[i + 1:])
        violations["overweight"] += max(0, sum(packages[pid]["weight"] for pid, _ in boxes) - truck["max_capacity"])
        value_per_truck.append(sum(packages[pid]["value"] for pid, _ in boxes))

    count = sum(v for k, v in violations.items() if k != "overweight")
    value = sum(value_per_truck)
    return {
        "objective": float(value - VIOLATION_PENALTY * count - OVERWEIGHT_PENALTY * violations["overweight"]),
        "value": float(value),
        "feasible": count == 0 and violations["overweight"] == 0,
        "violations": violations,
        "value_per_truck": value_per_truck,
    }


def climb_curve(rng: random.Random, start: float, end: float, steps: int) -> list[float]:
    inner = sorted(rng.uniform(start, end) for _ in range(steps - 1))
    return [round(v, 2) for v in (start, *inner, end)]


def stuck_events(history: list[float], patience: int) -> list[int]:
    events, streak = [], 0
    for i in range(1, len(history)):
        streak = 0 if history[i] > history[i - 1] else streak + 1
        if streak >= patience:
            events.append(i - 1)
            streak = 0
    return events


def sa_history(rng, start, end, t0, cooling, n):
    temps = [t0 * cooling ** k for k in range(n)]
    span = 1 - math.exp(-6)
    objective = [start]
    for k in range(1, n):
        target = start + (end - start) * (1 - math.exp(-6 * k / n)) / span
        objective.append(round(target + rng.gauss(0, 1) * 250 * temps[k] / t0))
    objective.append(end)
    acceptance = [1.0 if rng.random() < 0.45 else round(math.exp(-abs(rng.gauss(0, 60)) / t), 4) for t in temps]
    return objective, acceptance, [round(t, 4) for t in temps]


def result(algorithm, problem, problem_file, initial, final, params, duration, history, extra, iterations=None):
    ev0, ev1 = evaluate(problem, initial), evaluate(problem, final)
    return RunResult(
        algorithm=algorithm,
        label=algorithm,
        problem=problem,
        problem_file=problem_file,
        seed=1,
        params=params,
        initial_state=initial,
        initial_objective=ev0["objective"],
        initial_value=ev0["value"],
        initial_feasible=ev0["feasible"],
        initial_violations=ev0["violations"],
        final_state=final,
        final_objective=ev1["objective"],
        final_value=ev1["value"],
        feasible=ev1["feasible"],
        final_violations=ev1["violations"],
        duration_sec=duration,
        iterations=len(history["objective"]) - 1 if iterations is None else iterations,
        history=history,
        extra={**extra, "value_per_truck": ev1["value_per_truck"]},
    )


def build_mocks() -> dict[str, dict | RunResult]:
    rng = random.Random(2026)
    single = make_problem(rng, [{"id": "T1", "dimensions": {"w": 10, "l": 20, "h": 5}, "max_capacity": 500}], 16)
    multi = make_problem(rng, [
        {"id": "T1", "dimensions": {"w": 10, "l": 20, "h": 5}, "max_capacity": 400},
        {"id": "T2", "dimensions": {"w": 8, "l": 12, "h": 4}, "max_capacity": 250},
    ], 24)
    single_file = "src/tests/fixtures/mock_problem.json"
    multi_file = "src/tests/fixtures/mock_problem_multi_truck.json"

    initial, final = random_state(single, rng), pack(single)
    start, end = evaluate(single, initial)["objective"], evaluate(single, final)["objective"]
    mocks: dict[str, dict | RunResult] = {"mock_problem": single, "mock_problem_multi_truck": multi}

    mocks["mock_steepest_ascent_hc"] = result(
        "steepest_ascent_hc", single, single_file, initial, final,
        {"neighbor_limit": None, "max_iterations": None}, 2.41,
        {"objective": climb_curve(rng, start, end, 18)},
        {"stop_reason": "local_optimum", "evaluations": 18 * 140},
    )

    curve = climb_curve(rng, start, end, 16)
    for pos in sorted(rng.sample(range(8, 16), 6), reverse=True):
        curve.insert(pos, curve[pos])
    mocks["mock_sideways_move_hc"] = result(
        "sideways_move_hc", single, single_file, initial, final,
        {"max_sideways": 10, "neighbor_limit": None, "max_iterations": None}, 3.05,
        {"objective": curve},
        {"max_sideways": 10, "sideways_used": 6, "stop_reason": "local_optimum", "evaluations": 21 * 140},
    )

    starts = [start] + [evaluate(single, random_state(single, rng))["objective"] for _ in range(4)]
    ends = [round(end - rng.uniform(40, 200), 2) for _ in range(5)]
    ends[2] = end
    steps = [rng.randint(10, 20) for _ in range(5)]
    history = [v for s, e, n in zip(starts, ends, steps) for v in climb_curve(rng, s, e, n)]
    mocks["mock_random_restart_hc"] = result(
        "random_restart_hc", single, single_file, initial, final,
        {"max_restart": 4, "base_algorithm": "steepest_ascent_hc", "base_params": {}}, 11.73,
        {"objective": history},
        {"max_restart": 4, "restarts": 4, "iterations_per_restart": steps, "objective_per_restart": ends,
         "best_restart": 2, "stop_reason": "max_restart", "evaluations": sum(steps) * 140},
        iterations=sum(steps),
    )

    mocks["mock_simulated_annealing"] = sa_result(rng, single, single_file, initial, final, n=3000, duration=1.92)

    generations, population = 60, 30
    best = climb_curve(rng, start, end, generations)
    avg = [round(b - 400 * math.exp(-3 * g / generations) - abs(rng.gauss(0, 15)), 2)
           for g, b in enumerate(best)]
    mocks["mock_genetic_algorithm"] = result(
        "genetic_algorithm", single, single_file, initial, final,
        {"population_size": population, "generations": generations}, 6.58,
        {"objective": best, "max": best, "avg": avg},
        {"population_size": population, "generations": generations, "evaluations": population * (generations + 1)},
    )

    multi_initial, multi_final = random_state(multi, rng), pack(multi)
    mocks["mock_multi_truck_simulated_annealing"] = sa_result(
        rng, multi, multi_file, multi_initial, multi_final, n=2000, duration=2.37)
    return mocks


def sa_result(rng, problem, problem_file, initial, final, n, duration):
    t0, cooling, patience = 1000.0, 0.997, 50
    start, end = evaluate(problem, initial)["objective"], evaluate(problem, final)["objective"]
    objective, acceptance, temperature = sa_history(rng, start, end, t0, cooling, n)
    stuck = stuck_events(objective, patience)
    return result(
        "simulated_annealing", problem, problem_file, initial, final,
        {"t0": t0, "cooling": cooling, "t_min": 0.001, "max_iterations": n,
         "stuck_patience": patience, "return_best": False}, duration,
        {"objective": objective, "acceptance_prob": acceptance, "temperature": temperature},
        {"stuck_count": len(stuck),
         "stuck_definition": f"Satu kejadian 'stuck' dihitung setiap kali {patience} iterasi berturut-turut "
                             "berlalu tanpa satu pun move uphill yang diterima (mock).",
         "stuck_iterations": stuck,
         "accepted_moves": round(n * 0.62),
         "accepted_worse_moves": round(n * 0.21),
         "best_objective_seen": max(objective),
         "stop_reason": "max_iterations",
         "evaluations": n + 1},
    )


def main() -> None:
    for name, mock in build_mocks().items():
        path = FIXTURES / f"{name}.json"
        if isinstance(mock, RunResult):
            mock.save(path)
        else:
            path.write_text(json.dumps(mock, indent=2) + "\n", encoding="utf-8")
        print(f"ditulis: {path}")


if __name__ == "__main__":
    main()
