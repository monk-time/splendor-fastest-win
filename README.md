# splendor-fastest-win
An experimental tool to find fastest winning moves using bruteforce for the board game Splendor. It was born after a question on boardgames.stackexchange.com:

[Q: What is the fastest possible game in Splendor?](https://boardgames.stackexchange.com/questions/44948/what-is-the-fastest-possible-game-in-splendor)

The goal of the board game Splendor is to reach 15 points by either taking chips (gems) from the pool or buying cards with gems that give a permament gem bonus - a 1 gem discount for later buys.

<img src="https://github.com/monk-time/splendor-fastest-win/assets/7759622/9baa7e54-dd27-410d-8e86-e5e21c879de3" height="300px"/>

### How to run
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   . venv/Scripts/activate
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   python splendor_fastest_win.py
   ```

### How it works
The tool uses breadth-first search to greedily check all possible move sequences. Optionally you can use a heuristic that limits search space of BFS by using only the most promising game states.

Data for all cards is stored in [cards.csv](cards.csv). Cards are referenced by a string consisting of a card's point value, one-letter color and a sorted list of its non-zero cost values.

Before the first run the tool caches (pickles) a dictionary that lists all cards that can be bought with each set of gems (possible buys).

### Limitations
Unoptimized bruteforce takes way too much memory and is unfeasible beyond 8 moves, but with a `-u` key it can get to 15 moves needed to reach the goal. Further optimization is required.

### Usage
```
usage: splendor_fastest_win.py [-h] [-u] [-b] [-e] [goal_pts]

An experimental tool to find fastest winning moves using bruteforce for the board game Splendor.

positional arguments:
goal_pts             target amount of points

options:
-h, --help           show this help message and exit
-u, --use_heuristic  use a heuristic formula to limit the search space of BFS
-b, --buys           regenerate and store all possible buys
-e, --export         export possible buys to a .txt file
```
