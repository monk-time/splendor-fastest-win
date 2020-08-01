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


def test_state_iter(state1):
    next_steps = set(str(st) for st in state1)
    assert next_steps == {
        'Gems((1, 0, 0, 0, 3)) 0W3-0W12-1B4-2W5',
        'Gems((1, 2, 0, 0, 0)) 0B3-0W12-1B4-2W5',
        'Gems((0, 2, 0, 0, 3)) 0R3-0W12-1B4-2W5',
        'Gems((1, 2, 0, 0, 1)) 0W12-0B12-1B4-2W5',
        'Gems((1, 2, 0, 0, 3)) 0W12-0G12-1B4-2W5',
        'Gems((1, 1, 0, 0, 1)) 0W12-0W22-1B4-2W5',
        'Gems((0, 2, 0, 0, 2)) 0W12-1B4-0W113-2W5',
        'Gems((1, 0, 0, 0, 1)) 0W12-1B4-2W5-1G223',
        'Gems((2, 3, 1, 0, 3)) 0W12-1B4-2W5',
        'Gems((2, 3, 0, 1, 3)) 0W12-1B4-2W5',
        'Gems((2, 3, 0, 0, 4)) 0W12-1B4-2W5',
        'Gems((2, 2, 1, 1, 3)) 0W12-1B4-2W5',
        'Gems((2, 2, 1, 0, 4)) 0W12-1B4-2W5',
        'Gems((2, 2, 0, 1, 4)) 0W12-1B4-2W5',
        'Gems((1, 3, 1, 1, 3)) 0W12-1B4-2W5',
        'Gems((1, 3, 1, 0, 4)) 0W12-1B4-2W5',
        'Gems((1, 3, 0, 1, 4)) 0W12-1B4-2W5',
        'Gems((1, 2, 1, 1, 4)) 0W12-1B4-2W5',
        'Gems((3, 2, 0, 0, 3)) 0W12-1B4-2W5',
        'Gems((1, 4, 0, 0, 3)) 0W12-1B4-2W5',
        'Gems((1, 2, 2, 0, 3)) 0W12-1B4-2W5',
        'Gems((1, 2, 0, 2, 3)) 0W12-1B4-2W5',
        'Gems((1, 2, 0, 0, 5)) 0W12-1B4-2W5',
    }
