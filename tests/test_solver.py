import pytest

from cardparser import Gems, load_deck
from solver import State

deck = load_deck()


@pytest.fixture
def state1():
    return State(cards=(deck[40], deck[5], deck[21]), gems=Gems((1, 2, 0, 0, 3)))


def test_state_init(state1):
    st = State()
    assert st.cards == tuple()
    assert st.bonus == Gems((0, 0, 0, 0, 0))

    assert state1.bonus == Gems((2, 1, 0, 0, 0))


def test_state_repr(state1):
    st = State()
    assert repr(st) == 'Gems((0, 0, 0, 0, 0))'

    assert state1.cards == (deck[5], deck[21], deck[40])
    assert repr(state1) == 'Gems((1, 2, 0, 0, 3)) 0W12-1B4-2W5'
