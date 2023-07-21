from typing import Literal
from time import time

from chess_game.chess_game import ChessEngine, ChessGameByFen
from puzzle.puzzle_parser.puzzle_parser import Puzzle

global_counter = 1

def debug():
    global global_counter
    print(global_counter)
    global_counter += 1

def engine_solves_puzzle(puzzle: Puzzle, engine: ChessEngine) -> bool:
    game = ChessGameByFen(puzzle.fen)
    moves = puzzle.moves
    num_moves = len(moves)
    assert num_moves % 2 == 0
    num_moves = num_moves // 2
    total_time = 0
    for i in range(num_moves):
        game.play(moves[2 * i])
        start = time()
        predicted_move = engine.best_move(game)
        total_time += time() - start
        if predicted_move != moves[2 * i + 1]:
            return False, total_time/(i+1)
        game.play(predicted_move)
    return True, total_time/num_moves


def evaluate_engine_by_category(category: str, depth: int, algorithm: Literal["minimax", "abp", "abpi"] = "abpi", limit=None) -> float:
    file_name = "puzzle/puzzles/category_separated/" + category + ".csv"
    report_file_name = "puzzle/puzzles/category_reports/" + category + ".csv"
    total_count = 0
    correct_count = 0
    total_time = 0
    with open(file_name, "r") as f:
        for line in f:
            chess_engine = ChessEngine(depth = depth, algorithm=algorithm)
            puzzle = Puzzle(line)
            
            success, average_time_per_move = engine_solves_puzzle(puzzle, chess_engine)
            if success:
                correct_count += 1
            else:
                with open(report_file_name, "a") as rf:
                    rf.write(f"{puzzle.puzzle_id}\n")
            total_time += average_time_per_move
            total_count += 1
            if limit:
                if total_count >= limit:
                    break

    score = correct_count / total_count
    average_time_per_move = total_time / total_count
    return score, average_time_per_move
