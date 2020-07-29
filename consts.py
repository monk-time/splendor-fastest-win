from enum import Enum


class Color(Enum):
    WHITE = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    BLACK = 4

    def __repr__(self):
        return self.__str__()


# noinspection PyTypeChecker
COLOR_NUM = len(Color)

MAX_GEMS = 7
