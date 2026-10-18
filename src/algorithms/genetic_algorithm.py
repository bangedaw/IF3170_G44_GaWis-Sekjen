"""Genetic Algorithm implementation for 3D Bin Packing / Container Loading Problem.

Ref: M. L. Khodra, "Beyond Classical Search: Genetic Algorithm," YouTube, 2021.
Inherits from algorithms.base.LocalSearch.
"""

from __future__ import annotations

from typing import Any, ClassVar

from algorithms.base import LocalSearch


class GeneticAlgorithm(LocalSearch):
    name: ClassVar[str] = "genetic_algorithm"
    aliases: ClassVar[tuple[str, ...]] = ("ga", "genetic")
    default_params: ClassVar[dict[str, Any]] = {
        "population_size": 30,
        "generations": 60,
        "crossover_rate": 0.8,
        "mutation_rate": 0.2,
        "tournament_size": 3,
        "elitism": 2,
    }

    def _tournament_select(self, population: list[Any], fitness: list[float]) -> Any:
        k = min(int(self.params["tournament_size"]), len(population))
        contenders = self.rng.sample(range(len(population)), k)
        winner = max(contenders, key=lambda idx: fitness[idx])
        return population[winner]

    def _crossover(self, parent1: Any, parent2: Any) -> tuple[Any, Any]:
        """Uniform crossover at the package placement level."""
        if self.rng.random() > float(self.params["crossover_rate"]):
            return parent1, parent2

        is_state_model = hasattr(parent1, "placements")
        if is_state_model:
            from core.models import State
            p1 = list(parent1.placements)
            p2 = list(parent2.placements)
            c1_items = []
            c2_items = []
            for i in range(len(p1)):
                if self.rng.random() < 0.5:
                    c1_items.append(p1[i])
                    c2_items.append(p2[i])
                else:
                    c1_items.append(p2[i])
                    c2_items.append(p1[i])
            return State(self.problem.ids, tuple(c1_items)), State(self.problem.ids, tuple(c2_items))
        else:
            p1 = list(parent1)
            p2 = list(parent2)
            c1_items = []
            c2_items = []
            for i in range(len(p1)):
                if self.rng.random() < 0.5:
                    c1_items.append(p1[i])
                    c2_items.append(p2[i])
                else:
                    c1_items.append(p2[i])
                    c2_items.append(p1[i])
            return tuple(c1_items), tuple(c2_items)

    def _mutate(self, individual: Any) -> Any:
        """Mutate individual using core neighbor generator."""
        if self.rng.random() < float(self.params["mutation_rate"]):
            mutated, _ = self.random_neighbor(individual)
            return mutated
        return individual

    def _search(self) -> tuple[Any, Any]:
        pop_size = int(self.params["population_size"])
        generations = int(self.params["generations"])
        elitism_count = max(0, min(int(self.params["elitism"]), pop_size))

        # Initial population
        population: list[Any] = [self.random_state() for _ in range(pop_size)]
        fitness: list[float] = [self.objective(ind) for ind in population]

        best_idx = max(range(pop_size), key=lambda i: fitness[i])
        initial_best = population[best_idx]
        best_overall = initial_best
        best_overall_score = fitness[best_idx]

        # Record generation 0
        self.iterations = 0
        self.record("objective", float(best_overall_score))
        self.record("max", float(max(fitness)))
        self.record("avg", float(sum(fitness) / pop_size))

        for gen in range(1, generations + 1):
            ranked_indices = sorted(range(pop_size), key=lambda i: fitness[i], reverse=True)
            new_population: list[Any] = [population[i] for i in ranked_indices[:elitism_count]]

            while len(new_population) < pop_size:
                p1 = self._tournament_select(population, fitness)
                p2 = self._tournament_select(population, fitness)
                c1, c2 = self._crossover(p1, p2)
                c1 = self._mutate(c1)
                new_population.append(c1)
                if len(new_population) < pop_size:
                    c2 = self._mutate(c2)
                    new_population.append(c2)

            population = new_population
            fitness = [self.objective(ind) for ind in population]

            gen_best_idx = max(range(pop_size), key=lambda i: fitness[i])
            if fitness[gen_best_idx] > best_overall_score:
                best_overall = population[gen_best_idx]
                best_overall_score = fitness[gen_best_idx]

            self.iterations = gen
            self.record("objective", float(best_overall_score))
            self.record("max", float(max(fitness)))
            self.record("avg", float(sum(fitness) / pop_size))

        self.extra["population_size"] = pop_size
        self.extra["generations"] = generations

        return initial_best, best_overall
