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

    @classmethod
    def from_row(cls, row: List[str]) -> 'Card':
        *cost, pt, bonus = row
        return Card(cost=tuple(int(x) for x in cost),
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


@lru_cache(maxsize=None)
def get_deck() -> Cards:
    return load_deck()


def sort_cards(cards: Iterable[Card]) -> Cards:
    """Sort a deck of cards by total cost, then by points,
    then by card cost as a tuple, then by color."""
    key = lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus.value)
    return tuple(sorted(cards, key=key))


if __name__ == '__main__':
    deck = load_deck()
    for card in deck:
        print(card, repr(card))
