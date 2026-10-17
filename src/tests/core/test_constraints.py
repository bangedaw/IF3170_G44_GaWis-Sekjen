import pytest

from core.constraints import check_state

BIG = (10, 10, 10, 1000)


def violations(build, trucks, packages, spec):
    make_problem, make_state = build
    problem = make_problem(trucks, packages)
    return check_state(problem, make_state(problem, spec)).violations


def only(result, key):
    assert result[key] > 0
    assert all(v == 0 for k, v in result.items() if k != key), result
    return result[key]


def box(w=2, l=2, h=2, value=10, weight=1, fragile=False):
    return (w, l, h, value, weight, fragile)


def test_empty_and_single_package_on_floor_is_valid(build):
    assert not any(violations(build, [BIG], [box()], [None]).values())
    assert not any(violations(build, [BIG], [box()], [(0, 0, 0, 0)]).values())


def test_package_touching_walls_is_inside(build):
    assert not any(violations(build, [BIG], [box(10, 10, 10)], [(0, 0, 0, 0)]).values())


@pytest.mark.parametrize("pos", [(9, 0, 0), (0, 9, 0), (-1, 0, 0), (0, -1, 0), (0, 0, 9)])
def test_out_of_bounds(build, pos):
    result = violations(build, [BIG], [box()], [(0, *pos)])
    assert result["out_of_bounds"] == 1


def test_package_larger_than_truck_is_out_of_bounds(build):
    assert violations(build, [(4, 4, 4, 100)], [box(5, 1, 1)], [(0, 0, 0, 0)])["out_of_bounds"] == 1


def test_overlap(build):
    result = violations(build, [BIG], [box(), box()], [(0, 0, 0, 0), (0, 1, 1, 0)])
    assert only(result, "overlap") == 1


def test_touching_faces_do_not_overlap(build):
    spec = [(0, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (0, 0, 0, 2)]
    assert not any(violations(build, [BIG], [box()] * 4, spec).values())


def test_overlap_counts_pairs(build):
    assert violations(build, [BIG], [box()] * 3, [(0, 0, 0, 0)] * 3)["overlap"] == 3


def test_floating_package_in_the_air(build):
    assert only(violations(build, [BIG], [box()], [(0, 0, 0, 3)]), "floating") == 1


def test_package_resting_on_another_is_supported(build):
    assert not any(violations(build, [BIG], [box(), box()], [(0, 0, 0, 0), (0, 0, 0, 2)]).values())


def test_floating_when_gap_below(build):
    result = violations(build, [BIG], [box(), box()], [(0, 0, 0, 0), (0, 0, 0, 3)])
    assert only(result, "floating") == 1


def test_one_supported_point_is_enough(build):
    # alas atas hanya menumpu 1 sel (x=1,y=1) pada paket di bawahnya; spesifikasi: tidak melayang
    result = violations(build, [BIG], [box(), box(2, 2, 1)], [(0, 0, 0, 0), (0, 1, 1, 2)])
    assert not any(result.values())


def test_adjacent_but_not_overlapping_base_does_not_support(build):
    result = violations(build, [BIG], [box(), box()], [(0, 0, 0, 0), (0, 2, 0, 2)])
    assert only(result, "floating") == 1


def test_fragile_cannot_be_support(build):
    result = violations(build, [BIG], [box(fragile=True), box()], [(0, 0, 0, 0), (0, 0, 0, 2)])
    assert only(result, "fragile_support") == 1


def test_fragile_on_top_is_fine(build):
    result = violations(build, [BIG], [box(), box(fragile=True)], [(0, 0, 0, 0), (0, 0, 0, 2)])
    assert not any(result.values())


def test_fragile_beside_other_packages_is_fine(build):
    result = violations(build, [BIG], [box(fragile=True), box()], [(0, 0, 0, 0), (0, 2, 0, 0)])
    assert not any(result.values())


def test_package_on_fragile_and_nonfragile_still_violates(build):
    packages = [box(fragile=True), box(), box(4, 2, 1)]
    result = violations(build, [BIG], packages, [(0, 0, 0, 0), (0, 2, 0, 0), (0, 0, 0, 2)])
    assert only(result, "fragile_support") == 1


def test_overweight(build):
    result = violations(build, [(10, 10, 10, 15)], [box(weight=10), box(weight=10)], [(0, 0, 0, 0), (0, 2, 0, 0)])
    assert only(result, "overweight") == 5


def test_weight_at_capacity_is_allowed(build):
    result = violations(build, [(10, 10, 10, 20)], [box(weight=10), box(weight=10)], [(0, 0, 0, 0), (0, 2, 0, 0)])
    assert not any(result.values())


def test_outside_packages_do_not_count_toward_weight_or_geometry(build):
    result = violations(build, [(10, 10, 10, 15)], [box(weight=10), box(weight=10), box(20, 20, 20, weight=99)],
                        [(0, 0, 0, 0), None, None])
    assert not any(result.values())


def test_multi_truck_same_coordinates_do_not_overlap(build):
    result = violations(build, [BIG, BIG], [box(), box()], [(0, 0, 0, 0), (1, 0, 0, 0)])
    assert not any(result.values())


def test_multi_truck_capacity_is_per_truck(build):
    trucks = [(10, 10, 10, 15), (10, 10, 10, 15)]
    packages = [box(weight=10)] * 2
    assert not any(violations(build, trucks, packages, [(0, 0, 0, 0), (1, 0, 0, 0)]).values())
    assert violations(build, trucks, packages, [(0, 0, 0, 0), (0, 2, 0, 0)])["overweight"] == 5


def test_multi_truck_bounds_use_each_trucks_own_size(build):
    trucks = [(10, 10, 10, 100), (3, 3, 3, 100)]
    assert violations(build, trucks, [box(4, 4, 4)], [(0, 0, 0, 0)])["out_of_bounds"] == 0
    assert violations(build, trucks, [box(4, 4, 4)], [(1, 0, 0, 0)])["out_of_bounds"] == 1


def test_rotation_changes_what_fits(build):
    make_problem, make_state = build
    problem = make_problem([(3, 3, 6, 100)], [(2, 2, 5, 10, 1, False)])
    assert check_state(problem, make_state(problem, [(0, 0, 0, 0, "xyz")])).feasible
    assert not check_state(problem, make_state(problem, [(0, 0, 0, 0, "xzy")])).feasible  # dims (2,5,2): y keluar
