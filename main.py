"""
main.py
Main entry point - runs the cheese-finding game in a 30x30 maze, 16 cm per cell
"""

from game_engine import GameEngine

if __name__ == "__main__":
    game = GameEngine(
        size=30,
        cell_size_cm=16,
        seed=None,          # Set a number if you want to generate the same maze every time, e.g., seed=42
        solver="displacement",  # "displacement" = straight-line smell (no precomputation)
                                 # "scent"        = flood-fill distance field (shortest path)
    )
    game.run()
