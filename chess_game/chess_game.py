import chess
from typing import Union, List
from math import inf
from copy import deepcopy


class ChessGame:
    def __init__(self, board: chess.Board = None) -> None:
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board

    def legal_moves(self) -> List[chess.Move]:
        return list(self.board.legal_moves)

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

    def has_finished(self) -> bool:
        if self.board.result() == "*":
            return False
        return True

    def white_to_play(self) -> bool:
        return self.board.turn

    def child_game_copy(self, move: Union[str, chess.Move]) -> "ChessGame":
        child_game_board = deepcopy(self.board)
        child_game = ChessGame(board=child_game_board)
        child_game.play(move)
        return child_game
    
    def hash_game(self) -> str:
        return self.board.fen()

    def _play_move_from_string(self, move: str) -> None:
        self.board.push(chess.Move.from_uci(move))

    def _play_move_from_chess_move_class(self, move: chess.Move) -> None:
        self.board.push(move)

class ChessGameByFen(ChessGame):
    def __init__(self, fen: str) -> None:
        board = chess.Board(fen)
        super().__init__(board)


class ChessEngine:
    MATE_PUNCTUATION = 40
    DEPTH = 3
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
        # For storing calculated games and optimize time
        self.games_dictionary = dict()

        self.alpha: float = None
        self.beta: float = None

    def best_move(self, chess_game: ChessGame) -> chess.Move:
        assert not chess_game.has_finished()
        white = chess_game.white_to_play()
        self.alpha = -inf
        self.beta = +inf
        best_move = None
        best_move_value = None
        for move in chess_game.legal_moves():
            child_game = chess_game.child_game_copy(move)
            value = self._alpha_beta_fail_hard_recursion(child_game, ChessEngine.DEPTH)
            if best_move is None:
                best_move = move
                best_move_value = value
                continue
            if white:
                if value > best_move_value:
                    best_move_value = value
                    best_move = move
                continue
            # if black:
            if value < best_move_value:
                best_move_value = value
                best_move = move
        return best_move

    def _alpha_beta_fail_hard_recursion(self, chess_game: ChessGame, depth: int) -> float:
        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game)
        if chess_game.white_to_play():
            value = -inf
            for move in chess_game.legal_moves():
                child_game = chess_game.child_game_copy(move)
                alpha_beta = self._alpha_beta_fail_hard_recursion(child_game, depth - 1)
                value = max(value, alpha_beta)
                if value > self.beta:
                    break
                self.alpha = max(self.alpha, value)
            return value
        # if black:
        value = +inf
        for move in chess_game.legal_moves():
            child_game = chess_game.child_game_copy(move)
            alpha_beta = self._alpha_beta_fail_hard_recursion(child_game, depth - 1)
            value = min(value, alpha_beta)
            if value < self.alpha:
                break
            self.beta = min(self.beta, value)
        return value

    def _alpha_beta_fail_soft_recursion(self, chess_game: ChessGame, depth: int) -> float:
        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game)
        if chess_game.white_to_play():
            value = -inf
            for move in chess_game.legal_moves():
                child_game = chess_game.child_game_copy(move)
                alpha_beta = self._alpha_beta_fail_soft_recursion(child_game, depth - 1)
                value = max(value, alpha_beta)
                if value >= self.beta:
                    break
            return value
        # if black:
        value = +inf
        for move in chess_game.legal_moves():
            child_game = chess_game.child_game_copy(move)
            alpha_beta = self._alpha_beta_fail_soft_recursion(child_game, depth - 1)
            value = min(value, alpha_beta)
            if value <= self.alpha:
                break
        return value

    def _evaluate_game_node(self, game: ChessGame) -> float:
        """
        Evaluates the advantage or disadvantage of white pieces in a board.
        """
        game_hash = game.hash_game()
        if game_hash not in self.games_dictionary:

            self.games_dictionary[game_hash] = self._dummy_evaluation(game.board)
        return self.games_dictionary[game_hash]

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
