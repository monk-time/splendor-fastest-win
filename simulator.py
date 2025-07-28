"""
Splendor Board State Simulator

This module provides functionality to generate random Splendor board states
and analyze solution statistics using the solver, with support for parallel processing.
"""
import random
import time
import multiprocessing as mp
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from collections import defaultdict, deque
import statistics
import argparse
import os

from src.solver import State, deck, COLOR_NUM
from src.cardparser import Card, get_deck
from src.color import Color

# Constants for simulation
DEFAULT_NUM_SIMULATIONS = 1000
DEFAULT_GOAL_POINTS = 15

# 2-player game constants
INITIAL_GEMS = {
    Color.WHITE: 4,
    Color.BLUE: 4,
    Color.GREEN: 4,
    Color.RED: 4,
    Color.BLACK: 4,
    'gold': 5  # Gold (jokers)
}

# Number of cards per tier for 2 players
CARDS_PER_TIER = {
    1: 4,  # Tier 1 cards
    2: 4,  # Tier 2 cards
    3: 3,  # Tier 3 cards
}

# Number of nobles for 2 players
NOBLES_COUNT = 3

@dataclass
class BoardState:
    """Represents the complete game state for a 2-player Splendor game."""
    available_gems: Dict[Color, int]
    available_gold: int
    tier1_cards: List[Card]
    tier2_cards: List[Card]
    tier3_cards: List[Card]
    nobles: List[Card]
    
    def __str__(self):
        gems = ', '.join(f'{c.name}:{self.available_gems[c]}' for c in Color)
        return f"Gems: {gems}, Gold: {self.available_gold}\n" \
               f"T1: {[str(c) for c in self.tier1_cards]}\n" \
               f"T2: {[str(c) for c in self.tier2_cards]}\n" \
               f"T3: {[str(c) for c in self.tier3_cards]}\n" \
               f"Nobles: {[str(n) for n in self.nobles]}"

@dataclass
class SimulationResult:
    """Container for simulation results."""
    turns_to_win: List[int]
    avg_turns: float
    median_turns: float
    std_dev: float
    min_turns: int
    max_turns: int
    time_taken: float
    board_states: List[BoardState] = None


def get_cards_by_tier() -> Dict[int, List[Card]]:
    """Group all cards by their tier."""
    cards_by_tier = {1: [], 2: [], 3: []}
    for card in get_deck():
        if card.pt in [0, 1, 2]:
            cards_by_tier[1].append(card)
        elif card.pt in [3, 4]:
            cards_by_tier[2].append(card)
        else:  # card.pt >= 5
            cards_by_tier[3].append(card)
    return cards_by_tier

def generate_random_board_state() -> BoardState:
    """Generate a random valid 2-player Splendor board state."""
    # Initialize available gems
    available_gems = {color: INITIAL_GEMS[color] for color in Color}
    available_gold = INITIAL_GEMS['gold']
    
    # Get all cards grouped by tier
    cards_by_tier = get_cards_by_tier()
    
    # Randomly select cards for each tier
    selected_cards = {}
    for tier, count in CARDS_PER_TIER.items():
        selected = random.sample(cards_by_tier[tier], min(count, len(cards_by_tier[tier])))
        selected_cards[tier] = selected
    
    # Get all nobles (cards with 3+ points)
    nobles = [card for card in get_deck() if card.pt >= 3]
    selected_nobles = random.sample(nobles, min(NOBLES_COUNT, len(nobles)))
    
    return BoardState(
        available_gems=available_gems,
        available_gold=available_gold,
        tier1_cards=selected_cards[1],
        tier2_cards=selected_cards[2],
        tier3_cards=selected_cards[3],
        nobles=selected_nobles
    )

def board_state_to_initial_state(board: BoardState) -> State:
    """Convert a BoardState to the initial State for the solver."""
    # For now, we'll just return a new game state
    # In a more advanced version, we could initialize with the board state
    return State.newgame()


def simulate_game(goal_pts: int = DEFAULT_GOAL_POINTS, 
                 use_heuristic: bool = True, 
                 board: Optional[BoardState] = None,
                 verbose: bool = True) -> Tuple[int, Optional[BoardState]]:
    """
    Simulate a single game with the given parameters.
    
    Args:
        goal_pts: Points needed to win
        use_heuristic: Whether to use heuristic search
        board: Optional pre-generated board state
        verbose: Whether to print detailed turn information
        
    Returns:
        Tuple of (turns_taken, board_state_used)
    """
    # Generate a new random board if none provided
    if board is None:
        board = generate_random_board_state()
    
    if verbose:
        print("\n=== Initial Board State ===")
        print(board)
    
    # Convert the board state to initial solver state
    initial_state = board_state_to_initial_state(board)
    
    # Solve the game and get the solution path
    try:
        if not verbose:
            # Suppress output from the solver
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            solution = initial_state.solve(goal_pts=goal_pts, use_heuristic=use_heuristic)
            
            # Restore stdout
            sys.stdout = old_stdout
        else:
            solution = initial_state.solve(goal_pts=goal_pts, use_heuristic=use_heuristic)
            
        turns = len(solution) - 1  # Subtract 1 for initial state
        
        if verbose:
            print(f"\n=== Simulation Complete ===")
            print(f"Turns to reach {goal_pts} points: {turns}")
            print("-" * 40)
            
        return (turns, board)
        
    except Exception as e:
        if not verbose:
            # Restore stdout if we were suppressing output
            if 'old_stdout' in locals():
                sys.stdout = old_stdout
        print(f"Error during simulation: {e}")
        return (-1, board)


def worker(args):
    """Worker function for parallel processing."""
    goal_pts, use_heuristic, _, verbose = args
    return simulate_game(goal_pts, use_heuristic, verbose=verbose)

