from __future__ import annotations

import math

from algorithms.base import LocalSearch

STUCK_DEFINITION = (
    "Satu kejadian 'stuck' dihitung setiap kali {patience} iterasi berturut-turut berlalu "
    "tanpa satu pun move uphill (ΔE > 0) yang diterima, yaitu pencarian hanya diam atau "
    "turun di sekitar local optimum. Penghitung streak di-reset setelah kejadian dicatat "
    "dan setiap kali ada move uphill yang diterima."
)


class SimulatedAnnealing(LocalSearch):
    name = "simulated_annealing"
    aliases = ("sa",)
    default_params = {
        "t0": 100.0,
        "cooling": 0.9995,
        "t_min": 0.01,
        "max_iterations": 50_000,
        "stuck_patience": 500,
        "return_best": False,
    }

    def __init__(self, problem, objective="default", seed=None, **params):
        super().__init__(problem, objective, seed, **params)
        if self.params["t0"] <= 0 or not 0 < self.params["cooling"] < 1:
            raise ValueError(f"{self.name}: butuh t0 > 0 dan 0 < cooling < 1")

    def _search(self):
        p = self.params
        current = initial = self.random_state()
        current_value = self.objective(current)
        best, best_value = current, current_value
        self.record("objective", current_value)

        temperature = p["t0"]
        streak = accepted = accepted_worse = 0
        stuck_iterations = []
        while self.iterations < p["max_iterations"] and temperature > p["t_min"]:
            neighbor, _ = self.random_neighbor(current)
            neighbor_value = self.objective(neighbor)
            delta = neighbor_value - current_value
            probability = 1.0 if delta >= 0 else math.exp(delta / temperature)
            is_accepted = delta >= 0 or self.rng.random() < probability
            if is_accepted:
                current, current_value = neighbor, neighbor_value
                accepted += 1
                accepted_worse += delta < 0
            if is_accepted and delta > 0:
                streak = 0
            else:
                streak += 1
                if streak >= p["stuck_patience"]:
                    stuck_iterations.append(self.iterations)
                    streak = 0
            if current_value > best_value:
                best, best_value = current, current_value

            self.iterations += 1
            self.record("objective", current_value)
            self.record("acceptance_prob", probability)
            self.record("temperature", temperature)
            temperature *= p["cooling"]

        self.extra.update(
            stuck_count=len(stuck_iterations),
            stuck_definition=STUCK_DEFINITION.format(patience=p["stuck_patience"]),
            stuck_iterations=stuck_iterations,
            accepted_moves=accepted,
            accepted_worse_moves=accepted_worse,
            best_objective_seen=best_value,
            final_temperature=temperature,
            stop_reason="t_min" if temperature <= p["t_min"] else "max_iterations",
        )
        return initial, best if p["return_best"] else current
