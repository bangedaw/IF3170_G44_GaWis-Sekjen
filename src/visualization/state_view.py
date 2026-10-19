from __future__ import annotations

from pathlib import Path
from typing import Any

from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from core.models import Problem, State, Truck

PALETTE = (
    "#0033A0", "#F2B01E", "#0A8754", "#7B2CBF", "#E8702A",
    "#0096C7", "#D90429", "#588157", "#3A0CA3", "#F77F00",
)
FRAGILE_COLOR = "#D90429"
FRAGILE_EDGE = "#FFD166"
NORMAL_EDGE = "#1E293B"
TRUCK_FRAME_COLOR = "#334155"


def _resolve_problem_and_state(problem_input: Any, state_input: Any) -> tuple[Problem, State]:
    from core.io import load_problem, problem_from_dict, state_from_dict

    if isinstance(problem_input, (str, Path)):
        problem = load_problem(str(problem_input))
    elif isinstance(problem_input, dict):
        problem = problem_from_dict(problem_input)
    else:
        problem = problem_input

    if isinstance(state_input, dict):
        state = state_from_dict(state_input, problem)
    else:
        state = state_input

    return problem, state


def _make_box_faces(x: float, y: float, z: float, dx: float, dy: float, dz: float):
    v = [
        (x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z),
        (x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz),
    ]
    return [
        [v[0], v[1], v[2], v[3]],
        [v[4], v[5], v[6], v[7]],
        [v[0], v[1], v[5], v[4]],
        [v[2], v[3], v[7], v[6]],
        [v[0], v[3], v[7], v[4]],
        [v[1], v[2], v[6], v[5]],
    ]


def state_summary(problem_input: Any, state_input: Any) -> dict[str, Any]:
    from core.objective import evaluate

    problem, state = _resolve_problem_and_state(problem_input, state_input)
    evaluation = evaluate(problem, state)

    packages_by_id = {p.id: p for p in problem.packages}
    truck_stats = []
    inside_packages = []
    outside_packages = []

    for t_idx, truck in enumerate(problem.trucks):
        pkg_indices = [i for i, p in enumerate(state.placements) if p.truck == t_idx]
        cur_weight = float(sum(problem.weights[i] for i in pkg_indices))
        cur_vol = int(sum(problem.volumes[i] for i in pkg_indices))
        truck_val = float(sum(problem.values[i] for i in pkg_indices))
        truck_stats.append({
            "truck_index": t_idx,
            "id": truck.id,
            "dimensions": {"w": truck.w, "l": truck.l, "h": truck.h},
            "volume": truck.volume,
            "max_capacity": float(truck.max_capacity),
            "current_weight": cur_weight,
            "weight_pct": round((cur_weight / truck.max_capacity) * 100, 1) if truck.max_capacity > 0 else 0.0,
            "current_volume": cur_vol,
            "volume_pct": round((cur_vol / truck.volume) * 100, 1) if truck.volume > 0 else 0.0,
            "package_count": len(pkg_indices),
            "value": truck_val,
        })

    for pid, placement in zip(state.ids, state.placements):
        pkg = packages_by_id[pid]
        item: dict[str, Any] = {
            "id": pid,
            "value": float(pkg.value),
            "weight": float(pkg.weight),
            "is_fragile": bool(pkg.is_fragile),
            "eta": int(pkg.eta),
            "orientation": placement.orientation,
            "dims": list(placement.dims),
        }
        if placement.truck is not None:
            item["truck"] = int(placement.truck)
            item["truck_id"] = problem.trucks[placement.truck].id
            item["x"] = int(placement.x)
            item["y"] = int(placement.y)
            item["z"] = int(placement.z)
            inside_packages.append(item)
        else:
            item["truck"] = None
            outside_packages.append(item)

    return {
        "objective": float(evaluation.objective),
        "total_value": float(evaluation.total_value),
        "feasible": bool(evaluation.feasible),
        "violations": dict(evaluation.violations),
        "value_per_truck": list(evaluation.value_per_truck),
        "trucks": truck_stats,
        "inside_packages": inside_packages,
        "outside_packages": outside_packages,
        "total_packages": len(problem.packages),
        "inside_count": len(inside_packages),
        "outside_count": len(outside_packages),
    }


def draw_truck_wireframe(ax, truck: Truck) -> None:
    w, l, h = truck.w, truck.l, truck.h
    edges = [
        ([0, w], [0, 0], [0, 0]), ([w, w], [0, l], [0, 0]),
        ([w, 0], [l, l], [0, 0]), ([0, 0], [l, 0], [0, 0]),
        ([0, w], [0, 0], [h, h]), ([w, w], [0, l], [h, h]),
        ([w, 0], [l, l], [h, h]), ([0, 0], [l, 0], [h, h]),
        ([0, 0], [0, 0], [0, h]), ([w, w], [0, 0], [0, h]),
        ([w, w], [l, l], [0, h]), ([0, 0], [l, l], [0, h]),
    ]
    for xs, ys, zs in edges:
        ax.plot(xs, ys, zs, color=TRUCK_FRAME_COLOR, linewidth=1.5, linestyle="--", alpha=0.8)


