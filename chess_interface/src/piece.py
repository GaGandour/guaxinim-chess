import os


class Piece:
    def __init__(self, name, color, texture=None, texture_rect=None) -> None:
        self.name = name
        self.color = color
        self.texture = texture
        self.set_texture()
        self.texture_rect = texture_rect

    def set_texture(self, size=80):
        self.texture = os.path.join(f"chess_interface/assets/images/imgs-{size}px/{self.color}_{self.name}.png")


class Pawn(Piece):
    def __init__(self, color) -> None:
        self.dir = -1 if color == "white" else 1
        super().__init__("pawn", color)


class Knight(Piece):
    def __init__(self, color) -> None:
        super().__init__("knight", color)


class Bishop(Piece):
    def __init__(self, color) -> None:
        super().__init__("bishop", color)


class Rook(Piece):
    def __init__(self, color) -> None:
        super().__init__("rook", color)


class Queen(Piece):
    def __init__(self, color) -> None:
        super().__init__("queen", color)


class King(Piece):
    def __init__(self, color) -> None:
        super().__init__("king", color)


# The following dictionary maps python's chess package
# letter codes to the Piece classes created above.
PIECE_MAPPING = {
    "R": [Rook,   "white"],
    "N": [Knight, "white"],
    "B": [Bishop, "white"],
    "Q": [Queen,  "white"],
    "P": [Pawn,   "white"],
    "K": [King,   "white"],
    "r": [Rook,   "black"],
    "n": [Knight, "black"],
    "b": [Bishop, "black"],
    "q": [Queen,  "black"],
    "p": [Pawn,   "black"],
    "k": [King,   "black"],
    ".": [None, None],
}
