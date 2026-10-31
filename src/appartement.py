
DIRECTIONS = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "O": (0, -1),
}

# Types the robot is allowed to perceive.
PERCEPTION_TYPES = {
    "mur",
    "libre",
    "armoire",
    "dictionnaire",
    "resident",
}


class Appartement:

    def __init__(self, carte: dict):
        self.height = carte["dimensions"]["hauteur"]
        self.width = carte["dimensions"]["largeur"]
        self.robot_position = None

        # The real grid belongs exclusively to the simulator.
        self._grid = carte["grille"]
        self._legend = carte["legende"]

        self._validate_grid()

    
    def move(self, direction):
        if self.robot_position is None:
            raise ValueError("Robot has not been placed.")

        if direction not in DIRECTIONS:
            raise ValueError("Unknown direction.")

        dr, dc = DIRECTIONS[direction]
        row, col = self.robot_position
        new_position = (row + dr, col + dc)

        if self._cell_type(*new_position) != "libre":
            return self.robot_position, False

        self.robot_position = new_position
        return self.robot_position, True

    def placer_robot(self, position):
        row, col = position

        if not (0 <= row < self.height and 0 <= col < self.width):
            raise ValueError("Robot position is outside the apartment.")

        self.robot_position = (row, col)

    def _validate_grid(self):
        """Check that the apartment grid matches its dimensions."""
        if len(self._grid) != self.height:
            raise ValueError("Incorrect apartment height.")

        for row in self._grid:
            if len(row) != self.width:
                raise ValueError("Incorrect apartment width.")

        for row in self._grid:
            for symbol in row:
                if symbol not in self._legend:
                    raise ValueError(f"Unknown grid symbol: {symbol}")

    def _cell_type(self, row: int, col: int) -> str:
        """Translate a grid symbol into a cell type."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return "mur"

        symbol = self._grid[row][col]
        cell_type = self._legend[symbol]

        # The robot's starting position is walkable.
        # It is not a separate perception category.
        if cell_type == "depart du robot":
            return "libre"

        return cell_type

    def perceive(self):
        if self.robot_position is None:
            raise ValueError("Robot has not been placed.")

        return self._perceive_position(self.robot_position)

    def _perceive_position(self, position: tuple[int, int]) -> dict:
        """
        Return the four cells adjacent to the robot.
        The robot never receives the actual grid.
        """
        row, col = position

        if not (0 <= row < self.height and 0 <= col < self.width):
            raise ValueError("Robot position is outside the apartment.")

        observations = {}

        for direction, (dr, dc) in DIRECTIONS.items():
            neighbor_row = row + dr
            neighbor_col = col + dc

            observations[direction] = self._cell_type(
                neighbor_row,
                neighbor_col
            )

        # Check that the simulator returned valid observations.
        if any(value not in PERCEPTION_TYPES
               for value in observations.values()):
            raise ValueError("Invalid cell type in apartment perception.")

        return observations
    
  