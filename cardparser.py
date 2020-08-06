import csv
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Iterable, List, Tuple

from consts import Color, MAX_GEMS


class Gems(tuple):
    def __add__(self, other) -> 'Gems':
        # Any gem value of a card or a player's stash can never exceed MAX_GEMS
        return Gems(min(x + y, MAX_GEMS) for x, y in zip(self, other))

    def __sub__(self, other) -> 'Gems':
        # Any gem value of a card or a player's stash can never go below 0
        return Gems(max(x - y, 0) for x, y in zip(self, other))

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: Color

    @classmethod
    def from_row(cls, row: List[str]) -> 'Card':
        *cost, pt, bonus = row
        return Card(cost=Gems(int(x) for x in cost),
                    pt=int(pt),
                    bonus=Color[bonus.upper()])

    @cached_property
    def card_id(self) -> str:
        """A card's id consists of the card's point value, one-letter color
        and a sorted list of its non-zero cost values."""
        bonus_short = self.bonus.name[0] if self.bonus is not Color.BLACK else 'K'
        nonzero_costs = ''.join(sorted(str(x) for x in self.cost if x))
        return ''.join((str(self.pt), bonus_short, nonzero_costs))

    def __str__(self):
        return self.card_id


Cards = Tuple[Card, ...]


def load_deck() -> Cards:
    with open(Path(__file__).parent / 'cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [Card.from_row(row) for row in reader]
    return sort_cards(cards)


def sort_cards(cards: Iterable[Card]) -> Cards:
    """Sort a deck of cards by total cost, then by points,
    then by card cost as a tuple, then by color."""
    key = lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus.value)
    return tuple(sorted(cards, key=key))


if __name__ == '__main__':
    deck = load_deck()
    for card in deck:
        print(card, repr(card))
