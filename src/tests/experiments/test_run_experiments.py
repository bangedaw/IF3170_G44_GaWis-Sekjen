import json

import pytest

from experiments import run_experiments as runner


def config(problem_file, output_dir, **overrides):
    base = {
        "_comment": "diabaikan",
        "name": "uji",
        "output_dir": str(output_dir),
        "problem": str(problem_file),
        "seeds": [1, 2],
        "runs": [
            {"algorithm": "rw", "params": {"steps": 3}},
            {"algorithm": "random_walk", "label": "rw_s{steps}", "grid": {"steps": [1, 4]}, "seeds": [5]},
        ],
    }
    base.update(overrides)
    return base


def test_expand_config(dummy_algorithm, problem_file, tmp_path):
    specs = runner.expand_config(config(problem_file, tmp_path))
    assert [(s.label, s.seed, s.params) for s in specs] == [
        ("random_walk", 1, {"steps": 3}),
        ("random_walk", 2, {"steps": 3}),
        ("rw_s1", 5, {"steps": 1}),
        ("rw_s4", 5, {"steps": 4}),
    ]
    assert specs[0].output_path == tmp_path / "random_walk_1.json"
    assert all(s.algorithm == "random_walk" and s.objective == "default" for s in specs)


def test_default_label_includes_grid_params(dummy_algorithm, problem_file, tmp_path):
    cfg = config(problem_file, tmp_path, runs=[{"algorithm": "rw", "grid": {"steps": [2, 3]}}])
    assert [s.label for s in runner.expand_config(cfg)] == ["random_walk_steps2"] * 2 + ["random_walk_steps3"] * 2


def test_duplicate_output_rejected(dummy_algorithm, problem_file, tmp_path):
    cfg = config(problem_file, tmp_path, runs=[{"algorithm": "rw", "label": "sama", "grid": {"steps": [2, 3]}}])
    with pytest.raises(ValueError, match="file yang sama"):
        runner.expand_config(cfg)


def test_relative_paths_resolve_from_repo_root(dummy_algorithm):
    cfg = {"name": "x", "problem": "src/data/medium.json", "runs": [{"algorithm": "rw"}]}
    specs = runner.expand_config(cfg)
    assert len(specs) == 3
    assert specs[0].output_path == runner.REPO_ROOT / "output" / "x" / "random_walk_1.json"
    assert runner.repo_path(specs[0].problem_file) == runner.REPO_ROOT / "src" / "data" / "medium.json"


def test_main_runs_all_and_skips_existing(dummy_algorithm, problem_file, tmp_path, capsys):
    cfg_path = tmp_path / "cfg.json"
    out = tmp_path / "out"
    cfg_path.write_text(json.dumps(config(problem_file, out)), encoding="utf-8")

    assert runner.main([str(cfg_path), "--dry-run"]) == 0
    assert not out.exists()

    assert runner.main([str(cfg_path)]) == 0
    files = sorted(p.name for p in out.glob("*.json"))
    assert files == ["random_walk_1.json", "random_walk_2.json", "rw_s1_5.json", "rw_s4_5.json"]
    data = json.loads((out / "rw_s4_5.json").read_text(encoding="utf-8"))
    assert data["label"] == "rw_s4" and data["iterations"] == 4 and data["seed"] == 5
    assert data["problem"]["trucks"] and data["problem_file"] == str(problem_file)

    capsys.readouterr()
    assert runner.main([str(cfg_path), "--skip-existing", "--only", "rw_s"]) == 0
    assert capsys.readouterr().out.count("dilewati") == 2


def test_failed_run_does_not_stop_others(dummy_algorithm, problem_file, tmp_path, capsys):
    cfg = config(problem_file, tmp_path / "out", runs=[
        {"algorithm": "rw", "label": "rusak", "params": {"langkah": 3}},
        {"algorithm": "rw", "label": "baik"},
    ])
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    assert runner.main([str(cfg_path)]) == 1
    assert sorted(p.name for p in (tmp_path / "out").glob("*.json")) == ["baik_1.json", "baik_2.json"]
    assert "2 run gagal" in capsys.readouterr().out
