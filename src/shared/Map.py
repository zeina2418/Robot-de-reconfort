
from shared import TileType

class Map:
    
    def __init__(self, length, width)
        # initializes map with "0" = LIBRE for all cases
        self.map = [[0 for _ in range(length)] for _ in range(width)]

    def tile_type(length, width)
        return self.map[length][width]

    def set_tile_type(tile_type, length, width)
        self.map[length][width] = tile_type


