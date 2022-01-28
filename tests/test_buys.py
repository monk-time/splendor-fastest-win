from buys import BUYS_PATH, load_buys, possible_buys, store_buys
from cardparser import get_deck
from color import COLOR_NUM
from gems import MAX_GEMS

buys = possible_buys()


def test_possible_buys():
    assert len(buys) == (MAX_GEMS + 1) ** COLOR_NUM

    deck = get_deck()
    assert len(buys[(7, 7, 7, 7, 7)]) == len(deck)

    buy_ids = lambda t: [deck[c].str_id for c in buys[t]]
    assert buy_ids((0, 0, 0, 0, 0)) == []
    assert buy_ids((0, 0, 0, 0, 2)) == []
    assert buy_ids((0, 4, 0, 0, 0)) == ['0W3', '1K4']
    assert buy_ids((0, 0, 0, 2, 4)) == ['0B3', '0W12', '1G4']
    assert buy_ids((4, 4, 0, 1, 0)) == ['0W3', '0R3', '0G12', '0K122', '1R4', '1K4']


def test_store_buys():
    store_buys(buys)
    assert BUYS_PATH.exists()
    assert BUYS_PATH.stat().st_size > 1_000_000


def test_load_buys():
    buys_unpickled = load_buys()
    assert buys == buys_unpickled
