"""
solver.py
Two navigation strategies ("brains") for the mouse. Both receive only a
small observation dict built by build_observation() -- never the Maze or
cheese objects themselves -- and return a single action per move:
"FORWARD" | "BACKWARD" | "TURN_LEFT" | "TURN_RIGHT".

  * FloodFillSolver ("scent" mode): the world precomputes a distance
    field (BFS from the cheese along corridors) once at game start.
    The mouse then follows the gradient of that field one step at a
    time. Guarantees the shortest path.

  * LRTASolver ("displacement" mode): LRTA* (Korf, 1990). The mouse
    only knows the straight-line displacement vector to the cheese
    (the dashed line drawn on screen is exactly what it senses) and
    learns better distance estimates as it walks. Nothing is
    precomputed. Reaches the cheese on every finite maze but does not
    guarantee the shortest path.
"""

import math
from collections import deque

from maze_model import Maze
from agent import CLOCKWISE


def build_observation(mouse, maze):
    """
    Build the local observation handed to a solver. This is the ONLY
    window a solver gets into the world -- solvers never receive the
    Maze object or the full grid:
      position        -- the mouse's own (row, col)
      heading         -- the direction the mouse is facing
      open_directions -- which of N/E/S/W are walkable from here
      displacement    -- straight-line vector from mouse to cheese
    """
    r, c = mouse.position
    er, ec = maze.exit
    return {
        "position": mouse.position,
        "heading": mouse.heading,
        "open_directions": maze.neighbors_open(mouse.position),
        "displacement": (er - r, ec - c),
    }


def direction_to_action(direction, heading):
    """Map a target compass direction onto a single allowed action,
    given the current heading (only one turn per move)."""
    if direction == heading:
        return "FORWARD"
    diff = (CLOCKWISE.index(direction) - CLOCKWISE.index(heading)) % 4
    if diff == 2:
        return "BACKWARD"
    return "TURN_RIGHT" if diff == 1 else "TURN_LEFT"


class FloodFillSolver:
    """
    Scent-field navigator. The distance field (computed once, at game
    start) represents "the smell of the cheese has spread through the
    corridors": every cell knows how many steps it is from the cheese.
    Each move the mouse just compares the smell of the walkable
    neighboring cells and steps toward the strongest one.
    """

    def __init__(self, maze: Maze):
        self.distance_field = self._build_distance_field(maze)

    def _build_distance_field(self, maze: Maze):
        size = maze.size
        dist = [[None] * size for _ in range(size)]
        goal = maze.exit
        dist[goal[0]][goal[1]] = 0
        queue = deque([goal])
        while queue:
            r, c = queue.popleft()
            for d in maze.neighbors_open((r, c)):
                dr, dc = Maze.DELTA[d]
                nr, nc = r + dr, c + dc
                if dist[nr][nc] is None:
                    dist[nr][nc] = dist[r][c] + 1
                    queue.append((nr, nc))
        return dist

    def decide(self, observation) -> str:
        r, c = observation["position"]
        best_dir = None
        best_dist = self.distance_field[r][c]
        for d in observation["open_directions"]:
            dr, dc = Maze.DELTA[d]
            nd = self.distance_field[r + dr][c + dc]
            if nd < best_dist:
                best_dist = nd
                best_dir = d

        if best_dir is None:
            # Should never happen in a fully connected maze (unless already at the goal)
            return "FORWARD"
        return direction_to_action(best_dir, observation["heading"])

    def after_move(self, old_position, new_position, moved):
        pass  # stateless between moves -- nothing to remember


class LRTASolver:
    """
    LRTA* -- Learning Real-Time A* (Korf, 1990) -- using the
    straight-line displacement to the cheese as the initial heuristic.

    Perception: only the displacement vector (the dashed line on
    screen). The mouse starts out believing every cell is as close to
    the cheese as it smells in a straight line. Each move it:
      1. looks at the walkable neighbors and their believed distances
         h (first time a cell is seen, h = its straight-line distance),
      2. steps toward the neighbor with the lowest h,
      3. learns: the current cell must be at least (1 + that neighbor's
         h) away, so its own h is raised to that value if it was lower.

    When a dead end "smells close" the mouse walks in, but every pass
    raises the believed distances inside it -- like pouring water into
    a depression until it overflows -- so the trap loses its false
    attraction and the mouse leaves, never to be fooled by it again.
    Guaranteed to reach the goal on any finite maze.

    Unlike exploration-style navigators, this needs no tabu list, no
    visit counts, no randomness: its only memory is the learned h
    table, and identical mazes replay identically.
    """

    def __init__(self):
        self.h = {}  # cell -> believed distance to the cheese (learned)

    def decide(self, observation) -> str:
        r, c = observation["position"]
        gr, gc = observation["displacement"]
        candidates = observation["open_directions"]
        if not candidates:
            return "FORWARD"

        def h_of(d):
            dr, dc = Maze.DELTA[d]
            cell = (r + dr, c + dc)
            if cell not in self.h:
                # First impression of an unseen cell: its straight-line
                # distance, derived from the current displacement vector
                self.h[cell] = math.hypot(gr - dr, gc - dc)
            return self.h[cell]

        best_dir = min(candidates, key=lambda d: (h_of(d), CLOCKWISE.index(d)))

        # LRTA* learning update: standing here costs one step more than
        # the best neighbor, so raise this cell's believed distance
        current = (r, c)
        current_h = self.h.get(current, math.hypot(gr, gc))
        self.h[current] = max(current_h, 1.0 + h_of(best_dir))

        return direction_to_action(best_dir, observation["heading"])

    def after_move(self, old_position, new_position, moved):
        pass  # all learning happens inside decide()
