"""
test_sim.py
Headless verification (no game window): drive both solvers through
several seeded 30x30 mazes and confirm they reach the cheese, reporting
how many actions and cell moves each run used.

Run:  python test_sim.py
"""

import time

from maze_generator import MazeGenerator
from agent import Mouse
from solver import FloodFillSolver, LRTASolver, build_observation


def run_one(solver_name, seed, max_iterations=100000):
    maze = MazeGenerator(min_path_length=5, seed=seed).generate(30, 16)
    mouse = Mouse(maze.start, heading="E")
    solver = LRTASolver() if solver_name == "displacement" else FloodFillSolver(maze)

    iterations = 0
    computation_time = 0.0
    while mouse.position != maze.exit and iterations < max_iterations:
        iterations += 1
        t0 = time.perf_counter()
        observation = build_observation(mouse, maze)
        action = solver.decide(observation)
        old_position = mouse.position
        mouse.apply_action(action, maze)
        solver.after_move(old_position, mouse.position, mouse.position != old_position)
        computation_time += time.perf_counter() - t0

    reached = mouse.position == maze.exit
    return reached, iterations, mouse.moves_count, maze.reference_path_length, computation_time


if __name__ == "__main__":
    for solver_name in ("scent", "displacement"):
        reached_count = 0
        for seed in range(10):
            reached, actions, cell_moves, shortest, comp_time = run_one(solver_name, seed)
            reached_count += reached
            print(f"{solver_name:13s} seed={seed}: reached={str(reached):5s} "
                  f"actions={actions:6d}  cell moves={cell_moves:6d}  "
                  f"shortest path={shortest:4d}  computation={comp_time * 1000:.2f}ms")
        print(f"{solver_name}: {reached_count}/10 reached the cheese")
        print("-" * 78)
