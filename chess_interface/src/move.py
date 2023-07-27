from chess_interface.src.square import Square


class Move:
    def __init__(self, initial: Square, final: Square) -> None:
        """
        A move is defined by a initial square and final
        square. It represents the initial position and
        final position through which the piece moves.
        """
        self.initial = initial
        self.final = final

    def __str__(self) -> str:
        s = ""
        s += f"({self.initial.col}, {self.initial.row})"
        s += f" -> ({self.final.col}, {self.final.row})"
        return s

    def __eq__(self, other) -> bool:
        return self.initial == other.initial and self.final == other.final

    def uci_code(self) -> str:
        """
        Concatenates the two positions (initial and final)
        to create the move as a string in UCI code.
        """
        chess_move_string = self.initial.position + self.final.position
        return chess_move_string
