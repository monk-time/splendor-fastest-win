from collections import deque
from itertools import permutations
from typing import List, Tuple

from buys import get_buys
from cardparser import Card, Gems, sort_cards
from consts import GOAL_PTS, MAX_GEMS


class State:
    def __init__(self, gems=None, cards=None):
        self.gems: Gems = gems if gems else Gems((0, 0, 0, 0, 0))
        # Cards are guaranteed to be sorted by sort_cards().
        self.cards: Tuple[Card, ...] = tuple(cards) if cards else ()
        self.cards = sort_cards(self.cards)

    def __repr__(self):  # a string representation for printing
        if self.cards:
            return f'{self.gems} {"-".join(str(c) for c in self.cards)}'
        else:
            return repr(self.gems)

    def isgoal(self):
        return sum(card.pt for card in self.cards) >= GOAL_PTS

    from_supply_3: List[Gems] = list(map(Gems, set(permutations((1, 1, 1, 0, 0)))))
    from_supply_2: List[Gems] = list(map(Gems, set(permutations((2, 0, 0, 0, 0)))))

    def __iter__(self):
        # Possible actions:
        # 1. Buy 1 card
        for card in get_buys()[self.gems]:
            # Can't buy the same card twice
            if card in self.cards:
                continue
            # Player's deck always remains sorted
            yield State(gems=self.gems - card.cost,
                        cards=sort_cards((*self.cards, card)))

        # 2. Take 3 different chips (5*4*3 / 3! = 10 options)
        for comb in self.from_supply_3:
            gems = self.gems + comb
            # TODO: delete extra chips
            # TODO: use distinct_permutations (extract into a function)
            yield State(gems=gems, cards=self.cards)
        # 3. Take 2 chips of the same color (5 options)

    def solve(self, depth_first=False):
        queue = deque([self])
        trail = {repr(self): None}
        add_to_queue = queue.append if depth_first else queue.appendleft

        puzzle = self
        while not puzzle.isgoal():
            for next_step in puzzle:
                hash_ = repr(next_step)
                if hash_ in trail:
                    continue
                trail[hash_] = puzzle
                add_to_queue(next_step)
            puzzle = queue.pop()

        solution = deque()
        while puzzle:
            solution.appendleft(puzzle)
            puzzle = trail[repr(puzzle)]

        return list(solution)


if __name__ == '__main__':
    pass
