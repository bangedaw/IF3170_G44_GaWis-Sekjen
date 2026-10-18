from __future__ import annotations

from algorithms.hill_climbing.common import EPS, HillClimbing


class SidewaysMoveHC(HillClimbing):
    name = "sideways_move_hc"
    aliases = ("sideways_move", "sideways")
    default_params = {"max_sideways": 100, "neighbor_limit": None, "max_iterations": None}

    def climb(self, current):
        max_sideways = self.params["max_sideways"]
        current_value = self._start(current)
        steps = sideways = 0
        reason = "max_iterations"
        while self._below_limit(steps):
            neighbor, neighbor_value = self.best_neighbor(current)
            if neighbor is None or neighbor_value < current_value - EPS:
                reason = "local_optimum"
                break
            is_sideways = neighbor_value <= current_value + EPS
            if is_sideways and sideways >= max_sideways:
                reason = "max_sideways"
                break
            current, current_value = neighbor, neighbor_value
            steps += 1
            self._advance(current_value)
            if is_sideways:
                sideways += 1
                if sideways >= max_sideways:
                    reason = "max_sideways"
                    break
        self.extra["max_sideways"] = max_sideways
        self.extra["sideways_used"] = self.extra.get("sideways_used", 0) + sideways
        self.extra["stop_reason"] = reason
        return current
