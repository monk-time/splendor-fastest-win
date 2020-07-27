import csv
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import List


class Color(Enum):
    WHITE = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    BLACK = 4


class Gems(tuple):
    def __add__(self, other):
        return Gems(map(sum, zip(self, other)))

    def __sub__(self, other):
        return self.__add__(-x for x in other)


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


def load_deck() -> List[Card]:
    with open(Path(__file__).parent / 'cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [Card.from_row(row) for row in reader]
    cards.sort(key=lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus.value))
    return cards


if __name__ == '__main__':
    deck = load_deck()
    for card in deck:
        print(card, repr(card))
