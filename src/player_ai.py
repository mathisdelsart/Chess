"""AI Player for Chess Game - Currently plays random legal moves.

This module provides a placeholder AI implementation that makes random legal moves.
You can extend this to create a sophisticated chess AI using various techniques.
"""

import random
from typing import Tuple, Optional
from src.game_state import GameState


class PlayerAI:
    """Chess AI that selects moves for a given color.
    
    Current implementation: Random legal move selection.
    
    Future improvements could include:
    - Minimax algorithm with alpha-beta pruning
    - Position evaluation heuristics
    - Opening book knowledge
    - Endgame tablebase lookups
    """
    
    def __init__(self, color: int, game_state: GameState):
        """Initialize the AI player.
        
        Args:
            color: 1 for white, -1 for black
            game_state: Reference to the current game state
        """
        self.color = color
        self.game_state = game_state
    
    def play(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Select and return the next move to play.
        
        Uses the same system as human players: directly uses the available_moves
        that have already been validated by update_available_moves() in game.py.
        
        Returns:
            Tuple of (from_tile, to_tile) or None if no legal moves available.
            Example: ((6, 4), (4, 4)) means move piece from (6,4) to (4,4)
        """
        # Get all pieces of this AI's color
        pieces = self.game_state.get_pieces_by_color(self.color)
        
        # Collect all legal moves from available_moves
        # These moves have already been validated by update_available_moves()
        # called at the end of the previous turn in game.py
        legal_moves = []
        for piece in pieces:
            for move in piece.available_moves:
                legal_moves.append((piece.tile, move))
        
        # If no legal moves, return None (stalemate or checkmate)
        if not legal_moves:
            return None
        
        # Select a random legal move
        return random.choice(legal_moves)


# ========== How to Create a Better Chess AI ==========
"""
To improve this AI beyond random moves, consider implementing:

1. **Minimax Algorithm**
   - Recursively search future positions to a certain depth
   - Evaluate positions using a scoring function
   - Choose the move that leads to the best position

2. **Alpha-Beta Pruning**
   - Optimize minimax by skipping branches that won't affect the result
   - Can double the search depth with the same computation time

3. **Position Evaluation**
   - Material: Count piece values (Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9)
   - Position: Reward pieces in strong squares (center control, etc.)
   - King safety: Penalize exposed kings, reward castled positions
   - Pawn structure: Evaluate doubled pawns, passed pawns, isolated pawns

4. **Move Ordering**
   - Search promising moves first (captures, checks, threats)
   - Improves alpha-beta pruning effectiveness

5. **Opening Book**
   - Pre-store strong opening sequences
   - Avoid calculation in early game

6. **Endgame Tablebases**
   - Pre-computed perfect play for positions with few pieces
   - Guarantee optimal endgame play

Example implementation structure:

```python
def evaluate_position(self) -> float:
    '''Return score from AI's perspective (positive = good for AI)'''
    score = 0
    
    # Material count
    for piece in self.game_state.get_pieces_by_color(self.color):
        score += self.get_piece_value(piece)
    for piece in self.game_state.get_pieces_by_color(-self.color):
        score -= self.get_piece_value(piece)
    
    # Add positional bonuses (center control, development, etc.)
    # ...
    
    return score

def minimax(self, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    '''Minimax with alpha-beta pruning'''
    if depth == 0:
        return self.evaluate_position()
    
    if maximizing:
        max_eval = float('-inf')
        for move in self.get_all_legal_moves(self.color):
            # Make move
            eval = self.minimax(depth - 1, alpha, beta, False)
            # Unmake move
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        # Similar for minimizing player
        pass

def play(self) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    '''Choose best move using minimax'''
    best_move = None
    best_value = float('-inf')
    
    for move in self.get_all_legal_moves(self.color):
        # Make move
        value = self.minimax(depth=3, alpha=float('-inf'), 
                           beta=float('inf'), maximizing=False)
        # Unmake move
        
        if value > best_value:
            best_value = value
            best_move = move
    
    return best_move
```

Resources to learn more:
- Chess Programming Wiki: https://www.chessprogramming.org/
- Minimax algorithm: https://en.wikipedia.org/wiki/Minimax
- Alpha-Beta pruning: https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
"""
