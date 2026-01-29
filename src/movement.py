"""Movement strategies for chess pieces."""
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_state import GameState

# Direction constants for piece movement
ROOK_DIRECTIONS: List[Tuple[int, int]] = [
    (-1, 0),  # Up
    (1, 0),   # Down
    (0, -1),  # Left
    (0, 1)    # Right
]

BISHOP_DIRECTIONS: List[Tuple[int, int]] = [
    (-1, -1),  # Up-Left
    (-1, 1),   # Up-Right
    (1, -1),   # Down-Left
    (1, 1)     # Down-Right
]

QUEEN_DIRECTIONS: List[Tuple[int, int]] = ROOK_DIRECTIONS + BISHOP_DIRECTIONS

KNIGHT_OFFSETS: List[Tuple[int, int]] = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2), (1, 2),
    (2, -1), (2, 1)
]


def get_linear_moves(
    game_state: 'GameState',
    position: Tuple[int, int],
    color: int,
    directions: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """
    Calculate all possible moves along linear directions.
    Used by Rook, Bishop, and Queen.

    Args:
        game_state: Current game state containing the board
        position: Current (row, col) position of the piece
        color: Piece color (1 for white, -1 for black)
        directions: List of (row_delta, col_delta) directions to explore

    Returns:
        List of valid move positions as (row, col) tuples
    """
    moves = []
    row, col = position
    board = game_state.board

    for row_dir, col_dir in directions:
        for distance in range(1, 8):
            new_row = row + row_dir * distance
            new_col = col + col_dir * distance

            # Check bounds
            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                break

            target_piece = board[new_row][new_col]

            if target_piece is None:
                # Empty square - can move here
                moves.append((new_row, new_col))
            elif target_piece.color == -color:
                # Enemy piece - can capture but cannot go further
                moves.append((new_row, new_col))
                break
            else:
                # Own piece - blocked
                break

    return moves


def get_knight_moves(
    game_state: 'GameState',
    position: Tuple[int, int],
    color: int
) -> List[Tuple[int, int]]:
    """
    Calculate all possible knight moves (L-shaped).

    Args:
        game_state: Current game state containing the board
        position: Current (row, col) position of the knight
        color: Piece color (1 for white, -1 for black)

    Returns:
        List of valid move positions as (row, col) tuples
    """
    moves = []
    row, col = position
    board = game_state.board

    for row_off, col_off in KNIGHT_OFFSETS:
        new_row = row + row_off
        new_col = col + col_off

        if 0 <= new_row <= 7 and 0 <= new_col <= 7:
            target = board[new_row][new_col]
            if target is None or target.color == -color:
                moves.append((new_row, new_col))

    return moves


def get_king_moves(
    game_state: 'GameState',
    position: Tuple[int, int],
    color: int
) -> List[Tuple[int, int]]:
    """
    Calculate basic king moves (one square in any direction).
    Does not include castling - that is handled separately.

    Args:
        game_state: Current game state containing the board
        position: Current (row, col) position of the king
        color: Piece color (1 for white, -1 for black)

    Returns:
        List of valid move positions as (row, col) tuples
    """
    moves = []
    row, col = position
    board = game_state.board

    for row_off in range(-1, 2):
        for col_off in range(-1, 2):
            if row_off == 0 and col_off == 0:
                continue

            new_row = row + row_off
            new_col = col + col_off

            if 0 <= new_row <= 7 and 0 <= new_col <= 7:
                target = board[new_row][new_col]
                if target is None or target.color == -color:
                    moves.append((new_row, new_col))

    return moves
