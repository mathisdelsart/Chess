"""Chess game entry point."""
import pygame

from src.configs import WIDTH, HEIGHT

# Initialize pygame before loading assets
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")

# Import assets and components after pygame init
from src.assets import (
    black_king_image
)
from src.board import Board
from src.button import Sound_Button, BoardColor_Button
from src.piece import Piece
from src.game import Game

# Set window icon
pygame.display.set_icon(black_king_image)


def main():
    """Initialize and run the chess game."""
    # Create game components
    board = Board(screen)
    piece = Piece()  # Game logic manager

    # Create UI buttons with offset from corners
    button_size = 60
    offset = 50
    
    sound_button = Sound_Button(
        screen,
        button_size,
        (offset + button_size / 2, offset + button_size / 2)
    )

    board_color_button = BoardColor_Button(
        screen,
        button_size,
        (screen.get_width() - offset - button_size / 2, offset + button_size / 2)
    )

    # Create and run game
    game = Game(screen, piece, board, sound_button, board_color_button)
    game.run()


if __name__ == '__main__':
    main()
