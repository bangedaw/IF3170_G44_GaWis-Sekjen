from __future__ import annotations

ORIENTATIONS = ("xyz", "xzy", "yxz", "yzx", "zxy", "zyx")
AXES = "xyz"


def dims_for(base_dims: tuple[int, int, int], orientation: str) -> tuple[int, int, int]:
    return (
        base_dims[orientation.index("x")],
        base_dims[orientation.index("y")],
        base_dims[orientation.index("z")],
    )


def rotate(orientation: str, axis: str) -> str:
    if axis not in AXES:
        raise ValueError(f"sumbu harus salah satu dari 'xyz', bukan {axis!r}")
    a, b = (c for c in AXES if c != axis)
    return orientation.translate(str.maketrans({a: b, b: a}))
