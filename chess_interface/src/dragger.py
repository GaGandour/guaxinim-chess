import pygame
from typing import List, Tuple

from chess_interface.src.const import *
from chess_interface.src.piece import Piece


class Dragger:
    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0
        self.valid_moves = []

    def update_blit(self, surface: pygame.Surface) -> None:
        """
        Updates dragged piece image according
        to the current mouse position.
        """
        self.piece.set_texture(size=128)
        texture = self.piece.texture
        img = pygame.image.load(texture)
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.texture_rect)

    def update_mouse(self, pos: Tuple[int, int]) -> None:
        self.mouseX, self.mouseY = pos

    def save_initial(self, pos: Tuple[int, int]) -> None:
        """
        Saves the initial position
        of the piece being dragged.
        """
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE

    def save_valid_moves(self, valid_moves: List[Tuple[int, int]]) -> None:
        """
        Saves the position of all squares
        where the dragged piece may go.
        """
        self.valid_moves = valid_moves

    def drag_piece(self, piece: Piece) -> None:
        """
        Save the state of the chosen piece as dragging.
        """
        self.piece = piece
        self.dragging = True

    def undrag_piece(self) -> None:
        """
        Reset the state of the chosen piece and the stored valid moves.
        """
        self.piece = None
        self.dragging = False
        self.valid_moves = []
