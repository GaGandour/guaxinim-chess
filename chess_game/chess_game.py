import chess
import json
from typing import Union, List, Tuple
from math import inf
from copy import deepcopy


class ChessGame:
    def __init__(self, board: chess.Board = None) -> None:
        self.board: chess.Board = None
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board
        self.hash = self.hash_game()

    def legal_moves(self) -> List[chess.Move]:
        """
        Returns a list containing all the legal moves for the
        current board state.
        """
        legal_moves = list(self.board.legal_moves)
        legal_moves = sorted(legal_moves, key = lambda m: self._move_score(m))
        return legal_moves
    
    def _move_score(self, move: chess.Move) -> int:
        score = 0
        if self.board.is_capture(move):
            score += 1
        self.play(move)
        if self.board.is_check():
            score += 1
        self.pop_play()
        return -score
    
    def piece_legal_moves(self, piece_pos: str) -> List[chess.Move]:
        """
        Returns a list containing all the legal moves for a
        given piece. 
        """
        return [move for move in self.legal_moves() if move[0:2] == piece_pos]

    def play(self, move: Union[str, chess.Move]) -> None:
        """
        Plays a move in the board. The input can be either a string
        or a `chess.Move` class. example:

        ```
        game = ChessGame()
        game.play("d2d4") # white plays d4
        next_move = chess.Move.from_uci('d7d5')
        game.play(next_move) # black plays d5
        ```

        In this example, the first move (white) used a string as an input and
        the second one (black) used a `chess.Move` object as an input.
        """
        if type(move) == str:
            self._play_move_from_string(move)
        elif type(move) == chess.Move:
            self._play_move_from_chess_move_class(move)
        else:
            raise ValueError("move is neither a string nor a chess.Move")
        self.hash = self.hash_game()
        
    def play_by_san(self, move: str) -> None:
        self.board.push_san(move)
        self.hash = self.hash_game()

    def parse_san(self, move: str) -> chess.Move:
        return self.board.parse_san(move)


    def board_matrix(self) -> List[List[str]]:
        """
        Returns a matrix in which each element corresponds
        to a piece or a blank square (".") in the board.
        """
        matrix = str(self.board).split("\n")
        matrix = [line.split(' ') for line in matrix]
        return matrix

    def has_finished(self) -> bool:
        """
        Returns True if the game has
        finished. Returns False otherwise.
        """
        if self.board.result() == "*":
            return False
        return True

    def pop_play(self) -> None:
        """
        Undo one move.
        """
        self.board.pop()
        self.hash = self.hash_game()

    def white_to_play(self) -> bool:
        """
        Returns True if it's white's turn.
        Returns False otherwise.
        """
        return self.board.turn

    def child_game_copy(self, move: Union[str, chess.Move]) -> "ChessGame":
        """
        Do not use this method.

        Returns a copy of what a chess game would be if the
        given move is played.
        """
        child_game_board = deepcopy(self.board)
        child_game = ChessGame(board=child_game_board)
        child_game.play(move)
        return child_game

    def hash_game(self) -> str:
        """
        Returns the current board's FEN. It's a string that
        represents the board and current state of the game.
        """
        fen = self.board.fen()
        hash = " ".join(fen.split(" ")[:-2])
        return hash

    def _play_move_from_string(self, move: str) -> None:
        self.board.push(chess.Move.from_uci(move))

    def _play_move_from_chess_move_class(self, move: chess.Move) -> None:
        self.board.push(move)


class ChessGameByFen(ChessGame):
    def __init__(self, fen: str) -> None:
        board = chess.Board(fen)
        super().__init__(board)


