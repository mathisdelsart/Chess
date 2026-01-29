"""Main game loop and event handling."""
import pygame
import time

from src.configs import SIZE_SQUARE, COLORS_MOVES_BOARD
from src.assets import (
    move_sound, capture_sound, check_sound, castling_sound,
    checkmate_sound, stalemate_sound, game_start_sound,
    white_king_image, black_king_image, white_queen_image, black_queen_image,
    white_rook_image, black_rook_image, white_knight_image, black_knight_image,
    white_bishop_image, black_bishop_image
)
from src.menu import MainMenu, EndGameMenu
from src.player_ai import PlayerAI


class Game:
    """
    Main game controller handling the game loop, events, and display.

    Attributes:
        screen: Pygame display surface
        piece: Piece manager for game logic
        board: Board renderer
        sound_button: Sound toggle button
        board_color_button: Board color theme button
    """

    # Sound mapping for different move types
    MOVE_SOUNDS = {
        "move": move_sound,
        "capture": capture_sound,
        "check": check_sound,
        "castling": castling_sound,
        "checkmate": checkmate_sound,
        "stalemate": stalemate_sound,
    }

    def __init__(self, screen, piece, board, sound_button, board_color_button):
        self.screen = screen
        self.piece = piece
        self.board = board
        self.sound_button = sound_button
        self.board_color_button = board_color_button

        self.IA = False
        self.turn_IA = False
        self.running = True
        self.begin_menu = True
        self.end_menu = False
        self.white_turn = True
        self.winner = 0

        self.mouse_pressed = False
        self.mouse_just_released = False

        self.pressed_piece_image = None
        self.piece_moved = None

        self.tile_pressed = None
        self.tile_moved = None

        self.list_colors_player = [None, None]
        self.color_player = None
        
        self.player_color = 1  # 1 for white, -1 for black (player's chosen color)
        self.board_flipped = False  # True when board is displayed from black's perspective
        
        # AI player (initialized when AI game starts)
        self.ai_player = None

        # Initialize professional menus
        self._init_menus()

    def _init_menus(self):
        """Initialize the professional menu system."""
        # Main menu
        self.main_menu = MainMenu(
            self.screen,
            on_start_pvp=self._start_pvp_game,
            on_start_ai=self._start_ai_game
        )

        # Set decorative piece images for main menu
        self.main_menu.set_piece_images(
            white_king_image,
            black_king_image,
            white_queen_image,
            black_queen_image,
            white_rook_image,
            black_rook_image,
            white_knight_image,
            black_knight_image,
            white_bishop_image,
            black_bishop_image
        )
        
        # Set game control buttons (sound and board color) for display in menu
        self.main_menu.set_game_buttons(self.sound_button, self.board_color_button)

        # End game menu
        self.end_game_menu = EndGameMenu(
            self.screen,
            on_replay=self._replay_game,
            on_main_menu=self._return_to_main_menu
        )

    def _start_pvp_game(self):
        """Start a Player vs Player game."""
        self.IA = False
        self.begin_menu = False
        
        # Get selected color from main menu
        self.player_color = self.main_menu.get_selected_color()
        self.board_flipped = (self.player_color == -1)  # Flip board if player chose black
        
        if self.sound_button.sound_on:
            game_start_sound.play()

    def _start_ai_game(self):
        """Start a Player vs AI game."""
        self.IA = True
        self.begin_menu = False
        
        # Get selected color from main menu
        self.player_color = self.main_menu.get_selected_color()
        self.board_flipped = (self.player_color == -1)  # Flip board if player chose black
        
        # Initialize AI with opposite color
        ai_color = -self.player_color
        self.ai_player = PlayerAI(ai_color, self.piece._game_state)
        
        # If player chose black (-1), AI plays white first
        if self.player_color == -1:
            self.white_turn = True  # White's turn (AI)
            self.turn_IA = True      # It's AI's turn
        else:
            # Player chose white, player starts
            self.white_turn = True
            self.turn_IA = False
        
        if self.sound_button.sound_on:
            game_start_sound.play()

    def _replay_game(self):
        """Replay the game with same settings."""
        self.end_menu = False
        self.end_game_menu.hide()
        self.reset_game()
        if self.sound_button.sound_on:
            game_start_sound.play()

    def _return_to_main_menu(self):
        """Return to the main menu."""
        self.end_menu = False
        self.begin_menu = True
        self.end_game_menu.hide()
        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.white_turn = True
        self.winner = 0
        self.mouse_pressed = False
        self.mouse_just_released = False
        self.pressed_piece_image = None
        self.piece_moved = None
        self.tile_pressed = None
        self.tile_moved = None
        self.list_colors_player = [None, None]
        self.color_player = None
        self.turn_IA = False
        self.player_color = 1
        self.board_flipped = False

        # Reset game state
        from src.game_state import initialize_game
        new_game_state = initialize_game()
        
        self.piece._game_state = new_game_state
        
        # Reinitialize AI if in AI mode
        if self.IA and self.ai_player:
            self.ai_player = PlayerAI(-self.player_color, new_game_state)
        
        self.update_moves_first_turn()

    def play_music(self, move_type: str):
        """
        Play the appropriate sound for a move type.

        Args:
            move_type: Type of move ("move", "capture", "check", "castling",
                      "checkmate", "stalemate")
        """
        if self.sound_button.sound_on:
            sound = self.MOVE_SOUNDS.get(move_type)
            if sound:
                sound.play()

    def events_menu(self):
        """Handle events in the start menu."""
        mouse_pos = pygame.mouse.get_pos()
        self.main_menu.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.main_menu.handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
    
    def _mouse_to_tile(self, mouse_pos):
        """Convert mouse position to logical tile coordinates.
        
        Takes board flipping into account.
        """
        display_tile = (mouse_pos[1] // SIZE_SQUARE, mouse_pos[0] // SIZE_SQUARE)
        
        # If board is flipped, convert display coords back to logical coords
        if self.board_flipped:
            return (7 - display_tile[0], 7 - display_tile[1])
        return display_tile

    def events_game_without_IA(self):
        """Handle events during gameplay (without AI turn)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle end menu clicks
                if self.end_menu:
                    if event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        self.end_game_menu.handle_click(mouse_pos)
                    continue

                # Left click
                elif event.button == 1:
                    initial_pos_mouse = pygame.mouse.get_pos()
                    tile_clicked = self._mouse_to_tile(initial_pos_mouse)

                    # Check if click is on buttons
                    if (self.board_color_button.checkCollision(initial_pos_mouse) or 
                        self.sound_button.checkCollision(initial_pos_mouse)):
                        self.board_color_button.buttonUpdateClick(initial_pos_mouse)
                        self.sound_button.buttonUpdateClick(initial_pos_mouse)
                    else:
                        # Handle piece selection
                        piece = self.piece._game_state.board[tile_clicked[0]][tile_clicked[1]]

                        if piece is not None and not self.end_menu:
                            # Check if it's the correct player's turn
                            if ((self.white_turn and piece.color == 1) or
                                    (not self.white_turn and piece.color == -1)):
                                self.tile_pressed = tile_clicked
                                # Set color_player to show the selected piece (3rd colored tile)
                                # Keep list_colors_player[0] and [1] showing opponent's last move
                                self.color_player = tile_clicked
                                self.pressed_piece_image = piece.image
                                piece.image = None
                                self.mouse_just_released = True

            elif event.type == pygame.KEYDOWN:
                if self.end_menu:
                    self.end_game_menu.handle_keydown(event.key)

    def display_menu(self):
        """Render the start menu."""
        # Draw board as background with orientation based on selected color
        # If black is selected, show board from black's perspective
        self.board.flipped = (self.main_menu.get_selected_color() == -1)
        self.board.draw_board(self.board_color_button.mod_board)
        self.board.draw_pieces(
            self.piece._game_state.get_pieces_by_color(-1) + self.piece._game_state.get_pieces_by_color(1)
        )

        # Draw professional menu overlay
        self.main_menu.draw()

    def display_game(self):
        """Render the game board and pieces."""
        # Set board orientation based on player's chosen color
        self.board.flipped = self.board_flipped
        self.board.draw_board(self.board_color_button.mod_board)

        # Draw move highlights
        if self.list_colors_player[0] is not None:
            is_light_tile = not self.board.check_dark_tile(self.list_colors_player[0])
            self.board.draw_tile(
                self.list_colors_player[0],
                COLORS_MOVES_BOARD[self.board_color_button.mod_board][is_light_tile]
            )
        if self.list_colors_player[1] is not None:
            is_light_tile = not self.board.check_dark_tile(self.list_colors_player[1])
            self.board.draw_tile(
                self.list_colors_player[1],
                COLORS_MOVES_BOARD[self.board_color_button.mod_board][is_light_tile]
            )
        if self.color_player is not None:
            is_light_tile = not self.board.check_dark_tile(self.color_player)
            self.board.draw_tile(
                self.color_player,
                COLORS_MOVES_BOARD[self.board_color_button.mod_board][is_light_tile]
            )

        # Draw possible moves for selected piece
        if self.tile_pressed is not None:
            selected_piece = self.piece._game_state.board[self.tile_pressed[0]][self.tile_pressed[1]]
            if selected_piece is not None:
                self.board.draw_possible_moves(selected_piece.available_moves)

        # Draw pieces
        self.board.draw_pieces(
            self.piece._game_state.get_pieces_by_color(-1) + self.piece._game_state.get_pieces_by_color(1)
        )

        # Buttons are no longer displayed during the game (only in menu)

    def display_end_game(self):
        """Display the end game menu."""
        # Update menu with mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.end_game_menu.update(mouse_pos)

        # Draw the menu
        self.end_game_menu.draw()

    def update_moves_first_turn(self):
        """Update available moves for white pieces at game start."""
        for piece in self.piece._game_state.get_pieces_by_color(1):
            piece.update_possible_moves()

    def _determine_final_sound(self, original_move_type: str, game_state_type: str) -> str:
        """
        Determine which sound to play based on move type and game state.

        Priority:
        1. checkmate/stalemate (game-ending states)
        2. check (important game state)
        3. original move type (move/capture/castling)

        Args:
            original_move_type: The type returned by move_piece() - "move", "capture", or "castling"
            game_state_type: The type returned by update_available_moves() - "move", "check",
                           "checkmate", or "stalemate"

        Returns:
            The appropriate sound type to play
        """
        if game_state_type in ("checkmate", "stalemate"):
            return game_state_type
        elif game_state_type == "check":
            return "check"
        else:
            return original_move_type

    def run(self):
        """Main game loop."""
        self.update_moves_first_turn()

        clock = pygame.time.Clock()

        while self.running:
            # Start menu
            if self.begin_menu:
                self.events_menu()
                self.display_menu()

            # Active gameplay
            elif not self.end_menu:
                # Human turn (or no AI mode)
                if not self.IA or not self.turn_IA:
                    self.events_game_without_IA()
                    self.display_game()

                    self.mouse_pressed = pygame.mouse.get_pressed()[0]

                    # Dragging a piece
                    if self.mouse_pressed and self.mouse_just_released:
                        if self.tile_pressed is not None and self.pressed_piece_image is not None:
                            pos_mouse = pygame.mouse.get_pos()
                            self.screen.blit(
                                self.pressed_piece_image,
                                (pos_mouse[0] - SIZE_SQUARE / 2,
                                 pos_mouse[1] - SIZE_SQUARE / 2)
                            )

                    # Mouse released - attempt move
                    if not self.mouse_pressed and self.mouse_just_released:
                        self.mouse_just_released = False
                        final_pos_mouse = pygame.mouse.get_pos()
                        self.tile_moved = self._mouse_to_tile(final_pos_mouse)

                        piece_clicked = self.piece._game_state.board[self.tile_pressed[0]][self.tile_pressed[1]]

                        # Valid move
                        if self.tile_moved in piece_clicked.available_moves:
                            # Execute move and capture ORIGINAL move type
                            # This is the key fix for the sound bug!
                            original_move_type = piece_clicked.move_piece(
                                self.tile_pressed, self.tile_moved
                            )
                            self.piece_moved = piece_clicked

                            # Update game state
                            self.white_turn = not self.white_turn
                            self.piece_moved.image = self.pressed_piece_image
                            
                            # Update colored tiles to show current player's move
                            # Replace opponent's move tiles with our move tiles
                            self.list_colors_player[0] = self.tile_pressed  # Our departure tile
                            self.list_colors_player[1] = self.tile_moved     # Our arrival tile
                            self.color_player = None  # Clear selection highlight
                            self.tile_pressed = None
                            self.turn_IA = True

                            # Update available moves and get game state
                            game_state_type = self.piece.update_available_moves(self.piece_moved)

                            # Check for game over
                            if game_state_type in ("checkmate", "stalemate"):
                                if game_state_type == "checkmate":
                                    # The player who just moved wins
                                    self.winner = -1 if self.white_turn else 1
                                else:
                                    self.winner = 0  # Draw
                                self.end_menu = True
                                self.end_game_menu.show(self.winner)

                            # FIX: Determine correct sound to play
                            # Don't lose the original move type!
                            final_sound = self._determine_final_sound(
                                original_move_type, game_state_type
                            )
                            self.play_music(final_sound)
                            
                            # If AI mode and not game over, render the player's move before AI plays
                            if self.IA and self.turn_IA and not self.end_menu:
                                self.display_game()
                                pygame.display.update()

                        # Invalid move - restore piece
                        else:
                            piece_clicked.image = self.pressed_piece_image
                            self.tile_pressed = None
                            self.color_player = None  # Clear selection highlight only

                # AI turn
                if self.IA and self.turn_IA and self.ai_player:
                    # Small delay for better UX (so player can see AI is "thinking")
                    time.sleep(0.1)  # 100ms delay
                    
                    # Get AI move
                    ai_move = self.ai_player.play()
                    
                    if ai_move is not None:
                        from_tile, to_tile = ai_move
                        ai_piece = self.piece._game_state.board[from_tile[0]][from_tile[1]]
                        
                        # Execute AI move
                        original_move_type = ai_piece.move_piece(from_tile, to_tile)
                        
                        # Update game state
                        self.white_turn = not self.white_turn
                        self.turn_IA = False
                        
                        # Update colored tiles to show AI's move
                        self.list_colors_player[0] = from_tile
                        self.list_colors_player[1] = to_tile
                        self.color_player = None
                        
                        # Update available moves and check game state
                        game_state_type = self.piece.update_available_moves(ai_piece)
                        
                        # Check for game over
                        if game_state_type in ("checkmate", "stalemate"):
                            if game_state_type == "checkmate":
                                # AI just moved, so if it's checkmate, AI wins
                                self.winner = self.ai_player.color
                            else:
                                self.winner = 0  # Draw
                            self.end_menu = True
                            self.end_game_menu.show(self.winner)
                        
                        # Play sound
                        final_sound = self._determine_final_sound(original_move_type, game_state_type)
                        self.play_music(final_sound)
                    else:
                        # No legal moves for AI (shouldn't happen in normal play)
                        self.turn_IA = False

            # End game screen
            else:
                self.events_game_without_IA()
                self.display_game()
                self.display_end_game()

            pygame.display.update()
            clock.tick(60)  # Limit to 60 FPS for smooth animations
