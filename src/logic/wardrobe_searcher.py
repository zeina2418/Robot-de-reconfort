from shared.Emotion import Emotion
from shared.Wardrobe import Box, Wardrobe
from logic.emotion_wheel import EmotionWheel


class WardrobeSearcher:

    def __init__(self, wardrobe: Wardrobe, wheel: EmotionWheel):
        self._wardrobe = wardrobe
        self._emotionWheel = wheel
