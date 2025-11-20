"""Game logic for two-player board games."""
from typing import Optional, Tuple


class GameLogic:
    """Base class for game-specific logic."""
    
    def __init__(self, game_type: str):
        self.game_type = game_type
    
    def get_default_board(self) -> list:
        """Get default empty board for this game type."""
        raise NotImplementedError
    
    def validate_move(self, board: list, row: int, col: int, player_id: str) -> Tuple[bool, Optional[str]]:
        """Validate if a move is legal. Returns (is_valid, error_message)."""
        raise NotImplementedError
    
    def check_winner(self, board: list, row: int, col: int, player_id: str) -> Optional[str]:
        """Check if the move results in a win. Returns winner player_id or None."""
        raise NotImplementedError
    
    def check_draw(self, board: list, move_count: int) -> bool:
        """Check if the game is a draw. Returns True if draw."""
        raise NotImplementedError
    
    def get_board_size(self) -> Tuple[int, int]:
        """Get board dimensions (rows, cols)."""
        raise NotImplementedError


class TicTacToeLogic(GameLogic):
    """Tic-Tac-Toe game logic (3x3 grid)."""
    
    def __init__(self):
        super().__init__('tic_tac_toe')
        self.board_size = (3, 3)
    
    def get_default_board(self) -> list:
        """Get 3x3 empty board."""
        return [[None, None, None], [None, None, None], [None, None, None]]
    
    def validate_move(self, board: list, row: int, col: int, player_id: str) -> Tuple[bool, Optional[str]]:
        """Validate Tic-Tac-Toe move."""
        rows, cols = self.get_board_size()
        
        # Check coordinates are valid
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return False, f'Invalid coordinates: row={row}, col={col}. Must be 0-{rows-1}'
        
        # Check cell is empty
        if board[row][col] is not None:
            return False, f'Cell at ({row}, {col}) is already occupied'
        
        return True, None
    
    def check_winner(self, board: list, row: int, col: int, player_id: str) -> Optional[str]:
        """Check if player wins after making a move at (row, col)."""
        rows, cols = self.get_board_size()
        
        # Check row
        if all(board[row][c] == player_id for c in range(cols)):
            return player_id
        
        # Check column
        if all(board[r][col] == player_id for r in range(rows)):
            return player_id
        
        # Check main diagonal (if move is on diagonal)
        if row == col:
            if all(board[i][i] == player_id for i in range(rows)):
                return player_id
        
        # Check anti-diagonal (if move is on anti-diagonal)
        if row + col == rows - 1:
            if all(board[i][rows - 1 - i] == player_id for i in range(rows)):
                return player_id
        
        return None
    
    def check_draw(self, board: list, move_count: int) -> bool:
        """Check if Tic-Tac-Toe is a draw (9 moves, no winner)."""
        rows, cols = self.get_board_size()
        total_cells = rows * cols
        return move_count >= total_cells
    
    def get_board_size(self) -> Tuple[int, int]:
        """Get board dimensions."""
        return self.board_size


# Game logic factory
def get_game_logic(game_type: str) -> GameLogic:
    """Get game logic instance for the given game type."""
    if game_type == 'tic_tac_toe':
        return TicTacToeLogic()
    # Add other game types here
    # elif game_type == 'connect_four':
    #     return ConnectFourLogic()
    # elif game_type == 'checkers':
    #     return CheckersLogic()
    
    # Default to Tic-Tac-Toe for unknown types
    return TicTacToeLogic()

