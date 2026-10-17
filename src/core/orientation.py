"""Orientasi paket: 6 permutasi sumbu dan rotasi 90 derajat.

Orientasi adalah string permutasi dari "xyz". Karakter ke-0, ke-1, ke-2 menyatakan
sumbu truk tempat sisi w, l, h paket sejajar. "xyz" = {w:x, l:y, h:z} (default),
"yxz" = {w:y, l:x, h:z} (hasil rotasi 90 derajat terhadap sumbu z).
"""
from __future__ import annotations

ORIENTATIONS = ("xyz", "xzy", "yxz", "yzx", "zxy", "zyx")
AXES = "xyz"


def effective_dims(package, orientation: str) -> tuple[int, int, int]:
    """Dimensi (dx, dy, dz) paket terhadap sumbu truk untuk orientasi tertentu."""
    return dims_for(package.dims, orientation)


def dims_for(base_dims: tuple[int, int, int], orientation: str) -> tuple[int, int, int]:
    return (
        base_dims[orientation.index("x")],
        base_dims[orientation.index("y")],
        base_dims[orientation.index("z")],
    )


def rotate(orientation: str, axis: str) -> str:
    """Rotasi 90 derajat terhadap `axis`: dua sumbu lainnya saling bertukar.

    z menukar x<->y, x menukar y<->z, y menukar x<->z.
    """
    if axis not in AXES:
        raise ValueError(f"sumbu harus salah satu dari 'xyz', bukan {axis!r}")
    a, b = (c for c in AXES if c != axis)
    return orientation.translate(str.maketrans({a: b, b: a}))


def is_valid_orientation(orientation: str) -> bool:
    return orientation in ORIENTATIONS
