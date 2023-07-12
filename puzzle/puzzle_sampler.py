from puzzle.puzzle_parser.puzzle_parser import Puzzle
from puzzle.puzzle_themes import THEMES

PUZZLE_FOLDER = "puzzle/puzzles/"
FILE_NAME = "lichess_db_puzzle_small.csv"

# themes = set()

def action(puzzle: Puzzle) -> None:
    for theme in puzzle.themes:
        if theme in THEMES:
            with open(PUZZLE_FOLDER + f"category_separated/{theme}.csv", "a") as f:
                f.write(puzzle.puzzle_string)
    
def final_action() -> None:
    # theme_list = list(themes)
    # theme_list.sort()
    # for theme in theme_list:
    #     print(theme)
    pass


with open(PUZZLE_FOLDER + FILE_NAME, "r") as input_file:
    count = 0
    for line in input_file:
        count += 1
        if count == 1:
            continue
        puzzle = Puzzle(line)
        action(puzzle)
    final_action()
    print("\nFinished!")
