"""Professional menu system for the Chess game."""
import pygame
from typing import Tuple, Callable

from src.configs import WIDTH, HEIGHT


# ============== Color Palette ==============
class Colors:
    """Professional color palette for menus."""
    PRIMARY = (35, 35, 35)
    PRIMARY_LIGHT = (50, 50, 50)
    SECONDARY = (185, 155, 95)  # Gold
    SECONDARY_LIGHT = (210, 180, 120)

    TEXT_WHITE = (255, 255, 255)
    TEXT_LIGHT = (200, 200, 200)
    TEXT_GOLD = (200, 165, 70)

    OVERLAY = (20, 20, 20, 230)
    BUTTON_BG = (50, 50, 50)
    BUTTON_HOVER = (70, 70, 70)

    # Selection colors
    SELECTED = (100, 180, 100)  # Green for selected
    HOVER_HIGHLIGHT = (255, 255, 255, 50)


class MenuButton:
    """Modern button with hover effect."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 font_size: int = 28, on_click: Callable = None):
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.text = text
        self.on_click = on_click
        self.is_hovered = False

        self.font = pygame.font.Font(None, font_size)
        self.font_hover = pygame.font.Font(None, font_size + 2)

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        # Shadow
        shadow = self.rect.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=8)

        # Background
        bg = Colors.BUTTON_HOVER if self.is_hovered else Colors.BUTTON_BG
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)

        # Border
        border = Colors.SECONDARY_LIGHT if self.is_hovered else Colors.SECONDARY
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=8)

        # Text
        font = self.font_hover if self.is_hovered else self.font
        color = Colors.TEXT_WHITE if self.is_hovered else Colors.TEXT_LIGHT
        text_surf = font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        if self.rect.collidepoint(mouse_pos) and self.on_click:
            self.on_click()
            return True
        return False


class MainMenu:
    """
    Clean main menu with centered piece display and color selection.
    """

    def __init__(self, screen: pygame.Surface, on_start_pvp: Callable, on_start_ai: Callable):
        self.screen = screen
        self.on_start_pvp = on_start_pvp
        self.on_start_ai = on_start_ai

        # Player color selection (1 = white, -1 = black)
        self.selected_color = 1  # Default: white

        # Piece rects for click detection
        self.white_king_rect = None
        self.black_king_rect = None
        
        # References for sound and board color buttons (set externally)
        self.sound_button = None
        self.board_color_button = None

        # Buttons
        btn_y = HEIGHT // 2 + 160
        self.buttons = [
            MenuButton(WIDTH // 2, btn_y, 280, 50, "Player vs Player", 26, self._on_pvp_click),
            MenuButton(WIDTH // 2, btn_y + 65, 280, 50, "Player vs AI", 26, self._on_ai_click),
        ]

    def _on_pvp_click(self):
        self.on_start_pvp()

    def _on_ai_click(self):
        self.on_start_ai()

    def get_selected_color(self) -> int:
        """Return the selected player color (1=white, -1=black)."""
        return self.selected_color
    
    def set_game_buttons(self, sound_button, board_color_button):
        """Set references to sound and board color buttons for display in menu."""
        self.sound_button = sound_button
        self.board_color_button = board_color_button

    def set_piece_images(self, white_king, black_king, white_queen, black_queen,
                         white_rook=None, black_rook=None, white_knight=None,
                         black_knight=None, white_bishop=None, black_bishop=None):
        """Set piece images - display white and black king for color selection."""
        self.white_king = white_king
        self.black_king = black_king

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        for btn in self.buttons:
            btn.update(mouse_pos)

    def draw(self, board_surface: pygame.Surface = None) -> None:
        # Background overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(Colors.OVERLAY)
        self.screen.blit(overlay, (0, 0))

        # Title "CHESS"
        title_font = pygame.font.Font(None, 130)
        title = title_font.render("CHESS", True, Colors.TEXT_WHITE)
        title_shadow = title_font.render("CHESS", True, (0, 0, 0))
        self.screen.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, 95 + 3)))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 95)))

        # Gold line under title
        pygame.draw.line(self.screen, Colors.SECONDARY,
                         (WIDTH // 2 - 140, 155), (WIDTH // 2 + 140, 155), 3)

        # Subtitle
        sub_font = pygame.font.Font(None, 30)
        subtitle = sub_font.render("Select Game Mode", True, Colors.TEXT_LIGHT)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 185)))

        # Central panel for pieces
        panel_w, panel_h = 360, 220
        panel_x = (WIDTH - panel_w) // 2
        panel_y = 220

        # Panel shadow
        pygame.draw.rect(self.screen, (0, 0, 0),
                         (panel_x + 4, panel_y + 4, panel_w, panel_h), border_radius=12)
        # Panel background
        pygame.draw.rect(self.screen, Colors.PRIMARY,
                         (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        # Panel border
        pygame.draw.rect(self.screen, Colors.SECONDARY,
                         (panel_x, panel_y, panel_w, panel_h), width=2, border_radius=12)

        # "Choose your color" text
        choose_font = pygame.font.Font(None, 24)
        choose_text = choose_font.render("Click to choose your color", True, Colors.TEXT_LIGHT)
        self.screen.blit(choose_text, choose_text.get_rect(center=(WIDTH // 2, panel_y + 25)))

        # Draw the two kings - white on left, black on right
        if hasattr(self, 'white_king') and hasattr(self, 'black_king'):
            piece_size = 110
            white_scaled = pygame.transform.scale(self.white_king, (piece_size, piece_size))
            black_scaled = pygame.transform.scale(self.black_king, (piece_size, piece_size))

            center_y = panel_y + panel_h // 2 + 15
            spacing = 90

            # White king position
            white_x = WIDTH // 2 - spacing
            self.white_king_rect = white_scaled.get_rect(center=(white_x, center_y))

            # Black king position
            black_x = WIDTH // 2 + spacing
            self.black_king_rect = black_scaled.get_rect(center=(black_x, center_y))

            # Draw selection highlight (green circle behind selected piece)
            if self.selected_color == 1:
                pygame.draw.circle(self.screen, Colors.SELECTED, (white_x, center_y), piece_size // 2 + 8, 4)
            else:
                pygame.draw.circle(self.screen, Colors.SELECTED, (black_x, center_y), piece_size // 2 + 8, 4)

            # Draw hover highlight
            mouse_pos = pygame.mouse.get_pos()
            if self.white_king_rect.collidepoint(mouse_pos) and self.selected_color != 1:
                pygame.draw.circle(self.screen, (150, 150, 150), (white_x, center_y), piece_size // 2 + 5, 2)
            if self.black_king_rect.collidepoint(mouse_pos) and self.selected_color != -1:
                pygame.draw.circle(self.screen, (150, 150, 150), (black_x, center_y), piece_size // 2 + 5, 2)

            # Draw pieces
            self.screen.blit(white_scaled, self.white_king_rect)
            self.screen.blit(black_scaled, self.black_king_rect)

            # Labels under pieces
            label_font = pygame.font.Font(None, 22)
            white_label = label_font.render("WHITE", True, Colors.TEXT_WHITE if self.selected_color == 1 else Colors.TEXT_LIGHT)
            black_label = label_font.render("BLACK", True, Colors.TEXT_WHITE if self.selected_color == -1 else Colors.TEXT_LIGHT)
            self.screen.blit(white_label, white_label.get_rect(center=(white_x, center_y + piece_size // 2 + 20)))
            self.screen.blit(black_label, black_label.get_rect(center=(black_x, center_y + piece_size // 2 + 20)))

        # Draw buttons
        for btn in self.buttons:
            btn.draw(self.screen)
        
        # Draw game control buttons with improved styling
        if self.sound_button and self.board_color_button:
            mouse_pos = pygame.mouse.get_pos()
            
            # Check hover state
            sound_hovered = self.sound_button.checkCollision(mouse_pos)
            board_hovered = self.board_color_button.checkCollision(mouse_pos)
            
            # Display with labels and modern style
            self.sound_button.displayButtonWithLabel(sound_hovered)
            self.board_color_button.displayButtonWithLabel(board_hovered)

        # Footer
        footer_font = pygame.font.Font(None, 20)
        footer = footer_font.render("Press ESC to quit", True, (120, 120, 120))
        self.screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 30)))

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        # Check sound and board color buttons first
        if self.sound_button and self.sound_button.checkCollision(mouse_pos):
            self.sound_button.buttonUpdateClick(mouse_pos)
            return False  # Don't start game
        
        if self.board_color_button and self.board_color_button.checkCollision(mouse_pos):
            self.board_color_button.buttonUpdateClick(mouse_pos)
            return False  # Don't start game
        
        # Check if clicked on a king to select color
        if self.white_king_rect and self.white_king_rect.collidepoint(mouse_pos):
            self.selected_color = 1
            return False  # Don't start game, just select color

        if self.black_king_rect and self.black_king_rect.collidepoint(mouse_pos):
            self.selected_color = -1
            return False  # Don't start game, just select color

        # Check buttons
        for btn in self.buttons:
            if btn.handle_click(mouse_pos):
                return True
        return False


class EndGameMenu:
    """
    Clean end game menu showing result.
    """

    def __init__(self, screen: pygame.Surface, on_replay: Callable, on_main_menu: Callable):
        self.screen = screen
        self.winner = 0
        self.on_replay = on_replay
        self.on_main_menu = on_main_menu
        self.buttons = []
        self.is_visible = False

    def show(self, winner: int) -> None:
        self.winner = winner
        self.is_visible = True

        btn_y = HEIGHT // 2 + 60
        self.buttons = [
            MenuButton(WIDTH // 2, btn_y, 220, 45, "Play Again", 24, self.on_replay),
            MenuButton(WIDTH // 2, btn_y + 55, 220, 45, "Main Menu", 24, self.on_main_menu),
        ]

    def hide(self) -> None:
        self.is_visible = False

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        if not self.is_visible:
            return
        for btn in self.buttons:
            btn.update(mouse_pos)

    def draw(self) -> None:
        if not self.is_visible:
            return

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        # Panel
        panel_w, panel_h = 380, 320
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2

        # Shadow
        pygame.draw.rect(self.screen, (0, 0, 0),
                         (panel_x + 5, panel_y + 5, panel_w, panel_h), border_radius=15)
        # Background
        pygame.draw.rect(self.screen, Colors.PRIMARY,
                         (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        # Border
        pygame.draw.rect(self.screen, Colors.SECONDARY,
                         (panel_x, panel_y, panel_w, panel_h), width=3, border_radius=15)

        # "GAME OVER"
        header_font = pygame.font.Font(None, 38)
        header = header_font.render("GAME OVER", True, Colors.TEXT_GOLD)
        self.screen.blit(header, header.get_rect(center=(WIDTH // 2, panel_y + 45)))

        # Line
        pygame.draw.line(self.screen, Colors.SECONDARY,
                         (panel_x + 50, panel_y + 75), (panel_x + panel_w - 50, panel_y + 75), 2)

        # Result
        if self.winner == 1:
            result = "WHITE WINS!"
            color = Colors.TEXT_WHITE
        elif self.winner == -1:
            result = "BLACK WINS!"
            color = (180, 180, 180)
        else:
            result = "DRAW!"
            color = Colors.TEXT_GOLD

        result_font = pygame.font.Font(None, 56)
        result_surf = result_font.render(result, True, color)
        self.screen.blit(result_surf, result_surf.get_rect(center=(WIDTH // 2, panel_y + 120)))

        # Line
        pygame.draw.line(self.screen, Colors.SECONDARY,
                         (panel_x + 50, panel_y + 155), (panel_x + panel_w - 50, panel_y + 155), 2)

        # Buttons
        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        if not self.is_visible:
            return False
        for btn in self.buttons:
            if btn.handle_click(mouse_pos):
                return True
        return False

    def handle_keydown(self, key: int) -> bool:
        if not self.is_visible:
            return False
        if key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.on_replay()
            return True
        elif key == pygame.K_ESCAPE:
            self.on_main_menu()
            return True
        return False
