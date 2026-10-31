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
        self._current = self._boxes[0][0] # start position before reading json

    @property
    def current(self) -> Box:
        return self._current

    def current_casier(self):
        return (self.current.intensity, self.current.emotion)

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
            raise ValueError("can't move south from last line")
        self._current = self._boxes[self._current.intensity + 1][self._current.emotion]

    def move_e(self) -> None:
        self._current = self._boxes[self._current.intensity][(self._current.emotion + 1) % self.N_COLUMNS]

    def move_w(self) -> None:
        self._current = self._boxes[self._current.intensity][(self._current.emotion - 1) % self.N_COLUMNS]

    def fill_wardrobe(self, data: dict) -> None:
        # Place each object in its box
        emotions = data["emotions"]
        intensities = data["intensites"]
        seen = set()

        for entry in data["casiers"]:
            line, column = entry["ligne"], entry["colonne"]

            # Sanity check for boxes matrix range
            if not (0 <= line < self.N_LINES and 0 <= column < self.N_COLUMNS):
                raise ValueError(f"box [{line}, {column}] is outside the wardrobe")
            if (line, column) in seen:
                raise ValueError(f"box [{line}, {column}] appears twice")
            seen.add((line, column))

            # the labels must match the position
            if (emotions.index(entry["emotion"]) != column or intensities.index(entry["intensite"]) != line):
                raise ValueError(
                    f"box [{line}, {column}] has an inconsistent label: "
                    f"{entry['emotion']}/{entry['intensite']}"
                )

            if entry["objet"] is not None:
                self._boxes[line][column].set_object(entry["objet"])
            else: 
                self._boxes[line][column].set_empty()

        start_line, start_column = data["casier_depart"]
        if not (0 <= start_line < self.N_LINES and 0 <= start_column < self.N_COLUMNS):
            raise ValueError(f"casier_depart [{start_line}, {start_column}] is outside the wardrobe")
        self._current = self._boxes[start_line][start_column]