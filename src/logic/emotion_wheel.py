from shared.Emotion import Emotion
from shared.Wardrobe import Box, Wardrobe


class EmotionWheel:

    def __init__(self, start: Box, emotions=Emotion):
        self._size = len(Emotion)

    CLOCKWISE = 1
    ANTICLOCKWISE = -1

    @property
    def size(self) -> int:
        return self._size

    def distance(self, e1: Emotion, e2: Emotion) -> int:
        clockwise = (e2.value - e1.value) % self._size
        anticlockwise = self._size - abs(clockwise)

        # Using <= since preference for clockwise distances
        if(clockwise <= anticlockwise):
            return (clockwise, self.CLOCKWISE)
        else:
            return (anticlockwise, self.ANTICLOCKWISE)
