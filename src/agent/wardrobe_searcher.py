from collections import deque
from typing import Optional

from agent.wardrobe_memory import WardrobeMemory
from logic.emotion_wheel import EmotionWheel
from shared.Wardrobe import Box, BoxState, Direction, Wardrobe


class WardrobeSearcher:

    def __init__(self, memory: WardrobeMemory, wheel: EmotionWheel, start: Box):
        self._memory = memory
        self._wheel = wheel
        self._current: Box = start # box in front of the selector
        self._candidates: deque[Box] = deque()

    @property
    def current(self) -> Box:
        return self._current

    def search(self, candidates: list[Box], wardrobe: Wardrobe):
        self._candidates = deque(candidates)

        while (target := self.target_box()) is not None:
            route = self.get_route(target)
            if route:
                emotion, intensity = wardrobe.move_route(route)
                self._current = self._memory.box_at(emotion, intensity)

            if self.current.state == BoxState.UNKNOWN:
                self.record_content(wardrobe.check_object())

            if self.current.state == BoxState.FILLED:
                object = wardrobe.take_object()
                self.record_content()
                return object
            

    def target_box(self) -> Optional[Box]:
        # Remove empty boxes from candidate's list
        while self._candidates and self._candidates[0].state == BoxState.EMPTY:
            self._candidates.popleft()
        return self._candidates[0] if self._candidates else None

    def record_content(self, content: Optional[str]):
        self._memory.record(self._current.emotion, self._current.intensity, content)

    def get_route(self, target: Box) -> list[Direction]:
        i_steps = target.intensity.value - self._selector.intensity.value
        moves = [Direction.S if i_steps > 0 else Direction.N] * abs(i_steps)

        e_steps, sense = self._wheel.distance(self._selector.emotion, target.emotion)
        moves += [Direction.E if sense == EmotionWheel.CLOCKWISE else Direction.O] * e_steps
        return moves
        
