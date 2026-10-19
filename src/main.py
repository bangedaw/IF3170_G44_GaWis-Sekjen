from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from algorithms import registry
from experiments.run_experiments import execute, load_problem_file


def parse_params(params_json: str | None, pairs: list[str]) -> dict:
    params = {}
    if params_json:
        params.update(json.loads(params_json))
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ValueError(f"--param harus berbentuk key=value, bukan '{pair}'")
        try:
            params[key.strip()] = json.loads(value)
        except json.JSONDecodeError:
            params[key.strip()] = value
    return params


def print_algorithms() -> None:
    for name, cls in sorted(registry.algorithms().items()):
        print(f"{name:22} alias: {', '.join(cls.aliases) or '-'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jalankan satu algoritma local search pada satu problem.")
    parser.add_argument("--list", action="store_true", help="tampilkan daftar algoritma lalu keluar")
    parser.add_argument("--problem", help="file problem JSON (format kontrak 3.2)")
    parser.add_argument("--algo", help="nama algoritma atau alias (lihat --list)")
    parser.add_argument("--objective", default="default", help="nama objective function (default | alt)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--params", help="parameter algoritma sebagai JSON")
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                        help="satu parameter algoritma (boleh diulang)")
    parser.add_argument("--label", help="label run (default: nama algoritma)")
    parser.add_argument("--out", help="file .json tujuan, atau folder (disimpan sebagai <label>_<seed>.json)")
    args = parser.parse_args(argv)

    if args.list:
        print_algorithms()
        return 0
    if not args.problem or not args.algo:
        parser.error("--problem dan --algo wajib diisi (atau pakai --list)")

    params = parse_params(args.params, args.param)
    raw, problem = load_problem_file(args.problem)
    result = execute(registry.canonical_name(args.algo), problem, raw, Path(args.problem).as_posix(),
                     args.objective, args.seed, params, args.label)

    print(f"algoritma       : {result.algorithm} (label: {result.label})")
    print(f"objective       : {result.objective_name}, seed {result.seed}")
    print(f"params          : {json.dumps(result.params)}")
    print(f"objective awal  : {result.initial_objective:.4f} (value {result.initial_value:.2f})")
    print(f"objective akhir : {result.final_objective:.4f} (value {result.final_value:.2f}, feasible {result.feasible})")
    print(f"iterasi         : {result.iterations}")
    print(f"durasi          : {result.duration_sec:.3f} s")
    for key in ("stop_reason", "sideways_used", "restarts", "iterations_per_restart", "stuck_count", "value_per_truck"):
        if key in result.extra:
            print(f"{key:16}: {result.extra[key]}")

    if args.out:
        out = Path(args.out)
        if out.suffix.lower() != ".json":
            out = out / f"{result.label}_{result.seed}.json"
        print(f"disimpan ke     : {result.save(out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
