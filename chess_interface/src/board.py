import chess
from typing import List, Tuple

from chess_game.chess_game import ChessGame
from chess_interface.src.const import *
from chess_interface.src.square import Square
from chess_interface.src.piece import *
from chess_interface.src.move import Move
from chess_interface.src.sound import Sound


class Board:
    def __init__(self):
        self.squares: Square = [[None]*ROWS for col in range(COLS)]
        self.last_move: Move = None
        self.chess_game: ChessGame = ChessGame()
        self._create_squares()
        self._update_pieces()


    def move(self, move: Move, promotion: str = None) -> None:
        if promotion:
            self.chess_game.play(move.uci_code() + promotion)    
        else:
            self.chess_game.play(move.uci_code())
        self._update_pieces()

        
        
    def is_valid_move(self, move: Move) -> bool:
        """
        Checks if attempted move is valid or not.
        """
        return (
            chess.Move.from_uci(move.uci_code()) 
            in self.chess_game.piece_legal_moves(move.initial.position)
        ) 
    

    def is_promotion_move(self, move: Move) -> bool:
        """
        Checks if attempted move is promotion or not.
        """
        if 1 < int(move.uci_code()[-1]) < 8:
            return False
        return (
            chess.Move.from_uci(move.uci_code()+"q") 
            in self.chess_game.piece_legal_moves(move.initial.position)
        )


    def calc_moves(self, row, col) -> List[Tuple[int, int]]:
        """
        Calculate all the possible (valid) end positions
        of a piece based on the piece's initial position.
        """
        position = Square.row_col_to_position(row, col)
        valid_end_pos = [Square.position_to_row_col(str(move)[2:4]) for move in self.chess_game.piece_legal_moves(position)]
        return valid_end_pos


    def _create_squares(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)


    def _update_pieces(self) -> None:
        """
        Updates pieces in each of our board's squares 
        according to the board_matrix returned from chess_game
        """
        board_matrix = self.chess_game.board_matrix()
        for row in range(ROWS):
            for col in range(COLS):
                symbol = board_matrix[row][col]
                piece = PIECE_MAPPING[symbol][0]
                color = PIECE_MAPPING[symbol][1]
                self.squares[row][col] = Square(row, col, piece(color) if piece else piece)