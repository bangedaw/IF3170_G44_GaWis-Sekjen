from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PRESETS = {
    "small": dict(trucks=[(6, 8, 4, 100)], volume_ratio=1.4, max_side=(4, 5, 3), seed=11),
    "medium": dict(trucks=[(10, 20, 5, 500)], volume_ratio=1.2, seed=22),
    "large": dict(trucks=[(15, 30, 8, 1500)], volume_ratio=1.2, max_side=(7, 9, 4), seed=33),
    "multi_truck": dict(trucks=[(8, 12, 4, 300), (6, 10, 4, 180), (10, 16, 5, 450)],
                        volume_ratio=1.2, max_side=(5, 6, 3), seed=44),
}


def generate_problem(trucks: list[tuple[int, int, int, float]], seed: int, volume_ratio: float = 1.2,
                     weight_ratio: float = 1.4, fragile_ratio: float = 0.2,
                     max_side: tuple[int, int, int] | None = None) -> dict:
    rng = random.Random(seed)
    min_w = min(t[0] for t in trucks)
    min_l = min(t[1] for t in trucks)
    min_h = min(t[2] for t in trucks)
    if max_side is None:
        max_side = (max(2, min_w // 2), max(2, min_l // 3), max(1, (min_h * 3) // 5))

    target_volume = volume_ratio * sum(w * l * h for w, l, h, _ in trucks)
    shapes, volume = [], 0
    while volume < target_volume:
        w, l, h = (rng.randint(1 if side == 1 else 2, side) for side in max_side)
        shapes.append((w, l, h))
        volume += w * l * h

    raw_weights = [rng.uniform(0.5, 1.5) * (w * l * h) ** 0.5 for w, l, h in shapes]
    scale = weight_ratio * sum(t[3] for t in trucks) / sum(raw_weights)
    width = len(str(len(shapes)))
    packages = []
    for k, ((w, l, h), raw_weight) in enumerate(zip(shapes, raw_weights), start=1):
        packages.append({
            "id": f"P{k:0{width}d}",
            "dimensions": {"w": w, "l": l, "h": h},
            "value": int(w * l * h * rng.uniform(1.0, 4.0)) + rng.randint(5, 25),
            "weight": max(1, round(raw_weight * scale)),
            "is_fragile": rng.random() < fragile_ratio,
            "eta": rng.randint(1, 7),
        })
    return {
        "trucks": [{"id": f"T{k}", "dimensions": {"w": w, "l": l, "h": h}, "max_capacity": cap}
                   for k, (w, l, h, cap) in enumerate(trucks, start=1)],
        "packages": packages,
    }


def write_presets(out_dir: Path = DATA_DIR) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, spec in PRESETS.items():
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(generate_problem(**spec), indent=2) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Bangkitkan problem uji standar.")
    parser.add_argument("--out", type=Path, default=DATA_DIR, help="folder tujuan (default: src/data)")
    for path in write_presets(parser.parse_args(argv).out):
        print(path)


if __name__ == "__main__":
    main()
