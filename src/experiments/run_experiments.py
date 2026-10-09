from __future__ import annotations

import argparse
import itertools
import json
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from algorithms import registry
from algorithms.base import RunResult, load_core

DEFAULT_SEEDS = [1, 2, 3]


def repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else REPO_ROOT / path


def load_problem_file(path: str | Path) -> tuple[dict, object]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return raw, load_core().load_problem(str(path))


def execute(
    algorithm: str,
    problem,
    raw_problem: dict,
    problem_file: str,
    objective: str = "default",
    seed: int | None = None,
    params: dict | None = None,
    label: str | None = None,
) -> RunResult:
    result = registry.create(algorithm, problem, objective=objective, seed=seed, params=params).run()
    result.label = label or result.algorithm
    result.problem = raw_problem
    result.problem_file = problem_file
    return result


@dataclass
class RunSpec:
    algorithm: str
    label: str
    problem_file: str
    objective: str
    seed: int | None
    params: dict = field(default_factory=dict)
    output_path: Path = Path()


def _strip_comments(obj):
    if isinstance(obj, dict):
        return {k: _strip_comments(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_comments(v) for v in obj]
    return obj


def expand_config(config: dict) -> list[RunSpec]:
    config = _strip_comments(config)
    specs = []
    for entry in config["runs"]:
        algorithm = registry.canonical_name(entry["algorithm"])
        problem_file = entry.get("problem", config.get("problem"))
        if problem_file is None:
            raise ValueError(f"Run {algorithm} tidak punya 'problem'")
        objective = entry.get("objective", config.get("objective", "default"))
        seeds = entry.get("seeds", config.get("seeds", DEFAULT_SEEDS))
        output_dir = repo_path(entry.get("output_dir", config.get("output_dir", f"output/{config['name']}")))
        grid = entry.get("grid", {})
        template = entry.get("label") or algorithm + "".join(f"_{k}{{{k}}}" for k in grid)

        for combo in itertools.product(*grid.values()):
            params = {**entry.get("params", {}), **dict(zip(grid, combo))}
            label = template.format(**params, algorithm=algorithm, objective=objective)
            for seed in seeds:
                specs.append(RunSpec(
                    algorithm=algorithm,
                    label=label,
                    problem_file=problem_file,
                    objective=objective,
                    seed=seed,
                    params=params,
                    output_path=output_dir / f"{label}_{seed}.json",
                ))

    seen = set()
    for spec in specs:
        if spec.output_path in seen:
            raise ValueError(f"Dua run menulis ke file yang sama: {spec.output_path}. Bedakan 'label'-nya.")
        seen.add(spec.output_path)
    return specs


def load_config(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _display(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jalankan set eksperimen dari file konfigurasi.")
    parser.add_argument("configs", nargs="+", help="file konfigurasi JSON (src/experiments/configs/*.json)")
    parser.add_argument("--dry-run", action="store_true", help="tampilkan daftar run tanpa menjalankannya")
    parser.add_argument("--skip-existing", action="store_true", help="lewati run yang file hasilnya sudah ada")
    parser.add_argument("--only", metavar="TEKS", help="hanya jalankan run yang label-nya memuat TEKS")
    args = parser.parse_args(argv)

    specs = [spec for path in args.configs for spec in expand_config(load_config(path))]
    if args.only:
        specs = [s for s in specs if args.only in s.label]

    problems: dict[str, tuple[dict, object]] = {}
    failures = []
    for i, spec in enumerate(specs, 1):
        head = f"[{i}/{len(specs)}] {spec.label} seed={spec.seed}"
        if args.dry_run:
            print(f"{head} -> {_display(spec.output_path)}")
            continue
        if args.skip_existing and spec.output_path.exists():
            print(f"{head} dilewati (sudah ada)")
            continue
        try:
            if spec.problem_file not in problems:
                problems[spec.problem_file] = load_problem_file(repo_path(spec.problem_file))
            raw, problem = problems[spec.problem_file]
            result = execute(spec.algorithm, problem, raw, spec.problem_file, spec.objective,
                             spec.seed, spec.params, spec.label)
            result.save(spec.output_path)
        except Exception:
            failures.append(head)
            print(f"{head} GAGAL")
            traceback.print_exc()
            continue
        print(f"{head} obj={result.final_objective:.2f} value={result.final_value:.2f} "
              f"feasible={result.feasible} iter={result.iterations} "
              f"{result.duration_sec:.2f}s -> {_display(spec.output_path)}")

    if failures:
        print(f"\n{len(failures)} run gagal:\n  " + "\n  ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
