from shared.Emotion import Emotion
from shared.Intensity import Intensity
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

    def emotions_at(self, emotion: Emotion, distance: int) -> list[Emotion]:
        if distance == 0:
            return [emotion]
        return [Emotion((emotion.value + (self.CLOCKWISE*distance)) % self.size),
                Emotion((emotion.value + (self.ANTICLOCKWISE*distance)) % self.size)]

    def ordered_intensities(self, intensity: Intensity) -> list[Intensity]:
        if intensity == Intensity.FAIBLE:
            return [Intensity.FAIBLE, Intensity.MOYENNE, Intensity.FORTE]
        if intensity == Intensity.MOYENNE:
            return [Intensity.MOYENNE, Intensity.FAIBLE, Intensity.FORTE]
        if intensity == Intensity.FORTE:
            return [Intensity.FORTE, Intensity.MOYENNE, Intensity.FAIBLE]

    def candidates(self, emotion: Emotion, intensity: Intensity) -> list[tuple[Emotion, Intensity]]:
        result = []
        for distance in range(3):
            for level in self.ordered_intensities(intensity):
                for neighbor in self.emotions_at(emotion, distance):
                    result.append((neighbor, level))
        return result
