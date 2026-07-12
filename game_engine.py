"""
game_engine.py
The main game loop: wires all modules together, tracks computation time,
and checks the death/win conditions (requirements #9, #17).
"""

import time

from maze_generator import MazeGenerator
from agent import Mouse
from solver import FloodFillSolver
from renderer_pygame import PygameRenderer

MAX_COMPUTATION_SECONDS = 180  # 3 minutes (requirement #9)


class GameEngine:
    def __init__(self, size=30, cell_size_cm=16, seed=None, screenshot_dir=None):
        self.generator = MazeGenerator(min_path_length=5, seed=seed)
        self.maze = self.generator.generate(size, cell_size_cm)
        self.mouse = Mouse(self.maze.start, heading="E")
        self.solver = FloodFillSolver(self.maze)
        self.screenshot_dir = screenshot_dir
        self.renderer = PygameRenderer(self.maze, MAX_COMPUTATION_SECONDS)

    def run(self, max_steps=100000):
        status_text = ""
        step_no = 0
        run_start = time.perf_counter()

        while self.mouse.alive and self.mouse.position != self.maze.exit and step_no < max_steps:
            step_no += 1

            # --- This block represents ONE unit of "computation time" ---
            t0 = time.perf_counter()
            action = self.solver.decide_next_action(self.mouse, self.maze)
            self.mouse.apply_action(action, self.maze)
            t1 = time.perf_counter()
            self.mouse.total_computation_time += (t1 - t0)
            # --------------------------------------------------------------

            if self.mouse.total_computation_time > MAX_COMPUTATION_SECONDS:
                self.mouse.alive = False
                status_text = "Mouse died: exceeded 3 minutes of computation time"
                break

            self._render(status_text, time.perf_counter() - run_start)

            if self.screenshot_dir and step_no % 20 == 0:
                self.renderer.save_screenshot(f"{self.screenshot_dir}/step_{step_no:04d}.png")

            self.renderer.tick(30)

        total_elapsed = time.perf_counter() - run_start

        if self.mouse.position == self.maze.exit:
            status_text = (f"Success! Steps: {self.mouse.moves_count} | "
                            f"Time: {total_elapsed:.2f}s")
            print(f"Success! Total steps: {self.mouse.moves_count} | "
                  f"Total time (real): {total_elapsed:.4f}s | "
                  f"Computation time (algo): {self.mouse.total_computation_time * 1000:.4f}ms "
                  f"/ {MAX_COMPUTATION_SECONDS * 1000}ms budget")
            self._render(status_text, total_elapsed)
        elif not self.mouse.alive:
            print(status_text)

        if self.screenshot_dir:
            self.renderer.save_screenshot(f"{self.screenshot_dir}/final.png")
        self.renderer.wait_and_close(seconds=2)

        return status_text

    def _render(self, status_text, total_elapsed=0.0):
        self.renderer.render(self.maze, self.mouse, status_text, total_elapsed)
