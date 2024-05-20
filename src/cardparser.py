import csv
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache, cached_property
from pathlib import Path

from src.color import Color
from src.gems import Gems

CardIndex = int
CardIndices = tuple[CardIndex, ...]
Deck = tuple['Card', ...]

DECK_PATH = Path(__file__).parent.parent / 'cards.csv'


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: Color
    index: int

    @classmethod
    def from_row(cls, row: list[str], index: CardIndex) -> 'Card':
        *cost, pt, bonus = row
        return Card(
            cost=tuple(int(x) for x in cost),
            pt=int(pt),
            bonus=Color[bonus.upper()],
            index=index,
        )

    @cached_property
    def str_id(self) -> str:
        """Get a unique card id.

        It consists of the card's point value, one-letter color
        and a sorted list of its non-zero cost values.
        """
        bonus_short = (
            self.bonus.name[0] if self.bonus is not Color.BLACK else 'K'
        )
        nonzero_costs = ''.join(sorted(str(x) for x in self.cost if x))
        return ''.join((str(self.pt), bonus_short, nonzero_costs))

    def __str__(self):
        return self.str_id

    def __hash__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index


def load_deck() -> Deck:
    with DECK_PATH.open(encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        return tuple(Card.from_row(row, i) for i, row in enumerate(reader))


@cache
def get_deck() -> Deck:
    return load_deck()


def sort_cards(cards: Iterable[Card]) -> Deck:
    """Get a sorted a deck of cards.

    The deck is sorted by total cost, then by points,
    then by card cost as a tuple, then by color.
    """
    key = lambda c: (c.pt, sum(c.cost), sorted(c.cost), c.bonus.value)
    return tuple(sorted(cards, key=key))
