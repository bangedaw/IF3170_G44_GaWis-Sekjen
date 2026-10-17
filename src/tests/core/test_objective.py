import math

import pytest

from core import evaluate, get_objective

TRUCK = (10, 10, 10, 100)


def pk(value=10, weight=1, fragile=False, w=2, l=2, h=2):
    return (w, l, h, value, weight, fragile)


def test_default_objective_is_total_value_of_packages_inside(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10), pk(20), pk(40)])
    ev = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 2, 0, 0), None]))
    assert (ev.objective, ev.total_value, ev.feasible) == (30, 30, True)
    assert ev.value_per_truck == [30] and ev.weight_per_truck == [2]
    assert set(ev.violations) == {"overlap", "out_of_bounds", "floating", "fragile_support", "overweight"}


def test_violations_are_penalized_but_total_value_stays_pure(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10), pk(20)])
    ev = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 0, 0, 0)]))  # overlap
    assert ev.total_value == 30 and not ev.feasible and ev.violations["overlap"] == 1
    assert ev.objective == 30 - 20  # penalti = skor terbesar (20)


def test_each_violation_type_lowers_the_objective(build):
    make_problem, make_state = build
    problem = make_problem([(10, 10, 10, 15)], [pk(10, 10), pk(10, 10, fragile=True), pk(10, 1)])
    clean = evaluate(problem, make_state(problem, [(0, 0, 0, 0), None, None])).objective
    cases = {
        "overlap": [(0, 0, 0, 0), (0, 1, 1, 0), None],
        "out_of_bounds": [(0, 9, 0, 0), None, None],
        "floating": [(0, 0, 0, 5), None, None],
        "overweight": [(0, 0, 0, 0), (0, 4, 0, 0), None],
    }
    for kind, spec in cases.items():
        ev = evaluate(problem, make_state(problem, spec))
        assert ev.violations[kind] > 0 and not ev.feasible, kind
        assert ev.objective < ev.total_value, kind
    assert clean == 10


def test_removing_a_violating_package_never_hurts(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10), pk(50)])
    bad = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 0, 0, 0)])).objective
    removed = evaluate(problem, make_state(problem, [(0, 0, 0, 0), None])).objective
    assert removed >= bad


def test_more_overlap_is_worse(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10)] * 3)
    two = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 0, 0, 0), None])).objective
    three = evaluate(problem, make_state(problem, [(0, 0, 0, 0)] * 3)).objective
    assert three < two


def test_overweight_is_never_profitable(build):
    make_problem, make_state = build
    problem = make_problem([(10, 10, 10, 10)], [pk(10, 8), pk(10, 8), pk(5, 8)])
    fits = evaluate(problem, make_state(problem, [(0, 0, 0, 0), None, None])).objective
    one_over = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 2, 0, 0), None])).objective
    two_over = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 2, 0, 0), (0, 4, 0, 0)])).objective
    assert two_over < one_over <= fits


def test_get_objective_matches_evaluate(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10), pk(20)])
    state = make_state(problem, [(0, 0, 0, 0), (0, 3, 0, 0)])
    for name in ("default", "alt"):
        assert get_objective(name)(problem, state) == evaluate(problem, state, objective=name).objective


def test_unknown_objective_raises():
    with pytest.raises(ValueError):
        get_objective("nope")


def test_alt_prefers_urgent_packages(build):
    make_problem, make_state = build
    # P0 punya ETA 1 (mendesak), P2 punya ETA 3; value sama
    problem = make_problem([TRUCK], [pk(10), pk(10), pk(10)])
    urgent = evaluate(problem, make_state(problem, [(0, 0, 0, 0), None, None]), "alt").objective
    late = evaluate(problem, make_state(problem, [None, None, (0, 0, 0, 0)]), "alt").objective
    assert urgent > late
    assert evaluate(problem, make_state(problem, [(0, 0, 0, 0), None, None])).objective == \
        evaluate(problem, make_state(problem, [None, None, (0, 0, 0, 0)])).objective


def test_alt_rewards_utilization_but_total_value_stays_pure(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10)] * 2)
    one = evaluate(problem, make_state(problem, [(0, 0, 0, 0), None]), "alt")
    two = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (0, 2, 0, 0)]), "alt")
    assert two.objective > one.objective
    assert (one.total_value, two.total_value) == (10, 20)


def test_alt_with_equal_eta_and_single_package_is_finite(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK], [pk(10)])
    assert math.isfinite(evaluate(problem, make_state(problem, [(0, 0, 0, 0)]), "alt").objective)


def test_multi_truck_objective_is_fleet_total(build):
    make_problem, make_state = build
    problem = make_problem([TRUCK, TRUCK], [pk(10), pk(20), pk(30)])
    ev = evaluate(problem, make_state(problem, [(0, 0, 0, 0), (1, 0, 0, 0), (1, 2, 0, 0)]))
    assert ev.value_per_truck == [10, 50] and ev.total_value == 60 and ev.objective == 60
