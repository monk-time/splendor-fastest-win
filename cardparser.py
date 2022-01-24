import csv
from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Iterable, List, Tuple

from color import Color
from gems import Gems


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: Color
    num: int

    @classmethod
    def from_row(cls, row: List[str], num: int) -> 'Card':
        *cost, pt, bonus = row
        return Card(cost=tuple(int(x) for x in cost),
                    pt=int(pt),
                    bonus=Color[bonus.upper()],
                    num=num)

    @cached_property
    def card_id(self) -> str:
        """Unique card id consists of the card's point value, one-letter color
        and a sorted list of its non-zero cost values."""
        bonus_short = self.bonus.name[0] if self.bonus is not Color.BLACK else 'K'
        nonzero_costs = ''.join(sorted(str(x) for x in self.cost if x))
        return ''.join((str(self.pt), bonus_short, nonzero_costs))

    def __str__(self):
        return self.card_id

    def __hash__(self):
        return self.num

    def __eq__(self, other):
        return self.num == other.num


Deck = Tuple[Card, ...]


def load_deck() -> Deck:
    with open(Path(__file__).parent / 'cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = tuple(Card.from_row(row, i) for i, row in enumerate(reader))
    return cards


@lru_cache(maxsize=None)
def get_deck() -> Deck:
    return load_deck()


def sort_cards(cards: Iterable[Card]) -> Deck:
    """Sort a deck of cards by total cost, then by points,
    then by card cost as a tuple, then by color."""
    key = lambda c: (c.pt, sum(c.cost), sorted(c.cost), c.bonus.value)
    return tuple(sorted(cards, key=key))


if __name__ == '__main__':
    deck = load_deck()
    for card in deck:
        print(card, repr(card))
