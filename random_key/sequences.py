import random
import time
from collections import defaultdict, Counter
import math
from dataclasses import dataclass, field
from PySide6 import QtCore


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


@dataclass
class ItemSequence:
    item_name: str
    bound_key: str
    probability: int
    max_entropy: int
    min_entropy: int
    avoids: list

    def avoid(self, other):
        self.avoids.append(other)


def weighted_bool_from_range(start: int, end: int) -> bool:
    length = end - start + 1
    probability = 1 / length
    return random.random() < probability


class BlockSequence(QtCore.QObject):

    item_added = QtCore.Signal(str)
    stopped = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.items: list[ItemSequence] = []
        self.length: int = 1
        self._items: dict[str, ItemSequence] = {}

        self._running = False
        self._stop_flag = False

    def set_params(self, items, length):
        self.items = items
        self.length = length
        self._items: dict[str, ItemSequence] = {i.item_name: i for i in items}

    def stop(self):

        self._stop_flag = True

    @property
    def running(self):

        return self._running

    def run(self):

        self._stop_flag = False
        self._running = True

        sequence = []
        index = 1

        # Initialise a starting item
        target_keys = [i.item_name for i in self.items]
        weights = [i.probability for i in self.items]
        current_item = random.choices(target_keys, weights=weights, k=1)[0]

        min_item_entropy = self._items[current_item].min_entropy
        max_item_entropy = self._items[current_item].max_entropy
        current_avoids = self._items[current_item].avoids

        last_item = None
        last_item_avoids = []

        # slight delay so the UI Responds nicely
        signal_delay = 0.0001

        sequence.append(current_item)
        self.item_added.emit(current_item)
        while len(sequence) <= self.length - 1 and not self._stop_flag:

            # Check that current item does not neighbour last item
            if last_item not in current_avoids and current_item not in last_item_avoids:

                # add item if we below min entropy
                if index <= min_item_entropy:
                    sequence.append(current_item)
                    self.item_added.emit(current_item)
                    index += 1
                    time.sleep(signal_delay)
                    continue

                elif index <= max_item_entropy:

                    if weighted_bool_from_range(min_item_entropy, max_item_entropy):
                        index = 1000000
                        last_item = current_item
                        last_item_avoids = current_avoids
                    else:
                        sequence.append(current_item)
                        self.item_added.emit(current_item)
                        index += 1
                        time.sleep(signal_delay)
                    continue

                else:
                    last_item = current_item
                    last_item_avoids = current_avoids

            # Reset current item so it's not the same as the last item
            # Also Respect the items probability too.
            while current_item := random.choices(target_keys, weights=weights, k=1)[0]:
                if current_item != last_item:
                    break

            min_item_entropy = self._items[current_item].min_entropy
            max_item_entropy = self._items[current_item].max_entropy
            current_avoids = self._items[current_item].avoids
            index = 1

        if self._stop_flag:
            self.stopped.emit()

        self._running = False

        self.finished.emit()
        print("Finished")
