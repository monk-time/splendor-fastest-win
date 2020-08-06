from gems import subtract_with_bonus, take_gems


def test_take_gems():
    combs = list(take_gems([0, 0, 0, 0, 0]))
    assert len(combs) == 15
    assert combs == [
        [1, 1, 1, 0, 0],
        [1, 1, 0, 1, 0],
        [1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 0, 1],
        [0, 1, 0, 1, 1],
        [0, 0, 1, 1, 1],
        [2, 0, 0, 0, 0],
        [0, 2, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 2, 0],
        [0, 0, 0, 0, 2]
    ]

    combs = list(take_gems([6, 0, 0, 0, 0]))
    assert len(combs) == 14
    assert combs == [
        [7, 1, 1, 0, 0],
        [7, 1, 0, 1, 0],
        [7, 1, 0, 0, 1],
        [7, 0, 1, 1, 0],
        [7, 0, 1, 0, 1],
        [7, 0, 0, 1, 1],
        [6, 1, 1, 1, 0],
        [6, 1, 1, 0, 1],
        [6, 1, 0, 1, 1],
        [6, 0, 1, 1, 1],
        [6, 2, 0, 0, 0],
        [6, 0, 2, 0, 0],
        [6, 0, 0, 2, 0],
        [6, 0, 0, 0, 2]
    ]
    assert len(list(take_gems([0, 6, 0, 0, 0]))) == 14
    assert len(list(take_gems([0, 0, 6, 0, 0]))) == 14
    assert len(list(take_gems([0, 0, 0, 6, 0]))) == 14
    assert len(list(take_gems([0, 0, 0, 0, 6]))) == 14

    combs = list(take_gems([6, 6, 0, 0, 0]))
    assert len(combs) == 13
    assert len(list(take_gems([6, 0, 6, 0, 0]))) == 13
    assert len(list(take_gems([6, 0, 0, 0, 6]))) == 13
    assert len(list(take_gems([0, 6, 6, 0, 0]))) == 13
    assert len(list(take_gems([0, 0, 6, 0, 6]))) == 13

    combs = list(take_gems([7, 0, 0, 0, 0]))
    assert len(combs) == 8
    assert combs == [
        [7, 1, 1, 1, 0],
        [7, 1, 1, 0, 1],
        [7, 1, 0, 1, 1],
        [7, 0, 1, 1, 1],
        [7, 2, 0, 0, 0],
        [7, 0, 2, 0, 0],
        [7, 0, 0, 2, 0],
        [7, 0, 0, 0, 2]
    ]
    assert len(list(take_gems([0, 0, 7, 0, 0]))) == 8
    assert len(list(take_gems([0, 0, 0, 0, 7]))) == 8

    combs = list(take_gems([7, 7, 0, 0, 0]))
    assert len(combs) == 4
    assert combs == [
        [7, 7, 1, 1, 1],
        [7, 7, 2, 0, 0],
        [7, 7, 0, 2, 0],
        [7, 7, 0, 0, 2]
    ]
    assert len(list(take_gems([7, 0, 0, 0, 7]))) == 4
    assert len(list(take_gems([0, 7, 0, 7, 0]))) == 4
    assert len(list(take_gems([0, 0, 0, 7, 7]))) == 4

    combs = list(take_gems([7, 7, 7, 0, 0]))
    assert len(combs) == 3
    assert combs == [
        [7, 7, 7, 1, 1],
        [7, 7, 7, 2, 0],
        [7, 7, 7, 0, 2]
    ]
    assert len(list(take_gems([7, 7, 0, 0, 7]))) == 3
    assert len(list(take_gems([0, 7, 7, 7, 0]))) == 3
    assert len(list(take_gems([0, 0, 7, 7, 7]))) == 3

    combs = list(take_gems([7, 7, 7, 7, 0]))
    assert len(combs) == 2
    assert combs == [
        [7, 7, 7, 7, 1],
        [7, 7, 7, 7, 2]
    ]
    assert len(list(take_gems([7, 7, 7, 0, 7]))) == 2
    assert len(list(take_gems([0, 7, 7, 7, 7]))) == 2

    combs = list(take_gems([7, 7, 7, 7, 7]))
    assert len(combs) == 0
    assert combs == []

    combs = list(take_gems([4, 6, 1, 7, 0]))
    assert len(combs) == 7
    assert combs == [
        [5, 7, 2, 7, 0],
        [5, 7, 1, 7, 1],
        [5, 6, 2, 7, 1],
        [4, 7, 2, 7, 1],
        [6, 6, 1, 7, 0],
        [4, 6, 3, 7, 0],
        [4, 6, 1, 7, 2]
    ]


def test_subtract_with_bonus():
    assert subtract_with_bonus(gems=[1, 2, 0, 3, 1],
                               cost=[1, 0, 0, 2, 1],
                               bonus=[0, 1, 0, 1, 3]) == [0, 2, 0, 2, 1]
