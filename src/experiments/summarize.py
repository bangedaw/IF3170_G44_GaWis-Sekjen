from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

RUN_COLUMNS = [
    "experiment", "file", "label", "algorithm", "objective_name", "problem_file", "seed", "params",
    "initial_objective", "final_objective", "final_value", "feasible", "iterations", "duration_sec",
    "restarts", "max_restart", "sideways_used", "max_sideways", "stuck_count",
    "population_size", "generations", "value_per_truck",
]
GROUP_KEYS = ["experiment", "label", "algorithm", "objective_name", "problem_file", "params"]
METRICS = ["final_objective", "final_value", "iterations", "duration_sec"]


def load_runs(output_dir: Path) -> list[tuple[Path, dict]]:
    runs = []
    for path in sorted(output_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and "algorithm" in data and "final_objective" in data:
            runs.append((path, data))
    return runs


def run_row(path: Path, run: dict, output_dir: Path) -> dict:
    extra, params = run.get("extra", {}), run.get("params", {})
    rel = path.relative_to(output_dir)
    row = {
        "experiment": rel.parent.as_posix() if rel.parent != Path(".") else "",
        "file": rel.as_posix(),
        "label": run.get("label") or run["algorithm"],
        "params": json.dumps(params, sort_keys=True),
        "population_size": extra.get("population_size", params.get("population_size")),
        "generations": extra.get("generations", params.get("generations")),
        "value_per_truck": json.dumps(extra["value_per_truck"]) if "value_per_truck" in extra else None,
    }
    for key in ("algorithm", "objective_name", "problem_file", "seed", "initial_objective",
                "final_objective", "final_value", "feasible", "iterations", "duration_sec"):
        row[key] = run.get(key)
    for key in ("restarts", "max_restart", "sideways_used", "max_sideways", "stuck_count"):
        row[key] = extra.get(key)
    return row


def group_rows(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        groups.setdefault(tuple(row[k] for k in GROUP_KEYS), []).append(row)
    summary = []
    for key, members in groups.items():
        agg = dict(zip(GROUP_KEYS, key))
        agg["runs"] = len(members)
        agg["feasible_rate"] = sum(bool(m["feasible"]) for m in members) / len(members)
        agg["final_objective_max"] = max(float(m["final_objective"]) for m in members)
        for metric in METRICS:
            values = [float(m[metric]) for m in members if m[metric] is not None]
            agg[f"{metric}_mean"] = statistics.fmean(values) if values else None
            agg[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
        summary.append(agg)
    return summary


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}" if abs(value) < 1 else f"{value:.2f}"
    return str(value).replace("|", "\\|")


def markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    lines += ["| " + " | ".join(_fmt(row.get(c)) for c in columns) + " |" for row in rows]
    return "\n".join(lines)


def summarize(output_dir: Path) -> tuple[list[dict], list[dict]]:
    rows = [run_row(path, run, output_dir) for path, run in load_runs(output_dir)]
    rows.sort(key=lambda r: (r["experiment"], r["label"], str(r["seed"])))
    groups = group_rows(rows)

    group_columns = GROUP_KEYS + ["runs", "feasible_rate", "final_objective_max"] + [
        f"{m}_{s}" for m in METRICS for s in ("mean", "std")
    ]
    write_csv(output_dir / "summary.csv", rows, RUN_COLUMNS)
    write_csv(output_dir / "summary_by_config.csv", groups, group_columns)
    md_run_columns = [c for c in RUN_COLUMNS if c not in ("params", "problem_file")]
    md_group_columns = [c for c in group_columns if c not in ("params", "problem_file")]
    (output_dir / "summary.md").write_text(
        "# Rekap Hasil Eksperimen\n\n"
        "## Per konfigurasi\n\n" + markdown_table(groups, md_group_columns) + "\n\n"
        "## Per run\n\n" + markdown_table(rows, md_run_columns) + "\n",
        encoding="utf-8",
    )
    return rows, groups


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rekap hasil run di folder output.")
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "output"))
    args = parser.parse_args(argv)
    output_dir = Path(args.output_dir)
    rows, groups = summarize(output_dir)
    print(f"{len(rows)} run, {len(groups)} konfigurasi -> {output_dir / 'summary.csv'}, "
          f"{output_dir / 'summary_by_config.csv'}, {output_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
