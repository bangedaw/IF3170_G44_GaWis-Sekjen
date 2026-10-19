from __future__ import annotations

from algorithms.base import LocalSearch
from core.models import State


class GeneticAlgorithm(LocalSearch):
    name = "genetic_algorithm"
    aliases = ("ga", "genetic")
    default_params = {
        "population_size": 30,
        "generations": 60,
        "crossover_rate": 0.8,
        "mutation_rate": 0.2,
        "tournament_size": 3,
        "elitism": 2,
    }

    def _tournament_select(self, population: list[State], fitness: list[float]) -> State:
        k = min(int(self.params["tournament_size"]), len(population))
        contenders = self.rng.sample(range(len(population)), k)
        winner = max(contenders, key=lambda idx: fitness[idx])
        return population[winner]

    def _crossover(self, parent1, parent2):
        if self.rng.random() > float(self.params["crossover_rate"]):
            return parent1, parent2

        a_items = list(parent1.placements) if hasattr(parent1, "placements") else list(parent1)
        b_items = list(parent2.placements) if hasattr(parent2, "placements") else list(parent2)
        items1, items2 = [], []
        for a, b in zip(a_items, b_items):
            if self.rng.random() < 0.5:
                items1.append(a)
                items2.append(b)
            else:
                items1.append(b)
                items2.append(a)
        if not hasattr(parent1, "placements"):
            return tuple(items1), tuple(items2)
        return (State(self.problem.ids, tuple(items1)),
                State(self.problem.ids, tuple(items2)))

    def _mutate(self, individual):
        if self.rng.random() < float(self.params["mutation_rate"]):
            mutated, _ = self.random_neighbor(individual)
            return mutated
        return individual

    def _search(self) -> tuple[State, State]:
        pop_size = int(self.params["population_size"])
        generations = int(self.params["generations"])
        elitism_count = max(0, min(int(self.params["elitism"]), pop_size))

        population: list[State] = [self.random_state() for _ in range(pop_size)]
        fitness: list[float] = [self.objective(ind) for ind in population]

        best_idx = max(range(pop_size), key=lambda i: fitness[i])
        initial_best = population[best_idx]
        best_overall: State = initial_best
        best_overall_score: float = fitness[best_idx]

        self.iterations = 0
        self.record("objective", float(best_overall_score))
        self.record("max", float(max(fitness)))
        self.record("avg", float(sum(fitness) / pop_size))

        for gen in range(1, generations + 1):
            ranked = sorted(range(pop_size), key=lambda i: fitness[i], reverse=True)
            new_population: list[State] = [population[i] for i in ranked[:elitism_count]]

            while len(new_population) < pop_size:
                c1, c2 = self._crossover(
                    self._tournament_select(population, fitness),
                    self._tournament_select(population, fitness),
                )
                new_population.append(self._mutate(c1))
                if len(new_population) < pop_size:
                    new_population.append(self._mutate(c2))

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
