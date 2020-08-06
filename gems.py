from typing import Iterable, List

from color import COLOR_NUM

MAX_GEMS = 7

Gems = List[int]


def take_gems(g: Gems) -> Iterable[Gems]:
    slots = [i for i in range(COLOR_NUM) if g[i] < MAX_GEMS]
    n_slots = len(slots)
    # Take 3 gems of different colors (if possible)
    if not n_slots:
        return
    if n_slots < 3:
        for i in slots:
            g[i] += 1
        yield g[:]
        for i in slots:
            g[i] -= 1
    else:
        # Each cycle is guaranteed to run at least once
        for i in range(n_slots - 2):
            g[slots[i]] += 1
            for j in range(i + 1, n_slots - 1):
                g[slots[j]] += 1
                for k in range(j + 1, n_slots):
                    g[slots[k]] += 1
                    yield g[:]
                    g[slots[k]] -= 1
                g[slots[j]] -= 1
            g[slots[i]] += -1

    # Take 2 gems of the same color
    for i in range(COLOR_NUM):
        # Rule: only if there are at least four tokens left of that color
        if g[i] <= MAX_GEMS - 4:
            g[i] += 2
            yield g[:]
            g[i] -= 2


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
    return res
