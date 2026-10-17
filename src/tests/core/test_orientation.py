import pytest

from core.models import Package
from core.orientation import ORIENTATIONS, effective_dims, is_valid_orientation, rotate

PKG = Package("A", 2, 3, 5, 1, 1)


def test_six_distinct_orientations():
    assert len(ORIENTATIONS) == len(set(ORIENTATIONS)) == 6
    assert all(sorted(o) == ["x", "y", "z"] for o in ORIENTATIONS)


@pytest.mark.parametrize("orientation, expected", [
    ("xyz", (2, 3, 5)),
    ("yxz", (3, 2, 5)),   # w sejajar y, l sejajar x
    ("xzy", (2, 5, 3)),
    ("zyx", (5, 3, 2)),
    ("yzx", (5, 2, 3)),
    ("zxy", (3, 5, 2)),
])
def test_effective_dims(orientation, expected):
    assert effective_dims(PKG, orientation) == expected


def test_rotate_swaps_the_other_two_axes():
    assert rotate("xyz", "z") == "yxz"
    assert rotate("xyz", "x") == "xzy"
    assert rotate("xyz", "y") == "zyx"


@pytest.mark.parametrize("axis", "xyz")
def test_rotating_twice_is_identity(axis):
    for orientation in ORIENTATIONS:
        assert rotate(rotate(orientation, axis), axis) == orientation


def test_rotation_around_z_keeps_height():
    for orientation in ORIENTATIONS:
        assert effective_dims(PKG, rotate(orientation, "z"))[2] == effective_dims(PKG, orientation)[2]


def test_rotations_reach_all_six_orientations():
    seen, frontier = {"xyz"}, ["xyz"]
    while frontier:
        current = frontier.pop()
        for axis in "xyz":
            nxt = rotate(current, axis)
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    assert seen == set(ORIENTATIONS)


def test_invalid_axis_and_orientation():
    with pytest.raises(ValueError):
        rotate("xyz", "w")
    assert is_valid_orientation("yxz") and not is_valid_orientation("xxz")
