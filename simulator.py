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
    tier1_deck: List[Card] = None
    tier2_deck: List[Card] = None
    tier3_deck: List[Card] = None
    
    def __post_init__(self):
        # Initialize decks if not provided
        if self.tier1_deck is None:
            self.tier1_deck = []
        if self.tier2_deck is None:
            self.tier2_deck = []
        if self.tier3_deck is None:
            self.tier3_deck = []
    
    def draw_card(self, tier: int) -> Optional[Card]:
        """Draw a card from the specified tier's deck.
        
        Args:
            tier: The tier to draw from (1, 2, or 3)
            
        Returns:
            The drawn card, or None if no cards are available
        """
        if tier == 1 and self.tier1_deck:
            return self.tier1_deck.pop()
        elif tier == 2 and self.tier2_deck:
            return self.tier2_deck.pop()
        elif tier == 3 and self.tier3_deck:
            return self.tier3_deck.pop()
        return None
    
    def replace_card(self, tier: int, card_index: int) -> bool:
        """Replace a purchased card with a new one from the deck.
        
        Args:
            tier: The tier of the card to replace (1, 2, or 3)
            card_index: Index of the card in the tier's card list
            
        Returns:
            bool: True if a card was drawn to replace, False otherwise
        """
        drawn_card = self.draw_card(tier)
        if drawn_card is not None:
            if tier == 1 and card_index < len(self.tier1_cards):
                self.tier1_cards[card_index] = drawn_card
                return True
            elif tier == 2 and card_index < len(self.tier2_cards):
                self.tier2_cards[card_index] = drawn_card
                return True
            elif tier == 3 and card_index < len(self.tier3_cards):
                self.tier3_cards[card_index] = drawn_card
                return True
        return False
    
    def __str__(self):
        gems = ', '.join(f'{c.name}:{self.available_gems[c]}' for c in Color)
        remaining = f"\nRemaining: T1({len(self.tier1_deck)}) T2({len(self.tier2_deck)}) T3({len(self.tier3_deck)})"
        return (f"Gems: {gems}, Gold: {self.available_gold}\n"
                f"T1: {[str(c) for c in self.tier1_cards]}\n"
                f"T2: {[str(c) for c in self.tier2_cards]}\n"
                f"T3: {[str(c) for c in self.tier3_cards]}\n"
                f"Nobles: {[str(n) for n in self.nobles]}"
                f"{remaining if any([self.tier1_deck, self.tier2_deck, self.tier3_deck]) else ''}")

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
    """Generate a random valid 2-player Splendor board state with randomized card decks."""
    # Initialize available gems
    available_gems = {color: INITIAL_GEMS[color] for color in Color}
    available_gold = INITIAL_GEMS['gold']
    
    # Get all cards grouped by tier
    cards_by_tier = get_cards_by_tier()
    
    # Create and shuffle decks for each tier
    tier_decks = {}
    for tier in [1, 2, 3]:
        # Make a copy of the cards to avoid modifying the original list
        deck = list(cards_by_tier[tier])
        random.shuffle(deck)
        tier_decks[tier] = deck
    
    # Draw initial cards for each tier
    selected_cards = {}
    for tier, count in CARDS_PER_TIER.items():
        # Draw 'count' cards from the shuffled deck
        selected = []
        for _ in range(min(count, len(tier_decks[tier]))):
            selected.append(tier_decks[tier].pop())
        selected_cards[tier] = selected
    
    # Get all nobles (cards with 3+ points)
    nobles = [card for card in get_deck() if card.pt >= 3]
    selected_nobles = random.sample(nobles, min(NOBLES_COUNT, len(nobles)))
    
    # Create and return the board state with the remaining cards as decks
    return BoardState(
        available_gems=available_gems,
        available_gold=available_gold,
        tier1_cards=selected_cards[1],
        tier2_cards=selected_cards[2],
        tier3_cards=selected_cards[3],
        nobles=selected_nobles,
        tier1_deck=tier_decks[1],
        tier2_deck=tier_decks[2],
        tier3_deck=tier_decks[3]
    )

def board_state_to_initial_state(board: BoardState) -> State:
    """Convert a BoardState to the initial State for the solver."""
    # Start with a new game state
    state = State.newgame()
    
    # Set initial gems (starting with 0 gems as per standard Splendor rules)
    # Players take gems as their first action
    state.gems = (0, 0, 0, 0, 0)
    
    # Note: We don't need to set up the board's cards here because the solver
    # will only consider cards that are passed to its buy_card method
    
    return state


