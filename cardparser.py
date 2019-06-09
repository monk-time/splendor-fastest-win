import csv
from dataclasses import dataclass
from typing import List

COLORS = ('White', 'Blue', 'Green', 'Red', 'Black')
COLORS_SHORT = ('W', 'B', 'G', 'R', 'K')


class Gems(tuple):
    def __add__(self, other):
        return Gems(map(sum, zip(self, other)))

    def __sub__(self, other):
        return self.__add__(-x for x in other)


@dataclass(frozen=True)
class Card:
    cost: Gems
    pt: int
    bonus: int
    id: str

    def __str__(self):
        return self.id


def parse_card(row: List[str]) -> Card:
    *cost, pt, bonus = row
    card_id = ''.join([
        pt,
        COLORS_SHORT[COLORS.index(bonus)],
        ''.join(sorted(x for x in cost if x != "0")),
    ])
    return Card(cost=Gems(int(x) for x in cost),
                pt=int(pt),
                bonus=COLORS.index(bonus),
                id=card_id)


def load_deck() -> List[Card]:
    with open('cards.csv', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # skip the header
        cards = [parse_card(row) for row in reader]
    cards.sort(key=lambda c: (sum(c.cost), c.pt, sorted(c.cost), c.bonus))
    return cards


if __name__ == '__main__':
    deck = load_deck()
    for card in deck:
        print(card)
