from dataclasses import dataclass

from shared.Emotion import Emotion
from shared.Intensity import Intensity

@dataclass(frozen=True)
class Box:
    line: int
    column: int
    # object : Object

class Wardrobe:

    Box[8][4]

    N_LINES = len(Intensity)
    N_COLUMNS = len(Emotion)

    def __init__(self, start: Box):
        self._position = start

    @property
    def position(self) -> Box:
        return self._position

    def move_n(self):
        if (self._position.column == 0):
            raise ValueError(f"\Error: can't move north from column 0")
        self._position = Box(self._position.line, self._position.column - 1)

    def move_s(self):
        if (self._position.column == self.N_COLUMNS):
            raise ValueError(f"\Error: can't move south from column {self.N_COLUMNS}")
        self._position = Box(self._position.line, self._position.column - 1)

    def move_e(self):
        self._position = Box((self._position.line+ 1) % self.N_LINES, self._position.column)

    def move_o(self):
        self._position = Box((self._position.line+ 1) % self.N_LINES, self._position.column)

    def Look(self):
        positon.object
