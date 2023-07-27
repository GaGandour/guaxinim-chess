from typing import Union, Tuple


class Color:
    def __init__(self, light: Union[Tuple[int, int, int], str], dark: Union[Tuple[int, int, int], str]) -> None:
        self.light = light
        self.dark = dark
