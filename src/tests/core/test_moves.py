import random
from pathlib import Path

import pytest

from core import evaluate, load_problem, neighbors, random_neighbor, random_state
from core.orientation import dims_for

DATA = Path(__file__).resolve().parents[2] / "data"
BIG = (10, 10, 10, 1000)


def box(w=2, l=2, h=2, value=10, weight=1, fragile=False):
    return (w, l, h, value, weight, fragile)


def assert_well_formed(problem, before, after):
    assert after.ids == before.ids == problem.ids
    assert len(after.placements) == len(problem.packages)
    for i, p in enumerate(after.placements):
        assert p.dims == dims_for(problem.packages[i].dims, p.orientation)
        assert all(type(v) is int for v in (p.x, p.y, p.z)), p
        assert p.truck is None or 0 <= p.truck < len(problem.trucks)
        if p.truck is None:
            assert (p.x, p.y, p.z) == (0, 0, 0)


@pytest.mark.parametrize("name", ["small", "medium", "multi_truck"])
def test_random_walk_keeps_states_well_formed(name):
    problem = load_problem(DATA / f"{name}.json")
    rng = random.Random(7)
    state = random_state(problem, rng)
    seen = set()
    for _ in range(300):
        nxt, move = random_neighbor(problem, state, rng)
        assert_well_formed(problem, state, nxt)
        assert move["type"] in {"swap", "move", "rotate"}
        seen.add(move["type"])
        state = nxt
    assert seen == {"swap", "move", "rotate"}


def test_random_neighbor_is_reproducible_with_seed():
    problem = load_problem(DATA / "medium.json")
    runs = []
    for _ in range(2):
        rng = random.Random(11)
        state = random_state(problem, rng)
        for _ in range(40):
            state, _ = random_neighbor(problem, state, rng)
        runs.append(state)
    assert runs[0] == runs[1]


def test_random_neighbor_does_not_mutate_input():
    problem = load_problem(DATA / "small.json")
    rng = random.Random(1)
    state = random_state(problem, rng)
    snapshot = state.placements
    for _ in range(30):
        random_neighbor(problem, state, rng)
    assert state.placements == snapshot


@pytest.mark.parametrize("name", ["small", "medium", "multi_truck"])
def test_neighbors_of_feasible_state_are_nearly_all_feasible(name):
    problem = load_problem(DATA / f"{name}.json")
    state = random_state(problem, random.Random(5))
    assert evaluate(problem, state).feasible
    found = list(neighbors(problem, state, rng=random.Random(1), limit=300))
    assert found
    feasible = 0
    for nxt, move in found:
        assert_well_formed(problem, state, nxt)
        assert nxt != state
        feasible += evaluate(problem, nxt).feasible
    assert feasible / len(found) > 0.9


def test_neighbors_limit_and_determinism_without_rng():
    problem = load_problem(DATA / "medium.json")
    state = random_state(problem, random.Random(5))
    assert len(list(neighbors(problem, state, rng=random.Random(2), limit=25))) == 25
    first = [m for _, m in neighbors(problem, state, limit=40)]
    second = [m for _, m in neighbors(problem, state, limit=40)]
    assert first == second


def test_neighbors_cover_all_three_move_types():
    problem = load_problem(DATA / "medium.json")
    state = random_state(problem, random.Random(5))
    kinds = {m["type"] for _, m in neighbors(problem, state, rng=random.Random(3))}
    assert kinds == {"swap", "move", "rotate"}


def test_neighbors_can_move_between_trucks_and_in_and_out():
    problem = load_problem(DATA / "multi_truck.json")
    state = random_state(problem, random.Random(5))
    moves = [m for _, m in neighbors(problem, state, rng=random.Random(3))]
    trucks_to = {m["to"][0] for m in moves if m["type"] == "move" and m["to"]}
    assert trucks_to == set(range(len(problem.trucks)))
    assert any(m["type"] == "move" and m["to"] is None for m in moves)
    assert any(m["type"] == "move" and m["from"] is None for m in moves)


def test_rotate_changes_orientation_and_dims(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(2, 3, 4)])
    state = make_state(problem, [(0, 0, 0, 0)])
    rotated = {m["axis"]: s for s, m in neighbors(problem, state) if m["type"] == "rotate"}
    assert set(rotated) == {"x", "y", "z"}
    assert rotated["z"].placements[0].dims == (3, 2, 4)
    assert rotated["x"].placements[0].dims == (2, 4, 3)
    assert rotated["y"].placements[0].dims == (4, 3, 2)


def test_rotating_a_cube_is_not_a_neighbor(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(3, 3, 3)])
    state = make_state(problem, [(0, 0, 0, 0)])
    assert not [m for _, m in neighbors(problem, state) if m["type"] == "rotate"]


