"""Tests for planning/bfs.py and planning/wardrobe_planner.py.

Run from the project root, either way:
    python -m pytest tests/ -v
    python tests/test_planning.py      (no pytest needed)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bfs import shortest_path, adjacent_goals
from shared.Map import Map
from robot.memory import Memory


# Real map of appartement_01. Tests may read it: only the agent may not.
GRID = ["#############", "#......#....#", "#...........#", "#..P...#....#",
        "#.#########.#", "#......#....#", "#R..A..#...P#",
        "#.....D#....#", "#############"]


def walkable(p):
    return GRID[p[0]][p[1]] in ".R"   # A, D, P and # are blocked

def test_map():
    mental_map = Map(5, 5)
    memory = Memory(mental_map, None, None)

    memory.update_map(
        (2, 2),
        {"N": "libre", "S": "mur", "E": "armoire", "O": "dictionnaire"}
    )

    mental_map.display()

if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError:
                failed += 1
                print(f"FAIL  {name}")
    sys.exit(1 if failed else 0)