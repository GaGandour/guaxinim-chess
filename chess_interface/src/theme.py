from typing import Tuple, Union

from chess_interface.src.color import Color


class Theme:
    def __init__(
        self, 
        light_bg: Union[Tuple[int, int, int], str], 
        dark_bg: Union[Tuple[int, int, int], str], 
        light_trace: Union[Tuple[int, int, int], str], 
        dark_trace: Union[Tuple[int, int, int], str], 
        light_moves: Union[Tuple[int, int, int], str], 
        dark_moves: Union[Tuple[int, int, int], str]
        ) -> None:
        self.bg = Color(light_bg, dark_bg)
        self.trace = Color(light_trace, dark_trace)
        self.moves = Color(light_moves, dark_moves)
