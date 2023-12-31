import chess
import json
from typing import Union, List, Tuple, Literal
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
        Returns a list containing all the legal
        moves for the current board state.
        """
        legal_moves = list(self.board.legal_moves)
        return legal_moves

    def _legal_moves_sorted(self) -> List[chess.Move]:
        """
        Returns a list containing all the legal moves for
        the current board state. These moves are ordered by
        a score which prioritizes captures and checks.
        """
        legal_moves = list(self.board.legal_moves)
        legal_moves = sorted(legal_moves, key=lambda m: self._generate_move_score(m))
        return legal_moves

    def _generate_move_score(self, move: chess.Move) -> int:
        """
        Generate a score to prioritize moves in which
        a piece is captured or a check happens.
        """
        score = 0
        if self.board.is_capture(move):
            score += 1
        # self.play(move)
        # if self.board.is_check():
        #     score += 1
        # self.pop_play()
        return -score

    def piece_legal_moves(self, piece_pos: str) -> List[chess.Move]:
        """
        Returns a list containing all the legal
        moves for a given piece.
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
            raise ValueError("Move is neither a string nor a chess.Move")
        self.hash = self.hash_game()

    def _play_move_from_string(self, move: str) -> None:
        self.board.push(chess.Move.from_uci(move))

    def _play_move_from_chess_move_class(self, move: chess.Move) -> None:
        self.board.push(move)

    def play_by_san(self, move: str) -> None:
        """
        Plays a move according to a given SAN (Standard Algebraic Notation).
        """
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

    def __init__(self, depth: int = 6, algorithm: Literal["minimax", "abp", "abpi", "pvs"] = "abpi") -> None:
        self.games_dictionary = dict()
        self.tree_values_memory = dict()
        self.tree_moves_memory = dict()
        self.tree_height_memory = dict()
        self.tree_time_memory = dict()
        self.opening_sheet = dict()

        self.legal_moves = dict()  # dict[str, List[chess.Move]]
        self.legal_moves_depth = dict()  # dict[str, int]
        self.legal_moves_validity = dict()  # dict[str, int]

        self.depth = depth
        self.algorithm = algorithm
        with open("opening_parser/opening_sheet.json", "r") as f:
            self.opening_sheet = json.load(f)

    def best_move(self, chess_game: ChessGame) -> chess.Move:
        """
        Returns predicted best move given a chess game.
        """
        opening_move = self._try_to_get_opening_move(chess_game)
        if opening_move is not None:
            return opening_move

        assert not chess_game.has_finished()

        # Minimax
        if self.algorithm == "minimax":
            _, best_move = self._minimax(chess_game, self.depth)
            return best_move
        # Alpha-Beta Pruning
        elif self.algorithm == "abp":
            _, best_move = self._call_alpha_beta(chess_game, False)
        # Alpha-Beta Pruning with Improvements
        elif self.algorithm == "abpi":
            _, best_move = self._call_alpha_beta(chess_game, True)
        # ABP PVS variation (out of CT-213 Exam's scope!)
        elif self.algorithm == "pvs":
            _, best_move = self._call_pvs(chess_game)

        # Improvements related to repeated calculations
        if self.algorithm == "abpi" or self.algorithm == "pvs":
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
        """
        Check if current chess_game is among the ones
        recorded in the opening database. If it is among
        them, return the suggested move. Else, return None.
        """
        move = self.opening_sheet.get(chess_game.hash, None)
        if move is None:
            return None
        return chess.Move.from_uci(move)

    def _minimax(self, chess_game: ChessGame, depth: int) -> Tuple[float, chess.Move]:
        """
        Implements Minimax algorithm to find the next
        move given for a Chess board configuration.
        """
        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game), None
        # White's turn (maximizing)
        if chess_game.white_to_play():
            best_value = -inf
            best_move = None
            for move in chess_game.legal_moves():
                chess_game.play(move)
                value, _ = self._minimax(chess_game, depth - 1)
                chess_game.pop_play()
                if value > best_value:
                    best_move = move
                    best_value = value
            return best_value, best_move
        # Black's turn (minimizing)
        best_value = +inf
        best_move = None
        for move in chess_game.legal_moves():
            chess_game.play(move)
            value, _ = self._minimax(chess_game, depth - 1)
            chess_game.pop_play()
            if value < best_value:
                best_move = move
                best_value = value
        return best_value, best_move

    def _alpha_beta_basic(
        self, chess_game: ChessGame, depth: int, alpha: float, beta: float
    ) -> Tuple[float, chess.Move]:
        """
        Implements the basic Alpha-Beta Pruning
        algorithm, whithout any further improvement.
        """
        if depth == 0 or chess_game.has_finished():
            return self._evaluate_game_node(chess_game), None
        # White's turn (maximizing)
        if chess_game.white_to_play():
            best_value = -inf
            best_move = None
            for move in chess_game.legal_moves():
                chess_game.play(move)
                value, _ = self._alpha_beta_basic(chess_game, depth - 1, alpha, beta)
                chess_game.pop_play()
                if value > best_value:
                    best_value = value
                    best_move = move
                if value > beta:
                    break
                alpha = max(alpha, best_value)
            return best_value, best_move
        # Black's turn (minimizing)
        best_value = +inf
        best_move = None
        for move in chess_game.legal_moves():
            chess_game.play(move)
            value, _ = self._alpha_beta_basic(chess_game, depth - 1, alpha, beta)
            chess_game.pop_play()
            if value < best_value:
                best_value = value
                best_move = move
            if value < alpha:
                break
            beta = min(beta, best_value)
        return best_value, best_move

    def _call_alpha_beta(self, chess_game: ChessGame, improved: bool) -> Tuple[float, chess.Move]:
        """
        Provides the initial call to the Alpha-Beta Pruning algorithm.
        If 'improved' = True, it calls the improved method. Else
        it calls the default Alpha-Beta Pruning implementation.
        """
        alpha = -ChessEngine.MATE_PUNCTUATION
        beta = +ChessEngine.MATE_PUNCTUATION
        if not improved:
            return self._alpha_beta_basic(chess_game, self.depth, alpha, beta)
        return self._alpha_beta_improved(chess_game, self.depth, alpha, beta)

    def _alpha_beta_improved(
        self, chess_game: ChessGame, depth: int, alpha: float, beta: float
    ) -> Tuple[float, chess.Move]:
        """
        Implements the basic Alpha-Beta Pruning
        algorithm with some other improvements.
        """
        # Check if node was recently calculated
        pre_value_move = self._get_node_alpha_beta_value_and_move(chess_game, depth)
        if pre_value_move[0] is not None:
            return pre_value_move
        # Check if leaf or max depth was reached
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
            alpha_beta, _ = self._alpha_beta_improved(chess_game, depth - 1, alpha, beta)
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
        """
        Out of CT-213 Exam's scope!

        Provides the initial call to ABP PVS variation algorithm.
        """
        aspiration = False
        mtd = True
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
        elif mtd:
            test = 0
            while True:
                score, best_move = self._alpha_beta_recursion_pvs(chess_game, self.depth, test-0.005, test + 0.005)
                if test == score:
                    break
                test = score
        else:
            alpha = -ChessEngine.MATE_PUNCTUATION
            beta = +ChessEngine.MATE_PUNCTUATION
            score, best_move = self._alpha_beta_recursion_pvs(chess_game, self.depth, alpha, beta)
        return score, best_move

    def _alpha_beta_recursion_pvs(
        self, chess_game: ChessGame, depth: int, alpha: float, beta: float
    ) -> Tuple[float, chess.Move]:
        """
        Out of CT-213 Exam's scope!

        Implementation of Alpha-Beta Pruning PVS variation.
        """
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
            alpha_beta = 0
            if best_move is None:
                alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, alpha, beta)
                best_move = move
                best_value = alpha_beta
                chess_game.pop_play()
                continue
            else:
                alpha_beta, _ = self._alpha_beta_recursion_pvs(chess_game, depth - 1, alpha, alpha + 0.005)
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
        """
        Checks if the 'legal_moves' dictionary already contains
        the moves for the current board configuration.
        """
        legal_moves = self.legal_moves.get(chess_game.hash, None)
        if legal_moves:
            return legal_moves
        return chess_game.legal_moves()

    def _set_legal_moves(self, chess_game: ChessGame, move_value: dict, depth: int) -> None:
        """
        Saves the legal moves to the 'legal_moves' dictionary,
        ordering them by the values calculated in the current iteration.
        """
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
        """
        Checks if node was recently calculated. If it is still
        stored, return the stored value and respective move.
        """
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
        """
        Store recent nodes' value and move.
        """
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
        """
        Dummy evaluation. Evaluates considering only
        checkmates, stalemates and pawn/pieces values.
        """
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
        """
        Evaluates a board configuration according
        to some Chess heuristics listed below.
        """
        # MOBILITY_WEIGHT = 0.00001
        CENTRAL_CONTROL_WEIGHT = 0.05
        OUTER_CENTRAL_CONTROL_WEIGHT = 0.005
        MATERIAL_POINTS_WEIGHT = 1
        DEVELOPMENT_WEIGHT = 0.1

        # Checkmates and Stalemantes
        if board.result() == "0-1":
            return -ChessEngine.MATE_PUNCTUATION
        if board.result() == "1-0":
            return ChessEngine.MATE_PUNCTUATION
        if board.result() == "1/2-1/2":
            return 0

        board_rows = str(board).split("\n")

        # Material Evaluation
        material_points = 0
        for i in range(64):
            piece = str(board.piece_at(i))
            material_points += ChessEngine.PUNCTUATIONS.get(piece, 0)
        material_points *= MATERIAL_POINTS_WEIGHT

        # Mobility Evaluation
        # mobility = len(list(board.legal_moves)) * MOBILITY_WEIGHT
        # if not board.turn:
        #     mobility *= -1

        # Center Control Evaluation
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

        # Outer Center Control Evaluation
        outer_center_control = 0

        outer_center_control += len(board.attackers(chess.WHITE, chess.C6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.D6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.E6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F6))
        outer_center_control += len(board.attackers(chess.WHITE, chess.C5))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F5))
        outer_center_control += len(board.attackers(chess.WHITE, chess.C4))
        outer_center_control += len(board.attackers(chess.WHITE, chess.F4))
        # outer_center_control += len(board.attackers(chess.WHITE, chess.C3))
        # outer_center_control += len(board.attackers(chess.WHITE, chess.D3))
        # outer_center_control += len(board.attackers(chess.WHITE, chess.E3))
        # outer_center_control += len(board.attackers(chess.WHITE, chess.F3))

        # outer_center_control -= len(board.attackers(chess.BLACK, chess.C6))
        # outer_center_control -= len(board.attackers(chess.BLACK, chess.D6))
        # outer_center_control -= len(board.attackers(chess.BLACK, chess.E6))
        # outer_center_control -= len(board.attackers(chess.BLACK, chess.F6))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C5))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F5))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C4))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F4))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.C3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.D3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.E3))
        outer_center_control -= len(board.attackers(chess.BLACK, chess.F3))

        outer_center_control *= OUTER_CENTRAL_CONTROL_WEIGHT

        # Development Evaluation
        development = 0
        white_row = board_rows[7]
        black_row = board_rows[0]
        black_pieces_hiding = len([x for x in black_row if x in ["n", "b"]])
        white_pieces_hiding = len([x for x in white_row if x in ["N", "B"]])
        development = black_pieces_hiding - white_pieces_hiding
        development *= DEVELOPMENT_WEIGHT

        # Add All Evaluation Elements
        evaluation = 0
        evaluation += material_points
        # evaluation += mobility
        evaluation += central_control
        evaluation += outer_center_control
        evaluation += development
        # print("central control:", central_control)
        # print("outer central control:", outer_center_control)
        # print("mobility:", mobility)
        # print("material:", material_points)
        # print(evaluation)
        return evaluation
