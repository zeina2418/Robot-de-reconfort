from __future__ import annotations
from typing import TYPE_CHECKING

from shared.Map import Map

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
        if emotion.value >= self.N_COLUMNS or intensity.value >= self.N_LINES:
            raise ValueError("Position is out of range")
        return self._boxes[intensity.value][emotion.value]

    def state_at(self, emotion: Emotion, intensity: Intensity) -> BoxState:
        if emotion.value >= self.N_COLUMNS or intensity.value >= self.N_LINES:
            raise ValueError("Position is out of range")
        return self.box_at(emotion, intensity).state

    def record(self, emotion, intensity, obj: str | None):
        box = self.box_at(emotion, intensity)
        if obj:
            box.set_object(obj)
        else:
            box.set_empty()


class Memory:
    def __init__(self, mentalMap: Map, mentalWardrobe: WardrobeMemory, mentalDictionnary):
            self.map = mentalMap
            self.wardrobe = mentalWardrobe
            self.dictionnary = mentalDictionnary


    def update_map(self, position, perception):
        row, col = position

        directions = {
            "N": (-1, 0),
            "S": (1, 0),
            "E": (0, 1),
            "O": (0, -1),
        }

        symbols = {
            "mur": "#",
            "libre": ".",
            "armoire": "A",
            "dictionnaire": "D",
            "resident": "P",
        }

        for direction, observation in perception.items():
            if direction not in directions:
                continue

            if observation not in symbols:
                continue

            dr, dc = directions[direction]
            neighbor_row = row + dr
            neighbor_col = col + dc

            if (0 <= neighbor_row < self.map.height
                    and 0 <= neighbor_col < self.map.width):
                self.map.set_tile_type(
                    symbols[observation],
                    neighbor_row,
                    neighbor_col
                )
