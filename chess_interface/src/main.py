import pygame
import sys

from chess_game.chess_game import ChessEngine
from chess_interface.src.const import *
from chess_interface.src.interface import Interface
from chess_interface.src.square import Square
from chess_interface.src.move import Move

PVP_ON = False

class Main:

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('CT-213 Guaxinim Chess (Human x AI)')
        self.interface = Interface()
        self.engine = ChessEngine(depth=4)

    def mainloop(self):
        screen = self.screen
        interface = self.interface
        board = self.interface.board
        dragger = self.interface.dragger
        promotion_time = False        

        while True:
            # Draw stuff on screen
            interface.show_all(screen)
            if promotion_time:
                interface.show_promotion_dialog(screen)
            if dragger.dragging:
                dragger.update_blit(screen)
            # Handle events
            for event in pygame.event.get():
                # Player behavior
                if interface.next_player == 'white' or PVP_ON:
                    if not promotion_time:
                        # Click event
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
                # AI Behavior
                else:
                    best_move = self.engine.best_move(board.chess_game)
                    initial = Square.position_to_row_col(str(best_move)[0:2])
                    final = Square.position_to_row_col(str(best_move)[2:4])
                    
                    AI_initial = Square(initial[0], initial[1])
                    AI_final = Square(final[0], final[1])
                    AI_move = Move(AI_initial, AI_final)
                    
                    is_capture = board.squares[final[0]][final[1]].has_piece()
                    board.last_move = AI_move
                    board.move(AI_move)
                    interface.play_sound(is_capture)
                    interface.next_turn()
                    


                # Key press events
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