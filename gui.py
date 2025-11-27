import pygame
import sys
import math
from ultimate_engine import UltimateTicTacToe
from mcts import MCTS

# --- CONSTANTS ---
WIDTH, HEIGHT = 720, 800  # Extra height for text info
BOARD_SIZE = 720
CELL_SIZE = BOARD_SIZE // 9
GRID_SIZE = BOARD_SIZE // 3

# COLORS (NEON THEME)
COLOR_BG = (10, 14, 39)        # Dark Navy
COLOR_GRID_THIN = (50, 50, 50) # Faint Grey
COLOR_GRID_THICK = (0, 212, 255) # Neon Cyan
COLOR_X = (255, 68, 68)        # Neon Red
COLOR_O = (0, 212, 255)        # Neon Cyan
COLOR_VALID_ZONE = (30, 30, 60) # Slightly lighter background
COLOR_WON_X = (60, 20, 20)     # Dark Red tint
COLOR_WON_O = (20, 60, 60)     # Dark Cyan tint
COLOR_TEXT = (255, 255, 255)

class UltimateGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ultimate Tic-Tac-Toe AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 60, bold=True)
        self.small_font = pygame.font.SysFont("arial", 30)
        
        # Game Objects
        self.game = UltimateTicTacToe()
        self.ai = MCTS(iterations=1000)
        self.player_side = 1  # Human is X (1)
        self.last_move = None
        self.running = True

    def draw_board(self):
        self.screen.fill(COLOR_BG)
        
        # 1. Highlight Valid Constraints / Won Grids
        for grid_idx in range(9):
            row = grid_idx // 3
            col = grid_idx % 3
            x = col * GRID_SIZE
            y = row * GRID_SIZE
            rect = (x, y, GRID_SIZE, GRID_SIZE)

            # If grid is won, tint it
            if self.game.macro_board[grid_idx] == 1:
                pygame.draw.rect(self.screen, COLOR_WON_X, rect)
            elif self.game.macro_board[grid_idx] == -1:
                pygame.draw.rect(self.screen, COLOR_WON_O, rect)
            # If grid is the valid target, highlight it
            elif (self.game.next_valid_grid == grid_idx or self.game.next_valid_grid == -1) and not self.game.game_over:
                pygame.draw.rect(self.screen, COLOR_VALID_ZONE, rect)

        # 2. Draw Last Move Highlight
        if self.last_move is not None:
            r = self.last_move // 9
            c = self.last_move % 9 # Local cell index is not enough, need global coordinate
            
            # Global Row/Col calculation
            # Grid Row (0-2) * 3 + SubRow (0-2)
            gx = (self.last_move % 9 % 3) + ((self.last_move // 9 % 3) * 3)
            gy = (self.last_move % 9 // 3) + ((self.last_move // 9 // 3) * 3)
            
            x = gx * CELL_SIZE
            y = gy * CELL_SIZE
            pygame.draw.rect(self.screen, (255, 165, 0), (x, y, CELL_SIZE, CELL_SIZE), 2) # Orange border

        # 3. Draw Thin Lines (Mini Cells)
        for i in range(1, 9):
            # Vertical
            pygame.draw.line(self.screen, COLOR_GRID_THIN, (i * CELL_SIZE, 0), (i * CELL_SIZE, BOARD_SIZE), 2)
            # Horizontal
            pygame.draw.line(self.screen, COLOR_GRID_THIN, (0, i * CELL_SIZE), (BOARD_SIZE, i * CELL_SIZE), 2)

        # 4. Draw Thick Lines (Major Grids)
        for i in range(1, 3):
            # Vertical
            pygame.draw.line(self.screen, COLOR_GRID_THICK, (i * GRID_SIZE, 0), (i * GRID_SIZE, BOARD_SIZE), 6)
            # Horizontal
            pygame.draw.line(self.screen, COLOR_GRID_THICK, (0, i * GRID_SIZE), (BOARD_SIZE, i * GRID_SIZE), 6)

        # 5. Draw Marks (X and O)
        for i in range(81):
            if self.game.board[i] != 0:
                # Calculate pixel position
                # Global Col = (GridCol * 3) + CellCol
                grid_idx = i // 9
                cell_idx = i % 9
                
                grid_x = grid_idx % 3
                grid_y = grid_idx // 3
                cell_x = cell_idx % 3
                cell_y = cell_idx // 3
                
                pixel_x = (grid_x * 3 + cell_x) * CELL_SIZE + (CELL_SIZE // 2)
                pixel_y = (grid_y * 3 + cell_y) * CELL_SIZE + (CELL_SIZE // 2)
                
                text = "X" if self.game.board[i] == 1 else "O"
                color = COLOR_X if self.game.board[i] == 1 else COLOR_O
                
                surf = self.font.render(text, True, color)
                rect = surf.get_rect(center=(pixel_x, pixel_y))
                self.screen.blit(surf, rect)

        # 6. Draw Big Marks over Won Grids
        for i in range(9):
            if self.game.macro_board[i] != 0:
                row = i // 3
                col = i % 3
                x = col * GRID_SIZE + (GRID_SIZE // 2)
                y = row * GRID_SIZE + (GRID_SIZE // 2)
                
                text = "X" if self.game.macro_board[i] == 1 else "O"
                color = COLOR_X if self.game.macro_board[i] == 1 else COLOR_O
                
                # Draw huge letter
                big_font = pygame.font.SysFont("arial", 200, bold=True)
                surf = big_font.render(text, True, color)
                # Set alpha to be see-through
                surf.set_alpha(100) 
                rect = surf.get_rect(center=(x, y))
                self.screen.blit(surf, rect)

        # 7. Draw UI Text at bottom
        status = "Your Turn"
        if self.game.game_over:
            if self.game.winner == 1: status = "VICTORY!"
            elif self.game.winner == -1: status = "DEFEAT!"
            else: status = "DRAW"
        elif self.game.current_player != self.player_side:
            status = "AI Thinking..."
            
        text_surf = self.small_font.render(status, True, COLOR_TEXT)
        self.screen.blit(text_surf, (20, BOARD_SIZE + 20))

    def handle_click(self, pos):
        if self.game.game_over or self.game.current_player != self.player_side:
            return

        x, y = pos
        if y >= BOARD_SIZE: return # Clicked in UI area

        # Convert pixel to Grid/Cell
        col = x // CELL_SIZE
        row = y // CELL_SIZE
        
        # We need to convert (row, col) back to the 0-80 index logic
        # Global Row 0-8, Global Col 0-8
        
        # Which grid is this?
        grid_row = row // 3
        grid_col = col // 3
        grid_idx = grid_row * 3 + grid_col
        
        # Which cell inside that grid?
        cell_row = row % 3
        cell_col = col % 3
        cell_idx = cell_row * 3 + cell_col
        
        action_idx = (grid_idx * 9) + cell_idx
        
        if action_idx in self.game.get_valid_moves():
            self.game.make_move(action_idx)
            self.last_move = action_idx

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            
            # AI Logic
            if not self.game.game_over and self.game.current_player != self.player_side:
                # Force a redraw so we see "AI Thinking" text
                self.draw_board()
                pygame.display.flip()
                
                # AI Thinks
                move = self.ai.search(self.game)
                self.game.make_move(move)
                self.last_move = move

            self.draw_board()
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    gui = UltimateGUI()
    gui.run()