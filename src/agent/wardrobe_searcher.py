from collections import deque
from typing import Optional
from typing import NamedTuple

from agent.memory import WardrobeMemory
from logic.emotion_wheel import EmotionWheel
from shared.Wardrobe import BoxState, Direction, Wardrobe
from shared.Emotion import Emotion
from shared.Intensity import Intensity


class Position(NamedTuple):
    emotion: Emotion
    intensity: Intensity

class WardrobeSearcher:

    def __init__(self, memory: WardrobeMemory, wheel: EmotionWheel, start: Position):
        self._memory = memory
        self._wheel = wheel
        self._current: Position = start # position in front of the selector
        self._candidates: deque[Position] = deque()

    @property
    def current(self) -> Position:
        return self._current

    def search(self, emotion: Emotion, intensity: Intensity, wardrobe: Wardrobe):
        self._candidates = deque(self._wheel.candidates(emotion, intensity))

        while (target := self.target_box()) is not None:
            route = self.get_route(target)
            if route:
                self._current = wardrobe.move_route(route)

            box_state = self._memory.box_at(self._current.emotion, self._current.intensity)

            if box_state == BoxState.UNKNOWN:
                self.record_content(wardrobe.check_object())

            if box_state == BoxState.FILLED:
                object = wardrobe.take_object()
                self.record_content()
                return object
            else:
                # Remove empty box
                self._candidates.popleft()
            

    def target_box(self) -> Optional[Position]:
        while self._candidates and self._memory.state_at(self._candidates[0]) == BoxState.EMPTY:
            # Remove empty box from candidate's list
            self._candidates.popleft()
        return self._candidates[0] if self._candidates else None

    def record_content(self, content: Optional[str]):
        self._memory.record(self._current.emotion, self._current.intensity, content)

    def get_route(self, target: Position) -> list[Direction]:
        i_steps = target.intensity.value - self._current.intensity.value
        moves = [Direction.S if i_steps > 0 else Direction.N] * abs(i_steps)

        e_steps, sense = self._wheel.distance(self._current.emotion, target.emotion)
        moves += [Direction.E if sense == EmotionWheel.CLOCKWISE else Direction.W] * e_steps
        return moves
        
