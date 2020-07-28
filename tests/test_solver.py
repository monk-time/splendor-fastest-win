from cardparser import COLOR_NUM, Gems, load_deck
from solver import BUYS_PATH, MAX_GEMS, load_buys, possible_buys, store_buys

buys = possible_buys()


def test_possible_buys():
    assert len(buys) == (MAX_GEMS + 1) ** COLOR_NUM

    deck = load_deck()
    assert len(buys[Gems((7, 7, 7, 7, 7))]) == len(deck)

    buy_ids = lambda t: [c.card_id for c in buys[Gems(t)]]
    assert buy_ids((0, 0, 0, 0, 0)) == []
    assert buy_ids((0, 0, 0, 0, 2)) == []
    assert buy_ids((0, 4, 0, 0, 0)) == ['0W3', '1K4']
    assert buy_ids((0, 0, 0, 2, 4)) == ['0B3', '0W12', '1G4']
    assert buy_ids((4, 4, 0, 1, 0)) == ['0W3', '0R3', '0G12', '1R4', '1K4', '0K122']


def test_store_buys():
    store_buys(buys)
    assert BUYS_PATH.exists()
    assert BUYS_PATH.stat().st_size > 1_000_000


def test_load_buys():
    buys_unpickled = load_buys()
    assert buys == buys_unpickled