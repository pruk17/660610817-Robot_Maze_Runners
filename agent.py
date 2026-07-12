"""
agent.py
Mouse class: the player in the game, tracking its position and current
heading. It moves one cell at a time and can decide between 4 actions per
move: forward, backward, turn left, turn right (requirements #8, #15).
"""

# Clockwise direction order, used to compute left/right turns
CLOCKWISE = ["N", "E", "S", "W"]


class Mouse:
    def __init__(self, position, heading: str = "N"):
        self.position = position       # (row, col)
        self.heading = heading         # direction the mouse is currently facing
        self.alive = True
        self.moves_count = 0
        self.total_computation_time = 0.0
        self.path_history = [position]  # kept only for render/debug, not a precomputed path

    def turn_left(self):
        idx = CLOCKWISE.index(self.heading)
        self.heading = CLOCKWISE[(idx - 1) % 4]

    def turn_right(self):
        idx = CLOCKWISE.index(self.heading)
        self.heading = CLOCKWISE[(idx + 1) % 4]

    def opposite_heading(self):
        idx = CLOCKWISE.index(self.heading)
        return CLOCKWISE[(idx + 2) % 4]

    def apply_action(self, action: str, maze):
        """
        Perform one move based on the action decided by the solver.
        action: "FORWARD" | "BACKWARD" | "TURN_LEFT" | "TURN_RIGHT"
        Turning (TURN_LEFT/TURN_RIGHT) only changes heading, not position.
        Moving (FORWARD/BACKWARD) shifts position by 1 cell, provided there
        is no wall blocking the way.
        """
        if action == "TURN_LEFT":
            self.turn_left()
            return True

        if action == "TURN_RIGHT":
            self.turn_right()
            return True

        if action == "FORWARD":
            direction = self.heading
        elif action == "BACKWARD":
            direction = self.opposite_heading()
        else:
            raise ValueError(f"Unknown action: {action}")

        if not maze.can_move(self.position, direction):
            # Hit a wall -- this move is wasted but the mouse does not die
            return False

        from maze_model import Maze
        dr, dc = Maze.DELTA[direction]
        r, c = self.position
        self.position = (r + dr, c + dc)
        self.moves_count += 1
        self.path_history.append(self.position)
        return True
