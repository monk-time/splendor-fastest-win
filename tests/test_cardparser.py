from random import shuffle

import pytest

from src.cardparser import Card, Color, load_deck, sort_cards

# CSV header: White,Blue,Green,Red,Black,Pt,Bonus
samples = (
    (
        '0,0,0,2,1,0,White',
        Card(cost=(0, 0, 0, 2, 1), pt=0, bonus=Color.WHITE, index=0),
        '0W12',
    ),
    (
        '0,0,0,4,0,1,Blue',
        Card(cost=(0, 0, 0, 4, 0), pt=1, bonus=Color.BLUE, index=0),
        '1B4',
    ),
    (
        '6,0,0,0,0,3,White',
        Card(cost=(6, 0, 0, 0, 0), pt=3, bonus=Color.WHITE, index=0),
        '3W6',
    ),
    (
        '0,0,5,3,0,2,Black',
        Card(cost=(0, 0, 5, 3, 0), pt=2, bonus=Color.BLACK, index=0),
        '2K35',
    ),
)


@pytest.mark.parametrize('row, card, card_id', samples)
def test_card_from_row(row, card, card_id):  # noqa: ARG001
    assert Card.from_row(row.split(','), 0) == card


@pytest.mark.parametrize('row, card, card_id', samples)
def test_card_id(row, card, card_id):  # noqa: ARG001
    assert card.str_id == card_id


deck = load_deck()


def test_load_deck():
    assert len(deck) == 90
    assert deck[0] == Card(
        cost=(0, 3, 0, 0, 0), pt=0, bonus=Color.WHITE, index=0
    )
    assert deck[-1] == Card(
        cost=(3, 3, 5, 3, 0), pt=3, bonus=Color.BLACK, index=89
    )


def test_all_ids_unique():
    assert len({c.str_id for c in deck}) == len(deck)


def test_sort_cards():
    d = {str(c): c for c in deck}
    # Sort by points
    cards = (d['0W3'], d['0W22'], d['0W113'], d['1W223'], d['3W6'])
    assert sort_cards(cards[i] for i in (4, 2, 1, 3, 0)) == cards
    # Then by total cost
    cards = (
        d['0W22'],
        d['1W4'],
        d['1W223'],
        d['2W124'],
        d['3W3335'],
        d['4W7'],
    )
    assert sort_cards(cards[i] for i in (1, 0, 4, 3, 5, 2)) == cards
    # Then by card cost as a tuple
    cards = (d['0W22'], d['0W1111'], d['0W113'], d['0W122'], d['0W1112'])
    assert sort_cards(cards[i] for i in (0, 1, 4, 2, 3)) == cards
    # Then by color
    cards = (d['0W3'], d['0B3'], d['0G3'], d['0R3'], d['0K3'])
    assert sort_cards(cards[i] for i in (3, 1, 4, 2, 0)) == cards
    # Full randomized check
    indices = [0, 5, 10, 16, 17, 25, 32, 41, 50, 64, 78, 89]
    cards = tuple(deck[i] for i in indices)
    shuffle(indices.copy())
    assert sort_cards(deck[i] for i in indices) == cards
