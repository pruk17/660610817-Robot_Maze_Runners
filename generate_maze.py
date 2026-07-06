"""
generate_maze.py
Entry point script: generate a 30x30 maze (16 cm per cell) with exactly one
entrance and one exit that are always connected to each other, and with a
shortest path of at least 5 steps. Then display it as text and save it as
a PNG image.
"""

from maze_generator import MazeGenerator
from maze_visualizer import MazeTextVisualizer, MazeImageVisualizer

# --- Configuration ---
MAZE_SIZE = 30          # 30 x 30 cells (requirement #3)
CELL_SIZE_CM = 16       # each cell is 16 cm (requirement #4)
MIN_PATH_LENGTH = 5     # shortest path must require at least 5 steps (requirement #6)
SEED = None             # set an integer (e.g. 42) to reproduce the same maze every run


def main():
    generator = MazeGenerator(min_path_length=MIN_PATH_LENGTH, seed=SEED)
    maze = generator.generate(size=MAZE_SIZE, cell_size_cm=CELL_SIZE_CM)

    width_cm, height_cm = maze.real_size_cm()
    print(f"Maze generated: {MAZE_SIZE}x{MAZE_SIZE} cells, "
          f"{CELL_SIZE_CM} cm per cell, real size = {width_cm}x{height_cm} cm")
    print(f"Start point: {maze.start}   Exit point (cheese): {maze.exit}")
    print(f"Shortest path length (BFS): {maze.reference_path_length} steps")
    print("-" * 60)

    # Text rendering (console)
    MazeTextVisualizer().render(maze)

    # Image rendering (PNG file, drawn to real-world scale)
    output_path = MazeImageVisualizer().render(maze, output_path="maze.png")
    print(f"Maze image saved to: {output_path}")


if __name__ == "__main__":
    main()
