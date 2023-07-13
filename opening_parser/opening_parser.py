import json
from chess_game.chess_game import ChessGame
from typing import List

opening_sheet = dict()
opening_probabilities = dict()

def parse_opening(opening_string: str) -> List[str]:
    moves = opening_string.split(" ")
    moves_san = []
    for move in moves:
        moves_san.append(move.split(".")[-1])
    return moves_san

with open("opening_parser/Guaxinim Chess Openings - FinalTable.csv") as opening_table:
    count = 0
    for line in opening_table:
        count += 1
        if count == 1:
            continue
        fields = line.split(",")
        white_probability = float(fields[0][:-1])
        black_probability = float(fields[1][:-1])
        opening = fields[2]
        if opening[-1] == '\n':
            opening = opening[:-1]
        moves = parse_opening(opening)
        chess_game = ChessGame()
        for move in moves:
            probability = opening_probabilities.get(chess_game.hash_game(), 0)
            current_probability = black_probability
            if chess_game.white_to_play():
                current_probability = white_probability

            if current_probability > probability:
                opening_probabilities[chess_game.hash_game()] = white_probability
                opening_sheet[chess_game.hash_game()] = str(chess_game.parse_san(move))
            
            chess_game.play_by_san(move)




with open('opening_parser/opening_sheet.json', 'w') as f:
    json.dump(opening_sheet, f, indent=4)
