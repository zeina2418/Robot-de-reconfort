from collections import deque # double ended data structure that alows us to remove and add elements from both ends of a queue 

# Fixed order = deterministic paths. Positions are (line, column).
# Direction name + coordinate change
DIRECTIONS = (("N", (-1, 0)), ("S", (1, 0)), ("E", (0, 1)), ("O", (0, -1)))


# calculates the four positions surrounding a given position
# for example neighbors(2,3) returns : [(1, 3), (3, 3), (2, 4), (2, 2)]
def neighbors(pos):
    return [(pos[0] + dl, pos[1] + dc) for _, (dl, dc) in DIRECTIONS]


# here is the implementation of the BFS algorithm 
# it takes in : the strating postion, the goal position, and a boolean function deciding if we've hit a wall or not
def shortest_path(start, goals, is_walkable):
    # BFS. Returns a list of positions from start to a goal, or None.
    goals = set(goals)
    if start in goals:
        return [start] # if the goal position is the current position then a list containing the current position is returned 
    pred = {start: None}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for nxt in neighbors(current):
            if nxt in pred or not is_walkable(nxt):
                continue
            pred[nxt] = current
            if nxt in goals:
                return _rebuild(pred, nxt)
            queue.append(nxt)
    return None


def _rebuild(pred, cell):
    path = [cell]
    while pred[path[-1]] is not None:
        path.append(pred[path[-1]])
    return path[::-1]


def adjacent_goals(target, is_walkable):
    # Tiles from which the robot can interact with a target (A, D or P).
    return [n for n in neighbors(target) if is_walkable(n)]


def to_directions(path):
    # [(1,1),(2,1)] -> ['S']
    names = {delta: name for name, delta in DIRECTIONS}
    return [names[(b[0] - a[0], b[1] - a[1])] for a, b in zip(path, path[1:])]