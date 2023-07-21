

# Guaxinim-Chess!

This is a college project in python for the subject CT-213: Artificial Intelligence for Mobile Robotics, in ITA (Instituto Tecnológico de Aeronáutica, Brazil). "Guaxinim-Chess" is a chess engine developed by two ITA students: Emmanuel Dias ([`@emmanuelsdias`](https://github.com/emmanuelsdias)) and Gabriel Gandour ([`@GaGandour`](https://github.com/GaGandour)).

## How to Execute

### By Cloning the Repos

First, clone this git's repository. Then, you have to setup the needed environment by running `make install` command in the root folder. 

### Running interactive interface

To run the interactive interface, run the `python run_chess_interface.py` or `python3 run_chess_interface.py` command also in the root folder. Please pay attention to the `PVP_ON` and `DEPTH` global variables inside `chess_interface/src/main.py` file. Set them accordingly to your needs, though we suggest a depth value of 4 or less, otherwise the delay originated from the AI calculations gets too high.

### Evaluating the engine

To evaluate the engine, you may run the `python evaluate_engine_by_category.py` command in the root folder. You may edit the `evaluate_engine_by_category.py` file to choose which category, algorithm, depth and number of puzzles you want to evaluate.

## Code strucutre

### Chess Game

The `chess_game` provides the ChessGame class, responsible for managing the Chess logic and board legal moves and changes. Meanwhile, the ChessEngine class is responsible for implementing the algorithms for the AI. For now, there are three fully implemented algorithms (Minimax, Alpha-Beta Pruning and Alpha-Beta Pruning Improved), while a fourth one is in development (Alpha-Beta Pruning with PVS variation).

### Chess Interface

The `chess_interface` provides an interface to interact with the AI or simply play against another human.

#### Known bugs

For now, there is no indication that the game has finished in the interface, the player simply cannot move any piece since there aren't any available moves. Also, when winning against the AI, the game window automatically closes since the AI tries to assert the game hasn't ended before calculating the next move. Finally, pay attention not to drag a piece out of the game window, otherwise, the game crashes too.

### Opening Parser

The `opening_parser` provides the database and parser required for the AI to use in the first game moves. It's supposed to work in a similar way to a Chess player, who studies and memorizes the most famous openings. 

### Puzzle

The `puzzle` provides the database, parser and some functions to evaluate our engine based on its puzzle solving performance.

## Credits

The "Guaxinim-Chess" project used some valuable materials during its development, which are listed and credited below.

The puzzles' database located in the `puzzle` folder was addapted from the puzzles provided by Lichess.com. [[`Lichess.com's puzzles`](https://old.chesstempo.com/chess-openings.html)]

The opening moves' database located in the `opening_parser` folder was addapted from the openings provided by Chess Tempo. [[`ChessTempo's openings`](https://old.chesstempo.com/chess-openings.html)]

The chess interface located in the `chess_interface` folder was adapted from the Python Chess game developed by AlejoG10, mainly the graphical assets and codes related to the graphical display. The code is available [here](https://github.com/AlejoG10/python-chess-ai-yt/).