from typing import Tuple

class Square:

    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    ALPHACOLS_INVERSE = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

    def __init__(self, row: int, col: int, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacol = Square.ALPHACOLS[col]
        self.position = Square.row_col_to_position(row, col)
    
    def row_col_to_position(row, col) -> str:
        position = Square.ALPHACOLS[col] + str(8-row)
        return position

    def position_to_row_col(position) -> Tuple[int, int]:
        col_alpha = position[0]
        col = Square.ALPHACOLS_INVERSE[col_alpha]
        row = 8 - int(position[1])
        return row, col            

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def has_piece(self):
        return self.piece != None

    def isempty(self):
        return not self.has_piece()

    def has_team_piece(self, color):
        return self.has_piece() and self.piece.color == color

    def has_enemy_piece(self, color):
        return self.has_piece() and self.piece.color != color

    def isempty_or_enemy(self, color):
        return self.isempty() or self.has_enemy_piece(color)

    @staticmethod
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg > 7:
                return False
        
        return True

    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        return ALPHACOLS[col]