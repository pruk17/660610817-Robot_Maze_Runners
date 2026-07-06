"""
renderer_text.py
render Text in console (point 14: text mode)
"""


class TextRenderer:
    def render(self, maze, mouse):
        size = maze.size
        lines = []
        # write line by line each block is 2 characters (cell character + right wall)
        for r in range(size):
            top = ""
            mid = ""
            for c in range(size):
                cell = maze.grid[r][c]
                top += "+" + ("---" if cell.walls["N"] else "   ")
                if (r, c) == mouse.position:
                    symbol = {"N": "^", "S": "v", "E": ">", "W": "<"}[mouse.heading]
                elif (r, c) == maze.exit:
                    symbol = "C"  # Cheese
                elif (r, c) == maze.start:
                    symbol = "S"
                else:
                    symbol = " "
                mid += ("|" if cell.walls["W"] else " ") + f" {symbol} "
            lines.append(top + "+")
            lines.append(mid + "|")
        # lower wall of the last row
        bottom = ""
        for c in range(size):
            bottom += "+" + ("---" if maze.grid[size - 1][c].walls["S"] else "   ")
        lines.append(bottom + "+")

        print("\n".join(lines))
        print(f"Position: {mouse.position}  Heading: {mouse.heading}  "
              f"Moves: {mouse.moves_count}  Total Computation Time: {mouse.total_computation_time:.4f}s")
        print("-" * 60)
