import numpy as np

class UltimateTicTacToe:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = np.zeros(81, dtype=int)
        
        self.macro_board = np.zeros(9, dtype=int)
        
        self.next_valid_grid = -1 
        
        self.current_player = 1
        self.game_over = False
        self.winner = 0

    def get_valid_moves(self):
        """Returns a list of all valid indices (0-80) for the current state."""
        if self.game_over:
            return []

        valid_moves = []
        
        
        if self.next_valid_grid != -1:
            start_index = self.next_valid_grid * 9
            end_index = start_index + 9
            
            for i in range(start_index, end_index):
                if self.board[i] == 0:
                    valid_moves.append(i)
            
            if not valid_moves:
                self.next_valid_grid = -1 
        
        if self.next_valid_grid == -1:
            for i in range(81):
                # We can only play in grids that haven't been won yet
                grid_idx = i // 9
                if self.macro_board[grid_idx] == 0 and self.board[i] == 0:
                    valid_moves.append(i)
                    
        return valid_moves

    def make_move(self, action_idx):
        if action_idx not in self.get_valid_moves():
            return False # Illegal move

        # 1. Place the mark
        self.board[action_idx] = self.current_player

        # 2. Check if this move won the local mini-board
        grid_idx = action_idx // 9
        local_pos = action_idx % 9
        
        if self.check_mini_win(grid_idx):
            self.macro_board[grid_idx] = self.current_player
            self.check_macro_win()

        # 3. Set the constraint for the NEXT player
        # The next player must play in the grid corresponding to the local_pos
        # UNLESS that target grid is already won or full
        if self.macro_board[local_pos] != 0 or self.is_grid_full(local_pos):
            self.next_valid_grid = -1 # Free move
        else:
            self.next_valid_grid = local_pos

        # 4. Switch Player
        self.current_player *= -1
        return True

    def check_mini_win(self, grid_idx):
        """Checks if the current player won the specific 3x3 grid."""
        start = grid_idx * 9
        b = self.board[start : start+9]
        p = self.current_player
        
        wins = [
            (0,1,2), (3,4,5), (6,7,8), # Rows
            (0,3,6), (1,4,7), (2,5,8), # Cols
            (0,4,8), (2,4,6)           # Diagonals
        ]
        for w in wins:
            if b[w[0]] == p and b[w[1]] == p and b[w[2]] == p:
                return True
        return False

    def is_grid_full(self, grid_idx):
        start = grid_idx * 9
        # Return True if no zeros in this slice
        return not any(self.board[start : start+9] == 0)

    def check_macro_win(self):
        """Checks if the game is won based on the macro board."""
        b = self.macro_board
        p = self.current_player
        wins = [
            (0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)
        ]
        for w in wins:
            if b[w[0]] == p and b[w[1]] == p and b[w[2]] == p:
                self.winner = p
                self.game_over = True
                return
        
        # Check Draw
        if 0 not in self.macro_board and not self.game_over:
             # Or check if board is totally full
             self.game_over = True
             self.winner = 0 