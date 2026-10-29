from __future__ import annotations
from typing import TYPE_CHECKING

from shared.Map import Map

if TYPE_CHECKING:
    from shared.Wardrobe import Wardrobe
    
class Memory:
    def __init__(self, mentalMap: Map, mentalWardrobe: Wardrobe, mentalDictionnary):
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
