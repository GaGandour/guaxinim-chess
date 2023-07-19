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
        legal_moves = sorted(legal_moves, key=lambda m: self._move_score(m))
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
        return [move for move in self.legal_moves() if str(move)[0:2] == piece_pos]

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
        matrix = [line.split(" ") for line in matrix]
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
    WINDOW = 0.25

    def __init__(self, depth: int = 6) -> None:
        self.tree_values_memory = dict()
        self.tree_moves_memory = dict()
        self.tree_height_memory = dict()
        self.tree_time_memory = dict()
        self.opening_sheet = dict()

        self.legal_moves = dict()  # dict[str, List[chess.Move]]
        self.legal_moves_depth = dict()  # dict[str, int]
        self.legal_moves_validity = dict()  # dict[str, int]

        self.depth = depth
        with open("opening_parser/opening_sheet.json", "r") as f:
            self.opening_sheet = json.load(f)

    def best_move(self, chess_game: ChessGame) -> chess.Move:
        """
        Returns predicted best move given a chess game.
        """
        opening_move = self._try_to_get_opening_move(chess_game)
        if opening_move is not None:
            return opening_move

        # alpha_beta_function = self._call_alpha_beta
        alpha_beta_function = self._call_pvs

        assert not chess_game.has_finished()

        _, best_move = alpha_beta_function(chess_game)

        stored_positions = [position for position in self.tree_height_memory]
        for position in stored_positions:
            remaining_time = self.tree_time_memory[position]
            if remaining_time == 0:
                del self.tree_values_memory[position]
                del self.tree_moves_memory[position]
                del self.tree_height_memory[position]
                del self.tree_time_memory[position]
            else:
                self.tree_time_memory[position] -= 1

        stored_positions_for_legal_moves = [position for position in self.legal_moves_validity]
        for position in stored_positions_for_legal_moves:
            remaining_validity = self.legal_moves_validity[position]
            if remaining_validity == 0:
                del self.legal_moves[position]
                del self.legal_moves_depth[position]
                del self.legal_moves_validity[position]
            else:
                self.legal_moves_validity[position] -= 1

        return best_move

    def _try_to_get_opening_move(self, chess_game: ChessGame) -> chess.Move:
        move = self.opening_sheet.get(chess_game.hash, None)
        if move is None:
            return None
        return chess.Move.from_uci(move)
    
    def _call_alpha_beta(self, chess_game: ChessGame) -> Tuple[float, chess.Move]:
        alpha = -ChessEngine.MATE_PUNCTUATION
        beta = +ChessEngine.MATE_PUNCTUATION
        return self._alpha_beta_recursion(chess_game, self.depth, alpha, beta)

    def _alpha_beta_recursion(self, chess_game: ChessGame, depth: int, alpha, beta) -> Tuple[float, chess.Move]:
        pre_value_move = self._get_node_alpha_beta_value_and_move(chess_game, depth)
        if pre_value_move[0] is not None:
            return pre_value_move

        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game), None

        best_value = -inf
        best_move = None
        mate_punctuation = ChessEngine.MATE_PUNCTUATION

        white_to_play = 1 if chess_game.white_to_play() else -1

        best_value *= white_to_play
        mate_punctuation *= white_to_play

        legal_moves = self._get_legal_moves(chess_game)

        move_value = {a: -mate_punctuation for a in legal_moves}

        for move in legal_moves:
            chess_game.play(move)
            alpha_beta, _ = self._alpha_beta_recursion(chess_game, depth - 1, alpha, beta)
            chess_game.pop_play()
            move_value[move] = alpha_beta
            if (alpha_beta * white_to_play) >= (best_value * white_to_play):
                best_move = move
                best_value = alpha_beta
            if white_to_play == 1:
                # alpha = max(alpha, best_value)
                if best_value > alpha:
                    alpha = best_value
            else:
                # beta = min(beta, best_value)
                if best_value < beta:
                    beta = best_value
            if beta <= alpha:
                break
        return self._store_node_alpha_beta_value(chess_game, best_value, best_move, depth, move_value)
    
    def _call_pvs(self, chess_game: ChessGame) -> Tuple[float, chess.Move]:
        aspiration = True
        best_move = None
        score = None
        if aspiration:
            previous = self.tree_values_memory.get(chess_game.hash, 0)
            alpha = previous - ChessEngine.WINDOW
            beta = previous + ChessEngine.WINDOW
            while True:
                score, best_move = self._alpha_beta_recursion_pvs(chess_game, self.depth, alpha, beta)
                if score <= alpha:
                    alpha = -ChessEngine.MATE_PUNCTUATION
                elif score >= beta:
                    beta = ChessEngine.MATE_PUNCTUATION
                else:
                    break
        else:
            alpha = -ChessEngine.MATE_PUNCTUATION
            beta = +ChessEngine.MATE_PUNCTUATION
            score, best_move = self._alpha_beta_recursion_pvs(chess_game, self.depth, alpha, beta)
        return score, best_move
    
    def _alpha_beta_recursion_pvs(self, chess_game: ChessGame, depth: int, alpha, beta) -> Tuple[float, chess.Move]:
        pre_value_move = self._get_node_alpha_beta_value_and_move(chess_game, depth)
        if pre_value_move[0] is not None:
            return pre_value_move

        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game), None

        best_value = -inf
        best_move = None
        mate_punctuation = ChessEngine.MATE_PUNCTUATION

        white_to_play = 1 if chess_game.white_to_play() else -1

        best_value *= white_to_play
        mate_punctuation *= white_to_play

        legal_moves = self._get_legal_moves(chess_game)

        move_value = {a: -mate_punctuation for a in legal_moves}

        for move in legal_moves:
            chess_game.play(move)
            if best_move is None:
                alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, alpha, beta)
            else:
                if white_to_play == 1:
                    alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, alpha, alpha + 1)
                else:
                    alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, beta - 1, beta)
                if alpha_beta > alpha and alpha_beta < beta:
                    alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, alpha, beta)
            chess_game.pop_play()
            move_value[move] = alpha_beta
            if (alpha_beta * white_to_play) >= (best_value * white_to_play):
                best_move = move
                best_value = alpha_beta
            if white_to_play == 1:
                # alpha = max(alpha, best_value)
                if best_value >= alpha:
                    alpha = best_value
            else:
                # beta = min(beta, best_value)
                if best_value <= beta:
                    beta = best_value
            if alpha >= beta:
                break
        return self._store_node_alpha_beta_value(chess_game, best_value, best_move, depth, move_value)

    def _get_legal_moves(self, chess_game: ChessGame) -> List[chess.Move]:
        legal_moves = self.legal_moves.get(chess_game.hash, None)
        if legal_moves:
            return legal_moves
        return chess_game.legal_moves()

    def _set_legal_moves(self, chess_game: ChessGame, move_value: dict, depth: int) -> None:
        self.legal_moves_validity[chess_game.hash] = self.depth + 1
        stored_depth = self.legal_moves_depth.get(chess_game.hash, 0)
        if stored_depth < depth:
            move_value_list = sorted(
                [move for move in move_value],
                key=lambda move: move_value[move],
                reverse=chess_game.white_to_play(),
            )
            self.legal_moves_depth[chess_game.hash] = depth
            self.legal_moves[chess_game.hash] = move_value_list

    def _get_node_alpha_beta_value_and_move(self, game: ChessGame, height: int) -> Tuple[float, chess.Move]:
        game_hash = game.hash
        stored_height = self.tree_height_memory.get(game_hash, None)
        if stored_height is None:
            return None, None
        if stored_height >= height:
            return self.tree_values_memory.get(game_hash, None), self.tree_moves_memory.get(game_hash, None)
        return None, None

    def _store_node_alpha_beta_value(
        self,
        game: ChessGame,
        alpha_beta_value: float,
        move: chess.Move,
        height: int,
        move_value: dict,
    ) -> Tuple[float, chess.Move]:
        game_hash = game.hash
        self.tree_values_memory[game_hash] = alpha_beta_value
        self.tree_moves_memory[game_hash] = move
        self.tree_height_memory[game_hash] = height
        self.tree_time_memory[game_hash] = height + 1

        self._set_legal_moves(game, move_value, height)
        return alpha_beta_value, move

    def _evaluate_game_node(self, game: ChessGame) -> float:
        """
        Evaluates the advantage or disadvantage of white pieces in a board.
        """
        return self._alternative_evaluation(game.board)

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

    def _alternative_evaluation(self, board: chess.Board) -> float:
        MOBILITY_WEIGHT = 0.00001
        CENTRAL_CONTROL_WEIGHT = 0.05
        OUTER_CENTRAL_CONTROL_WEIGHT = 0.005
        MATERIAL_POINTS_WEIGHT = 1
        DEVELOPMENT_WEIGHT = 0.035

        # Checkmates and Stalemantes
        if board.result() == "0-1":
            return -ChessEngine.MATE_PUNCTUATION
        if board.result() == "1-0":
            return ChessEngine.MATE_PUNCTUATION
        if board.result() == "1/2-1/2":
            return 0

        board_rows = str(board).split("\n")

        material_points = 0
        # Material Evaluation
        for i in range(64):
            piece = str(board.piece_at(i))
            material_points += ChessEngine.PUNCTUATIONS.get(piece, 0)
        material_points *= MATERIAL_POINTS_WEIGHT

        # Mobility Evaluation
        mobility = len(list(board.legal_moves)) * MOBILITY_WEIGHT
        if not board.turn:
            mobility *= -1

        # Center Control
        central_control = 0

        central_control += len(board.attackers(chess.WHITE, chess.D4))
        central_control += len(board.attackers(chess.WHITE, chess.D5))
        central_control += len(board.attackers(chess.WHITE, chess.E4))
        central_control += len(board.attackers(chess.WHITE, chess.E5))

        central_control -= len(board.attackers(chess.BLACK, chess.D4))
        central_control -= len(board.attackers(chess.BLACK, chess.D5))
        central_control -= len(board.attackers(chess.BLACK, chess.E4))
        central_control -= len(board.attackers(chess.BLACK, chess.E5))

        central_control *= CENTRAL_CONTROL_WEIGHT

        # Outer Center Control
        outer_center_control = 0

        outer_center_control += len(board.attackers(chess.WHITE, chess.C6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.D6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.E6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.C5))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F5))
        outer_center_control += len(board.attackers(chess.WHITE, chess.C4))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F4))
        outer_center_control += len(board.attackers(chess.WHITE, chess.C3))
        outer_center_control += len(board.attackers(chess.WHITE, chess.D3))
        outer_center_control += len(board.attackers(chess.WHITE, chess.E3))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F3))

        outer_center_control -= len(board.attackers(chess.BLACK, chess.C6))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.D6))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.E6))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F6))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C5))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F5))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C4))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F4))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.D3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.E3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F3))

        outer_center_control *= OUTER_CENTRAL_CONTROL_WEIGHT

        development = 0
        white_row = board_rows[7]
        black_row = board_rows[0]
        black_pieces_hiding = len([x for x in black_row if x != "." and x != "k"])
        white_pieces_hiding = len([x for x in white_row if x != "." and x != "K"])
        development = black_pieces_hiding - white_pieces_hiding
        development *= DEVELOPMENT_WEIGHT

        evaluation = 0
        evaluation += material_points
        evaluation += mobility
        evaluation += central_control
        evaluation += outer_center_control
        evaluation += development
        # print("central control:", central_control)
        # print("outer central control:", outer_center_control)
        # print("mobility:", mobility)
        # print("material:", material_points)
        # print(evaluation)
        return evaluation
