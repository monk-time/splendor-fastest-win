import csv
from dataclasses import dataclass
from typing import List, Tuple

Gems = Tuple[int, ...]
COLORS = ('White', 'Blue', 'Green', 'Red', 'Black')


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: int


def parse_card(row: List[str]) -> Card:
    *cost, pt, bonus = row
    return Card(cost=tuple(int(x) if x else 0 for x in cost),
                pt=int(pt) if pt else 0,
                bonus=COLORS.index(bonus))


def load_deck() -> List[Card]:
    with open('cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [parse_card(row) for row in reader]
    cards.sort(key=lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus))
    return cards
