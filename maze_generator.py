"""
maze_generator.py
Generates a "perfect maze" (a maze where every cell is connected by exactly
one unique path -- this automatically guarantees requirement #5: start and
exit are always reachable from each other) using the Recursive Backtracking
algorithm. After generation, a BFS check ensures the shortest path from
start to exit is at least min_path_length steps (requirement #6);
otherwise the maze is regenerated.
"""

import random
from collections import deque

from maze_model import Maze


class MazeGenerator:
    def __init__(self, min_path_length: int = 5, seed: int = None):
        self.min_path_length = min_path_length
        self.rng = random.Random(seed)

    def generate(self, size: int = 30, cell_size_cm: int = 16) -> Maze:
        """Generate a maze, regenerating until the shortest path requirement is met."""
        while True:
            maze = self._carve_maze(size, cell_size_cm)
            path_len = self._shortest_path_length(maze)
            if path_len >= self.min_path_length:
                maze.reference_path_length = path_len
                return maze
            # Too short (extremely unlikely for a 30x30 maze) -> try again

    def _carve_maze(self, size, cell_size_cm) -> Maze:
        """Carve passages using randomized DFS (iterative recursive backtracking)."""
        maze = Maze(size, cell_size_cm)
        stack = [(0, 0)]
        maze.grid[0][0].visited_by_generator = True
        visited_count = 1
        total_cells = size * size

        while stack:
            r, c = stack[-1]
            unvisited_dirs = []
            for d, (dr, dc) in Maze.DELTA.items():
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and not maze.grid[nr][nc].visited_by_generator:
                    unvisited_dirs.append((d, (nr, nc)))

            if not unvisited_dirs:
                # Dead end -- backtrack
                stack.pop()
                continue

            # Pick a random unvisited neighbor and carve a passage to it
            direction, (nr, nc) = self.rng.choice(unvisited_dirs)
            maze.open_wall((r, c), (nr, nc), direction)
            maze.grid[nr][nc].visited_by_generator = True
            visited_count += 1
            stack.append((nr, nc))

        maze.start = (0, 0)
        maze.exit = (size - 1, size - 1)
        return maze

    def _shortest_path_length(self, maze: Maze) -> int:
        """BFS to find the shortest path length (number of steps) from start to exit."""
        start, goal = maze.start, maze.exit
        visited = {start}
        queue = deque([(start, 0)])
        while queue:
            pos, dist = queue.popleft()
            if pos == goal:
                return dist
            for d in maze.neighbors_open(pos):
                dr, dc = Maze.DELTA[d]
                new_pos = (pos[0] + dr, pos[1] + dc)
                if new_pos not in visited:
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
        return -1  # should never happen since a perfect maze connects everything
