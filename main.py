"""
main.py
Main entry point - runs the cheese-finding game in a 30x30 maze, 16 cm per cell
"""

from game_engine import GameEngine

if __name__ == "__main__":
    game = GameEngine(
        size=30,
        cell_size_cm=16,
        seed=None,          # Insert a number if you want to generate the same maze every time, e.g., seed=42
        render_mode="pygame",   # Change to "text" if you want to see the console version
        step_delay_ms=60,
    )
    game.run()
