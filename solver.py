from bisect import insort
from random import randint

from buys import get_buys
from cardparser import CardIndices, get_deck
from color import COLOR_NUM
from gems import MAX_GEMS, Gems, get_takes, increase_bonus, subtract_with_bonus

deck = get_deck()


class State:
    # Based on Raymond Hettinger's generic puzzle solver:
    # https://rhettinger.github.io/puzzle.html

    def __init__(self, cards, bonus, gems, pts, saved):
        self.cards: CardIndices = cards
        self.bonus: Gems = bonus
        self.gems: Gems = gems
        self.pts: int = pts
        self.saved: int = saved
        self.hash: int = hash((self.cards, self.gems))

    @classmethod
    def newgame(cls) -> 'State':
        no_gems = (0,) * COLOR_NUM
        return State(cards=(), bonus=no_gems, gems=no_gems, pts=0, saved=0)

    def __repr__(self):  # a string representation for printing
        if self.cards:
            return (
                f'{self.gems!r} {"-".join(str(deck[c]) for c in self.cards)}'
            )
        return f'{self.gems!r}'

    def __hash__(self):
        return self.hash

    def __eq__(self, other) -> bool:
        return self.hash == other.hash

    def buy_card(self, card_num: int) -> 'State':
        # Because the simulation uses pre-generated table of possible buys,
        # this method doesn't check if player has enough gems to buy a card.
        cards_mut = list(self.cards)
        # noinspection PyArgumentList
        insort(cards_mut, card_num)
        cards = tuple(cards_mut)
        card = deck[card_num]
        bonus = increase_bonus(self.bonus, card.bonus)
        gems, saved = subtract_with_bonus(self.gems, card.cost, self.bonus)

        return State(
            cards=cards,
            bonus=bonus,
            gems=gems,
            pts=self.pts + card.pt,
            saved=self.saved + saved,
        )

    def __iter__(self):
        # Possible actions:
        # 1. Buy 1 card
        g1, g2, g3, g4, g5 = self.gems
        b1, b2, b3, b4, b5 = self.bonus
        key = (
            min(g1 + b1, MAX_GEMS),
            min(g2 + b2, MAX_GEMS),
            min(g3 + b3, MAX_GEMS),
            min(g4 + b4, MAX_GEMS),
            min(g5 + b5, MAX_GEMS),
        )
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
            yield State(
                cards=self.cards,
                bonus=self.bonus,
                gems=gems,
                pts=self.pts,
                saved=self.saved,
            )

    def solve(
        self, goal_pts: int = 15, use_heuristic: bool = False
    ) -> list['State']:
        queue = [self]
        trail = {self: None}
        heuristic = (
            lambda st: (st.saved**0.4) * (st.pts**2.5)
            + randint(1, 100) * 0.01
        )

        puzzle = self
        turn = 0
        max_pts = 0
        while queue:
            print(f'{turn=:<10} {queue[0]}')
            next_queue = []
            for puzzle in queue:
                if puzzle.pts > max_pts:
                    max_pts = puzzle.pts
                    print(f'{max_pts=:<7} {puzzle}')
                if puzzle.pts >= goal_pts:
                    next_queue.clear()
                    break
                for next_step in puzzle:
                    if next_step in trail:
                        continue
                    trail[next_step] = puzzle
                    next_queue.append(next_step)

            queue = (
                sorted(next_queue, key=heuristic, reverse=True)[:300_000]
                if use_heuristic
                else next_queue
            )
            turn += 1

        solution = []
        while puzzle:
            solution.append(puzzle)
            puzzle = trail[puzzle]

        return list(reversed(solution))
