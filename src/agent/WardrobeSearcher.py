from src.shared.Emotion import Emotion
from shared.Wardrobe import Box, Wardrobe
from logic.EmotionWheel import EmotionWheel


class WardrobeSearcher:

    def __init__(self, wheel: EmotionWheel):
            self._emotionWheel = wheel
