import pytest

from cardparser import load_deck
from solver import State

deck = load_deck()


@pytest.fixture
def state1():
    st = State.newgame()
    for card in (deck[40], deck[5], deck[21]):
        st = st.buy_card(card)
    st.gems = (1, 2, 0, 0, 3)
    return st


def test_state_newgame(state1):
    st = State.newgame()
    assert st.cards == tuple()
    assert st.bonus == (0, 0, 0, 0, 0)

    assert state1.bonus == (2, 1, 0, 0, 0)


def test_state_buy_card():
    st = State.newgame()
    st.gems = (4, 3, 0, 7, 2)

    st = st.buy_card(deck[40])
    assert st == State(cards=(deck[40],),
                       bonus=(1, 0, 0, 0, 0), gems=(4, 3, 0, 2, 2),
                       turn=1, pts=2)

    st = st.buy_card(deck[5])
    assert st == State(cards=(deck[5], deck[40]),
                       bonus=(2, 0, 0, 0, 0), gems=(4, 3, 0, 0, 1),
                       turn=2, pts=2)

    st = st.buy_card(deck[57])
    assert st == State(cards=(deck[5], deck[40], deck[57]),
                       bonus=(2, 0, 1, 0, 0), gems=(2, 1, 0, 0, 0),
                       turn=3, pts=4)


def test_state_repr(state1):
    st = State.newgame()
    assert repr(st) == '(0, 0, 0, 0, 0)'

    assert state1.cards == (deck[5], deck[21], deck[40])
    assert repr(state1) == '(1, 2, 0, 0, 3) 0W12-1B4-2W5'


def test_state_iter(state1):
    next_steps = set(str(st) for st in state1)
    assert next_steps == {
        '(1, 0, 0, 0, 3) 0W3-0W12-1B4-2W5',
        '(1, 2, 0, 0, 0) 0B3-0W12-1B4-2W5',
        '(0, 2, 0, 0, 3) 0R3-0W12-1B4-2W5',
        '(1, 2, 0, 0, 1) 0W12-0B12-1B4-2W5',
        '(1, 2, 0, 0, 3) 0W12-0G12-1B4-2W5',
        '(1, 1, 0, 0, 1) 0W12-0W22-1B4-2W5',
        '(0, 2, 0, 0, 2) 0W12-1B4-0W113-2W5',
        '(1, 0, 0, 0, 1) 0W12-1B4-2W5-1G223',
        '(2, 3, 1, 0, 3) 0W12-1B4-2W5',
        '(2, 3, 0, 1, 3) 0W12-1B4-2W5',
        '(2, 3, 0, 0, 4) 0W12-1B4-2W5',
        '(2, 2, 1, 1, 3) 0W12-1B4-2W5',
        '(2, 2, 1, 0, 4) 0W12-1B4-2W5',
        '(2, 2, 0, 1, 4) 0W12-1B4-2W5',
        '(1, 3, 1, 1, 3) 0W12-1B4-2W5',
        '(1, 3, 1, 0, 4) 0W12-1B4-2W5',
        '(1, 3, 0, 1, 4) 0W12-1B4-2W5',
        '(1, 2, 1, 1, 4) 0W12-1B4-2W5',
        '(3, 2, 0, 0, 3) 0W12-1B4-2W5',
        '(1, 4, 0, 0, 3) 0W12-1B4-2W5',
        '(1, 2, 2, 0, 3) 0W12-1B4-2W5',
        '(1, 2, 0, 2, 3) 0W12-1B4-2W5',
        '(1, 2, 0, 0, 5) 0W12-1B4-2W5',
    }


def test_state_solve3():
    solution = [str(st) for st in State.newgame().solve(goal_pts=3)]
    assert solution == [
        '(0, 0, 0, 0, 0)',
        '(1, 1, 1, 0, 0)',
        '(3, 1, 1, 0, 0)',
        '(5, 1, 1, 0, 0)',
        '(6, 2, 2, 0, 0)',
        '(0, 2, 2, 0, 0) 3W6'
    ]


def test_state_solve4():
    solution = [str(st) for st in State.newgame().solve(goal_pts=4)]
    # assert solution == [
    #     '(0, 0, 0, 0, 0)',
    #     '(1, 1, 1, 0, 0)',
    #     '(2, 2, 2, 0, 0)',
    #     '(3, 3, 3, 0, 0)',
    #     '(4, 3, 4, 0, 1)',
    #     '(0, 1, 4, 0, 0) 2G124',
    #     '(0, 1, 0, 0, 0) 2G5-2G124'
    # ]
    assert solution == [
        '(0, 0, 0, 0, 0)',
        '(1, 1, 1, 0, 0)',
        '(3, 1, 1, 0, 0)',
        '(5, 1, 1, 0, 0)',
        '(6, 2, 2, 0, 0)',
        '(7, 1, 1, 1, 0)',
        '(0, 1, 1, 1, 0) 4B7'
    ]
