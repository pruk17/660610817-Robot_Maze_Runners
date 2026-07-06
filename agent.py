"""
agent.py
Mouse class: The player in the game. Has a position and a heading.
Can move one cell at a time and decide on 4 actions per move:
Move forward, move backward, turn left, turn right (points 8, 15)
"""

# Clockwise direction order for calculating left/right turns
CLOCKWISE = ["N", "E", "S", "W"]


class Mouse:
    def __init__(self, position, heading: str = "N"):
        self.position = position       # (row, col)
        self.heading = heading         # The direction the mouse is facing
        self.alive = True
        self.moves_count = 0
        self.total_computation_time = 0.0
        self.path_history = [position]  # Store for rendering/debugging only, not the actual known path

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
        Performs 1 movement based on the action decided by the solver
        action: "FORWARD" | "BACKWARD" | "TURN_LEFT" | "TURN_RIGHT"
        Turning (TURN_LEFT/TURN_RIGHT) only changes the heading without moving the position
        Moving (FORWARD/BACKWARD) moves the position by 1 cell according to the condition that there is no wall blocking the way
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
            # Hit a wall - consider this move as failed but not fatal (just don't move)
            return False

        from maze_model import Maze
        dr, dc = Maze.DELTA[direction]
        r, c = self.position
        self.position = (r + dr, c + dc)
        self.moves_count += 1
        self.path_history.append(self.position)
        return True
