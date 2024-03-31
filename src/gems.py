from collections.abc import Iterable
from functools import cache, partial
from itertools import chain, product

from more_itertools import distinct_permutations

from src.color import COLOR_NUM, Color

MAX_GEMS = 7

Gems = tuple[int, ...]
GemSets = tuple[Gems, ...]

all_gem_sets: GemSets = tuple(product(range(MAX_GEMS + 1), repeat=COLOR_NUM))


def uniq_perms_for_all(patterns: GemSets) -> GemSets:
    """Combine all unique permutations into one tuple."""
    return tuple(chain(*map(distinct_permutations, patterns)))


patterns_take_3_at = {
    '7': uniq_perms_for_all(((1, 1, 1, 0, 0),)),
    '8': uniq_perms_for_all(((1, 1, 1, -1, 0), (1, 1, 0, 0, 0))),
    '9': uniq_perms_for_all((
        (1, 1, 1, -1, -1),
        (1, 1, -1, 0, 0),
        (1, 0, 0, 0, 0),
    )),
    '10': uniq_perms_for_all(((1, 1, -1, -1, 0), (1, -1, 0, 0, 0))),
}

patterns_take_2_at = {
    '8': uniq_perms_for_all(((2, 0, 0, 0, 0),)),
    '9': uniq_perms_for_all(((2, -1, 0, 0, 0),)),
    '10': uniq_perms_for_all(((2, -1, -1, 0, 0), (2, -2, 0, 0, 0))),
}


def add(g1: Gems, g2: Gems) -> Gems:
    return (
        g1[0] + g2[0],
        g1[1] + g2[1],
        g1[2] + g2[2],
        g1[3] + g2[3],
        g1[4] + g2[4],
    )


def is_valid(g: Gems) -> bool:
    return all(0 <= x <= MAX_GEMS for x in g)


def take_by_patterns(
    g: Gems, patterns: GemSets, *, check_for_2: bool = False
) -> Iterable[Gems]:
    for p in patterns:
        # Rule: add 2 only if there are at least 4 tokens left of that color
        # In case of solo play this means if a player has no more than 6
        if check_for_2:
            i = p.index(2)
            if g[i] > MAX_GEMS - 4:
                continue
        g2 = add(g, p)
        if is_valid(g2):
            yield g2


def factory(patterns: GemSets, *, check_for_2: bool = False):
    return partial(
        take_by_patterns, patterns=patterns, check_for_2=check_for_2
    )


take_3_at_7 = factory(patterns_take_3_at['7'])
take_3_at_8 = factory(patterns_take_3_at['8'])
take_3_at_9 = factory(patterns_take_3_at['9'])
take_3_at_10 = factory(patterns_take_3_at['10'])
# Patterns for take_2_* should not repeat patterns for take_3
take_2_at_8 = factory(patterns_take_2_at['8'], check_for_2=True)
take_2_at_9 = factory(patterns_take_2_at['9'], check_for_2=True)
take_2_at_10 = factory(patterns_take_2_at['10'], check_for_2=True)


def take_gems(g: Gems) -> Iterable[Gems]:
    total = sum(g)
    if total > 10:
        return

    # Take 3 gems of different colors (if possible)
    # Rule: a player must have no more than 10 gems at the end of the turn,
    # else they must return gems (old or newly taken) until they have 10.
    if total <= 7:
        yield from take_3_at_7(g)
    elif total == 8:
        yield from take_3_at_8(g)
    elif total == 9:
        yield from take_3_at_9(g)
    elif total == 10:
        yield from take_3_at_10(g)

    # Take 2 gems of the same color
    if total <= 8:
        yield from take_2_at_8(g)
    elif total == 9:
        yield from take_2_at_9(g)
    elif total == 10:
        yield from take_2_at_10(g)


@cache
def get_takes() -> dict[Gems, tuple[Gems, ...]]:
    return {g: tuple(take_gems(g)) for g in all_gem_sets}


def subtract_with_bonus(
    gems: Gems, cost: Gems, bonus: Gems
) -> tuple[Gems, int]:
    # Assuming this function is never called with cost > gems
    # gems - (cost - bonus)
    res = []
    saved = 0
    for i in range(COLOR_NUM):
        c = cost[i] - bonus[i]
        if c < 0:
            c = 0
        if c < cost[i]:
            saved += cost[i] - c
        g = gems[i] - c
        if g < 0:
            g = 0
        res.append(g)
    return tuple(res), saved


single_gem_hands = (
    (1, 0, 0, 0, 0),
    (0, 1, 0, 0, 0),
    (0, 0, 1, 0, 0),
    (0, 0, 0, 1, 0),
    (0, 0, 0, 0, 1),
)


@cache
def increase_bonus(bonus: Gems, color: Color) -> Gems:
    return add(bonus, single_gem_hands[color.value])
