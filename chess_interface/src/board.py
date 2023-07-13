from typing import List

from chess_game.chess_game import ChessGame

from chess_interface.src.const import *
from chess_interface.src.square import Square
from chess_interface.src.piece import *
from chess_interface.src.move import Move
from chess_interface.src.sound import Sound

import copy
import os

class Board:
    def __init__(self):
        self.squares: Square = [[None]*ROWS for col in range(COLS)]
        self.last_move: Move = None
        self.chess_game: ChessGame = ChessGame()
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, move: Move):
        self.chess_game.play(move.uci_code())
        
        
    def valid_move(self, move: Move):
        return move.uci_code() in self.chess_game.piece_legal_moves(move.initial.position)


    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True


    def calc_moves(self, row, col) -> List[Move]:
        '''
            Calculate all the possible (valid) moves of an specific piece on a specific position
        '''
        initial_square = Square(row, col)
        position = initial_square.position
        chess_legal_moves = self.chess_game.piece_legal_moves(position) # chess.Moves
        chess_legal_finals = [str(move[2:]) for move in chess_legal_moves] # "a8" com o ultimo quadrado do movimento
        final_squares_row_cols = [initial_square.position_to_row_col(p) for p in chess_legal_finals] # (0, 1)
        final_squares = [Square(row=r[0], col=r[1]) for r in final_squares_row_cols]
        moves = [Move(initial=initial_square, final=final_square) for final_square in final_squares]
        return moves

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))