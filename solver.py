import time
from collections import deque
from itertools import permutations
from typing import List, Tuple

from buys import get_buys
from cardparser import Card, Gems, sort_cards
from consts import COLOR_NUM

GOAL_PTS = 15


class State:
    def __init__(self, cards=None, bonus=None, gems=None, turn=0):
        if cards is None:  # empty state
            cards = ()
            bonus = Gems((0,) * COLOR_NUM)
        elif bonus is None:  # init. from cards
            cards = sort_cards(cards)
            bonus = [0] * COLOR_NUM
            for c in cards:
                bonus[c.bonus.value] += 1
            bonus = Gems(bonus)

        self.cards: Tuple[Card, ...] = cards
        self.bonus: Gems = bonus
        self.gems: Gems = gems if gems else Gems((0,) * COLOR_NUM)
        self.turn: int = turn

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
        for card in get_buys()[self.gems + self.bonus]:
            # Can't buy the same card twice
            if card in self.cards:
                continue
            gems = self.gems - (card.cost - self.bonus)
            cards = sort_cards((*self.cards, card))
            i = card.bonus.value
            bonus = Gems(self.bonus[:i] + (self.bonus[i] + 1,) +
                         self.bonus[i + 1:])
            yield State(cards=cards, bonus=bonus, gems=gems, turn=self.turn + 1)

        # 2. Take 3 different chips (5*4*3 / 3! = 10 options)
        #    or 2 chips of the same color (5 options)
        # Assuming the best scenario, there's no need to track gems
        # in the pool, since we are only limited by the total number
        # of gems in the game.
        for comb in self.from_supply_3 + self.from_supply_2:
            gems = self.gems + comb
            yield State(cards=self.cards, bonus=self.bonus,
                        gems=gems, turn=self.turn + 1)

    def solve(self, depth_first=False):
        queue = deque([self])
        trail = {repr(self): None}
        add_to_queue = queue.append if depth_first else queue.appendleft

        puzzle = self
        turn = 0
        while not puzzle.isgoal():
            for next_step in puzzle:
                hash_ = repr(next_step)
                if hash_ in trail:
                    continue
                trail[hash_] = puzzle
                add_to_queue(next_step)
            puzzle = queue.pop()
            if puzzle.turn > turn:
                turn = puzzle.turn
                print(puzzle.turn, puzzle)

        solution = deque()
        while puzzle:
            solution.appendleft(puzzle)
            puzzle = trail[repr(puzzle)]

        return list(solution)


if __name__ == '__main__':
    start = time.time()
    print(State().solve())
    total = time.time() - start
    print(f'{total:.4g} sec')
