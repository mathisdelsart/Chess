"""Base Piece class for all chess pieces."""
from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.game_state import GameState


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
        board_pieces = self._game_state.board
        opponent_king = self.get_king(-moved_piece.color)
        list_moves_to_remove = []

        # Simulation 1: Temporarily remove checking piece
        board_pieces[piece_that_check.tile[0]][piece_that_check.tile[1]] = None
        self.remove_piece(piece_that_check)

        if self.king_in_chess(opponent_king):
            # Double check - only king can move
            opponent_piece.available_moves = []
        else:
            for opponent_move in opponent_piece.available_moves:
                if opponent_move != piece_that_check.tile:
                    # Simulation 2: Try this move
                    save_piece_moved_tile = board_pieces[opponent_move[0]][opponent_move[1]]
                    board_pieces[opponent_move[0]][opponent_move[1]] = opponent_piece

                    piece_that_check.update_possible_moves()
                    if opponent_king.tile in piece_that_check.available_moves:
                        list_moves_to_remove.append(opponent_move)

                    # End Simulation 2
                    board_pieces[opponent_move[0]][opponent_move[1]] = save_piece_moved_tile

            # End Simulation 1
            board_pieces[opponent_piece.tile[0]][opponent_piece.tile[1]] = opponent_piece

            for move_to_remove in list_moves_to_remove:
                if move_to_remove in opponent_piece.available_moves:
                    opponent_piece.available_moves.remove(move_to_remove)

        # Restore checking piece
        board_pieces[piece_that_check.tile[0]][piece_that_check.tile[1]] = piece_that_check
        self.add_piece(piece_that_check)

    def remove_moves_that_puts_king_in_chess(self, moved_piece_color: int) -> None:
        """Remove moves that would leave the player's own king in check."""
        board_pieces = self._game_state.board
        opponent_king = self.get_king(-moved_piece_color)

        for opponent_piece in self._game_state.get_pieces_by_color(-moved_piece_color):
            list_moves_to_remove = []

            for piece in self._game_state.get_pieces_by_color(moved_piece_color):
                piece.update_possible_moves()

                if opponent_piece.tile in piece.available_moves:
                    # Simulation 1: Remove opponent piece temporarily
                    board_pieces[opponent_piece.tile[0]][opponent_piece.tile[1]] = None

                    for move_opponent_piece in opponent_piece.available_moves:
                        # Simulation 2: Try opponent's move
                        save_piece_moved_tile = board_pieces[move_opponent_piece[0]][move_opponent_piece[1]]
                        board_pieces[move_opponent_piece[0]][move_opponent_piece[1]] = opponent_piece

                        piece.update_possible_moves()
                        if opponent_king.tile in piece.available_moves:
                            list_moves_to_remove.append(move_opponent_piece)

                        # End Simulation 2
                        board_pieces[move_opponent_piece[0]][move_opponent_piece[1]] = save_piece_moved_tile

                    # End Simulation 1
                    board_pieces[opponent_piece.tile[0]][opponent_piece.tile[1]] = opponent_piece

            for move_to_remove in list_moves_to_remove:
                if move_to_remove in opponent_piece.available_moves:
                    opponent_piece.available_moves.remove(move_to_remove)

    def remove_moves_of_king_that_chess_him(self, opponent_king: 'Piece') -> None:
        """Remove king moves that would put the king in check."""
        board_pieces = self._game_state.board
        list_moves_to_remove = []

        # Simulation 1: Remove king from board
        board_pieces[opponent_king.tile[0]][opponent_king.tile[1]] = None
        save_opponent_king_tile = opponent_king.tile

        for move_opponent_king in opponent_king.available_moves:
            # Simulation 2: Try king move
            save_opponent_king_moved_tile = board_pieces[move_opponent_king[0]][move_opponent_king[1]]
            board_pieces[move_opponent_king[0]][move_opponent_king[1]] = opponent_king
            opponent_king.tile = move_opponent_king

            if self.king_in_chess(opponent_king):
                list_moves_to_remove.append(move_opponent_king)

            # End Simulation 2
            board_pieces[move_opponent_king[0]][move_opponent_king[1]] = save_opponent_king_moved_tile

        # End Simulation 1
        opponent_king.tile = save_opponent_king_tile
        board_pieces[opponent_king.tile[0]][opponent_king.tile[1]] = opponent_king

        for move_to_remove in list_moves_to_remove:
            if move_to_remove in opponent_king.available_moves:
                opponent_king.available_moves.remove(move_to_remove)

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
