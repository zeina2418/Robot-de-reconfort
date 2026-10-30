from enum import Enum

from shared.Emotion import Emotion
from shared.Intensity import Intensity

class Direction(Enum):
     
    N = 0  # North
    S = 1  # South
    E = 2  # East
    W = 3  # West


class BoxState(Enum):
    UNKNOWN = 0   # the robot never stood in front of it
    EMPTY = 1     # seen, nothing inside
    FILLED = 2    # seen, contains an object

class Box:
    intensity: int
    emotion: int
    state: BoxState = BoxState.UNKNOWN
    object: str = ""

    def __init__(self, line, column):
        self.intensity = line
        self.emotion = column

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
        if self.state != BoxState.FILLED:
            raise ValueError("can't take: the box is empty or has not been checked")
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

    def take_object(self) -> str:
        return self.current.get_object()

    def check_object(self) -> str:
        return self.current.object

    def move_route(self, route: list[Direction]):
        for move in route:
            if move is Direction.N:
                self.move_n()
            if move is Direction.S:
                self.move_s()
            if move is Direction.E:
                self.move_e()
            if move is Direction.W:
                self.move_w()
        return self.current.emotion, self.current.intensity

    # Moving methods
    def move_n(self):
        if (self._current.intensity == 0):
            raise ValueError("can't move north from line 0")
        self._current = self._boxes[self._current.intensity - 1][self._current.emotion]

    def move_s(self) -> None:
        if self._current.intensity == self.N_LINES - 1:
            raise ValueError("can't move south from line 0")
        self._current = self._boxes[self._current.intensity + 1][self._current.emotion]

    def move_e(self) -> None:
        self._current = self._boxes[self._current.intensity][(self._current.emotion + 1) % self.N_COLUMNS]

    def move_w(self) -> None:
        self._current = self._boxes[self._current.intensity][(self._current.emotion - 1) % self.N_COLUMNS]
