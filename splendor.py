import csv
from dataclasses import dataclass
from itertools import product
from typing import List, Tuple

Gems = Tuple[int, ...]
COLORS = ('White', 'Blue', 'Green', 'Red', 'Black')
MAX_GEMS = 7


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


def load_cards() -> List[Card]:
    with open('cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [parse_card(row) for row in reader]
    cards.sort(key=lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus))
    return cards


def possible_buys(cards: List[Card]):
    # a = list(chain.from_iterable(map(tuple, split_n(i, 5)) for i in range(5)))
    gem_combs = product(range(MAX_GEMS + 1), repeat=len(COLORS))
    less_or_equal = lambda t1, t2: all(i <= j for i, j in zip(t1, t2))
    get_buys = lambda comb: [c for c in cards if less_or_equal(c.cost, comb)]
    return {comb: get_buys(comb) for comb in gem_combs}


if __name__ == '__main__':
    cards_ = load_cards()
    buys = possible_buys(cards_)
    # import pprint
    # with open('temp.txt', mode='w') as f:
    #     f.write(pprint.pformat(buys))
    # import pickle
    # with open('data.pickle', 'wb') as f:
    #     pickle.dump(buys, f, pickle.HIGHEST_PROTOCOL)

"""
15 turns
either:
take 1 card
take three chips - 10 options
take two chips - 5 options
"""
