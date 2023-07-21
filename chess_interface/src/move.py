from chess_interface.src.square import Square


class Move:
    def __init__(self, initial, final):
        # initial and final are squares
        self.initial: Square = initial
        self.final: Square = final

    def __str__(self):
        s = ""
        s += f"({self.initial.col}, {self.initial.row})"
        s += f" -> ({self.final.col}, {self.final.row})"
        return s

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final

    def uci_code(self) -> str:
        chess_move_string = self.initial.position + self.final.position
        return chess_move_string
