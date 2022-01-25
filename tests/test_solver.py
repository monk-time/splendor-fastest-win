import pytest

from solver import State


@pytest.fixture
def state1():
    st = State.newgame()
    for card in (40, 5, 21):
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

    st = st.buy_card(50)
    assert st == State(cards=(50,),
                       bonus=(1, 0, 0, 0, 0), gems=(4, 3, 0, 2, 2),
                       turn=1, pts=2, saved=0)

    st = st.buy_card(6)
    assert st == State(cards=(6, 50),
                       bonus=(1, 1, 0, 0, 0), gems=(4, 3, 0, 2, 0),
                       turn=2, pts=2, saved=1)

    st = st.buy_card(57)
    assert st == State(cards=(6, 50, 57),
                       bonus=(1, 1, 1, 0, 0), gems=(1, 2, 0, 2, 0),
                       turn=3, pts=4, saved=3)


def test_state_repr(state1):
    st = State.newgame()
    assert repr(st) == '(0, 0, 0, 0, 0)'

    assert state1.cards == (5, 21, 40)
    assert repr(state1) == '(1, 2, 0, 0, 3) 0W12-0B113-1W223'


def test_state_iter(state1):
    next_steps = set(str(st) for st in state1)
    assert next_steps == {
        '(2, 3, 0, 1, 3) 0W12-0B113-1W223',
        '(2, 2, 0, 1, 4) 0W12-0B113-1W223',
        '(1, 3, 1, 1, 3) 0W12-0B113-1W223',
        '(1, 2, 1, 1, 4) 0W12-0B113-1W223',
        '(1, 1, 0, 0, 1) 0W12-0W22-0B113-1W223',
        '(0, 2, 0, 0, 2) 0W12-0W113-0B113-1W223',
        '(2, 3, 1, 0, 3) 0W12-0B113-1W223',
        '(2, 2, 1, 0, 4) 0W12-0B113-1W223',
        '(1, 2, 0, 0, 3) 0W12-0G12-0B113-1W223',
        '(1, 4, 0, 0, 3) 0W12-0B113-1W223',
        '(1, 2, 0, 2, 3) 0W12-0B113-1W223',
        '(0, 2, 0, 0, 3) 0R3-0W12-0B113-1W223',
        '(3, 2, 0, 0, 3) 0W12-0B113-1W223',
        '(1, 2, 0, 0, 5) 0W12-0B113-1W223',
        '(1, 2, 0, 0, 0) 0B3-0W12-0B113-1W223',
        '(1, 0, 0, 0, 3) 0W3-0W12-0B113-1W223',
        '(2, 3, 0, 0, 4) 0W12-0B113-1W223',
        '(1, 0, 0, 0, 1) 0W12-0B113-1W223-1G223',
        '(1, 2, 0, 0, 1) 0W12-0B12-0B113-1W223',
        '(2, 2, 1, 1, 3) 0W12-0B113-1W223',
        '(1, 3, 1, 0, 4) 0W12-0B113-1W223',
        '(1, 2, 2, 0, 3) 0W12-0B113-1W223',
        '(1, 3, 0, 1, 4) 0W12-0B113-1W223'
    }


def test_state_solve3():
    solution = [str(st) for st in State.newgame().solve(goal_pts=3)]
    assert solution == [
        '(0, 0, 0, 0, 0)',
        '(0, 0, 1, 1, 1)',
        '(0, 0, 1, 1, 3)',
        '(0, 0, 1, 1, 5)',
        '(0, 0, 2, 2, 6)',
        '(0, 0, 2, 2, 0) 3K6'
    ]

# def test_state_solve4():
#     solution = [str(st) for st in State.newgame().solve(goal_pts=4)]
#     assert solution == [
#         '(0, 0, 0, 0, 0)',
#         '(0, 0, 1, 1, 1)',
#         '(0, 0, 1, 1, 3)',
#         '(0, 0, 1, 1, 5)',
#         '(0, 0, 2, 2, 6)',
#         '(0, 0, 0, 1, 6) 0K12',
#         '(0, 0, 0, 1, 0) 0K12-4W7'
#     ]
