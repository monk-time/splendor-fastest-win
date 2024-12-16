#!/usr/bin/env python

"""A tool to bruteforce fastest winning moves for the board game Splendor."""

import argparse
import sys

from src.buys import export_buys_to_txt, load_buys
from src.color import Color
from src.solver import State


def cli():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'goal_pts',
        help='target amount of points',
        nargs='?',
        type=int,
    )
    parser.add_argument(
        '-u',
        '--use_heuristic',
        help='use a heuristic formula to limit the search space of BFS',
        action='store_true',
    )
    parser.add_argument(
        '-b',
        '--buys',
        help='regenerate and store all possible buys',
        action='store_true',
    )
    parser.add_argument(
        '-e',
        '--export',
        help='export possible buys to a .txt file',
        action='store_true',
    )
    if len(sys.argv) == 1:  # no arguments given
        parser.print_help()
        parser.exit()
    args = parser.parse_args()
    try:
        if args.export:
            export_buys_to_txt()
            return
        if args.buys:
            load_buys(update=True)
        if args.goal_pts:
            solution = State.newgame().solve(
                goal_pts=args.goal_pts,
                use_heuristic=args.use_heuristic,
            )
            print('\nSolution:')
            print(f'({", ".join(c.name.title() for c in Color)}) Cards')
            for state in solution:
                print(state)
    except KeyboardInterrupt:
        print('Execution stopped by the user.')
        parser.exit()


if __name__ == '__main__':
    cli()
