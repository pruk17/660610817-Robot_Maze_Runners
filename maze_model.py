"""
maze_model.py
Core data structures for the maze: Cell (a single cell) and Maze (the full board).
"""


class Cell:
    """A single cell in the maze. Stores the wall state on 4 sides."""

    def __init__(self):
        # True = wall present (cannot pass through), False = open passage
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited_by_generator = False  # used only during maze generation


class Maze:
    """A size x size maze. Each cell represents cell_size_cm centimeters."""

    OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
    # Position delta (row, col) when moving in each direction
    DELTA = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}

    def __init__(self, size: int = 30, cell_size_cm: int = 16):
        self.size = size
        self.cell_size_cm = cell_size_cm
        self.grid = [[Cell() for _ in range(size)] for _ in range(size)]
        self.start = (0, 0)
        self.exit = (size - 1, size - 1)

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.size and 0 <= c < self.size

    def can_move(self, pos, direction):
        """Check whether moving from pos in the given direction is possible
        (no wall blocking and the destination is inside the grid)."""
        r, c = pos
        if self.grid[r][c].walls[direction]:
            return False
        dr, dc = self.DELTA[direction]
        new_pos = (r + dr, c + dc)
        return self.in_bounds(new_pos)

    def open_wall(self, pos_a, pos_b, direction):
        """Open the wall between cell a and cell b (used during maze generation)."""
        ra, ca = pos_a
        rb, cb = pos_b
        self.grid[ra][ca].walls[direction] = False
        self.grid[rb][cb].walls[self.OPPOSITE[direction]] = False

    def neighbors_open(self, pos):
        """Return the list of directions that are actually walkable from this position."""
        return [d for d in ("N", "S", "E", "W") if self.can_move(pos, d)]

    def real_size_cm(self):
        """Return the real-world size of the whole maze in centimeters."""
        side = self.size * self.cell_size_cm
        return side, side
