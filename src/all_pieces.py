"""Concrete chess piece implementations."""
from typing import Tuple, Optional, TYPE_CHECKING

from src.piece import (
    Piece, get_linear_moves, get_knight_moves, get_king_moves,
    ROOK_DIRECTIONS, BISHOP_DIRECTIONS, QUEEN_DIRECTIONS
)
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


class Pawn(Piece):
    """
    Pawn piece with special moves: double move, en passant, and promotion.
    """

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
        direction = -self.color  # White moves up (-1), Black moves down (+1)

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
                # Use isinstance instead of type comparison
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

            # Set correct image
            if self.color == 1:
                new_queen.image = white_queen_image
            else:
                new_queen.image = black_queen_image

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
    """
    King piece with castling support.
    """

    def __init__(self, tile: Tuple[int, int], color: int,
                 rook_left: Optional['Rook'], rook_right: Optional['Rook'],
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)

        self.image = white_king_image if color == 1 else black_king_image

        # References to rooks for castling
        self.rook_left = rook_left
        self.rook_right = rook_right

    def update_possible_moves(self) -> None:
        """Calculate king moves including basic moves and castling."""
        # Basic king moves (one square in any direction)
        self.available_moves = get_king_moves(
            self._game_state, self.tile, self.color
        )

        # Add castling moves if available
        self._check_castling()

    def _tiles_empty(self, tiles: list) -> bool:
        """Check if all specified tiles are empty."""
        for tile in tiles:
            if self._game_state.get_piece_at(tile[0], tile[1]) is not None:
                return False
        return True

    def _tiles_not_attacked(self, tiles: list) -> bool:
        """Check if none of the tiles are attacked by opponent pieces."""
        # Add king's current position
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
    """
    Knight piece with L-shaped movement.
    """

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)

        self.image = white_knight_image if color == 1 else black_knight_image

    def update_possible_moves(self) -> None:
        """Calculate knight L-shaped moves."""
        self.available_moves = get_knight_moves(
            self._game_state, self.tile, self.color
        )


class Rook(Piece):
    """
    Rook piece with linear horizontal/vertical movement.
    """

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
    """
    Bishop piece with diagonal movement.
    """

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
    """
    Queen piece combining rook and bishop movement.
    """

    def __init__(self, tile: Tuple[int, int], color: int,
                 game_state: 'GameState' = None):
        super().__init__(tile, color, game_state)

        self.image = white_queen_image if color == 1 else black_queen_image

    def update_possible_moves(self) -> None:
        """Calculate queen moves (rook + bishop combined)."""
        self.available_moves = get_linear_moves(
            self._game_state, self.tile, self.color, QUEEN_DIRECTIONS
        )
