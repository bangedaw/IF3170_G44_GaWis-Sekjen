from algorithms.base import LocalSearch


class RandomWalk(LocalSearch):
    name = "random_walk"
    aliases = ("rw",)
    default_params = {"steps": 5}

    def _search(self):
        current = initial = self.random_state()
        self.record("objective", self.objective(current))
        for _ in range(self.params["steps"]):
            current, _ = self.random_neighbor(current)
            self.iterations += 1
            self.record("objective", self.objective(current))
        return initial, current
