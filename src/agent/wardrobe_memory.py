from shared.Wardrobe import Box, BoxState
from shared.Emotion import Emotion
from shared.Intensity import Intensity


class WardrobeMemory:

    N_COLUMNS = len(Emotion)
    N_LINES = len(Intensity)

    def __init__(self):
        self._boxes = [
            [Box(line, column) for column in range(self.N_COLUMNS)]
                               for line in range(self.N_LINES)
            ]

    def box_at(self, emotion: Emotion, intensity: Intensity) -> Box:
        return self._boxes[intensity.value][emotion.value]

    def state_at(self, emotion: Emotion, intensity: Intensity) -> BoxState:
        return self.box_at(emotion, intensity).state

    def record(self, emotion, intensity, obj: str | None):
        box = self.box_at(emotion, intensity)
        if obj:
            box.set_object(obj)
        else:
            box.set_empty()
    