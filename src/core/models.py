from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import NamedTuple

from .orientation import dims_for


@dataclass(frozen=True)
class Package:
    id: str
    w: int
    l: int
    h: int
    value: float
    weight: float
    is_fragile: bool = False
    eta: int = 0

    @property
    def dims(self) -> tuple[int, int, int]:
        return (self.w, self.l, self.h)

    @property
    def volume(self) -> int:
        return self.w * self.l * self.h


@dataclass(frozen=True)
class Truck:
    id: str
    w: int
    l: int
    h: int
    max_capacity: float

    @property
    def dims(self) -> tuple[int, int, int]:
        return (self.w, self.l, self.h)

    @property
    def volume(self) -> int:
        return self.w * self.l * self.h


@dataclass(frozen=True, eq=False)
class Problem:
    trucks: tuple[Truck, ...]
    packages: tuple[Package, ...]
    cache: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        if not self.trucks:
            raise ValueError("problem harus memiliki minimal satu truk")
        ids = [p.id for p in self.packages]
        if len(set(ids)) != len(ids):
            raise ValueError("id paket harus unik")

    @cached_property
    def ids(self) -> tuple[str, ...]:
        return tuple(p.id for p in self.packages)

    @cached_property
    def index_of(self) -> dict[str, int]:
        return {p.id: i for i, p in enumerate(self.packages)}

    @cached_property
    def values(self) -> tuple[float, ...]:
        return tuple(p.value for p in self.packages)

    @cached_property
    def weights(self) -> tuple[float, ...]:
        return tuple(p.weight for p in self.packages)

    @cached_property
    def fragile(self) -> tuple[bool, ...]:
        return tuple(p.is_fragile for p in self.packages)

    @cached_property
    def volumes(self) -> tuple[int, ...]:
        return tuple(p.volume for p in self.packages)

    def place(self, index: int, truck: int, x: int, y: int, z: int, orientation: str = "xyz") -> Placement:
        return Placement(truck, int(x), int(y), int(z), orientation,
                         dims_for(self.packages[index].dims, orientation))

    def outside(self, index: int, orientation: str = "xyz") -> Placement:
        return Placement(None, 0, 0, 0, orientation, dims_for(self.packages[index].dims, orientation))


class Placement(NamedTuple):
    truck: int | None
    x: int = 0
    y: int = 0
    z: int = 0
    orientation: str = "xyz"
    dims: tuple[int, int, int] = (0, 0, 0)

    @property
    def inside(self) -> bool:
        return self.truck is not None


@dataclass(frozen=True)
class State:
    ids: tuple[str, ...] = field(compare=False)
    placements: tuple[Placement, ...]

    def __len__(self) -> int:
        return len(self.placements)
