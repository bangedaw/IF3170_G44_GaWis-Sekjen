from __future__ import annotations

from algorithms.hill_climbing.common import EPS, HillClimbing

MODES = ("uphill", "random")


class StochasticHC(HillClimbing):
    name = "stochastic_hc"
    aliases = ("stochastic",)
    default_params = {"mode": "uphill", "weighted": False, "neighbor_limit": None, "max_iterations": 1000}

    def __init__(self, problem, objective="default", seed=None, **params):
        super().__init__(problem, objective, seed, **params)
        if self.params["mode"] not in MODES:
            raise ValueError(f"{self.name}: mode harus salah satu dari {MODES}")
        if self.params["mode"] == "random" and self.params["max_iterations"] is None:
            raise ValueError(f"{self.name}: mode 'random' membutuhkan max_iterations")

    def climb(self, current):
        if self.params["mode"] == "random":
            return self._climb_random(current)
        return self._climb_uphill(current)

    def _climb_uphill(self, current):
        current_value = self._start(current)
        steps = 0
        while self._below_limit(steps):
            uphill = []
            for neighbor, _ in self.neighbors(current, limit=self.params["neighbor_limit"]):
                value = self.objective(neighbor)
                if value > current_value + EPS:
                    uphill.append((neighbor, value))
            if not uphill:
                self.extra["stop_reason"] = "local_optimum"
                return current
            if self.params["weighted"]:
                weights = [value - current_value for _, value in uphill]
                current, current_value = self.rng.choices(uphill, weights=weights)[0]
            else:
                current, current_value = self.rng.choice(uphill)
            steps += 1
            self._advance(current_value)
        self.extra["stop_reason"] = "max_iterations"
        return current

    def _climb_random(self, current):
        current_value = self._start(current)
        for _ in range(self.params["max_iterations"]):
            neighbor, _ = self.random_neighbor(current)
            value = self.objective(neighbor)
            if value > current_value + EPS:
                current, current_value = neighbor, value
            self._advance(current_value)
        self.extra["stop_reason"] = "max_iterations"
        return current
