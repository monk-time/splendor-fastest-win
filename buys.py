import pickle
from itertools import product
from pathlib import Path
from typing import Dict, List

from cardparser import Card, Gems, load_deck
from consts import COLOR_NUM, MAX_GEMS

BUYS_PATH = Path(__file__).parent / 'buys.pickle'

Buys = Dict[Gems, List[Card]]


def possible_buys() -> Buys:
    deck = load_deck()
    gem_combs = map(Gems, product(range(MAX_GEMS + 1), repeat=COLOR_NUM))
    less_or_equal = lambda t1, t2: all(i <= j for i, j in zip(t1, t2))
    get_buys = lambda comb: [c for c in deck if less_or_equal(c.cost, comb)]
    return {comb: get_buys(comb) for comb in gem_combs}


def store_buys(buys: Buys):
    with open(BUYS_PATH, 'wb') as f:
        pickle.dump(buys, f, pickle.HIGHEST_PROTOCOL)


def load_buys(update: bool = False) -> Buys:
    if not BUYS_PATH.exists() or update:
        print('Generating buys...')
        buys = possible_buys()
        print('Pickling buys...')
        store_buys(buys)
        print('Pickling finished.')
        return buys

    with open(BUYS_PATH, 'rb') as f:
        print('Unpickling buys...')
        return pickle.load(f)


_buys_cached = None


def get_buys() -> Buys:
    global _buys_cached
    if not _buys_cached:
        _buys_cached = load_buys()
    return _buys_cached


if __name__ == '__main__':
    import pprint

    buys = load_buys(update=True)
    with open('buys.txt', mode='w') as f:
        print('Writing buys to a text file...')
        f.write(pprint.pformat(buys))
