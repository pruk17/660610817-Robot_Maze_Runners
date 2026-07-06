"""
game_engine.py
Main game loop: connects all modules together, tracks computation time, checks for death/victory (points 9, 17)
"""

import time

from maze_generator import MazeGenerator
from agent import Mouse
from solver import FloodFillSolver
from renderer_text import TextRenderer

MAX_COMPUTATION_SECONDS = 180  # 3 minutes (point 9)


class GameEngine:
    def __init__(self, size=30, cell_size_cm=16, seed=None,
                 render_mode="pygame", step_delay_ms=60, screenshot_dir=None):
        self.generator = MazeGenerator(min_path_length=5, seed=seed)
        self.maze = self.generator.generate(size, cell_size_cm)
        self.mouse = Mouse(self.maze.start, heading="E")
        self.solver = FloodFillSolver(self.maze)
        self.render_mode = render_mode
        self.step_delay_ms = step_delay_ms
        self.screenshot_dir = screenshot_dir

        if render_mode == "pygame":
            from renderer_pygame import PygameRenderer
            self.renderer = PygameRenderer(self.maze)
        else:
            self.renderer = TextRenderer()

    def run(self, max_steps=100000):
        status_text = ""
        step_no = 0

        while self.mouse.alive and self.mouse.position != self.maze.exit and step_no < max_steps:
            step_no += 1

            # --- นี่คือ "1 ครั้งของ computation time" ---
            t0 = time.perf_counter()
            action = self.solver.decide_next_action(self.mouse, self.maze)
            self.mouse.apply_action(action, self.maze)
            t1 = time.perf_counter()
            self.mouse.total_computation_time += (t1 - t0)
            # --------------------------------------------

            if self.mouse.total_computation_time > MAX_COMPUTATION_SECONDS:
                self.mouse.alive = False
                status_text = "Died: computation time exceeded 3 minutes"
                break

            self._render(status_text)

            if self.screenshot_dir and step_no % 20 == 0 and self.render_mode == "pygame":
                self.renderer.save_screenshot(f"{self.screenshot_dir}/step_{step_no:04d}.png")

            if self.render_mode == "pygame":
                self.renderer.tick(30)
            elif self.step_delay_ms:
                time.sleep(self.step_delay_ms / 1000)

        if self.mouse.position == self.maze.exit:
            status_text = (f"Success! Total steps: {self.mouse.moves_count} | "
                            f"Total computation time: {self.mouse.total_computation_time:.4f} seconds")
            self._render(status_text)
            print(status_text)
        elif not self.mouse.alive:
            print(status_text)

        if self.render_mode == "pygame":
            if self.screenshot_dir:
                self.renderer.save_screenshot(f"{self.screenshot_dir}/final.png")
            self.renderer.wait_and_close(seconds=2)

        return status_text

    def _render(self, status_text):
        if self.render_mode == "pygame":
            self.renderer.render(self.maze, self.mouse, status_text)
        else:
            self.renderer.render(self.maze, self.mouse)
