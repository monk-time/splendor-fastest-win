import pickle
from functools import lru_cache
from pathlib import Path
from typing import Dict

from cardparser import CardNums, get_deck
from gems import Gems, all_gem_sets

BUYS_PATH = Path(__file__).parent / 'buys.pickle'

Buys = Dict[Gems, CardNums]


def possible_buys() -> Buys:
    deck = get_deck()
    less_or_equal = lambda t1, t2: all(i <= j for i, j in zip(t1, t2))
    gen_buys = lambda g: (c.num for c in deck if less_or_equal(c.cost, g))
    return {g: tuple(gen_buys(g)) for g in all_gem_sets}


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


@lru_cache(maxsize=None)
def get_buys() -> Buys:
    return load_buys()


if __name__ == '__main__':
    buys = load_buys(update=True)
    with open('buys.txt', mode='w') as f:
        print('Writing buys to a text file...')
        for g in buys:
            f.write(f'{g}: {buys[g]}\n')
