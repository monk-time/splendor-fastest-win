import time
from collections import deque

from buys import get_buys
from cardparser import Card, Cards, sort_cards
from color import COLOR_NUM
from gems import Gems, MAX_GEMS, get_takes, subtract_with_bonus


class State:
    # Based on Raymond Hettinger's generic puzzle solver:
    # https://rhettinger.github.io/puzzle.html

    def __init__(self, cards, bonus, gems, turn, pts):
        self.cards: Cards = cards
        self.bonus: Gems = bonus
        self.gems: Gems = gems
        self.turn: int = turn
        self.pts: int = pts

    @classmethod
    def newgame(cls) -> 'State':
        no_gems = (0,) * COLOR_NUM
        return State(cards=(), bonus=no_gems, gems=no_gems, turn=0, pts=0)

    def __repr__(self):  # a string representation for printing
        if self.cards:
            return f'{self.gems!r} {"-".join(str(c) for c in self.cards)}'
        else:
            return f'{self.gems!r}'

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__

    def buy_card(self, card: Card) -> 'State':
        # Because the simulation uses pre-generated table of possible buys,
        # this method doesn't check if the player has enough gems to buy a card.
        cards = sort_cards((*self.cards, card))
        i = card.bonus.value
        bonus = (self.bonus[:i] + (self.bonus[i] + 1,) + self.bonus[i + 1:])
        gems = subtract_with_bonus(self.gems, card.cost, self.bonus)
        pts = self.pts + card.pt

        return State(cards=cards, bonus=bonus, gems=gems,
                     turn=self.turn + 1, pts=pts)

    def __iter__(self):
        # Possible actions:
        # 1. Buy 1 card
        key = tuple(min(x + y, MAX_GEMS) for x, y in zip(self.gems, self.bonus))
        for card in get_buys()[key]:
            # Can't buy the same card twice
            if card in self.cards:
                continue

            yield self.buy_card(card)

        # 2. Take 3 different chips (5*4*3 / 3! = 10 options)
        #    or 2 chips of the same color (5 options)
        # Assuming the best scenario, there's no need to track gems
        # in the pool, since we are only limited by the total number
        # of gems in the game.
        for gems in get_takes()[self.gems]:
            yield State(cards=self.cards, bonus=self.bonus,
                        gems=gems, turn=self.turn + 1, pts=self.pts)

    def solve(self, depth_first=False, goal_pts: int = 15):
        queue = deque([self])
        trail = {repr(self): None}
        add_to_queue = queue.append if depth_first else queue.appendleft

        puzzle = self
        turn = 0
        max_pts = 0
        while puzzle.pts < goal_pts:
            for next_step in puzzle:
                hash_ = repr(next_step)
                if hash_ in trail:
                    continue
                trail[hash_] = puzzle
                add_to_queue(next_step)
            puzzle = queue.pop()
            if puzzle.turn > turn:
                turn = max(turn, puzzle.turn)
                print(f'{turn=}     {puzzle}')
            if puzzle.pts > max_pts:
                max_pts = max(max_pts, puzzle.pts)
                print(f'{max_pts=}  {puzzle}')

        solution = deque()
        while puzzle:
            solution.appendleft(puzzle)
            puzzle = trail[repr(puzzle)]

        return list(solution)


if __name__ == '__main__':
    start = time.time()
    print(State.newgame().solve(goal_pts=3))
    total = time.time() - start
    print(f'{total:.4g} sec')

    # import cProfile
    # cProfile.run('State.newgame().solve(goal_pts=4)')
