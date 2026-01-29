"""Chess piece classes and movement logic."""
from typing import List, Tuple, Optional, TYPE_CHECKING

from src.assets import (
    white_pawn_image, black_pawn_image,
    white_queen_image, black_queen_image,
    white_king_image, black_king_image,
    white_knight_image, black_knight_image,
    white_rook_image, black_rook_image,
    white_bishop_image, black_bishop_image
)

if TYPE_CHECKING:
    from src.game_state import GameState


# ========== Direction Constants ==========

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


# ========== Movement Functions ==========

def get_linear_moves(
    game_state: 'GameState',
    position: Tuple[int, int],
    color: int,
    directions: List[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """Calculate all possible moves along linear directions (Rook, Bishop, Queen)."""
    moves = []
    row, col = position
    board = game_state.board

    for row_dir, col_dir in directions:
        for distance in range(1, 8):
            new_row = row + row_dir * distance
            new_col = col + col_dir * distance

            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                break

            target_piece = board[new_row][new_col]

            if target_piece is None:
                moves.append((new_row, new_col))
            elif target_piece.color == -color:
                moves.append((new_row, new_col))
                break
            else:
                break

    return moves


def get_knight_moves(
    game_state: 'GameState',
    position: Tuple[int, int],
    color: int
) -> List[Tuple[int, int]]:
    """Calculate all possible knight moves (L-shaped)."""
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
    """Calculate basic king moves (one square in any direction)."""
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


# ========== Helper Function ==========

def simulate_move(board, piece, target_tile):
    """Context manager for simulating piece moves without permanent changes.
    
    Temporarily moves a piece to test board state, then restores original state.
    Returns original piece at target position.
    """
    original_piece = board[target_tile[0]][target_tile[1]]
    original_tile = piece.tile if piece else None
    
    board[target_tile[0]][target_tile[1]] = piece
    if piece:
        piece.tile = target_tile
        if original_tile:
            board[original_tile[0]][original_tile[1]] = None
    
    yield original_piece
    
    # Restore
    board[target_tile[0]][target_tile[1]] = original_piece
    if piece and original_tile:
        piece.tile = original_tile
        board[original_tile[0]][original_tile[1]] = piece


class Piece:
    """Base class for all chess pieces.
    
    Attributes:
        tile: Position as (row, col)
        color: 1 for white, -1 for black
        image: Pygame surface for rendering
        first_move: True if piece hasn't moved yet
        available_moves: List of legal move positions
    """

    def __init__(self, tile: Tuple[int, int] = None, color: int = None,
                 game_state: 'GameState' = None):
        """Initialize a piece.

        Args:
            tile: Position as (row, col)
            color: 1 for white, -1 for black
            game_state: GameState instance
        """
        self.tile = tile
        self.color = color
        self.image = None
        self.first_move = True
        self.available_moves: List[Tuple[int, int]] = []

        # Store game state reference
        if game_state is not None:
            self._game_state = game_state
        else:
            from src.game_state import GameState
            self._game_state = GameState()
            self._game_state.setup_initial_position()

    # ========== Piece Management Methods ==========

    def add_piece(self, piece: 'Piece') -> None:
        """Add a piece to the game state."""
        self._game_state.add_piece(piece)

    def remove_piece(self, piece: 'Piece') -> None:
        """Remove a piece from the game state."""
        self._game_state.remove_piece(piece)

    def get_mod_move(self, new_tile: Tuple[int, int]) -> str:
        """
        Determine the type of move being made.

        Args:
            new_tile: Destination position

        Returns:
            "capture" if capturing, "move" otherwise
        """
        if self._game_state.get_piece_at(new_tile[0], new_tile[1]) is not None:
            return "capture"
        return "move"

    # ========== Movement Methods ==========

    def update_possible_moves(self) -> None:
        """
        Calculate all possible moves for this piece.
        Must be overridden by subclasses.
        """
        pass

    def move_piece(self, current_tile: Tuple[int, int], new_tile: Tuple[int, int]) -> str:
        """
        Execute a move on the board.

        Args:
            current_tile: Starting position (row, col)
            new_tile: Destination position (row, col)

        Returns:
            Move type as string ("move" or "capture")
        """
        board_pieces = self._game_state.board

        # Determine move type BEFORE modifying board
        mod_of_move = self.get_mod_move(new_tile)

        # Remove captured piece
        piece_eaten = board_pieces[new_tile[0]][new_tile[1]]
        self.remove_piece(piece_eaten)

        # Update board
        board_pieces[new_tile[0]][new_tile[1]] = self
        board_pieces[current_tile[0]][current_tile[1]] = None
        self.tile = new_tile

        if self.first_move:
            self.first_move = False

        return mod_of_move

    # ========== King-related Methods ==========

    def get_king(self, color: int) -> Optional['Piece']:
        """
        Get the king of specified color.

        Args:
            color: 1 for white, -1 for black

        Returns:
            The King piece or None
        """
        return self._game_state.get_king(color)

    def get_piece_that_check(self, moved_piece_color: int) -> Optional['Piece']:
        """
        Find the piece giving check to the opponent king.

        Args:
            moved_piece_color: Color of the player who just moved

        Returns:
            The piece giving check, or None
        """
        opponent_king = self.get_king(-moved_piece_color)
        for piece in self._game_state.get_pieces_by_color(moved_piece_color):
            piece.update_possible_moves()
            if opponent_king.tile in piece.available_moves:
                return piece
        return None

    # ========== Check/Checkmate Detection Methods ==========

    def king_in_chess(self, king: 'Piece') -> bool:
        """
        Determine if the given king is in check.

        Args:
            king: The King piece to check

        Returns:
            True if king is in check
        """
        for piece in self._game_state.get_pieces_by_color(-king.color):
            piece.update_possible_moves()
            if king.tile in piece.available_moves:
                return True
        return False

    def player_cant_move(self, piece_color: int) -> bool:
        """
        Check if a player has no legal moves.

        Args:
            piece_color: Color of the player to check

        Returns:
            True if player has no legal moves
        """
        for piece in self._game_state.get_pieces_by_color(piece_color):
            if piece.available_moves:
                return False
        return True

    def removes_moves_that_doesnt_protect_king(self, moved_piece: 'Piece',
                                                opponent_piece: 'Piece',
                                                piece_that_check: 'Piece') -> None:
        """Filter opponent piece moves to only those that block or capture the checker."""
        board = self._game_state.board
        opponent_king = self.get_king(-moved_piece.color)

        # Temporarily remove checking piece
        check_tile = piece_that_check.tile
        board[check_tile[0]][check_tile[1]] = None
        self.remove_piece(piece_that_check)

        if self.king_in_chess(opponent_king):
            # Double check - only king can move
            opponent_piece.available_moves = []
        else:
            moves_to_remove = []
            for move in opponent_piece.available_moves:
                if move != check_tile:
                    # Try this move
                    saved = board[move[0]][move[1]]
                    board[move[0]][move[1]] = opponent_piece

                    piece_that_check.update_possible_moves()
                    if opponent_king.tile in piece_that_check.available_moves:
                        moves_to_remove.append(move)

                    board[move[0]][move[1]] = saved

            board[opponent_piece.tile[0]][opponent_piece.tile[1]] = opponent_piece
            opponent_piece.available_moves = [m for m in opponent_piece.available_moves if m not in moves_to_remove]

        # Restore checking piece
        board[check_tile[0]][check_tile[1]] = piece_that_check
        self.add_piece(piece_that_check)

    def remove_moves_that_puts_king_in_chess(self, moved_piece_color: int) -> None:
        """Remove moves that would leave the player's own king in check."""
        board = self._game_state.board
        opponent_king = self.get_king(-moved_piece_color)

        for opponent_piece in self._game_state.get_pieces_by_color(-moved_piece_color):
            moves_to_remove = []

            for piece in self._game_state.get_pieces_by_color(moved_piece_color):
                piece.update_possible_moves()

                if opponent_piece.tile in piece.available_moves:
                    # Temporarily remove opponent piece
                    opp_tile = opponent_piece.tile
                    board[opp_tile[0]][opp_tile[1]] = None

                    for move in opponent_piece.available_moves:
                        # Try opponent's move
                        saved = board[move[0]][move[1]]
                        board[move[0]][move[1]] = opponent_piece

                        piece.update_possible_moves()
                        if opponent_king.tile in piece.available_moves:
                            moves_to_remove.append(move)

                        board[move[0]][move[1]] = saved

                    # Restore opponent piece
                    board[opp_tile[0]][opp_tile[1]] = opponent_piece

            opponent_piece.available_moves = [m for m in opponent_piece.available_moves if m not in moves_to_remove]

    def remove_moves_of_king_that_chess_him(self, opponent_king: 'Piece') -> None:
        """Remove king moves that would put the king in check."""
        board = self._game_state.board
        king_tile = opponent_king.tile
        
        # Temporarily remove king from board
        board[king_tile[0]][king_tile[1]] = None
        moves_to_remove = []

        for move in opponent_king.available_moves:
            # Try king move
            saved = board[move[0]][move[1]]
            board[move[0]][move[1]] = opponent_king
            opponent_king.tile = move

            if self.king_in_chess(opponent_king):
                moves_to_remove.append(move)

            board[move[0]][move[1]] = saved

        # Restore king
        opponent_king.tile = king_tile
        board[king_tile[0]][king_tile[1]] = opponent_king
        opponent_king.available_moves = [m for m in opponent_king.available_moves if m not in moves_to_remove]

    def update_available_moves(self, moved_piece: 'Piece') -> str:
        """
        Update all available moves after a piece moves.
        Checks for check, checkmate, and stalemate.

        Args:
            moved_piece: The piece that just moved

        Returns:
            Move type as string: "move", "check", "checkmate", or "stalemate"
        """
        # Update all opponent piece moves
        for piece in self._game_state.get_pieces_by_color(-moved_piece.color):
            piece.update_possible_moves()

        opponent_king = self.get_king(-moved_piece.color)

        # If opponent king is NOT in check
        if not self.king_in_chess(opponent_king):
            self.remove_moves_that_puts_king_in_chess(moved_piece.color)
            self.remove_moves_of_king_that_chess_him(opponent_king)

            if self.player_cant_move(-moved_piece.color):
                return "stalemate"
            return "move"

        # If opponent king IS in check
        else:
            for opponent_piece in self._game_state.get_pieces_by_color(-moved_piece.color):
                if opponent_piece == self.get_king(-moved_piece.color):
                    self.remove_moves_of_king_that_chess_him(opponent_piece)
                else:
                    piece_that_check = self.get_piece_that_check(moved_piece.color)
                    self.removes_moves_that_doesnt_protect_king(
                        moved_piece, opponent_piece, piece_that_check
                    )

                if self.player_cant_move(-moved_piece.color):
                    return "checkmate"

            return "check"


# ========== Concrete Piece Classes ==========


class Pawn(Piece):
    """Pawn piece with special moves: double move, en passant, and promotion."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_pawn_image if color == 1 else black_pawn_image
        self.just_moved = False

    def update_possible_moves(self) -> None:
        """Calculate pawn moves including forward moves, captures, and en passant."""
        self.available_moves = []
        board_pieces = self._game_state.board
        row, col = self.tile
        direction = -self.color

        # Forward move (one square)
        new_row = row + direction
        if 0 <= new_row <= 7:
            if board_pieces[new_row][col] is None:
                self.available_moves.append((new_row, col))

                # Double move on first turn
                if self.first_move:
                    double_row = row + 2 * direction
                    if 0 <= double_row <= 7 and board_pieces[double_row][col] is None:
                        self.available_moves.append((double_row, col))

        # Diagonal captures
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            if 0 <= new_col <= 7 and 0 <= new_row <= 7:
                target = board_pieces[new_row][new_col]
                if target is not None and target.color == -self.color:
                    self.available_moves.append((new_row, new_col))

        # En passant
        self._check_en_passant()

    def _check_en_passant(self) -> None:
        """Check and add en passant capture moves."""
        board_pieces = self._game_state.board
        row, col = self.tile

        for col_offset in [-1, 1]:
            new_col = col + col_offset
            if 0 <= new_col <= 7:
                adjacent = board_pieces[row][new_col]
                if isinstance(adjacent, Pawn) and adjacent.just_moved:
                    self.available_moves.append((row - self.color, new_col))

    def move_piece(self, current_tile: Tuple[int, int], new_tile: Tuple[int, int]) -> str:
        """Handle pawn-specific moves: promotion and en passant."""
        board_pieces = self._game_state.board

        # Promotion - pawn reaches opposite end
        if new_tile[0] == 0 or new_tile[0] == 7:
            mod_of_move = self.get_mod_move(new_tile)

            # Create new queen
            new_queen = Queen(new_tile, self.color, self._game_state)
            new_queen.first_move = False
            new_queen.image = white_queen_image if self.color == 1 else black_queen_image

            # Remove captured piece if any
            piece_eaten = board_pieces[new_tile[0]][new_tile[1]]
            if piece_eaten is not None:
                self.remove_piece(piece_eaten)

            # Replace pawn with queen
            self.remove_piece(self)
            self.add_piece(new_queen)
            board_pieces[new_tile[0]][new_tile[1]] = new_queen
            board_pieces[current_tile[0]][current_tile[1]] = None

            return mod_of_move

        # Track double move for en passant
        if abs(new_tile[0] - current_tile[0]) == 2 and self.first_move:
            self.just_moved = True
        else:
            self.just_moved = False

        # En passant capture - diagonal move to empty square
        if board_pieces[new_tile[0]][new_tile[1]] is None and new_tile[1] != current_tile[1]:
            # Capture the pawn that is beside us
            piece_eaten = board_pieces[new_tile[0] + self.color][new_tile[1]]
            self.remove_piece(piece_eaten)
            board_pieces[new_tile[0] + self.color][new_tile[1]] = None

        return super().move_piece(current_tile, new_tile)


class King(Piece):
    """King piece with castling support."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 rook_left: Optional['Rook'], rook_right: Optional['Rook'],
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_king_image if color == 1 else black_king_image
        self.rook_left = rook_left
        self.rook_right = rook_right

    def update_possible_moves(self) -> None:
        """Calculate king moves including basic moves and castling."""
        self.available_moves = get_king_moves(self._game_state, self.tile, self.color)
        self._check_castling()

    def _tiles_empty(self, tiles: list) -> bool:
        """Check if all specified tiles are empty."""
        for tile in tiles:
            if self._game_state.get_piece_at(tile[0], tile[1]) is not None:
                return False
        return True

    def _tiles_not_attacked(self, tiles: list) -> bool:
        """Check if none of the tiles are attacked by opponent pieces."""
        if self.color == 1:
            tiles = tiles + [(7, 4)]
            opponent_pieces = self._game_state.get_pieces_by_color(-1)
        else:
            tiles = tiles + [(0, 4)]
            opponent_pieces = self._game_state.get_pieces_by_color(1)

        for piece in opponent_pieces:
            for tile in tiles:
                if tile in piece.available_moves:
                    return False
        return True

    def _check_castling(self) -> None:
        """Add castling moves if legal."""
        if not self.first_move:
            return

        row = 7 if self.color == 1 else 0

        # Kingside castling (right)
        if self.rook_right is not None and self.rook_right.first_move:
            kingside_tiles = [(row, 5), (row, 6)]
            if self._tiles_empty(kingside_tiles) and self._tiles_not_attacked(kingside_tiles):
                self.available_moves.append((row, 6))

        # Queenside castling (left)
        if self.rook_left is not None and self.rook_left.first_move:
            queenside_empty = [(row, 1), (row, 2), (row, 3)]
            queenside_check = [(row, 2), (row, 3)]
            if self._tiles_empty(queenside_empty) and self._tiles_not_attacked(queenside_check):
                self.available_moves.append((row, 2))

    def move_piece(self, current_tile: Tuple[int, int], new_tile: Tuple[int, int]) -> str:
        """Handle king moves including castling."""
        board_pieces = self._game_state.board
        row = new_tile[0]

        if self.first_move:
            # Kingside castling
            if new_tile[1] == 6:
                rook = board_pieces[row][7]
                board_pieces[row][5] = rook
                board_pieces[row][7] = None
                rook.tile = (row, 5)
                rook.first_move = False
                super().move_piece(current_tile, new_tile)
                return "castling"

            # Queenside castling
            if new_tile[1] == 2:
                rook = board_pieces[row][0]
                board_pieces[row][3] = rook
                board_pieces[row][0] = None
                rook.tile = (row, 3)
                rook.first_move = False
                super().move_piece(current_tile, new_tile)
                return "castling"

        return super().move_piece(current_tile, new_tile)


class Knight(Piece):
    """Knight piece with L-shaped movement."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_knight_image if color == 1 else black_knight_image

    def update_possible_moves(self) -> None:
        """Calculate knight L-shaped moves."""
        self.available_moves = get_knight_moves(self._game_state, self.tile, self.color)


class Rook(Piece):
    """Rook piece with linear horizontal/vertical movement."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_rook_image if color == 1 else black_rook_image

    def update_possible_moves(self) -> None:
        """Calculate rook moves along ranks and files."""
        self.available_moves = get_linear_moves(
            self._game_state, self.tile, self.color, ROOK_DIRECTIONS
        )


class Bishop(Piece):
    """Bishop piece with diagonal movement."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_bishop_image if color == 1 else black_bishop_image

    def update_possible_moves(self) -> None:
        """Calculate bishop moves along diagonals."""
        self.available_moves = get_linear_moves(
            self._game_state, self.tile, self.color, BISHOP_DIRECTIONS
        )


class Queen(Piece):
    """Queen piece combining rook and bishop movement."""

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)
        self.image = white_queen_image if color == 1 else black_queen_image

    def update_possible_moves(self) -> None:
        """Calculate queen moves (rook + bishop combined)."""
        self.available_moves = get_linear_moves(
            self._game_state, self.tile, self.color, QUEEN_DIRECTIONS
        )
