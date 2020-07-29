from cardparser import Gems, load_deck
from solver import State


def test_state_repr():
    st = State()
    assert repr(st) == 'Gems((0, 0, 0, 0, 0))'

    deck = load_deck()
    st = State(gems=Gems((1, 2, 0, 0, 3)), cards=(deck[40], deck[5], deck[21]))
    assert st.cards == (deck[5], deck[21], deck[40])
    assert repr(st) == 'Gems((1, 2, 0, 0, 3)) 0W12-1B4-2W5'
