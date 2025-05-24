import random


class WFC1D:
    def __init__(self, length, rules, probabilities):
        self.length = length
        self.rules = rules
        self.probabilities = probabilities
        self.positions = [set(rules.keys()) for _ in range(length)]
        self.collapsed = [None] * length

    def entropy(self, options):
        # Shannon entropy approx based on probabilities
        import math

        total_prob = sum(self.probabilities[o] for o in options)
        if total_prob == 0 or len(options) == 1:
            return 0
        entropy = 0
        for o in options:
            p = self.probabilities[o] / total_prob
            entropy -= p * math.log(p)
        return entropy

    def get_lowest_entropy_pos(self):
        min_entropy = float("inf")
        candidates = []
        for i, opts in enumerate(self.positions):
            if self.collapsed[i] is not None:
                continue
            e = self.entropy(opts)
            if e < min_entropy and len(opts) > 0:
                min_entropy = e
                candidates = [i]
            elif e == min_entropy:
                candidates.append(i)
        if not candidates:
            return None
        return random.choice(candidates)

    def collapse(self, pos):
        opts = list(self.positions[pos])
        weights = [self.probabilities[o] for o in opts]
        chosen = random.choices(opts, weights)[0]
        self.positions[pos] = {chosen}
        self.collapsed[pos] = chosen
        return chosen

    def propagate(self, start_pos):
        # Propagate constraints forward and backward
        stack = [start_pos]
        while stack:
            pos = stack.pop()
            val = next(iter(self.positions[pos]))

            # Propagate forward
            if pos + 1 < self.length and self.collapsed[pos + 1] is None:
                before = set(self.positions[pos + 1])
                allowed = {
                    o for o in before if o not in self.rules[val].get("no_next", [])
                }
                if allowed != before:
                    self.positions[pos + 1] = allowed
                    if len(allowed) == 1:
                        self.collapsed[pos + 1] = next(iter(allowed))
                        stack.append(pos + 1)

            # Propagate backward
            if pos - 1 >= 0 and self.collapsed[pos - 1] is None:
                before = set(self.positions[pos - 1])
                allowed = {
                    o for o in before if val not in self.rules[o].get("no_next", [])
                }
                if allowed != before:
                    self.positions[pos - 1] = allowed
                    if len(allowed) == 1:
                        self.collapsed[pos - 1] = next(iter(allowed))
                        stack.append(pos - 1)

    def enforce_repeat_limits(self):
        # This is a bit more complex because repetition is sequential.
        # You could implement this as a post-processing step or more advanced propagation.
        pass

    def run(self):
        while True:
            pos = self.get_lowest_entropy_pos()
            if pos is None:
                break  # done or no positions left

            chosen = self.collapse(pos)
            self.propagate(pos)

        if None in self.collapsed:
            raise RuntimeError("Failed to fully collapse: no valid solutions")

        return self.collapsed


def generate_random_number(
    target_keys: list[int], weights: list[int], length: int
) -> int:
    return random.choices(target_keys, weights=weights, k=length)
