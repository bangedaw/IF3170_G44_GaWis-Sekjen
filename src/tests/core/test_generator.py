import json

from core.generator import PRESETS, generate_problem, write_presets
from core.io import problem_from_dict


def test_generator_is_seeded():
    spec = dict(trucks=[(10, 20, 5, 500)], seed=3)
    assert generate_problem(**spec) == generate_problem(**spec)
    assert generate_problem(**spec) != generate_problem(trucks=[(10, 20, 5, 500)], seed=4)


def test_generated_problem_is_loadable_and_constrained():
    raw = generate_problem(trucks=[(10, 20, 5, 500), (6, 8, 4, 100)], seed=1, volume_ratio=1.3)
    problem = problem_from_dict(raw)
    assert sum(p.volume for p in problem.packages) >= 1.3 * sum(t.volume for t in problem.trucks)
    assert sum(p.weight for p in problem.packages) > sum(t.max_capacity for t in problem.trucks)
    assert any(p.is_fragile for p in problem.packages)
    assert all(1 <= p.eta <= 7 and p.weight >= 1 and p.value > 0 for p in problem.packages)


def test_write_presets_matches_committed_data(tmp_path):
    from core.generator import DATA_DIR
    paths = write_presets(tmp_path)
    assert {p.stem for p in paths} == set(PRESETS)
    for path in paths:
        assert json.loads(path.read_text()) == json.loads((DATA_DIR / path.name).read_text())
