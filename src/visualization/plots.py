"""Plot hasil run. Input berupa RunResult, dict (isi JSON hasil run), atau path file JSON.

Semua fungsi mengembalikan `matplotlib.figure.Figure` (tanpa pyplot, jadi aman dipakai di server atau
Streamlit) dan menyimpan PNG bila `save` diberikan.

    python -m visualization.plots output            # buat semua PNG ke output/plots/
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Callable, Iterable

from matplotlib.figure import Figure

PALETTE = ("#2b6cb0", "#dd6b20", "#2f855a", "#b83280", "#6b46c1", "#718096", "#c05621", "#2c7a7b")
LINE, BAND, MUTED = PALETTE[0], PALETTE[1], "#718096"


def load_run(run) -> dict:
    if isinstance(run, (str, Path)):
        return json.loads(Path(run).read_text(encoding="utf-8"))
    if hasattr(run, "to_dict"):
        return run.to_dict()
    return run


def _name(run: dict) -> str:
    return run.get("label") or run.get("algorithm", "run")


def _title(run: dict) -> str:
    seed = run.get("seed")
    return f"{_name(run)}" + (f" (seed {seed})" if seed is not None else "")


def _finish(fig: Figure, save) -> Figure:
    fig.tight_layout()
    if save is not None:
        path = Path(save)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight")
    return fig


def _style(ax, xlabel: str, ylabel: str) -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def plot_objective(run, save=None, mark_restarts: bool = True) -> Figure:
    """Nilai objective terhadap banyak iterasi yang telah dilewati."""
    run = load_run(run)
    values = run["history"]["objective"]
    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()
    ax.plot(range(len(values)), values, color=LINE, linewidth=1.4)
    if values:
        ax.scatter([0, len(values) - 1], [values[0], values[-1]], color=BAND, zorder=3, s=22)
        ax.annotate(f"awal {values[0]:.1f}", (0, values[0]), textcoords="offset points", xytext=(6, -12),
                    fontsize=8, color=MUTED)
        ax.annotate(f"akhir {values[-1]:.1f}", (len(values) - 1, values[-1]), textcoords="offset points",
                    xytext=(-6, 8), ha="right", fontsize=8, color=MUTED)
    per_restart = run.get("extra", {}).get("iterations_per_restart")
    if mark_restarts and per_restart and len(per_restart) > 1:
        edge = 0
        for count in per_restart[:-1]:
            edge += count
            if 0 < edge < len(values):
                ax.axvline(edge, color=MUTED, linestyle=":", linewidth=1)
    ax.set_title(f"{_title(run)}: objective vs iterasi")
    _style(ax, "Iterasi", "Nilai objective")
    return _finish(fig, save)


def plot_acceptance_prob(run, save=None) -> Figure:
    """e^(dE/T) terhadap banyak iterasi (Simulated Annealing), dengan temperatur pada sumbu kanan."""
    run = load_run(run)
    history = run["history"]
    probs = history.get("acceptance_prob")
    if probs is None:
        raise ValueError(f"{_name(run)} tidak punya history.acceptance_prob (bukan Simulated Annealing?)")
    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()
    ax.plot(range(1, len(probs) + 1), probs, color=LINE, linewidth=0.8, alpha=0.9, label="e^(ΔE/T)")
    ax.axhline(1.0, color=MUTED, linestyle=":", linewidth=1)
    _style(ax, "Iterasi", "e^(ΔE/T)")
    temperature = history.get("temperature")
    if temperature:
        right = ax.twinx()
        right.plot(range(1, len(temperature) + 1), temperature, color=BAND, linestyle="--", linewidth=1.2,
                   label="temperatur")
        right.set_ylabel("Temperatur")
        right.spines["top"].set_visible(False)
    stuck = run.get("extra", {}).get("stuck_count")
    suffix = f", stuck {stuck}x" if stuck is not None else ""
    ax.set_title(f"{_title(run)}: e^(ΔE/T) vs iterasi{suffix}")
    return _finish(fig, save)


def plot_ga(run, save=None) -> Figure:
    """Objective maksimum dan rata-rata populasi terhadap generasi (Genetic Algorithm)."""
    run = load_run(run)
    history = run["history"]
    if "max" not in history or "avg" not in history:
        raise ValueError(f"{_name(run)} tidak punya history.max/avg (bukan Genetic Algorithm?)")
    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()
    ax.plot(range(len(history["max"])), history["max"], color=LINE, linewidth=1.6, label="maksimum")
    ax.plot(range(len(history["avg"])), history["avg"], color=BAND, linewidth=1.4, label="rata-rata")
    extra = run.get("extra", {})
    detail = ", ".join(f"{label} {extra[key]}" for key, label in
                       (("population_size", "populasi"), ("generations", "generasi")) if key in extra)
    ax.set_title(f"{_title(run)}: objective populasi" + (f" ({detail})" if detail else ""))
    ax.legend(frameon=False)
    _style(ax, "Iterasi (generasi)", "Nilai objective")
    return _finish(fig, save)


def plot_compare(runs: Iterable, group_by: Callable[[dict], str] = _name, save=None) -> Figure:
    """Perbandingan nilai akhir dan durasi antar-kelompok run (mis. varian algoritma atau konfigurasi)."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for run in map(load_run, runs):
        groups[group_by(run)].append(run)
    if not groups:
        raise ValueError("tidak ada run untuk dibandingkan")
    names = list(groups)
    fig = Figure(figsize=(max(7, 1.3 * len(names) + 3), 4.2))
    panels = fig.subplots(1, 2)
    for ax, (key, title, ylabel) in zip(panels, (("final_objective", "Nilai objective akhir", "Objective"),
                                                  ("duration_sec", "Durasi pencarian", "Detik"))):
        series = [[r[key] for r in groups[name]] for name in names]
        ax.bar(range(len(names)), [mean(s) for s in series], yerr=[pstdev(s) if len(s) > 1 else 0 for s in series],
               color=[PALETTE[i % len(PALETTE)] for i in range(len(names))], alpha=0.75, capsize=4)
        for x, s in enumerate(series):
            ax.scatter([x] * len(s), s, color="black", s=12, zorder=3)
        ax.set_xticks(range(len(names)), names, rotation=30, ha="right", fontsize=8)
        ax.set_title(title)
        _style(ax, "", ylabel)
    return _finish(fig, save)


