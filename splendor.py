import csv
from dataclasses import dataclass
from itertools import chain
from pprint import pprint
from typing import List, Tuple

from more_itertools import chunked

Gems = Tuple[int, ...]
COLORS = ('White', 'Blue', 'Green', 'Red', 'Black')


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: int
    total: int


def parse_card(row: List[str]) -> Card:
    *cost, pt, bonus = row
    cost: Gems = tuple(int(x) if x else 0 for x in cost)
    pt = int(pt) if pt else 0
    bonus = COLORS.index(bonus)
    return Card(cost, pt, bonus, sum(cost))


def load_cards() -> List[Card]:
    with open('cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [parse_card(row) for row in reader]
    cards.sort(key=lambda c: (c.total, c.pt, sorted(c.cost), c.bonus))
    return cards


def split_n(n: int, bins: int, res: List[int] = None):
    if res is None:
        res: List[int] = []
    partial_sum = sum(res)
    for i in range(n - partial_sum + 1):
        res_new = res + [i]
        if bins > 2:
            yield from split_n(n, bins - 1, res_new)
        else:
            res_new.append(n - partial_sum - i)
            yield res_new


if __name__ == '__main__':
    cards = load_cards()
    for chunk in chunked(cards, 5):
        pprint(chunk)
        print()

"""
15 turns
either:
take 1 card
take three chips - 10 options
take two chips - 5 options
"""
