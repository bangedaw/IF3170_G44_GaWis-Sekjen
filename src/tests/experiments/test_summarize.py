import csv
import json

import pytest

from experiments import run_experiments as runner
from experiments import summarize


@pytest.fixture
def output_dir(dummy_algorithm, problem_file, tmp_path):
    raw, problem = runner.load_problem_file(problem_file)
    out = tmp_path / "output"
    for steps in (2, 6):
        for seed in (1, 2, 3):
            result = runner.execute("rw", problem, raw, "problem.json", seed=seed,
                                    params={"steps": steps}, label=f"rw_s{steps}")
            result.save(out / "exp" / f"rw_s{steps}_{seed}.json")
    (out / "bukan_run.json").write_text('{"halo": 1}', encoding="utf-8")
    return out


def test_summarize_per_run_and_per_config(output_dir):
    rows, groups = summarize.summarize(output_dir)
    assert len(rows) == 6
    assert {r["experiment"] for r in rows} == {"exp"}
    assert len(groups) == 2

    group = next(g for g in groups if g["label"] == "rw_s6")
    finals = [r["final_objective"] for r in rows if r["label"] == "rw_s6"]
    assert group["runs"] == 3
    assert group["final_objective_mean"] == pytest.approx(sum(finals) / 3)
    assert group["final_objective_max"] == max(finals)
    assert group["iterations_mean"] == 6 and group["iterations_std"] == 0

    with (output_dir / "summary.csv").open(encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == 6
    with (output_dir / "summary_by_config.csv").open(encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == 2
    md = (output_dir / "summary.md").read_text(encoding="utf-8")
    assert "## Per konfigurasi" in md and "rw_s2" in md


def test_value_per_truck_column(output_dir):
    rows, _ = summarize.summarize(output_dir)
    assert all(len(json.loads(r["value_per_truck"])) == 2 for r in rows)


def test_main(output_dir, capsys):
    assert summarize.main(["--output-dir", str(output_dir)]) == 0
    assert "6 run, 2 konfigurasi" in capsys.readouterr().out
