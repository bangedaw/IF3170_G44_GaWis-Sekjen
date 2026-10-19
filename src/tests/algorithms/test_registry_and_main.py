import json

import pytest

import main
from algorithms import registry


def test_name_and_alias_resolve(dummy_algorithm):
    assert registry.get_algorithm("random_walk") is dummy_algorithm
    assert registry.get_algorithm("RW") is dummy_algorithm
    assert registry.canonical_name("random-walk") == "random_walk"


def test_unknown_algorithm(dummy_algorithm):
    with pytest.raises(KeyError, match="tidak dikenal"):
        registry.get_algorithm("tabu_search")


def test_create_passes_params(dummy_algorithm, knapsack):
    algo = registry.create("rw", knapsack, objective="alt", seed=4, params={"steps": 2})
    assert algo.params == {"steps": 2} and algo.seed == 4 and algo.objective_name == "alt"


def test_parse_params_combines_json_and_pairs():
    params = main.parse_params('{"t0": 100, "cooling": 0.9}', ["cooling=0.95", "return_best=true", "mode=random"])
    assert params == {"t0": 100, "cooling": 0.95, "return_best": True, "mode": "random"}


def test_cli_runs_and_saves(dummy_algorithm, problem_file, tmp_path, capsys):
    out_dir = tmp_path / "out"
    code = main.main(["--problem", str(problem_file), "--algo", "rw", "--seed", "3",
                      "--param", "steps=7", "--out", str(out_dir)])
    assert code == 0
    data = json.loads((out_dir / "random_walk_3.json").read_text(encoding="utf-8"))
    assert data["algorithm"] == "random_walk" and data["label"] == "random_walk" and data["seed"] == 3
    assert data["params"] == {"steps": 7} and data["iterations"] == 7
    assert data["problem"] == json.loads(problem_file.read_text(encoding="utf-8"))
    assert data["problem_file"].endswith("problem.json")
    assert len(data["extra"]["value_per_truck"]) == 2
    assert "objective akhir" in capsys.readouterr().out


def test_cli_out_to_file(dummy_algorithm, problem_file, tmp_path):
    out = tmp_path / "custom.json"
    assert main.main(["--problem", str(problem_file), "--algo", "rw", "--label", "coba", "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))["label"] == "coba"


def test_cli_list(dummy_algorithm, capsys):
    assert main.main(["--list"]) == 0
    assert "random_walk" in capsys.readouterr().out
