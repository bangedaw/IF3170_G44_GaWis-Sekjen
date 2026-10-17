"""Heuristik kandidat koordinat dan gravity settle.

Ruang koordinat penuh (W x L x H posisi per paket per truk) terlalu besar untuk dienumerasi,
jadi posisi penempatan dibatasi ke "titik jangkar" yang bersentuhan dengan dinding truk atau
paket lain (mirip extreme points pada bin packing 3D, mis. Crainic, Perboli & Tadei, 2008):

  1. Jangkar (x, y) diambil dari sudut-sudut paket yang sudah ada (sisi kanan, sisi depan,
     sudut sendiri, sisi sebelum paket) ditambah sudut/dinding truk.
  2. Untuk tiap jangkar, z ditentukan dengan "menjatuhkan" paket: z = sisi atas tertinggi
     di antara paket yang alasnya beririsan (0 bila lantai). Hasilnya selalu tersangga dan
     tidak pernah beririsan dengan paket lain.
  3. Ditolak bila keluar dinding, bertumpu pada paket pecah-belah, atau (untuk paket
     pecah-belah) bila ada paket yang tepat di atasnya.

Jadi setiap kandidat otomatis memenuhi constraint geometri dan tersangga; hanya berat yang
harus diperiksa pemanggil.

`settle` adalah kebalikannya: setelah sebuah paket diangkat/dirotasi, paket yang tadinya
bertumpu padanya dijatuhkan ke penyangga tertinggi di bawahnya (gravitasi), supaya satu
move tidak otomatis menimbulkan banyak pelanggaran "melayang".
"""
from __future__ import annotations

import numpy as np

from .models import Placement, Problem

_EMPTY = np.zeros((0, 3), dtype=np.int64)


class TruckBoxes:
    """Kotak-kotak di dalam satu truk sebagai array numpy (kolom x, y, z, dx, dy, dz)."""
    __slots__ = ("size", "x", "y", "z", "x2", "y2", "z2", "fragile")

    def __init__(self, problem: Problem, placements, truck: int, exclude: tuple[int, ...] = ()):
        members = [i for i, p in enumerate(placements) if p.truck == truck and i not in exclude]
        self.size = len(members)
        if members:
            rows = np.array([(p.x, p.y, p.z, *p.dims) for p in (placements[i] for i in members)], dtype=np.int64)
            self.x, self.y, self.z = rows[:, 0], rows[:, 1], rows[:, 2]
            self.x2, self.y2, self.z2 = self.x + rows[:, 3], self.y + rows[:, 4], self.z + rows[:, 5]
            self.fragile = np.array([problem.fragile[i] for i in members], dtype=bool)


def candidate_positions(boxes: TruckBoxes, truck, dims: tuple[int, int, int], fragile: bool,
                        anchors: tuple[np.ndarray, np.ndarray] | None = None) -> np.ndarray:
    """Posisi (x, y, z) valid secara geometri; array berukuran (C, 3).

    `anchors` = (xs, ys) memaksa pemakaian jangkar tertentu (dipakai oleh swap).
    """
    dx, dy, dz = dims
    W, L, H = truck.w, truck.l, truck.h
    if dx > W or dy > L or dz > H:
        return _EMPTY
    if anchors is not None:
        ax, ay = np.asarray(anchors[0], dtype=np.int64), np.asarray(anchors[1], dtype=np.int64)
    elif boxes.size == 0:
        return np.zeros((1, 3), dtype=np.int64)
    else:
        bx, by, bx2, by2 = boxes.x, boxes.y, boxes.x2, boxes.y2
        zero = np.zeros(boxes.size, dtype=np.int64)
        corners = np.array([0, W - dx, 0, W - dx], dtype=np.int64)
        ax = np.concatenate((corners, bx2, bx, bx, bx2, bx - dx, bx, zero))
        ay = np.concatenate((np.array([0, 0, L - dy, L - dy], dtype=np.int64), by, by2, by, zero, by, by - dy, by2))

    inside = (ax >= 0) & (ay >= 0) & (ax <= W - dx) & (ay <= L - dy)
    ax, ay = ax[inside], ay[inside]
    if ax.size == 0:
        return _EMPTY
    _, first = np.unique(ax * (L + 1) + ay, return_index=True)
    ax, ay = ax[first], ay[first]
    if boxes.size == 0:
        return np.stack([ax, ay, np.zeros_like(ax)], axis=1)

    ov = ((ax[:, None] < boxes.x2[None, :]) & (boxes.x[None, :] < (ax + dx)[:, None])
          & (ay[:, None] < boxes.y2[None, :]) & (boxes.y[None, :] < (ay + dy)[:, None]))
    z = np.where(ov, boxes.z2[None, :], 0).max(axis=1)
    valid = z + dz <= H
    valid &= ~(ov & (boxes.z2[None, :] == z[:, None]) & boxes.fragile[None, :]).any(axis=1)
    if fragile:
        valid &= ~(ov & (boxes.z[None, :] == (z + dz)[:, None])).any(axis=1)
    return np.stack([ax, ay, z], axis=1)[valid]


def has_dependents(placements, index: int) -> bool:
    """Apakah ada paket yang bertumpu langsung di atas paket `index`."""
    p = placements[index]
    if p.truck is None:
        return False
    x2, y2, top = p.x + p.dims[0], p.y + p.dims[1], p.z + p.dims[2]
    for j, q in enumerate(placements):
        if j != index and q.truck == p.truck and q.z == top and q.x < x2 and p.x < q.x + q.dims[0] \
                and q.y < y2 and p.y < q.y + q.dims[1]:
            return True
    return False


def settle(placements: list[Placement], truck: int) -> None:
    """Jatuhkan paket yang melayang di `truck` ke penyangga tertingginya (in-place)."""
    order = sorted((i for i, p in enumerate(placements) if p.truck == truck and p.z > 0),
                   key=lambda i: placements[i].z)
    if not order:
        return
    rest = [(p.x, p.y, p.x + p.dims[0], p.y + p.dims[1], p.z + p.dims[2])
            for p in placements if p.truck == truck and p.z <= 0]
    for i in order:
        p = placements[i]
        x2, y2 = p.x + p.dims[0], p.y + p.dims[1]
        base, supported = 0, False
        for ox, oy, ox2, oy2, top in rest:
            if p.x < ox2 and ox < x2 and p.y < oy2 and oy < y2:
                if top == p.z:
                    supported = True
                    break
                if top < p.z and top > base:
                    base = top
        z = p.z if supported else base
        if z != p.z:
            placements[i] = p._replace(z=z)
        rest.append((p.x, p.y, x2, y2, z + p.dims[2]))
