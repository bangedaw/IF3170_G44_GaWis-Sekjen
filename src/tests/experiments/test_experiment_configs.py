from pathlib import Path

import pytest

from experiments import run_experiments as runner

CONFIGS = sorted((Path(runner.SRC_DIR) / "experiments" / "configs").glob("*.json"))


def test_required_configs_exist():
    assert {"hill_climbing.json", "simulated_annealing.json"} <= {p.name for p in CONFIGS}


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.stem)
def test_config_expands_to_valid_runs(path):
    specs = runner.expand_config(runner.load_config(path))
    assert specs
    for spec in specs:
        assert runner.repo_path(spec.problem_file).exists()
        cls = runner.registry.get_algorithm(spec.algorithm)
        assert set(spec.params) <= set(cls.default_params)
        assert spec.seed in (1, 2, 3)


def test_mandatory_experiment_sizes():
    hill_climbing = runner.expand_config(runner.load_config(runner.SRC_DIR / "experiments/configs/hill_climbing.json"))
    annealing = runner.expand_config(runner.load_config(runner.SRC_DIR / "experiments/configs/simulated_annealing.json"))
    assert len(hill_climbing) == 15 and len({s.algorithm for s in hill_climbing}) == 5
    assert len(annealing) == 3