def run_simulations(num_simulations: int = DEFAULT_NUM_SIMULATIONS,
                  goal_pts: int = DEFAULT_GOAL_POINTS,
                  use_heuristic: bool = True,
                  num_workers: Optional[int] = None,
                  verbose: bool = True) -> SimulationResult:
    """
    Run multiple simulations in parallel and collect statistics.
    
    Args:
        num_simulations: Number of simulations to run
        goal_pts: Points needed to win
        use_heuristic: Whether to use heuristic search
        num_workers: Number of worker processes to use (default: min(CPU cores, num_simulations))
        
    Returns:
        SimulationResult with statistics and board states
    """
    start_time = time.time()
    
    if num_workers is None:
        num_workers = min(os.cpu_count() or 4, num_simulations)  # Don't use more workers than simulations
    else:
        num_workers = min(num_workers, num_simulations)
    
    print(f"Running {num_simulations} simulations across {num_workers} workers...")
    
    # Prepare arguments for workers
    args = [(goal_pts, use_heuristic, i, verbose) for i in range(num_simulations)]
    
    # Use a process pool for parallel execution
    with mp.Pool(processes=num_workers) as pool:
        # Initialize progress tracking
        completed = 0
        turns = []
        board_states = []
        
        # Process results as they complete
        for i, (turns_taken, board_state) in enumerate(pool.imap_unordered(worker, args)):
            if turns_taken > 0:  # Only count successful simulations
                turns.append(turns_taken)
                board_states.append(board_state)
            
            # Update progress
            completed = i + 1
            if completed % 10 == 0 or completed == num_simulations:
                print(f"\rCompleted {completed}/{num_simulations} simulations...", end="")
    
    # Calculate statistics
    time_taken = time.time() - start_time
    print()  # New line after progress updates
    
    return SimulationResult(
        turns_to_win=turns,
        avg_turns=statistics.mean(turns) if turns else float('nan'),
        median_turns=statistics.median(turns) if turns else float('nan'),
        std_dev=statistics.stdev(turns) if len(turns) > 1 else 0,
        min_turns=min(turns) if turns else -1,
        max_turns=max(turns) if turns else -1,
        time_taken=time_taken,
        board_states=board_states
    )


def print_simulation_results(result: SimulationResult, show_boards: int = 3):
    """Print the results of the simulation in a readable format.
    
    Args:
        result: The simulation results to print
        show_boards: Number of board states to display (0 for none, -1 for all)
    """
    print("\n=== Simulation Results ===")
    print(f"Number of simulations: {len(result.turns_to_win)}")
    print(f"Average turns to win: {result.avg_turns:.2f}")
    print(f"Median turns to win: {result.median_turns}")
    print(f"Standard deviation: {result.std_dev:.2f}")
    print(f"Minimum turns: {result.min_turns}")
    print(f"Maximum turns: {result.max_turns}")
    print(f"Time taken: {result.time_taken:.2f} seconds")
    
    # Show sample board states if available
    if result.board_states and show_boards != 0:
        print("\n=== Sample Board States ===")
        num_boards = len(result.board_states) if show_boards == -1 else min(show_boards, len(result.board_states))
        
        for i in range(num_boards):
            print(f"\nBoard {i+1} (Turns to win: {result.turns_to_win[i] if i < len(result.turns_to_win) else 'N/A'}")
            print("-" * 40)
            print(result.board_states[i])
            
        if num_boards < len(result.board_states):
            print(f"\n... and {len(result.board_states) - num_boards} more board states not shown.")
    
    print("\n" + "=" * 50 + "\n")


def main():
    """Main function to run the simulator from command line."""
    parser = argparse.ArgumentParser(description='Run Splendor simulations in parallel')
    parser.add_argument('-n', '--num-simulations', type=int, default=DEFAULT_NUM_SIMULATIONS,
                       help=f'Number of simulations to run (default: {DEFAULT_NUM_SIMULATIONS})')
    parser.add_argument('-p', '--goal-points', type=int, default=DEFAULT_GOAL_POINTS,
                       help=f'Points needed to win (default: {DEFAULT_GOAL_POINTS})')
    parser.add_argument('-w', '--workers', type=int, default=None,
                       help='Number of worker processes (default: min(CPU cores, num_simulations))')
    parser.add_argument('--no-heuristic', action='store_false', dest='use_heuristic',
                       help='Disable heuristic search (uses full BFS)')
    parser.add_argument('--show-boards', type=int, default=3,
                       help='Number of board states to display (0 for none, -1 for all, default: 3)')
    parser.add_argument('--quiet', action='store_false', dest='verbose',
                       help='Suppress detailed output for each simulation')
    
    args = parser.parse_args()
    
    print(f"Starting {args.num_simulations} simulations with goal of {args.goal_points} points...")
    if args.use_heuristic:
        print("Using heuristic search (faster but may not find optimal solution)")
    else:
        print("Using full BFS (slower but finds optimal solution)")
    
    if args.workers is None:
        num_workers = min(os.cpu_count() or 4, args.num_simulations)
        print(f"Using {num_workers} worker processes")
    else:
        num_workers = min(args.workers, args.num_simulations)
        print(f"Using {num_workers} worker processes")
    
    # Generate a sample board state to show
    print("\n=== Sample Initial Board State ===")
    sample_board = generate_random_board_state()
    print(sample_board)
    print("=" * 40 + "\n")
    
    result = run_simulations(
        num_simulations=args.num_simulations,
        goal_pts=args.goal_points,
        use_heuristic=args.use_heuristic,
        num_workers=num_workers,
        verbose=args.verbose
    )
    
    print_simulation_results(result, show_boards=args.show_boards)


if __name__ == "__main__":
    main()
