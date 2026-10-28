from dataclasses import dataclass
import string

from Emotion import Emotion
from Intensity import Intensity

@dataclass(frozen=True)
class Box:
    line: int
    column: int
    object: string

class Wardrobe:

    N_LINES = len(Intensity)
    N_COLUMNS = len(Emotion)

    def __init__(self):
        self._boxes = [self.N_LINES][self.N_COLUMNS]
