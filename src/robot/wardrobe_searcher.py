from collections import deque
from typing import Optional
from typing import NamedTuple

from robot.memory import WardrobeMemory
from logic.emotion_wheel import EmotionWheel
from shared.Wardrobe import BoxState, Direction, Wardrobe
from shared.Emotion import Emotion
from shared.Intensity import Intensity
from shared.errors import EmptyWardrobeError


class Position(NamedTuple):
    emotion: Emotion
    intensity: Intensity

class WardrobeSearcher:

    def __init__(
        self,
        memory: WardrobeMemory,
        wheel: EmotionWheel,
        start: Position,
        trace,
        demande,
        robot_position
    ):
        self._memory = memory
        self._wheel = wheel
        self._current = start
        self._candidates = deque()
        self._trace = trace
        self._demande = demande
        self._robot_position = robot_position

    @property
    def current(self) -> Position:
        return self._current

    def search(self, emotion: Emotion, intensity: Intensity, wardrobe: Wardrobe):
        self._candidates = deque(
            Position(e, i) for e, i in self._wheel.candidates(emotion, intensity)
        )

        while (target := self.target_box()) is not None:
            route = self.get_route(target)
            if route:
                print("CURRENT:", self._current)
                print("TARGET:", target)
                print("ROUTE:", route)
                for move in route:
                    old_casier = (
                        self._current.intensity.value,
                        self._current.emotion.value
                    )

                    direction = {
                        Direction.N: "N",
                        Direction.S: "S",
                        Direction.E: "E",
                        Direction.W: "O"
                    }[move]

                    self._trace.ajouter_pas(
                        demande=self._demande,
                        position=self._robot_position,
                        casier=old_casier,
                        action="CHERCHER",
                        argument=direction
                    )

                    wardrobe.move_route([move])

                    self._current = Position(
                        Emotion(wardrobe.current.emotion),
                        Intensity(wardrobe.current.intensity)
                    )

            box_state = self._memory.state_at(self._current.emotion, self._current.intensity)

            if box_state == BoxState.UNKNOWN:
                box_state = self.record_content(wardrobe.check_object())

            if box_state == BoxState.FILLED:
                old_casier = (
                    self._current.intensity.value,
                    self._current.emotion.value
                )

                object = wardrobe.take_object()

                self._trace.ajouter_pas(
                    demande=self._demande,
                    position=self._robot_position,
                    casier=old_casier,
                    action="PRENDRE",
                    argument=object,
                    contenu_casier=object
                )

                self.record_content(None)
                return object

            # Remove empty box
            self._candidates.popleft()
        raise EmptyWardrobeError(f"No object found in valid boxes for {emotion.name}/{intensity.name}")


    def target_box(self) -> Optional[Position]:
        while self._candidates and self._memory.state_at(self._candidates[0].emotion, self._candidates[0].intensity) == BoxState.EMPTY:
            # Remove empty box from candidate's list
            self._candidates.popleft()
        return self._candidates[0] if self._candidates else None

    def record_content(self, content: Optional[str]) -> BoxState:
        return self._memory.record(self._current.emotion, self._current.intensity, content)

    def get_route(self, target: Position) -> list[Direction]:
        current_row = self._current.intensity.value
        target_row = target.intensity.value

        current_col = self._current.emotion.value
        target_col = target.emotion.value

        # Vertical movement
        if target_row > current_row:
            vertical_moves = [Direction.S] * (target_row - current_row)
        else:
            vertical_moves = [Direction.N] * (current_row - target_row)

        # Horizontal movement
        e_steps, sense = self._wheel.distance(
            self._current.emotion,
            target.emotion
        )

        horizontal_direction = (
            Direction.E if sense == EmotionWheel.CLOCKWISE
            else Direction.W
        )

        horizontal_moves = [horizontal_direction] * e_steps

        return vertical_moves + horizontal_moves

        
