import pygame
from src.configs import *

class Board:
    
    def __init__(self, screen):
        self.screen = screen
        self.flipped = False  # True when viewing from black's perspective
    
    def _flip_coords(self, tile):
        """Convert logical tile coordinates to display coordinates.
        
        When flipped=True, inverts the board so black pieces appear at bottom.
        tile is (row, col) where row 0 is top, row 7 is bottom.
        """
        if self.flipped:
            return (7 - tile[0], 7 - tile[1])
        return tile

    def draw_tile(self, tile, color):
        display_tile = self._flip_coords(tile)
        pygame.draw.rect(self.screen, color, (display_tile[1] * SIZE_SQUARE, display_tile[0] * SIZE_SQUARE, SIZE_SQUARE, SIZE_SQUARE))
    
    def check_dark_tile(self, tile):
        return (tile[0] + tile[1]) % 2 != 0

    def draw_board(self, mod_board):
        for i in range(ROW):
            for j in range(COL):
                if self.check_dark_tile((i, j)):
                    self.draw_tile((i, j), COLORS_BOARD[mod_board][1])
                else:
                    self.draw_tile((i, j), COLORS_BOARD[mod_board][0])
    
    def draw_possible_moves(self, available_moves):
        for move_tile in available_moves:
            if self.check_dark_tile(move_tile):
                self.draw_tile(move_tile, COLOR_POSSIBLE_MOVES_DARK)
            else:
                self.draw_tile(move_tile, COLOR_POSSIBLE_MOVES_LIGHT)
    
    def draw_pieces(self, list_pieces):
        for piece in list_pieces:
            if piece.image != None:
                display_tile = self._flip_coords(piece.tile)
                self.screen.blit(piece.image, (display_tile[1] * SIZE_SQUARE, display_tile[0] * SIZE_SQUARE))