def simulate_game(goal_pts: int = DEFAULT_GOAL_POINTS, 
                 use_heuristic: bool = True, 
                 board: Optional[BoardState] = None,
                 verbose: bool = True) -> Tuple[int, Optional[BoardState]]:
    """
    Simulate a single game with the given parameters using brute-force DFS for each turn.
    
    Args:
        goal_pts: Points needed to win
        use_heuristic: Whether to use heuristic search in the solver
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
    
    # Make a deep copy of the board to avoid modifying the original
    import copy
    board = copy.deepcopy(board)
    
    # Convert the board state to initial solver state
    state = board_state_to_initial_state(board)
    
    # Keep track of the solution path
    solution = [state]
    
    # Simulate each turn
    turn = 0
    while state.pts < goal_pts and turn < 50:  # Reduced max turns since we're doing DFS
        if verbose:
            print(f"\n=== Turn {turn + 1} ===")
            print(f"Current state: {state}")
            print(f"Current board:")
            print(board)
        
        # For each possible move (buying an available card), run the solver
        # to see how quickly we can win from that state
        best_move = None
        best_turns = float('inf')
        best_next_state = None
        valid_move_found = False
        
        # Check all available cards on the board
        for tier, cards in [(1, board.tier1_cards), 
                           (2, board.tier2_cards), 
                           (3, board.tier3_cards)]:
            for i, card in enumerate(cards):
                if card is None:
                    continue
                    
                # Debug output
                if verbose:
                    print(f"\nChecking card: {card}")
                    print(f"  Original cost: {card.cost}")
                    print(f"  Player gems: {state.gems}")
                cost = list(card.cost)
                bonus = list(state.bonus)
                
                # Apply bonus discounts
                for j in range(len(cost)):
                    cost[j] = max(0, cost[j] - bonus[j])
                
                if verbose:
                    print(f"  Effective cost after bonus: {cost}")
                
                # Check if we have enough gems to cover the remaining cost
                can_afford = all(g >= c for g, c in zip(state.gems, cost))
                if verbose:
                    print(f"  Can afford: {can_afford}")
                    
                if can_afford:
                    valid_move_found = True
                    # This is a valid move - create a copy of the board state
                    board_copy = copy.deepcopy(board)
                    
                    # Apply the move (buy the card using the card's index)
                    next_state = state.buy_card(card.index)
                    
                    # Replace the bought card with a new one from the deck
                    card_replaced = board_copy.replace_card(tier, i)
                    
                    if verbose:
                        print(f"  Testing move: Buy {card} (Tier {tier})")
                        print(f"  New state: {next_state}")
                        if card_replaced:
                            print(f"  Replaced with: {getattr(board_copy, f'tier{tier}_cards')[i]}")
                        else:
                            print("  No more cards in deck to replace")
                    
                    # Run the solver from this new state
                    try:
                        solution = list(next_state.solve(goal_pts=goal_pts, use_heuristic=use_heuristic))
                        turns_to_win = len(solution) - 1  # Subtract 1 because the initial state is included
                        
                        if verbose:
                            print(f"  Solution found in {turns_to_win} turns")
                        
                        if turns_to_win < best_turns:
                            best_turns = turns_to_win
                            best_move = f"Buy {card} (Tier {tier})"
                            best_next_state = next_state
                            best_board = copy.deepcopy(board_copy)
                            
                    except Exception as e:
                        if verbose:
                            print(f"  No solution found from this state: {e}")
        
        # If no cards can be bought, take gems
        if not valid_move_found:
            if verbose:
                print("No cards can be bought, taking gems...")
            
            # Take one of each gem if available (simplified for now)
            gems = list(state.gems)
            for i in range(5):
                if board.available_gems[Color(i)] > 0:
                    gems[i] += 1
                    # Update board's available gems (simplified)
                    board.available_gems[Color(i)] -= 1
            
            # Create new state with updated gems
            next_state = State(
                cards=state.cards,
                bonus=state.bonus,
                gems=tuple(gems),
                pts=state.pts,
                saved=state.saved
            )
            
            best_move = "Take one of each available gem"
            best_next_state = next_state
            best_board = board
            
            if verbose:
                print(f"New state after taking gems: {next_state}")
        
        # If still no valid moves, the game is stuck
        if best_move is None:
            if verbose:
                print("No valid moves left!")
            return -1, board
        
        # Apply the best move
        if verbose:
            print(f"\nBest move: {best_move}")
            if best_turns != float('inf'):
                print(f"(wins in {best_turns} turns)")
        
        state = best_next_state
        board = best_board
        turn += 1
        
        # Check for noble visits
        for noble in board.nobles[:]:
            # Check if player meets the noble's bonus requirements
            # Noble's cost represents the required number of each bonus type
            if all(b >= n for b, n in zip(state.bonus, noble.cost)):
                state.pts += noble.pt  # Add noble's points (typically 3)
                board.nobles.remove(noble)
                if verbose:
                    print(f"\n=== Noble Visit! ===")
                    print(f"Visited noble requiring {noble.cost} bonuses")
                    print(f"Player bonuses: {state.bonus}")
                    print(f"New score: {state.pts} points")
                break
        
    if state.pts >= goal_pts:
        turns_taken = turn  # Subtract 1 because initial state is included
        if verbose:
            print(f"\n=== Game Won in {turns_taken} turns! ===")
            print(f"Final score: {state.pts} points")
        return turns_taken, board
    else:
        if verbose:
            print("\n=== Game Over - No Solution Found ===")
        return -1, board


def worker(args):
    """Worker function for parallel processing."""
    goal_pts, use_heuristic, board_arg, verbose = args
    # If board_arg is None, generate a new random board
    board = generate_random_board_state() if board_arg is None else board_arg
    return simulate_game(goal_pts, use_heuristic, board=board, verbose=verbose)

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
    # For each simulation, we'll generate a new random board
    args = [(goal_pts, use_heuristic, None, verbose) for _ in range(num_simulations)]
    
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
                if board_state is not None:
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
