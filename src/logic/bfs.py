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
    # pred is a dictionary of predecessors. It records where each discovered position came from.
    pred = {start: None}
    # The queue starts with only the starting position
    queue = deque([start])
    while queue:# repeat as long as the queue is not empty.
        current = queue.popleft() # removes the oldest position and stores it in current
        # checking the surrounding neighbors of the current position
        for nxt in neighbors(current):
            if nxt in pred or not is_walkable(nxt): # checking that we're not hitting a wall
                continue
            pred[nxt] = current # If the position is valid and has not been discovered, record the position from which it was reached.
            # Check whether the destination has been found
            if nxt in goals:
                # As soon as a neighboring position belongs to the set of goals, the function reconstructs and returns the path.
                return _rebuild(pred, nxt)
            # Otherwise, add the position to the queue
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



