from __future__ import annotations

from algorithms.hill_climbing.common import EPS, HillClimbing


class FirstChoiceHC(HillClimbing):
    name = "first_choice_hc"
    aliases = ("first_choice", "fchc")
    default_params = {"neighbor_limit": None, "max_iterations": None}

    def climb(self, current):
        current_value = self._start(current)
        steps = 0
        while self._below_limit(steps):
            for neighbor, _ in self.neighbors(current, limit=self.params["neighbor_limit"]):
                value = self.objective(neighbor)
                if value > current_value + EPS:
                    current, current_value = neighbor, value
                    break
            else:
                self.extra["stop_reason"] = "local_optimum"
                return current
            steps += 1
            self._advance(current_value)
        self.extra["stop_reason"] = "max_iterations"
        return current
