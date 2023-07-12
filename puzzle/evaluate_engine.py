from chess_game.chess_game import ChessEngine, ChessGameByFen
from puzzle.puzzle_parser.puzzle_parser import Puzzle
from time import time

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
    for i in range(num_moves):
        game.play(moves[2 * i])
        predicted_move = engine.best_move(game)
        if predicted_move != moves[2 * i + 1]:
            return False
        game.play(predicted_move)
    return True


def evaluate_engine_by_category(category: str, limit=None) -> float:
    file_name = "puzzle/puzzles/category_separated/" + category + ".csv"
    report_file_name = "puzzle/puzzles/category_reports/" + category + ".csv"
    chess_engine = ChessEngine()
    total_count = 0
    correct_count = 0
    total_time = 0
    with open(file_name, "r") as f:
        for line in f:
            puzzle = Puzzle(line)
            start = time()
            if engine_solves_puzzle(puzzle, chess_engine):
                correct_count += 1
            else:
                with open(report_file_name, "a") as rf:
                    rf.write(f"{puzzle.puzzle_id}\n")
            total_time += time() - start
            total_count += 1
            if limit:
                if total_count >= limit:
                    break

    score = correct_count / total_count
    average_time = total_time / total_count
    return score, average_time