def _is_run(data) -> bool:
    return isinstance(data, dict) and "algorithm" in data and "history" in data and "final_state" in data


def generate_plots(output_dir, plots_dir=None) -> list[Path]:
    """Buat PNG untuk semua file hasil run di `output_dir` (rekursif) ke `plots_dir` (default output/plots)."""
    output_dir = Path(output_dir)
    plots_dir = Path(plots_dir) if plots_dir else output_dir / "plots"
    written, by_folder = [], defaultdict(list)

    def emit(figure_fn, run, path):
        figure_fn(run, save=path)
        written.append(path)

    for path in sorted(output_dir.rglob("*.json")):
        if plots_dir in path.parents:
            continue
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not _is_run(run):
            continue
        folder = plots_dir / path.parent.relative_to(output_dir)
        by_folder[folder].append(run)
        history = run["history"]
        if "max" in history and "avg" in history:
            emit(plot_ga, run, folder / f"{path.stem}_ga.png")
        else:
            emit(plot_objective, run, folder / f"{path.stem}_objective.png")
        if "acceptance_prob" in history:
            emit(plot_acceptance_prob, run, folder / f"{path.stem}_acceptance.png")
    for folder, runs in by_folder.items():
        if len(runs) > 1:
            plot_compare(runs, save=folder / "compare.png")
            written.append(folder / "compare.png")
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Buat PNG plot dari semua hasil run di sebuah folder.")
    parser.add_argument("output_dir", help="folder berisi JSON hasil run (rekursif)")
    parser.add_argument("--out", help="folder tujuan PNG (default: <output_dir>/plots)")
    args = parser.parse_args(argv)
    for path in generate_plots(args.output_dir, args.out):
        print(path)


if __name__ == "__main__":
    main()
