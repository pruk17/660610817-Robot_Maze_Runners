"""
solver.py
FloodFillSolver: simulates the "cheese scent" that the mouse can sense in
every cell (a distance-to-cheese value per cell), but the mouse still only
decides a single move at a time (turn left/right/forward/backward).
No full path is precomputed or stored (requirement #16) -- only a
per-cell distance field (like a scent) is available.
"""

from collections import deque

from maze_model import Maze
from agent import CLOCKWISE


class FloodFillSolver:
    def __init__(self, maze: Maze):
        # Compute the "scent field" (distance field) from the exit to every
        # cell once, at the start of the game. This represents "the mouse
        # can smell the cheese" (requirement #12), but it is not a
        # ready-made path -- the mouse still has to decide its own moves
        # step by step based on this field.
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

    def decide_next_action(self, mouse, maze: Maze) -> str:
        """
        Decide a single action for this move only. Looks at the distance
        (scent) value of the walkable neighboring cells and picks the
        direction closest to the cheese. If that direction doesn't match
        the current heading, the mouse must turn first (1 move = only one
        turn at a time).
        """
        r, c = mouse.position
        current_dist = self.distance_field[r][c]

        best_dir = None
        best_dist = current_dist
        for d in maze.neighbors_open((r, c)):
            dr, dc = Maze.DELTA[d]
            nr, nc = r + dr, c + dc
            nd = self.distance_field[nr][nc]
            if nd < best_dist:
                best_dist = nd
                best_dir = d

        if best_dir is None:
            # Should never happen in a fully connected maze (unless already at the goal)
            return "FORWARD"

        if best_dir == mouse.heading:
            return "FORWARD"
        if best_dir == mouse.opposite_heading():
            return "BACKWARD"

        # Needs to turn -- decide left or right (only one turn per move)
        idx_current = CLOCKWISE.index(mouse.heading)
        idx_target = CLOCKWISE.index(best_dir)
        diff = (idx_target - idx_current) % 4
        return "TURN_RIGHT" if diff == 1 else "TURN_LEFT"
