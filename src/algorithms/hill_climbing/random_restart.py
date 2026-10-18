from __future__ import annotations

import math

from algorithms import registry
from algorithms.base import LocalSearch
from algorithms.hill_climbing.common import HillClimbing


class RandomRestartHC(LocalSearch):
    name = "random_restart_hc"
    aliases = ("random_restart", "rrhc")
    default_params = {"max_restart": 10, "base_algorithm": "steepest_ascent_hc", "base_params": {}}

    def __init__(self, problem, objective="default", seed=None, **params):
        super().__init__(problem, objective, seed, **params)
        climber_cls = registry.get_algorithm(self.params["base_algorithm"])
        if not issubclass(climber_cls, HillClimbing):
            raise ValueError(f"{self.name}: base_algorithm harus varian Hill-climbing, bukan {climber_cls.name}")
        self._climber_cls = climber_cls
        self._new_climber()

    def _new_climber(self) -> HillClimbing:
        return self._climber_cls(self.problem, self.objective_name, **self.params["base_params"])

    def _search(self):
        climber = self._new_climber()
        climber.rng = self.rng
        initial = best = None
        best_value = -math.inf
        iterations_per_restart, start_objectives, final_objectives = [], [], []
        for attempt in range(self.params["max_restart"] + 1):
            climber.history = {"objective": []}
            start = self.random_state()
            before = climber.iterations
            final = climber.climb(start)
            values = climber.history["objective"]
            self.history["objective"].extend(values if attempt == 0 else values[1:])
            iterations_per_restart.append(climber.iterations - before)
            start_objectives.append(values[0])
            final_objectives.append(values[-1])
            if initial is None:
                initial = start
            if values[-1] > best_value:
                best, best_value = final, values[-1]

        self.iterations = climber.iterations
        self.evaluations = climber.evaluations
        self.extra.update(
            max_restart=self.params["max_restart"],
            restarts=len(iterations_per_restart) - 1,
            iterations_per_restart=iterations_per_restart,
            start_objective_per_restart=start_objectives,
            objective_per_restart=final_objectives,
            best_restart=final_objectives.index(best_value),
            base_extra=dict(climber.extra),
            stop_reason="max_restart",
        )
        return initial, best
