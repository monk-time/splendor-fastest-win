import time
from bisect import insort
from collections import deque

from buys import get_buys
from cardparser import CardNums, get_deck
from color import COLOR_NUM
from gems import Gems, MAX_GEMS, get_takes, increase_bonus, subtract_with_bonus

deck = get_deck()


class State:
    # Based on Raymond Hettinger's generic puzzle solver:
    # https://rhettinger.github.io/puzzle.html

    def __init__(self, cards, bonus, gems, turn, pts):
        self.cards: CardNums = cards
        self.bonus: Gems = bonus
        self.gems: Gems = gems
        self.turn: int = turn
        self.pts: int = pts
        self.hash: int = hash((self.cards, self.gems, self.turn))

    @classmethod
    def newgame(cls) -> 'State':
        no_gems = (0,) * COLOR_NUM
        return State(cards=(), bonus=no_gems, gems=no_gems, turn=0, pts=0)

    def __repr__(self):  # a string representation for printing
        if self.cards:
            return f'{self.gems!r} {"-".join(str(deck[c]) for c in self.cards)}'
        else:
            return f'{self.gems!r}'

    def __hash__(self):
        return self.hash

    def __eq__(self, other) -> bool:
        return self.hash == other.hash

    def buy_card(self, card_num: int) -> 'State':
        # Because the simulation uses pre-generated table of possible buys,
        # this method doesn't check if the player has enough gems to buy a card.
        cards_mut = list(self.cards)
        # noinspection PyArgumentList
        insort(cards_mut, card_num)
        cards = tuple(cards_mut)
        card = deck[card_num]
        bonus = increase_bonus(self.bonus, card.bonus)
        gems = subtract_with_bonus(self.gems, card.cost, self.bonus)
        pts = self.pts + card.pt

        return State(cards=cards, bonus=bonus, gems=gems,
                     turn=self.turn + 1, pts=pts)

    def __iter__(self):
        # Possible actions:
        # 1. Buy 1 card
        key = tuple(min(x + y, MAX_GEMS) for x, y in zip(self.gems, self.bonus))
        for card_num in get_buys()[key]:
            # Can't buy the same card twice
            if card_num in self.cards:
                continue

            yield self.buy_card(card_num)

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
        trail = {self: None}
        add_to_queue = queue.append if depth_first else queue.appendleft

        puzzle = self
        turn = 0
        max_pts = 0
        while puzzle.pts < goal_pts:
            for next_step in puzzle:
                if next_step in trail:
                    continue
                trail[next_step] = puzzle
                add_to_queue(next_step)
            puzzle = queue.pop()
            if puzzle.turn > turn:
                turn = puzzle.turn
                print(f'{turn=}     {puzzle}')
            if puzzle.pts > max_pts:
                max_pts = puzzle.pts
                print(f'{max_pts=}  {puzzle}')

        solution = deque()
        while puzzle:
            solution.appendleft(puzzle)
            puzzle = trail[puzzle]

        return list(solution)


if __name__ == '__main__':
    start = time.time()
    print(State.newgame().solve(goal_pts=4))
    total = time.time() - start
    print(f'{total:.4g} sec')

    # import cProfile
    # cProfile.run('State.newgame().solve(goal_pts=6)')
