from __future__ import annotations

import json
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, fields
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, ClassVar, Iterable

CORE_API = {
    "load_problem": "core.io",
    "state_to_dict": "core.io",
    "state_from_dict": "core.io",
    "random_state": "core.initializer",
    "evaluate": "core.objective",
    "get_objective": "core.objective",
    "random_neighbor": "core.moves",
    "neighbors": "core.moves",
}


def load_core() -> SimpleNamespace:
    return SimpleNamespace(**{name: getattr(import_module(module), name) for name, module in CORE_API.items()})


@dataclass(kw_only=True)
class RunResult:
    algorithm: str
    label: str | None = None
    objective_name: str = "default"
    problem: dict | None = None
    problem_file: str | None = None
    seed: int | None = None
    params: dict = field(default_factory=dict)
    initial_state: dict = field(default_factory=dict)
    initial_objective: float = 0.0
    initial_value: float = 0.0
    initial_feasible: bool = False
    initial_violations: dict = field(default_factory=dict)
    final_state: dict = field(default_factory=dict)
    final_objective: float = 0.0
    final_value: float = 0.0
    feasible: bool = False
    final_violations: dict = field(default_factory=dict)
    duration_sec: float = 0.0
    iterations: int = 0
    history: dict = field(default_factory=lambda: {"objective": []})
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> RunResult:
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def to_json(self) -> str:
        text = json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=_json_default)
        return _NUMBER_ARRAY.sub(lambda m: "[" + ", ".join(_NUMBER.findall(m.group(0))) + "]", text)

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json() + "\n", encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: str | Path) -> RunResult:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


_NUMBER = re.compile(r"-?\d[\d.eE+-]*")
_NUMBER_ARRAY = re.compile(r"\[\s*-?\d[\d.eE+-]*(?:,\s*-?\d[\d.eE+-]*)*\s*\]")


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if isinstance(obj, (set, frozenset)):
        return sorted(obj)
    raise TypeError(f"Objek {type(obj).__name__} tidak bisa diserialisasi ke JSON")


class LocalSearch(ABC):
    name: ClassVar[str] = "local_search"
    aliases: ClassVar[tuple[str, ...]] = ()
    default_params: ClassVar[dict[str, Any]] = {}

    def __init__(self, problem, objective: str = "default", seed: int | None = None, **params):
        unknown = sorted(set(params) - set(self.default_params))
        if unknown:
            raise ValueError(
                f"{self.name}: parameter tidak dikenal {unknown}; "
                f"parameter yang tersedia: {sorted(self.default_params)}"
            )
        self.core = load_core()
        self.problem = problem
        self.objective_name = objective
        self.seed = seed
        self.params = {**self.default_params, **params}
        self.rng = random.Random(seed)
        self._objective_fn = self.core.get_objective(objective)
        self._reset_log()

    def _reset_log(self) -> None:
        self.iterations = 0
        self.evaluations = 0
        self.history: dict[str, list] = {"objective": []}
        self.extra: dict[str, Any] = {}

    def objective(self, state) -> float:
        self.evaluations += 1
        return self._objective_fn(self.problem, state)

    def random_state(self):
        return self.core.random_state(self.problem, self.rng)

    def random_neighbor(self, state):
        return self.core.random_neighbor(self.problem, state, self.rng)

    def neighbors(self, state, limit: int | None = None) -> Iterable:
        return self.core.neighbors(self.problem, state, rng=self.rng, limit=limit)

    def record(self, series: str, value) -> None:
        self.history.setdefault(series, []).append(value)

    def run(self) -> RunResult:
        self.rng = random.Random(self.seed)
        self._reset_log()
        start = time.perf_counter()
        initial, final = self._search()
        duration = time.perf_counter() - start
        return self._build_result(initial, final, duration)

    @abstractmethod
    def _search(self) -> tuple[Any, Any]:
        ...

    def _build_result(self, initial, final, duration: float) -> RunResult:
        ev0 = self.core.evaluate(self.problem, initial, objective=self.objective_name)
        ev1 = self.core.evaluate(self.problem, final, objective=self.objective_name)
        extra = {**self.extra, "evaluations": self.evaluations}
        value_per_truck = getattr(ev1, "value_per_truck", None)
        if value_per_truck is not None:
            extra["value_per_truck"] = list(value_per_truck)
        return RunResult(
            algorithm=self.name,
            objective_name=self.objective_name,
            seed=self.seed,
            params=dict(self.params),
            initial_state=self.core.state_to_dict(initial),
            initial_objective=float(ev0.objective),
            initial_value=float(ev0.total_value),
            initial_feasible=bool(ev0.feasible),
            initial_violations=dict(ev0.violations),
            final_state=self.core.state_to_dict(final),
            final_objective=float(ev1.objective),
            final_value=float(ev1.total_value),
            feasible=bool(ev1.feasible),
            final_violations=dict(ev1.violations),
            duration_sec=duration,
            iterations=self.iterations,
            history=self.history,
            extra=extra,
        )
