"""Tests for planning/bfs.py and planning/wardrobe_planner.py.

Run from the project root, either way:
    python -m pytest tests/ -v
    python tests/test_planning.py      (no pytest needed)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bfs import shortest_path, adjacent_goals


# Real map of appartement_01. Tests may read it: only the agent may not.
GRID = ["#############", "#......#....#", "#...........#", "#..P...#....#",
        "#.#########.#", "#......#....#", "#R..A..#...P#",
        "#.....D#....#", "#############"]


def walkable(p):
    return GRID[p[0]][p[1]] in ".R"   # A, D, P and # are blocked


# --- BFS (Annexe B.3) ------------------------------------------------------

def test_bfs_annexe_b3():
    grid = ["######", "#R.#.#", "#.#..#", "#...##", "######"]
    ok = lambda p: 0 <= p[0] < 5 and 0 <= p[1] < 6 and grid[p[0]][p[1]] != "#"
    path = shortest_path((1, 1), [(1, 4)], ok)
    assert len(path) - 1 == 7


def test_no_path():
    ok = lambda p: p in {(1, 1), (1, 2)}              # goal (1, 4) is walled off
    assert shortest_path((1, 1), [(1, 4)], ok) is None


# --- BFS on appartement_01 -------------------------------------------------

def test_to_dictionary():
    goals = adjacent_goals((7, 6), walkable)
    assert len(shortest_path((6, 1), goals, walkable)) - 1 == 5


def test_to_r2():
    goals = adjacent_goals((3, 3), walkable)
    assert len(shortest_path((6, 1), goals, walkable)) - 1 == 4


def test_to_r1_detour():
    goals = adjacent_goals((6, 11), walkable)
    assert len(shortest_path((6, 1), goals, walkable)) - 1 == 17


def test_walled_in_resident():
    blocked = lambda p: walkable(p) and p != (4, 11)  # the only link to the right side
    goals = adjacent_goals((6, 11), blocked)
    assert shortest_path((6, 1), goals, blocked) is None


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