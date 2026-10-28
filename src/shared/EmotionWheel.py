from shared.Emotion import Emotion
from Wardrobe import Box, Wardrobe


class EmotionWheel:

    def __init__(self, start: Box, boxes: Wardrobe, emotions=Emotion):
        self._current = start
        self._boxes = boxes
        self._size = len(Emotion)

    CLOCKWISE = 1
    ANTICLOCKWISE = -1

    @property
    def size(self) -> int:
        return self._size

    @property
    def position(self) -> Box:
        return self._current

    def distance(self, e1: Emotion, e2: Emotion) -> int:
        clockwise = (e2.value - e1.value) % self._size
        anticlockwise = self._size - abs(clockwise)

        # Using <= since preference for clockwise distances
        if(clockwise <= anticlockwise):
            return (clockwise, self.CLOCKWISE)
        else:
            return (anticlockwise, self.ANTICLOCKWISE)

    def get_neighbor(self, e: Emotion, distance: int, direction: int) -> Emotion : 
        # To be a neighbor, it has to be 2 cases distance maximum
        if (abs(distance) > 2):
            return -1
        return Emotion((e.value + distance*direction) % self._size)

    def move_n(self):
        if (self._current.column == 0):
            raise ValueError("\\Error: can't move north from column 0")
        self._current = self._boxes[self._current.line][self._current.column - 1]

    def move_s(self):
        if (self._current.column == self._boxes.N_COLUMNS):
            raise ValueError(f"\\Error: can't move south from column {self._boxes.N_COLUMNS}")
        self._current = self._boxes[self._current.line][self._current.column - 1]

    def move_e(self):
        self._current = self._boxes[(self._current.line+ 1) % self.N_LINES][self._current.column]

    def move_o(self):
        self._current = self._boxes[(self._current.line- 1) % self.N_LINES][self._current.column]

    def check_object(self):
        return self._current.object