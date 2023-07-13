from typing import List
from chess import Move


class Puzzle:
    def __init__(self, puzzle_string: str) -> None:
        self.puzzle_string: str = puzzle_string
        self.puzzle_id: str = None
        self.fen: str = None
        self.moves: List[Move] = None
        self.num_moves: int = None
        self.rating: int = None
        self.rating_deviation: int = None
        self.popularity: int = None
        self.nb_plays: int = None
        self.themes: List[str] = None
        self.game_url: str = None
        self.opening_tags: List[str] = None
        self.parse_puzzle(puzzle_string)

    def parse_puzzle(self, puzzle_string: str) -> None:
        fields = puzzle_string.split(",")
        self.puzzle_id = fields[0]
        self.fen = fields[1]
        moves_strings = fields[2].split(" ")
        self.moves = [Move.from_uci(move_string) for move_string in moves_strings]
        self.num_moves = len(self.moves) // 2
        self.rating = int(fields[3])
        self.rating_deviation = int(fields[4])
        self.popularity = int(fields[5])
        self.nb_plays = int(fields[6])
        self.themes = fields[7].split(" ")
        self.game_url = fields[8]
        self.opening_tags = fields[9].split(" ")
