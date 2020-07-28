import pytest

from cardparser import Card, Color, Gems, load_deck


def test_gems():
    a = Gems((0, 1, 0, 2, 0))
    b = Gems((3, 0, 1, 1, 0))
    assert a + b == Gems((3, 1, 1, 3, 0))
    assert a - b == Gems((-3, 1, -1, 1, 0))
    assert type(a + b) == type(a - b) == Gems
    assert repr(a) == 'Gems((0, 1, 0, 2, 0))'


# CSV header: White,Blue,Green,Red,Black,Pt,Bonus
samples = (
    ('0,0,0,2,1,0,White',
     Card(cost=Gems((0, 0, 0, 2, 1)), pt=0, bonus=Color.WHITE),
     '0W12'),
    ('0,0,0,4,0,1,Blue',
     Card(cost=Gems((0, 0, 0, 4, 0)), pt=1, bonus=Color.BLUE),
     '1B4'),
    ('6,0,0,0,0,3,White',
     Card(cost=Gems((6, 0, 0, 0, 0)), pt=3, bonus=Color.WHITE),
     '3W6'),
    ('0,0,5,3,0,2,Black',
     Card(cost=Gems((0, 0, 5, 3, 0)), pt=2, bonus=Color.BLACK),
     '2K35'),
)


@pytest.mark.parametrize("row, card, card_id", samples)
def test_card_from_row(row, card, card_id):
    assert Card.from_row(row.split(',')) == card


@pytest.mark.parametrize("row, card, card_id", samples)
def test_card_id(row, card, card_id):
    assert card.card_id == card_id


def test_load_deck():
    deck = load_deck()
    assert len(deck) == 90
    assert deck[0] == Card(cost=Gems((0, 3, 0, 0, 0)), pt=0, bonus=Color.WHITE)
    assert deck[-1] == Card(cost=Gems((3, 3, 5, 3, 0)), pt=3, bonus=Color.BLACK)


def test_all_ids_unique():
    deck = load_deck()
    assert len(set(c.card_id for c in deck)) == len(deck)