def test_rotate_is_rejected_when_it_would_hit_the_wall_or_a_neighbor(build):
    make_problem, make_state = build
    problem = make_problem([(4, 4, 4, 100)], [box(2, 2, 4), box(2, 2, 2)])
    state = make_state(problem, [(0, 0, 0, 0), (0, 2, 0, 0)])
    rotations = [(m["axis"], s) for s, m in neighbors(problem, state) if m["type"] == "rotate" and m["package"] == "P0"]
    for _, nxt in rotations:
        assert evaluate(problem, nxt).feasible


def test_lifting_a_support_drops_the_package_above(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(), box()])
    state = make_state(problem, [(0, 0, 0, 0), (0, 0, 0, 2)])
    removed = [s for s, m in neighbors(problem, state) if m["type"] == "move" and m["mode"] == "remove"
               and m["package"] == "P0"]
    assert len(removed) == 1
    assert removed[0].placements[0].truck is None
    assert removed[0].placements[1].z == 0
    assert evaluate(problem, removed[0]).feasible


def test_swap_exchanges_slots_and_stays_valid(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(2, 2, 2), box(3, 3, 3)])
    state = make_state(problem, [(0, 0, 0, 0), (0, 5, 5, 0)])
    swaps = [s for s, m in neighbors(problem, state) if m["type"] == "swap"]
    assert len(swaps) == 1
    nxt = swaps[0]
    assert (nxt.placements[0].x, nxt.placements[0].y) == (5, 5)
    assert (nxt.placements[1].x, nxt.placements[1].y) == (0, 0)
    assert evaluate(problem, nxt).feasible


def test_swap_inside_with_outside_exchanges_membership(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(), box(value=99)])
    state = make_state(problem, [(0, 3, 3, 0), None])
    swaps = [s for s, m in neighbors(problem, state) if m["type"] == "swap"]
    assert len(swaps) == 1
    assert swaps[0].placements[0].truck is None
    assert (swaps[0].placements[1].truck, swaps[0].placements[1].x, swaps[0].placements[1].y) == (0, 3, 3)


def test_two_outside_packages_are_never_swapped(build):
    make_problem, make_state = build
    problem = make_problem([BIG], [box(), box()])
    state = make_state(problem, [None, None])
    assert not [m for _, m in neighbors(problem, state) if m["type"] == "swap"]


def test_move_respects_truck_capacity(build):
    make_problem, make_state = build
    problem = make_problem([(10, 10, 10, 10)], [box(weight=10), box(weight=5)])
    state = make_state(problem, [(0, 0, 0, 0), None])
    into_truck = [m for _, m in neighbors(problem, state) if m["type"] == "move" and m["package"] == "P1" and m["to"]]
    assert not into_truck


def test_nothing_is_moved_on_top_of_a_fragile_package(build):
    make_problem, make_state = build
    # lantai 4x4 sepenuhnya ditutup paket pecah-belah, jadi satu-satunya tempat kosong ada di atasnya
    problem = make_problem([(4, 4, 6, 100)], [box(4, 4, 2, fragile=True), box(4, 4, 2), box(4, 4, 2, fragile=True)])
    state = make_state(problem, [(0, 0, 0, 0), None, None])
    entering = [m for _, m in neighbors(problem, state) if m["type"] == "move" and m["to"] and m["package"] != "P0"]
    assert not entering


def test_fragile_package_may_sit_on_top_but_nothing_goes_on_it(build):
    make_problem, make_state = build
    problem = make_problem([(4, 4, 6, 100)], [box(4, 4, 2), box(4, 4, 2, fragile=True), box(4, 4, 2)])
    state = make_state(problem, [(0, 0, 0, 0), None, None])
    onto = {m["package"]: (s, m) for s, m in neighbors(problem, state) if m["type"] == "move" and m["to"]}
    assert set(onto) == {"P1", "P2"}
    assert onto["P1"][1]["to"] == [0, 0, 0, 2] and evaluate(problem, onto["P1"][0]).feasible
    stacked = make_state(problem, [(0, 0, 0, 0), (0, 0, 0, 2), None])
    assert not [m for _, m in neighbors(problem, stacked) if m["type"] == "move" and m["package"] == "P2" and m["to"]]


def test_random_neighbor_free_mode_exists_and_can_break_constraints():
    problem = load_problem(DATA / "medium.json")
    rng = random.Random(9)
    state = random_state(problem, rng)
    modes, broke = set(), False
    for _ in range(400):
        nxt, move = random_neighbor(problem, state, rng)
        modes.add(move.get("mode"))
        broke |= not evaluate(problem, nxt).feasible
    assert {"candidate", "free", "remove"} <= modes
    assert broke


def test_degenerate_problems(build):
    make_problem, make_state = build
    empty = make_problem([BIG], [])
    state = make_state(empty, [])
    assert random_neighbor(empty, state, random.Random(1))[1]["type"] == "none"
    assert list(neighbors(empty, state)) == []
    single = make_problem([BIG], [box(3, 3, 3)])
    nxt, move = random_neighbor(single, make_state(single, [(0, 0, 0, 0)]), random.Random(1))
    assert move["type"] in {"move", "none"}
