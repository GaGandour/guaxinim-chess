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
    for i in range(num_moves):
        game.play(moves[2*i])
        debug()
        predicted_move = engine.best_move(game)
        debug()
        if predicted_move != moves[2*i + 1]:
            return False
        game.play(predicted_move)
    return True
        

def evaluate_engine_by_category(category: str, limit = None) -> float:
    file_name = "puzzle/puzzles/category_separated/" + category + ".csv"
    chess_engine = ChessEngine()
    total_count = 0
    correct_count = 0
    with open(file_name, "r") as f:
        for line in f:
            puzzle = Puzzle(line)
            if engine_solves_puzzle(puzzle, chess_engine):
                correct_count += 1
            total_count += 1
            if limit:
                if total_count >= limit:
                    break
    return correct_count/total_count

