import pygame

from chess_game.chess_game import ChessGame

from chess_interface.src.const import *
from chess_interface.src.board import Board
from chess_interface.src.dragger import Dragger
from chess_interface.src.config import Config
from chess_interface.src.square import Square
from chess_interface.src.piece import *


class Interface:
    def __init__(self) -> None:
        self.next_player = "white"
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.theme = self.config.theme

    def show_bg(self, surface: pygame.Surface) -> None:
        """
        Display board's squares and labels
        """
        for row in range(ROWS):
            for col in range(COLS):
                color = self.theme.bg.light if (row + col) % 2 == 0 else self.theme.bg.dark
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)
                # Row labels (1, 2, 3, ...)
                if col == 0:
                    color = self.theme.bg.dark if row % 2 == 0 else self.theme.bg.light
                    label = self.config.font.render(str(ROWS - row), 1, color)
                    label_pos = (5, 5 + row * SQSIZE)
                    surface.blit(label, label_pos)
                # Column labels (a, b, c, ...)
                if row == 7:
                    color = self.theme.bg.dark if (row + col) % 2 == 0 else self.theme.bg.light
                    label = self.config.font.render(Square.get_alphacol(col), 1, color)
                    label_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(label, label_pos)

    def show_pieces(self, surface: pygame.Surface) -> None:
        """
        Display every piece not being dragged.
        """
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    # Display all pieces except piece being dragged
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = (
                            col * SQSIZE + SQSIZE // 2,
                            row * SQSIZE + SQSIZE // 2,
                        )
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface: pygame.Surface) -> None:
        """
        Display all possible (valid) moves when dragging a piece.
        """
        if self.dragger.dragging:
            for move in self.dragger.valid_moves:
                color = self.theme.moves.light if (move[0] + move[1]) % 2 == 0 else self.theme.moves.dark
                rect = (move[1] * SQSIZE, move[0] * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface: pygame.Surface) -> None:
        """
        Highlights the initial and final squares
        of the most recent piece movement.
        """
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                color = self.theme.trace.light if (pos.row + pos.col) % 2 == 0 else self.theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface: pygame.Surface) -> None:
        """
        Highlights the border of the square
        which the mouse is currently hovering.
        """
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (
                self.hovered_sqr.col * SQSIZE,
                self.hovered_sqr.row * SQSIZE,
                SQSIZE,
                SQSIZE,
            )
            pygame.draw.rect(surface, color, rect, width=3)

    def show_promotion_dialog(self, surface: pygame.Surface) -> None:
        """
        Displays promotion dialog, containing possible
        pieces and respective numbers to press.
        """
        transparency = pygame.Surface((WIDTH, HEIGHT))
        transparency.set_alpha(192)
        transparency.fill(self.theme.bg.dark)
        surface.blit(transparency, (0, 0))

        message = "Choose the piece you want to promote to!"
        text = self.config.font_big.render(message, 1, "black", "white")
        text_rect = text.get_rect(center=(4 * SQSIZE, -5 + 3.5 * SQSIZE))
        surface.blit(text, text_rect)

        for piece, num in [
            (Queen("white"), 1),
            (Rook("white"), 2),
            (Knight("white"), 3),
            (Bishop("white"), 4),
        ]:
            # Draw piece
            texture = piece.texture
            img = pygame.image.load(texture)
            img_center = ((num + 1.5) * SQSIZE, 4 * SQSIZE)
            piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, piece.texture_rect)
            # Draw corresponding number
            number = self.config.font_big.render(str(num), 1, "black", "white")
            number_rect = number.get_rect(center=((num + 1.5) * SQSIZE, 5 + 4.5 * SQSIZE))
            surface.blit(number, number_rect)

    def show_all(self, surface: pygame.Surface) -> None:
        """
        Display in the correct layer order all the previous
        blits functions in the, except for the promotion dialog.
        """
        self.show_bg(surface)
        self.show_last_move(surface)
        self.show_moves(surface)
        self.show_pieces(surface)
        self.show_hover(surface)

    def next_turn(self) -> None:
        """
        Sets the 'next_player' attribute to the other player.
        """
        self.next_player = "white" if self.next_player == "black" else "black"

    def set_hover(self, row, col) -> None:
        """
        Sets the 'hovered_sqr' attribute as the given coordinates.
        """
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self) -> None:
        """
        Changes current color theme to the next one. Loops
        through the [green, brown, blue, gray] order.
        """
        self.config.change_theme()
        self.theme = self.config.theme

    def play_sound(self, captured=False) -> None:
        """
        Plays one of the two available sounds: one meant
        for captures and one meant for all other movements.
        """
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self) -> None:
        self.__init__()
