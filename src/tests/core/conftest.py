import pytest

from core.models import Package, Problem, State, Truck


def make_problem(trucks, packages) -> Problem:
    """trucks: [(w, l, h, kapasitas)]; packages: [(w, l, h, value, weight, fragile)]."""
    return Problem(
        tuple(Truck(f"T{k}", w, l, h, cap) for k, (w, l, h, cap) in enumerate(trucks)),
        tuple(Package(f"P{k}", w, l, h, value, weight, fragile, eta=k + 1)
              for k, (w, l, h, value, weight, fragile) in enumerate(packages)),
    )


def make_state(problem: Problem, spec) -> State:
    """spec per paket: None (di luar) atau (truk, x, y, z) / (truk, x, y, z, orientasi)."""
    placements = []
    for i, item in enumerate(spec):
        if item is None:
            placements.append(problem.outside(i))
        else:
            placements.append(problem.place(i, *item))
    return State(problem.ids, tuple(placements))


@pytest.fixture
def build():
    return make_problem, make_state
