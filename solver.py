from collections import deque
from itertools import product
from typing import List

from cardparser import Gems, Card, COLORS, load_deck

MAX_GEMS = 7
GOAL_PTS = 15


def possible_buys(deck: List[Card]):
    gem_combs = product(range(MAX_GEMS + 1), repeat=len(COLORS))
    less_or_equal = lambda t1, t2: all(i <= j for i, j in zip(t1, t2))
    get_buys = lambda comb: [c for c in deck if less_or_equal(c.cost, comb)]
    return {comb: get_buys(comb) for comb in gem_combs}


deck = load_deck()
buys = possible_buys(deck)


class State:
    def __init__(self, gems: Gems = None, cards: List[Card] = None):
        self.gems = gems if gems else (0, 0, 0, 0, 0)
        self.cards = cards if cards else []

    def __repr__(self):  # a string representation for printing
        return f'{self.gems} {"-".join(str(c) for c in self.cards)}'

    def canonical(self):  # a string representation after adjusting for symmetry
        return f'{self.gems} {"-".join(sorted(str(c) for c in self.cards))}'

    def isgoal(self):
        return sum(card.pt for card in self.cards) == GOAL_PTS

    def __iter__(self):
        pass

    def solve(self, depth_first=False):
        queue = deque([self])
        trail = {self.canonical(): None}
        load = queue.append if depth_first else queue.appendleft

        puzzle = self
        while not puzzle.isgoal():
            for next_step in puzzle:
                c = next_step.canonical()
                if c in trail:
                    continue
                trail[c] = puzzle
                load(next_step)
            puzzle = queue.pop()

        solution = deque()
        while puzzle:
            solution.appendleft(puzzle)
            puzzle = trail[puzzle.canonical()]

        return list(solution)


if __name__ == '__main__':
    st = State(cards=[deck[40], deck[5], deck[21]])
    print(repr(st))
    print(st.canonical())

# import pprint
# with open('temp.txt', mode='w') as f:
#     f.write(pprint.pformat(buys))
# import pickle
# with open('data.pickle', 'wb') as f:
#     pickle.dump(buys, f, pickle.HIGHEST_PROTOCOL)

"""
15 turns
either:
buy 1 card
take 3 chips - 10 options
take 2 chips - 5 options
"""
