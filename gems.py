from itertools import chain, permutations, product
from typing import Dict, Iterable, Tuple

from color import COLOR_NUM

MAX_GEMS = 7

Gems = Tuple[int, ...]


def get_combs(t: Gems) -> Tuple[Gems, ...]:
    return tuple(map(tuple, sorted(set(permutations(t)), reverse=True)))


def add(g1: Gems, g2: Gems) -> Gems:
    return tuple(x + y for x, y in zip(g1, g2))


def is_valid(g: Gems) -> bool:
    return all(0 <= x <= MAX_GEMS for x in g)


skip_neg = True


def gem_getter(patterns: Iterable[Gems], check_for_2: bool = False):
    def take_gems_by_patterns(g: Gems) -> Iterable[Gems]:
        for p in chain(*map(get_combs, patterns)):
            # Optimization: assume that you don't return gems
            # in the optimal solution
            if skip_neg and any(x < 0 for x in p):
                continue
            # Rule: add 2 only if there are at least 4 tokens left of that color
            if check_for_2:
                i = p.index(2)
                if g[i] > MAX_GEMS - 4:
                    continue
            g2 = add(g, p)
            if is_valid(g2):
                yield g2

    return take_gems_by_patterns


take_3_at_7 = gem_getter(((1, 1, 1, 0, 0),))
take_3_at_8 = gem_getter(((1, 1, 1, -1, 0), (1, 1, 0, 0, 0)))
take_3_at_9 = gem_getter(((1, 1, 1, -1, -1), (1, 1, -1, 0, 0), (1, 0, 0, 0, 0)))
take_3_at_10 = gem_getter(((1, 1, -1, -1, 0), (1, -1, 0, 0, 0)))
# Patterns for take_2_* should not repeat patterns for take_3
take_2_at_8 = gem_getter(((2, 0, 0, 0, 0),), check_for_2=True)
take_2_at_9 = gem_getter(((2, -1, 0, 0, 0),), check_for_2=True)
take_2_at_10 = gem_getter(((2, -1, -1, 0, 0), (2, -2, 0, 0, 0)), check_for_2=True)


def take_gems(g: Gems) -> Iterable[Gems]:
    total = sum(g)
    if total > 10:
        return

    # Take 3 gems of different colors (if possible)
    # Rule: a player must have no more than 10 gems at the end of the turn,
    # else they must return gems (either old or newly taken) until they have 10.
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


_takes_cached = None


def get_takes() -> Dict[Gems, Tuple[Gems, ...]]:
    global _takes_cached
    if not _takes_cached:
        _takes_cached = {g: tuple(take_gems(g))
                         for g in product(range(MAX_GEMS + 1), repeat=COLOR_NUM)}
    return _takes_cached


def subtract_with_bonus(gems: Gems, cost: Gems, bonus: Gems) -> Gems:
    # Assuming this function is never called with cost > gems
    # gems - (cost - bonus)
    res = []
    for i in range(COLOR_NUM):
        c = cost[i] - bonus[i]
        if c < 0:
            c = 0
        g = gems[i] - c
        if g < 0:
            g = 0
        res.append(g)
    return tuple(res)
