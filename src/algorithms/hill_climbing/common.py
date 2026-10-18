from __future__ import annotations

import math
from abc import abstractmethod

from algorithms.base import LocalSearch

EPS = 1e-9


class HillClimbing(LocalSearch):
    def _search(self):
        initial = self.random_state()
        return initial, self.climb(initial)

    @abstractmethod
    def climb(self, state):
        ...

    def _start(self, state) -> float:
        value = self.objective(state)
        self.record("objective", value)
        return value

    def _advance(self, value: float) -> None:
        self.iterations += 1
        self.record("objective", value)

    def _below_limit(self, steps: int) -> bool:
        limit = self.params.get("max_iterations")
        return limit is None or steps < limit

    def best_neighbor(self, state):
        best, best_value = [], -math.inf
        for neighbor, _ in self.neighbors(state, limit=self.params.get("neighbor_limit")):
            value = self.objective(neighbor)
            if value > best_value + EPS:
                best, best_value = [neighbor], value
            elif value >= best_value - EPS:
                best.append(neighbor)
        if not best:
            return None, -math.inf
        return self.rng.choice(best), best_value
