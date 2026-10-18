from __future__ import annotations

from algorithms.hill_climbing.common import EPS, HillClimbing


class SteepestAscentHC(HillClimbing):
    name = "steepest_ascent_hc"
    aliases = ("steepest_ascent", "steepest", "sahc")
    default_params = {"neighbor_limit": None, "max_iterations": None}

    def climb(self, current):
        current_value = self._start(current)
        steps = 0
        while self._below_limit(steps):
            neighbor, neighbor_value = self.best_neighbor(current)
            if neighbor is None or neighbor_value <= current_value + EPS:
                self.extra["stop_reason"] = "local_optimum"
                return current
            current, current_value = neighbor, neighbor_value
            steps += 1
            self._advance(current_value)
        self.extra["stop_reason"] = "max_iterations"
        return current
