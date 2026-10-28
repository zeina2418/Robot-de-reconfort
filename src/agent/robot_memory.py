from shared.Wardrobe import Box, Wardrobe
from shared.Emotion import Emotion
from shared.Intensity import Intensity

class Memory:

    N_LINES = len(Intensity)
    N_COLUMNS = len(Emotion)

    def __init__(self):
        self._boxes = [
            [Box(line, column) for column in range(self.N_COLUMNS)]
                               for line in range(self.N_LINES)
            ]

    