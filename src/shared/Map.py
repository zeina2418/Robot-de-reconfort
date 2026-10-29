class Map:

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

        # Each cell is a string: "?" means unknown
        self.grid: list[str] = ["?" * width for _ in range(height)]

    def tile_type(self, row: int, col: int) -> str:
        # Returns the character representing the cell
        return self.grid[row][col]

    def set_tile_type(self, tile_type: str, row: int, col: int) -> None:
        # Replaces the character at the given position
        line = self.grid[row]
        self.grid[row] = line[:col] + tile_type + line[col + 1:]

    def display(self) -> None:
        for row in self.grid:
            print(row)