def render_truck_3d(ax, truck: Truck, truck_index: int, problem: Problem, state: State,
                    title: str | None = None) -> None:
    draw_truck_wireframe(ax, truck)

    packages_by_id = {p.id: p for p in problem.packages}
    placed = [
        (idx, pid, p)
        for idx, (pid, p) in enumerate(zip(state.ids, state.placements))
        if p.truck == truck_index
    ]

    for color_idx, (_, pid, placement) in enumerate(placed):
        pkg = packages_by_id[pid]
        dx, dy, dz = placement.dims
        faces = _make_box_faces(placement.x, placement.y, placement.z, dx, dy, dz)

        if pkg.is_fragile:
            face_color, edge_color, alpha, edge_width = FRAGILE_COLOR, FRAGILE_EDGE, 0.85, 1.6
        else:
            face_color, edge_color, alpha, edge_width = PALETTE[color_idx % len(PALETTE)], NORMAL_EDGE, 0.70, 1.0

        ax.add_collection3d(
            Poly3DCollection(faces, facecolors=face_color, edgecolors=edge_color,
                             linewidths=edge_width, alpha=alpha)
        )
        cx = placement.x + dx / 2.0
        cy = placement.y + dy / 2.0
        cz = placement.z + dz / 2.0
        ax.text(cx, cy, cz, f"{pid}\n{'[!]' if pkg.is_fragile else ''}v={pkg.value:.0f}",
                color="black", fontsize=7, ha="center", va="center", weight="bold")

    ax.set_xlim(0, max(1, truck.w))
    ax.set_ylim(0, max(1, truck.l))
    ax.set_zlim(0, max(1, truck.h))
    ax.set_xlabel("Width (X)", fontsize=8)
    ax.set_ylabel("Length (Y)", fontsize=8)
    ax.set_zlabel("Height (Z)", fontsize=8)
    ax.set_title(title or f"Truk {truck.id} ({truck.w}x{truck.l}x{truck.h})", fontsize=10, weight="bold")
    ax.view_init(elev=25, azim=-45)


def render_state_figure(problem_input: Any, state_input: Any, truck_index: int | None = None,
                        save: str | Path | None = None, title: str | None = None) -> Figure:
    problem, state = _resolve_problem_and_state(problem_input, state_input)
    summary = state_summary(problem, state)

    trucks_to_draw = (
        [(truck_index, problem.trucks[truck_index])]
        if truck_index is not None
        else list(enumerate(problem.trucks))
    )
    ncols = len(trucks_to_draw)
    fig = Figure(figsize=(max(7, 5 * ncols), 6))

    for col_idx, (t_idx, truck) in enumerate(trucks_to_draw, start=1):
        ax = fig.add_subplot(1, ncols, col_idx, projection="3d")
        t_stat = summary["trucks"][t_idx]
        t_title = (
            f"{truck.id} (Nilai: {t_stat['value']:.0f} | "
            f"Berat: {t_stat['current_weight']:.0f}/{truck.max_capacity:.0f})"
        )
        render_truck_3d(ax, truck, t_idx, problem, state, title=t_title)

    fig.suptitle(
        title or (
            f"State: Value={summary['total_value']:.0f} | Feasible={summary['feasible']} | "
            f"Paket Masuk={summary['inside_count']}/{summary['total_packages']}"
        ),
        fontsize=11, weight="bold",
    )
    fig.tight_layout()

    if save is not None:
        p = Path(save)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=150, bbox_inches="tight")

    return fig


def render_state_comparison(problem_input: Any, initial_state_input: Any, final_state_input: Any,
                            truck_index: int = 0, save: str | Path | None = None,
                            title: str | None = None) -> Figure:
    problem, s_init = _resolve_problem_and_state(problem_input, initial_state_input)
    _, s_final = _resolve_problem_and_state(problem_input, final_state_input)

    truck = problem.trucks[truck_index]
    sum_init = state_summary(problem, s_init)
    sum_final = state_summary(problem, s_final)

    fig = Figure(figsize=(13, 6))
    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2 = fig.add_subplot(1, 2, 2, projection="3d")

    render_truck_3d(ax1, truck, truck_index, problem, s_init,
                    title=f"INITIAL STATE (Nilai: {sum_init['total_value']:.0f}, Feasible: {sum_init['feasible']})")
    render_truck_3d(ax2, truck, truck_index, problem, s_final,
                    title=f"FINAL STATE (Nilai: {sum_final['total_value']:.0f}, Feasible: {sum_final['feasible']})")

    fig.suptitle(title or f"Perbandingan Initial vs Final State (Truk {truck.id})", fontsize=12, weight="bold")
    fig.tight_layout()

    if save is not None:
        p = Path(save)
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=150, bbox_inches="tight")

    return fig


def state_to_3d_data(problem_input: Any, state_input: Any) -> dict[str, Any]:
    problem, state = _resolve_problem_and_state(problem_input, state_input)
    summary = state_summary(problem, state)
    summary["palette"] = list(PALETTE)
    summary["fragile_color"] = FRAGILE_COLOR
    summary["truck_frame_color"] = TRUCK_FRAME_COLOR
    return summary
