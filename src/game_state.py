"""
GameState class that encapsulates the complete state of a chess game.
"""
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.piece import Piece, King


def initialize_game() -> 'GameState':
    """
    Initialize or reset the game to starting position.

    Returns:
        The initialized GameState instance
    """
    game_state = GameState()
    game_state.setup_initial_position()
    return game_state


class GameState:
    """Encapsulates the complete state of a chess game.

    Attributes:
        board: 8x8 grid with Piece instances or None
        _white_pieces: List of all white pieces
        _black_pieces: List of all black pieces
        _white_king: Reference to white King
        _black_king: Reference to black King
    """

    def __init__(self):
        self.board: List[List[Optional['Piece']]] = [[None] * 8 for _ in range(8)]
        self._white_pieces: List['Piece'] = []
        self._black_pieces: List['Piece'] = []
        self._white_king: Optional['King'] = None
        self._black_king: Optional['King'] = None
        
        # Dictionaries for cleaner color-based access
        self._pieces = {1: self._white_pieces, -1: self._black_pieces}
        self._kings = {1: None, -1: None}

    def get_piece_at(self, row: int, col: int) -> Optional['Piece']:
        """Get piece at given board position."""
        if 0 <= row <= 7 and 0 <= col <= 7:
            return self.board[row][col]
        return None

    def set_piece_at(self, row: int, col: int, piece: Optional['Piece']) -> None:
        """Set piece at given board position."""
        if 0 <= row <= 7 and 0 <= col <= 7:
            self.board[row][col] = piece

    def get_pieces_by_color(self, color: int) -> List['Piece']:
        """Get all pieces of a given color (1 for white, -1 for black)."""
        return self._pieces[color]

    def get_king(self, color: int) -> Optional['King']:
        """Get the king of the specified color."""
        return self._kings[color]

    def set_king(self, color: int, king: 'King') -> None:
        """Set the king reference for a color."""
        self._kings[color] = king
        if color == 1:
            self._white_king = king
        else:
            self._black_king = king

    def add_piece(self, piece: 'Piece') -> None:
        """Add a piece to the appropriate list."""
        if piece is not None and piece not in self._pieces[piece.color]:
            self._pieces[piece.color].append(piece)

    def remove_piece(self, piece: 'Piece') -> None:
        """Remove a piece from the game."""
        if piece is not None and piece in self._pieces[piece.color]:
            self._pieces[piece.color].remove(piece)

    def setup_initial_position(self) -> None:
        """Set up the initial chess position."""
        # Import here to avoid circular imports
        from src.piece import Rook, Knight, Bishop, Queen, King, Pawn

        # Clear existing state
        self.board = [[None] * 8 for _ in range(8)]
        self._white_pieces.clear()
        self._black_pieces.clear()

        # Create rooks first (needed for King castling references)
        rook_white_left = Rook((7, 0), 1, self)
        rook_white_right = Rook((7, 7), 1, self)
        rook_black_left = Rook((0, 0), -1, self)
        rook_black_right = Rook((0, 7), -1, self)

        # Black pieces (row 0)
        black_king = King((0, 4), -1, rook_black_left, rook_black_right, self)
        self._black_king = black_king
        self._kings[-1] = black_king

        self.board[0] = [
            rook_black_left,
            Knight((0, 1), -1, self),
            Bishop((0, 2), -1, self),
            Queen((0, 3), -1, self),
            black_king,
            Bishop((0, 5), -1, self),
            Knight((0, 6), -1, self),
            rook_black_right
        ]

        # Black pawns (row 1)
        self.board[1] = [Pawn((1, j), -1, self) for j in range(8)]

        # Empty rows (2-5)
        for i in range(2, 6):
            self.board[i] = [None] * 8

        # White pawns (row 6)
        self.board[6] = [Pawn((6, j), 1, self) for j in range(8)]

        # White pieces (row 7)
        white_king = King((7, 4), 1, rook_white_left, rook_white_right, self)
        self._white_king = white_king
        self._kings[1] = white_king

        self.board[7] = [
            rook_white_left,
            Knight((7, 1), 1, self),
            Bishop((7, 2), 1, self),
            Queen((7, 3), 1, self),
            white_king,
            Bishop((7, 5), 1, self),
            Knight((7, 6), 1, self),
            rook_white_right
        ]

        # Populate piece lists
        for row in range(2):
            for col in range(8):
                self._black_pieces.append(self.board[row][col])

        for row in range(6, 8):
            for col in range(8):
                self._white_pieces.append(self.board[row][col])
