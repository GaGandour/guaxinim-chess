import pygame
import sys

from chess_interface.src.const import *
from chess_interface.src.interface import Interface
from chess_interface.src.square import Square
from chess_interface.src.move import Move

class Main:

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('CT-213 Guaxinim Chess (Human x AI)')
        self.interface = Interface()

    def mainloop(self):
        screen = self.screen
        interface = self.interface
        board = self.interface.board
        dragger = self.interface.dragger
        promotion_time = False

        while True:
            interface.show_all(screen)
            if promotion_time:
                interface.show_promotion_dialog(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                # Click event
                if not promotion_time:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        # If clicked square has a piece
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            # If piece is from the correct player
                            if piece.color == interface.next_player:
                                dragger.save_initial(event.pos)
                                dragger.save_valid_moves(board.calc_moves(clicked_row, clicked_col))
                                dragger.drag_piece(piece)
                
                    # Mouse motion
                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        interface.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                
                    # Click release event
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragger.dragging:
                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            # create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)
                            
                            # If a valid move
                            if initial != final:
                                if board.is_promotion_move(move):
                                    promotion_time = True
                                if board.is_valid_move(move):
                                    is_capture = board.squares[released_row][released_col].has_piece()
                                    board.last_move = move
                                    board.move(move)
                                    interface.play_sound(is_capture)
                                    interface.next_turn()
                        
                        dragger.undrag_piece()
                
                # Key press event
                if event.type == pygame.KEYDOWN:
                    
                    # Promotion
                    if promotion_time:
                        chosen = None
                        if event.key == pygame.K_1:
                            chosen = "q"
                        if event.key == pygame.K_2:
                            chosen = "r"
                        if event.key == pygame.K_3:
                            chosen = "n"
                        if event.key == pygame.K_4:
                            chosen = "b"
                        if chosen:
                            promotion_time = False
                            is_capture = board.squares[released_row][released_col].has_piece()
                            board.last_move = move
                            board.move(move, promotion=chosen)
                            interface.play_sound(is_capture)
                            interface.next_turn()

                    # Color theme change
                    if event.key == pygame.K_t:
                        interface.change_theme()

                    # Game reset
                    if event.key == pygame.K_r:
                        interface.reset()
                        interface = self.interface
                        board = self.interface.board
                        dragger = self.interface.dragger

                # Quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()


main = Main()
main.mainloop()