from dataclasses import dataclass
from enum import Enum

from shared.Emotion import Emotion
from shared.Intensity import Intensity

class BoxState(Enum):
    UNKNOWN = 0   # the robot never stood in front of it
    EMPTY = 1     # seen, nothing inside
    FILLED = 2    # seen, contains an object

class Box:
    line: int
    column: int
    state: BoxState = BoxState.UNKNOWN
    object: str = ""

    def check_object(self):
        return self.object

    def box_state(self):
        return self.state

    def set_object(self, obj: str):
        self.object = obj
        self.state = BoxState.FILLED

    def set_empty(self) -> None:
        self.object = ""
        self.state = BoxState.EMPTY

    def get_object(self):
        obj = self.object
        self.set_empty()
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
