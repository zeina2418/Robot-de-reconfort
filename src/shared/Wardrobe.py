from dataclasses import dataclass

from shared.Emotion import Emotion
from shared.Intensity import Intensity


class Box:
    line: int
    column: int
    known: bool = False
    object: str = ""

    def check_object(self):
        return self.object

    def is_known_object(self):
        return self.know

    def empty_box(self):
        return self.know is True and self.object == ""

    def set_object(self, obj: str):
        self.object = obj

    def get_object(self):
        obj = self.object
        self.object = ""
        return obj


class Wardrobe:

    N_LINES = len(Intensity)
    N_COLUMNS = len(Emotion)

    def __init__(self):
        self._boxes = [
            [Box(line, column) for column in range(self.N_COLUMNS)]
            for line in range(self.N_LINES)
        ]
        self._current = self._boxes[0][0] # start position

    @property
    def current(self) -> Box:
        return self._current

    # Moving methods
    def move_n(self):
        if (self._current.column == 0):
            raise ValueError("\\Error: can't move north from column 0")
        self._current = self._boxes[self._current.line - 1][self._current.column]

    def move_s(self) -> None:
        if self._current.line == self.N_LINES - 1:
            raise ValueError(f"can't move south from line {self.N_LINES - 1}")
        self._current = self._boxes[self._current.line + 1][self._current.column]

    def move_e(self) -> None:
        self._current = self._boxes[self._current.line][(self._current.column + 1) % self.N_COLUMNS]

    def move_o(self) -> None:
        self._current = self._boxes[self._current.line][(self._current.column - 1) % self.N_COLUMNS]
