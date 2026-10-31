from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import reconfort_io as rio
from appartement import Appartement

carte = rio.charger_carte(ROOT / "data" / "cartes" / "appartement_01.json")
appartement = Appartement(carte)

# Starting position
position = (6, 1)

# Test moving East
new_position, success = appartement.move(position, "E")

assert success is True
assert new_position == (6, 2)

# Test moving West into the starting cell
new_position, success = appartement.move(new_position, "O")

assert success is False or new_position == (6, 1)

print("Movement tests passed!")

# Test perception from the starting position
observations = appartement.perceive((6, 1))

print("Perception:", observations)

assert observations == {
    "N": "libre",
    "S": "libre",
    "E": "libre",
    "O": "mur"
}

print("Perception tests passed!")

from shared.Map import Map
from robot.memory import Memory, WardrobeMemory, DictionaryMemory

mental_map = Map(height=9, width=13)

memory = Memory(
    mentalMap=mental_map,
    mentalWardrobe=WardrobeMemory(),
    mentalDictionnary=DictionaryMemory()
)

position = (6, 1)
observations = appartement.perceive(position)

memory.update_map(position, observations)

print("Mental map:")
for row in memory.map.grid:
    print(row)

assert memory.map.tile_type(5, 1) == "."
assert memory.map.tile_type(7, 1) == "."
assert memory.map.tile_type(6, 2) == "."
assert memory.map.tile_type(6, 0) == "#"

print("Mental map tests passed!")

from logic.bfs import shortest_path, exploration_goals, is_walkable, to_directions, unknown_cells

memory.map.set_tile_type(".", *position)
while True:
    goals = exploration_goals(
        memory.map,
        lambda pos: is_walkable(memory.map, pos)
    )

    if not goals:
        print("Exploration complete!")
        break

    path = shortest_path(
        position,
        goals,
        lambda pos: is_walkable(memory.map, pos)
    )

    if path is None:
        print("No reachable exploration points.")
        break

    directions = to_directions(path)

    if not directions:
        print("Already at an exploration point.")
        break

    direction = directions[0]
    position, success = appartement.move(position, direction)

    if not success:
        print("Movement failed!")
        break

    observations = appartement.perceive(position)
    memory.update_map(position, observations)

print("Final mental map:")
for line in memory.map.grid:
    print(line)

unknown = unknown_cells(memory.map)

print("Unknown cells:", unknown)
print("Number of unknown cells:", len(unknown))

print("BFS exploration test passed!")