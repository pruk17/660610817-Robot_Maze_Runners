"""
maze_visualizer.py
Visualization utilities for a generated Maze: text (console) rendering
and image (PNG) rendering using matplotlib.
"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


class MazeTextVisualizer:
    """Render the maze as ASCII text in the console."""

    def render(self, maze):
        size = maze.size
        lines = []
        for r in range(size):
            top = ""
            mid = ""
            for c in range(size):
                cell = maze.grid[r][c]
                top += "+" + ("---" if cell.walls["N"] else "   ")
                if (r, c) == maze.start:
                    symbol = "S"  # Start point
                elif (r, c) == maze.exit:
                    symbol = "C"  # Cheese / exit point
                else:
                    symbol = " "
                mid += ("|" if cell.walls["W"] else " ") + f" {symbol} "
            lines.append(top + "+")
            lines.append(mid + "|")

        # Bottom border row
        bottom = ""
        for c in range(size):
            bottom += "+" + ("---" if maze.grid[size - 1][c].walls["S"] else "   ")
        lines.append(bottom + "+")

        text = "\n".join(lines)
        print(text)
        return text


class MazeImageVisualizer:
    """Render the maze as a PNG image using matplotlib, drawn to real-world scale."""

    def render(self, maze, output_path="maze.png", show_grid_lines=False):
        size = maze.size
        cell_cm = maze.cell_size_cm
        fig, ax = plt.subplots(figsize=(8, 8))

        # Draw every wall segment as a line, positioned using real cell size (cm)
        for r in range(size):
            for c in range(size):
                cell = maze.grid[r][c]
                x0, y0 = c * cell_cm, (size - 1 - r) * cell_cm  # flip Y so row 0 is on top
                x1, y1 = x0 + cell_cm, y0 + cell_cm

                if cell.walls["N"]:
                    ax.add_line(Line2D([x0, x1], [y1, y1], color="black", linewidth=1.5))
                if cell.walls["S"]:
                    ax.add_line(Line2D([x0, x1], [y0, y0], color="black", linewidth=1.5))
                if cell.walls["W"]:
                    ax.add_line(Line2D([x0, x0], [y0, y1], color="black", linewidth=1.5))
                if cell.walls["E"]:
                    ax.add_line(Line2D([x1, x1], [y0, y1], color="black", linewidth=1.5))

        # Mark start point
        sr, sc = maze.start
        sx = sc * cell_cm + cell_cm / 2
        sy = (size - 1 - sr) * cell_cm + cell_cm / 2
        ax.scatter([sx], [sy], color="dodgerblue", s=120, label="Start", zorder=5)

        # Mark exit point (cheese)
        er, ec = maze.exit
        ex = ec * cell_cm + cell_cm / 2
        ey = (size - 1 - er) * cell_cm + cell_cm / 2
        ax.scatter([ex], [ey], color="gold", s=160, marker="*", label="Cheese (Exit)", zorder=5)

        total_side_cm = size * cell_cm
        ax.set_xlim(-cell_cm * 0.5, total_side_cm + cell_cm * 0.5)
        ax.set_ylim(-cell_cm * 0.5, total_side_cm + cell_cm * 0.5)
        ax.set_aspect("equal")
        ax.set_title(f"Maze {size}x{size} | cell = {cell_cm} cm | "
                     f"real size = {total_side_cm}x{total_side_cm} cm")
        ax.legend(loc="upper right")

        if show_grid_lines:
            ax.set_xticks(range(0, total_side_cm + 1, cell_cm))
            ax.set_yticks(range(0, total_side_cm + 1, cell_cm))
            ax.grid(True, linewidth=0.3, alpha=0.3)
        else:
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
        return output_path