class ChessEngine:
    MATE_PUNCTUATION = 100
    DEPTH = 5
    PUNCTUATIONS = {
        "R": 5,
        "N": 3,
        "B": 3,
        "Q": 9,
        "P": 1,
        "r": -5,
        "n": -3,
        "b": -3,
        "q": -9,
        "p": -1,
    }

    def __init__(self) -> None:
        self.games_dictionary = dict()
        self.tree_values_memory = dict()
        self.tree_moves_memory = dict()
        self.tree_height_memory = dict()
        self.opening_sheet = dict()
        with open("opening_parser/opening_sheet.json", "r") as f:
            self.opening_sheet = json.load(f)

    def best_move(self, chess_game: ChessGame) -> chess.Move:
        """
        Returns predicted best move given a chess game.
        """
        opening_move = self._try_to_get_opening_move(chess_game)
        if opening_move is not None:
            return opening_move
        
        alpha_beta_function = self._alpha_beta_recursion
        
        assert not chess_game.has_finished()
        
        alpha = -inf
        beta = +inf
        _, best_move = alpha_beta_function(chess_game, ChessEngine.DEPTH, alpha, beta)

        stored_positions = [position for position in self.tree_height_memory]
        for position in stored_positions:
            stored_height = self.tree_height_memory[position]
            if stored_height == 0:
                del self.tree_values_memory[position]
                del self.tree_moves_memory[position]
                del self.tree_height_memory[position]
            else:
                self.tree_height_memory[position] -= 1
        return best_move
    
    def _try_to_get_opening_move(self, chess_game: ChessGame) -> chess.Move:
        move = self.opening_sheet.get(chess_game.hash, None)
        if move is None:
            return None
        return chess.Move.from_uci(move)
    
    def _alpha_beta_recursion(self, chess_game: ChessGame, depth: int, alpha, beta) -> Tuple[float, chess.Move]:
        pre_value_move = self._get_node_alpha_beta_value_and_move(chess_game, depth)
        if pre_value_move[0] is not None:
            return pre_value_move
        
        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game), None
        if chess_game.white_to_play():
            best_value = -inf
            best_move = None
            for move in chess_game.legal_moves():
                chess_game.play(move)
                alpha_beta, _ = self._alpha_beta_recursion(chess_game, depth - 1, alpha, beta)
                chess_game.pop_play()
                if alpha_beta == ChessEngine.MATE_PUNCTUATION:
                    return self._store_node_alpha_beta_value(chess_game, alpha_beta, move, depth)
                if alpha_beta >= best_value:
                    best_move = move
                    best_value = alpha_beta
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return self._store_node_alpha_beta_value(chess_game, best_value, best_move, depth)
        # if black:
        best_value = +inf
        best_move = None
        for move in chess_game.legal_moves():
            chess_game.play(move)
            alpha_beta, _ = self._alpha_beta_recursion(chess_game, depth - 1, alpha, beta)
            chess_game.pop_play()
            if alpha_beta == -ChessEngine.MATE_PUNCTUATION:
                return self._store_node_alpha_beta_value(chess_game, alpha_beta, move, depth)
            if alpha_beta <= best_value:
                best_value = alpha_beta
                best_move = move
            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return self._store_node_alpha_beta_value(chess_game, best_value, best_move, depth)
    
    def _get_node_alpha_beta_value_and_move(self, game: ChessGame, height: int) -> Tuple[float, chess.Move]:
        game_hash = game.hash
        stored_height = self.tree_height_memory.get(game_hash, None)
        if stored_height is None:
            return None, None
        if stored_height >= height:
            return self.tree_values_memory.get(game_hash, None), self.tree_moves_memory.get(game_hash, None)
        return None, None
    
    def _store_node_alpha_beta_value(self, game: ChessGame, alpha_beta_value: float, move: chess.Move, height: int) -> Tuple[float, chess.Move]:
        game_hash = game.hash
        self.tree_values_memory[game_hash] = alpha_beta_value
        self.tree_moves_memory[game_hash] = move
        self.tree_height_memory[game_hash] = height
        return alpha_beta_value, move

    def _evaluate_game_node(self, game: ChessGame) -> float:
        """
        Evaluates the advantage or disadvantage of white pieces in a board.
        """
        return self._dummy_evaluation(game.board)

    def _dummy_evaluation(self, board: chess.Board) -> float:
        # DUMMY EVALUATION

        if board.result() == "0-1":
            return -ChessEngine.MATE_PUNCTUATION
        if board.result() == "1-0":
            return ChessEngine.MATE_PUNCTUATION
        if board.result() == "1/2-1/2":
            return 0

        evaluation = 0
        for i in range(64):
            piece = str(board.piece_at(i))
            evaluation += ChessEngine.PUNCTUATIONS.get(piece, 0)
        return evaluation
